from flask import render_template, flash, url_for, redirect, request, send_from_directory, abort, escape, make_response, jsonify
from app import app, db, models
import os
import sys
from app.forms import LoginForm, WorkForm
from app.models import Schools, Media, Work
from flask_login import current_user, login_user, logout_user, login_required, AnonymousUserMixin
from flask_cors import CORS
from werkzeug.utils import secure_filename
from contextlib import contextmanager
from sqlalchemy.orm import exc as sqlalchemy_exc

CORS(app)

max_characters_allowed_bio = 190
max_characters_allowed_work_title = 50
max_characters_allowed_work_desc = 350

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = db.Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

@app.route('/')
def index():
    works = Work.query.all()
    return render_template('index.html', works=works[:3], title='Home')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('/errors/404.html')


@app.errorhandler(500)
def server_error(error):
    return render_template('/errors/500.html')


@app.route('/schools')
def school_index():
    return render_template('/schools/index.html', title='Schools')


def get_author_from_id(author_id):
    return Schools.query.filter_by(id=author_id).all()[0].name


def true_if_owner(obj, author):
    ownership = False
    try:
        if obj.author_id == author.id:
            ownership = True
    except AttributeError:
        print('Attribute error in is_owner()', file=sys.stdout)
    return ownership


app.jinja_env.globals.update(get_author_from_id=get_author_from_id)


@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):

    date = date.format()
    native = date.replace(tzinfo=None)
    format_string ='%b %d, %Y'
    return native.strftime(format_string)


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


@app.route('/schools/Regionale-Scholengemeenschap-t-Rijks')
def school_netherlands():
    netherlands = Schools.query.filter_by(country='The Netherlands').first()
    return populate_school_template(netherlands)


@app.route('/schools/Arsakeio-Tositseio-Lykeio-Ekalis')
def school_greece():
    greece = Schools.query.filter_by(country='Greece').first()
    return populate_school_template(greece)


@app.route('/schools/Lycee-Vauban')
def school_france():
    france = Schools.query.filter_by(country='France').first()
    return populate_school_template(france)


@app.route('/schools/Gimnazija-Kran')
def school_slovenia():
    slovenia = Schools.query.filter_by(country='Slovenia').first()
    return populate_school_template(slovenia)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Schools.query.filter_by(username=form.username.data).first()
        if user is None or not user.validate_password(form.password.data):
            return redirect(url_for('login'))

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
                img_ids = []
                for media in author_media:
                    img_urls.append(media.path[5:])
                    img_ids.append(media.id)
                return jsonify({'ids': img_ids, 'urls': img_urls})
            else:
                return '', 404
        else:
            return '', 200

    if request.method == 'POST':
        content = request.get_json(silent=True)
        request_type = content['type']
        print('[ POST type = {} ]'.format(request_type), file=sys.stdout)
        # Edit school description
        if request_type == 1:
            description = content['description'].strip()
            description = (description[:max_characters_allowed_bio]) \
                if len(description) > max_characters_allowed_bio else description

            if current_user.description.split() != description.split():
                current_user.description = description
                db.session.commit()
                print(current_user.description + '\n + \n' + description, file=sys.stdout)
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
            title = content['title'].strip()
            title = (title[:max_characters_allowed_work_title]) \
                if len(title) > max_characters_allowed_work_title else title
            description = content['description'].strip()
            description = (description[:max_characters_allowed_work_desc]) \
                if len(description) > max_characters_allowed_work_desc else description
            attached_media = content['attached_media']
            id_list = []
            print(attached_media, file=sys.stdout)
            for media in attached_media:
                try:
                    path = media[25:]
                    id_list.append(str(Media.query.filter(Media.path.contains(path)).first().id))
                except TypeError:
                    pass
            id_list = ','.join(id_list)
            description = (description[:max_characters_allowed_bio]) \
                if len(description) > max_characters_allowed_bio else description

            if true_if_owner(selected_work, current_user):

                selected_work.title = title
                selected_work.description = description
                selected_work.attached_media = id_list
                db.session.commit()

    return '', 204


@app.route('/upload', methods=['POST'])
@login_required
def upload_handler():
    file = request.files['file']

    # Making the filename unique
    n_occurences = file.filename.count('.')
    split_filename = file.filename.split('.')
    filename = ''
    if n_occurences:
        for i in range(n_occurences + 1):
            string = split_filename[i]
            # This is the true extension
            if i == n_occurences:
                filename += str(current_user.id) + '.' + string
            else:
                filename += string + '_'

    ret = allowed_media(filename)
    upload_flag = ret[0]
    media_type = ret[1]

    if upload_flag:
        save_path = os.path.join(app.config["MEDIA_UPLOADS"], secure_filename(filename))
        current_chunk = int(request.form['dzchunkindex'])
        # If the file already exists it's ok if we are appending to it,
        # but not if it's new file that would overwrite the existing one

        if os.path.exists(save_path) and current_chunk == 0:
            return make_response(('You already uploaded this file', 400))

        try:
            with open(save_path, 'ab') as f:
                f.seek(int(request.form['dzchunkbyteoffset']))
                f.write(file.stream.read())
        except OSError:
            # log.exception will include the traceback so we can see what's wrong
            #log.exception('Could not write to file')
            return make_response(("Not sure why,"
                                  " but we couldn't write the file to disk", 500))

        total_chunks = int(request.form['dztotalchunkcount'])
        if current_chunk + 1 == total_chunks:
            # This was the last chunk, the file should be complete and the size we expect
            if os.path.getsize(save_path) != int(request.form['dztotalfilesize']):
                #log.error(f"File {file.filename} was completed, "
                          #f"but has a size mismatch."
                          #f"Was {os.path.getsize(save_path)} but we"
                          #f" expected {request.form['dztotalfilesize']} ")
                return make_response(('Size mismatch', 500))
            else:
                #log.info(f'File {file.filename} has been uploaded successfully')
                new_media = Media(
                    author_id=current_user.id,
                    path=save_path,
                    type=media_type
                )
                db.session.add(new_media)
                db.session.commit()
    else:
        return make_response(("Invalid filetype supplied.", 500))
    return make_response(("Upload successful", 200))


def allowed_media(filename):

    response_bool = None
    response_filetype = None
    if '.' not in filename:
        response_bool = False
    if response_bool is None:
        n_occurrences = filename.count('.')
        if n_occurrences == 1:
            ext = filename.rsplit('.', 1)[1]
        else:
            raise ValueError('Invalid filename supplied in allowed_media, ')

        print('n: ' + str(n_occurrences) + '  ' + filename + ' Wowowow ' + ext.upper(), file=sys.stdout)
        if ext.upper() in app.config['ALLOWED_IMAGE_EXTENSIONS']:
            response_filetype = 1
            response_bool = True
        elif ext.upper() in app.config['ALLOWED_VIDEO_EXTENSIONS']:
            response_filetype = 2
            response_bool = True
        elif ext.upper() in app.config['ALLOWED_PDF_EXTENSIONS']:
            response_filetype = 3
            response_bool = True
        else:
            response_bool = False
    return [response_bool, response_filetype]


@app.route('/works/<work_id>', methods=('GET', 'POST'))
def user_work(work_id):
    current_work = Work.query.filter_by(id=work_id).first()
    if current_work is not None:
        is_owner = true_if_owner(current_work, current_user)
        media_list = []
        attached_media = []
        attached_media_new = []

        try:
            attached_media = current_work.attached_media.split(',')
        except AttributeError:
            pass
        for idx, media_id in enumerate(attached_media):
            if Media.query.filter_by(id=media_id).scalar() is not None:
                attached_media_new.append(str(media_id))
                media_list.append(Media.query.filter_by(id=media_id).one())

        if attached_media_new != attached_media:
            current_work.attached_media = ','.join(attached_media_new)
            db.session.commit()

        form = WorkForm()

        return render_template(
            '/works/work.html',
            work=current_work,
            is_owner=is_owner,
            form=form,
            media_list=media_list)
    else:
        abort(404)

@app.route('/works/new-work', methods=('GET', 'POST'))
@login_required
def new_work():
    form = WorkForm()
    print('wow', file=sys.stdout)
    if request.method == 'POST':

        content = request.get_json()
        title = content['title'].strip()
        title = (title[:max_characters_allowed_work_title]) \
            if len(title) > max_characters_allowed_work_title else title
        description = content['description'].strip()
        description = (description[:max_characters_allowed_work_desc]) \
            if len(description) > max_characters_allowed_work_desc else description
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
    if true_if_owner(work, current_user):
        db.session.delete(work)
        db.session.commit()

    return '', 204

@app.route('/media/delete', methods=['POST'])
@login_required
def delete_media():
    media_id = request.get_json()["media_id"]
    media = None
    try:
        media = Media.query.filter_by(id=media_id).one()
    except sqlalchemy_exc.NoResultFound:
        pass
    except Exception:
        raise
    if media is not None and true_if_owner(media, current_user):
        db.session.delete(media)
        db.session.commit()
        try:
            os.remove(media.path)
        except FileNotFoundError:
            pass
        except Exception:
            raise

    return '', 204