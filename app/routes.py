from flask import render_template, flash, url_for, redirect, request, send_from_directory, abort, escape, make_response, jsonify
from app import app, db
import os
import sys
from app.forms import LoginForm, WorkForm
from app.models import Schools, Media, Work
from flask_login import current_user, login_user, logout_user, login_required, AnonymousUserMixin
from dateutil import parser
from werkzeug.urls import url_parse
from flask_cors import CORS

CORS(app)

max_characters_allowed_bio = 190
max_characters_allowed_work_title = 50
max_characters_allowed_work_desc = 350

@app.route('/')
def index():
    works = Work.query.all()
    return render_template('index.html', works=works[:3], title='Home')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('/errors/404.html')


@app.errorhandler(500)
def page_not_found(error):
    return render_template('/errors/500.html')


@app.route('/schools')
def school_index():
    return render_template('/schools/index.html', title='Schools')


def get_author_from_id(author_id):
    return Schools.query.filter_by(id=author_id).all()[0].name


app.jinja_env.globals.update(get_author_from_id=get_author_from_id)

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):

    date = date.format()
    native = date.replace(tzinfo=None)
    format='%b %d, %Y'
    return native.strftime(format)

@app.route('/works')
def work_index():
    return render_template(
        '/works/index.html',
        title='Works',
        works=Work.query.all())


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(
            app.root_path,
            'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.ico')


@app.route('/schools/user-page')
@login_required
def user_page():

    return populate_school_template(current_user, is_school_owner=1)


def populate_school_template(school_obj, is_school_owner=0):

    header_img_filename = 'resources/' + school_obj.header_img
    works = Work.query.filter_by(author_id=school_obj.id).all()
    media_list = Media.query.filter_by(author_id=school_obj.id).all()
    images_path = []
    videos_path = []
    for media in media_list:
        path = media.path
        path = path[5:]
        if media.type == 1:
            images_path.append(path)
        elif media.type == 2:
            videos_path.append(path)
        else:
            pass
    if school_obj.description is not None and len(school_obj.description) < 1:
        description = 'You can write whatever you want here!'
    else:
        description = school_obj.description

    return render_template('/schools/school-template.html',
                           user=school_obj,
                           description=description,
                           header_img_filename=header_img_filename,
                           is_school_owner=is_school_owner,
                           media_list=media_list,
                           works=works)


@app.route('/schools/Sandnes-videregaende-skole')
def school_norway():
    norway = Schools.query.filter_by(country='Norway').first()
    return populate_school_template(norway)


@app.route('/schools/Liceo-Scientifico-Statale-Galileo-Galilei')
def school_italy():
    italy = Schools.query.filter_by(country='Italy').first()
    return populate_school_template(italy)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Schools.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        print(form.remember_me.data, file=sys.stdout)
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/backend', methods=['POST', 'GET'])
@login_required
def handle_request():

    if request.method == 'GET':
        if request.args:
            request_type = int(request.args.get('t'))
            if request_type == 1:
                author_media = Media.query.filter_by(author_id=current_user.id).all()
                img_urls = []
                for media in author_media:
                    img_urls.append(media.path[5:])
                    print(media.path[5:], file=sys.stdout)
                return jsonify(img_urls)
            elif request_type == 2:
                latest_work = db.session.query(Work).filter(Work.id == db.session.query(db.func.max(Work.id)))
            else:
                return '', 404
        else:
            return '', 200

    if request.method == 'POST':
        content = request.get_json(silent=True)
        request_type = content['type']

        # Edit school description
        if request_type == 1:
            description = content['description']
            description = (description[:max_characters_allowed_bio]) \
                if len(description) > max_characters_allowed_bio else description

            if current_user.description.split() != description.split():
                current_user.description = description
                #print(len(description), file=sys.stdout)
                db.session.commit()
            return '', 204
        elif request_type == 2:
            image = request.files['image']

            image.save(
                os.path.join(
                    app.config["IMAGE_UPLOADS"],
                    image.filename))
        elif request_type == 3:
            work_id = content['work_id']
            selected_work = Work.query.get_or_404(work_id)
            title = content['title']
            title = (title[:max_characters_allowed_work_title]) \
                if len(title) > max_characters_allowed_work_title else title
            description = content['description']
            description = (description[:max_characters_allowed_work_desc]) \
                if len(title) > max_characters_allowed_work_desc else title
            attached_media = content['attached_media']
            id_list = []

            for media in attached_media:
                path = media[25:]

                id_list.append(str(Media.query.filter(Media.path.contains(path)).first().id))
            id_list = ','.join(id_list)
            description = (description[:max_characters_allowed_bio]) \
                if len(description) > max_characters_allowed_bio else description

            if selected_work.author_id == current_user.id:
                if selected_work.title.split() != title.split():
                    selected_work.title = title
                if selected_work.description.split() != description.split():
                    selected_work.description = description
                if selected_work.attached_media != id_list:
                    selected_work.attached_media = id_list
                else:
                    pass
                db.session.commit()


    return '', 204


@app.route('/upload', methods=['POST'])
@login_required
def upload_handler():
    media = request.files['media']
    filename = media.filename
    ret = allowed_media(filename)
    upload_flag = ret[0]
    #print(upload_flag, file=sys.stdout)
    media_type = ret[1]
    if upload_flag:
        image_path = os.path.join(app.config["IMAGE_UPLOADS"], filename)
        new_media = Media(
            author_id=current_user.id,
            path=image_path,
            type=media_type
        )
        db.session.add(new_media)
        db.session.commit()
        media.save(image_path)
    return '', 204


def allowed_media(filename):
    if '.' not in filename:
        return False

    ext = filename.rsplit('.', 1)[1]

    if ext.upper() in app.config['ALLOWED_IMAGE_EXTENSIONS']:
        return [True, 1]
    elif ext.upper() in app.config['ALLOWED_VIDEO_EXTENSIONS']:
        return [True, 2]
    else:
        return False


@app.route('/works/<work_id>', methods=('GET', 'POST'))
def user_work(work_id):
    current_work = Work.query.get_or_404(work_id)
    is_owner = 0
    if current_work.author_id == current_user.id:
        is_owner = 1
    media_list = []
    attached_media = []
    try:
        attached_media = current_work.attached_media.split(',')
    except AttributeError:
        pass
    for media_id in attached_media:
        media_list.append(Media.query.get_or_404(media_id))

    form = WorkForm()
    print('getting request', file=sys.stdout)
    return render_template(
        '/works/work.html',
        work=current_work,
        is_owner=is_owner,
        form=form,
        media_list=media_list)

@app.route('/works/new-work', methods=('GET', 'POST'))
@login_required
def new_work():
    form = WorkForm()
    print('wow', file=sys.stdout)
    if request.method == 'POST':

        content = request.get_json()
        title = content['title']
        title = (title[:max_characters_allowed_work_title]) \
            if len(title) > max_characters_allowed_work_title else title
        description = content['description']
        description = (description[:max_characters_allowed_work_desc]) \
            if len(title) > max_characters_allowed_work_desc else title
        attached_media = content['attached_media']
        id_list = []
        for media in attached_media:
            path = media[25:]
            id_list.append(str(Media.query.filter(Media.path.contains(path)).first().id))
        id_list = ','.join(id_list)

        work = Work(author_id=current_user.id, title=title, description=description, attached_media=id_list)
        db.session.add(work)
        db.session.commit()

        return jsonify(work.id)
    else:
        print('wow - 1', file=sys.stdout)
        return render_template(
            '/works/new-work.html',
            form=form)


@app.route('/works/delete', methods=['POST'])
@login_required
def delete_work():
    print(request.get_json(), file=sys.stdout)
    work_id = request.get_json()["work_id"]
    print('Work_id: ' + str(work_id), file=sys.stdout)
    work = Work.query.filter_by(id=work_id).one()
    if work.author_id == current_user.id:
        db.session.delete(work)
        db.session.commit()

    return '', 204