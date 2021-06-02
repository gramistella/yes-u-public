from flask import render_template, url_for, redirect, request, send_from_directory, abort, make_response, jsonify
from app import app, db
import os
import sys
from app.forms import LoginForm, WorkForm
from app.models import Schools, Media, Work
from flask_login import current_user, login_user, logout_user, login_required
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from sqlalchemy.orm import exc as sqlalchemy_exc
from moviepy.editor import VideoFileClip
from PIL import Image, ImageDraw, ImageFont
from datetime import timedelta

CORS(app)

max_characters_allowed_bio = 2013
max_characters_allowed_work_title = 50
max_characters_allowed_work_desc = 2013


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


def get_footer():
    desc = "Made with ♥ by <a href=\"https://github.com/gramistella\">Giovanni Ramistella</a>  | Liceo Galileo Galilei, CT"
    return desc


app.jinja_env.globals.update(
    get_author_from_id=get_author_from_id,
    get_footer=get_footer
)


def true_if_owner(obj, author):
    ownership = False
    try:
        if obj.author_id == author.id or author.id == 7:
            ownership = True
    except AttributeError:
        print('Attribute error in is_owner()', file=sys.stdout)
    return ownership


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):

    date = date.format()
    native = date.replace(tzinfo=None)
    format_string = '%b %d, %Y'
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
    if current_user.username == "admin":
        template = populate_admin_template(current_user)
    else:
        template = populate_school_template(current_user, is_school_owner=1)
    return template


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
                           enable_user_buttons=True,
                           is_school_owner=is_school_owner,
                           media_list=media_list,
                           works=works)


def populate_admin_template(admin_obj):

    header_img_filename = "" #'resources/' + school_obj.header_img
    works = Work.query.all()
    media_list = Media.query.all()
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
    description = "From here you can edit/delete all content uploaded on the website. Editing the attached media " \
                  " on a published work is not available."

    return render_template('/schools/school-template.html',
                           user=admin_obj,
                           description=description,
                           header_img_filename=header_img_filename,
                           enable_user_buttons=False,
                           is_school_owner=True,
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


@app.route('/schools/<school_id>')
def school_handler(school_id):
    school_page = None
    school_id = safe_cast(school_id, int)
    if school_id == 1:
        school_page = 'norway'
    elif school_id == 2:
        school_page = 'italy'
    elif school_id == 3:
        school_page = 'netherlands'
    elif school_id == 4:
        school_page = 'greece'
    elif school_id == 5:
        school_page = 'france'
    elif school_id == 6:
        school_page = 'slovenia'

    if school_page is not None:
        school_page = 'school_' + school_page
        return redirect(url_for(school_page), code=302)
    else:
        return redirect(url_for('index'))


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
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
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
        #print('[ POST type = {} ]'.format(request_type), file=sys.stdout)
        # Edit school description
        if request_type == 1:
            description = content['description'].strip()
            description = (description[:max_characters_allowed_bio]) \
                if len(description) > max_characters_allowed_bio else description
            if current_user.description.split() != description.split():
                current_user.description = description.replace("\n", " ")
                db.session.commit()
                #print(current_user.description + '\n + \n' + description, file=sys.stdout)
            return '', 204
        # Edit school description
        elif request_type == 2:
            image = request.files['image']

            image.save(
                os.path.join(
                    app.config["IMAGE_UPLOADS"],
                    image.filename))
        # Edit work
        elif request_type == 3:
            work_id = content['work_id']
            selected_work = Work.query.get_or_404(work_id)
            title = content['title'].strip()
            title = (title[:max_characters_allowed_work_title]) \
                if len(title) > max_characters_allowed_work_title else title
            description = content['description'].replace("\n", " ").strip()
            description = (description[:max_characters_allowed_work_desc]) \
                if len(description) > max_characters_allowed_work_desc else description
            attached_media = content['attached_media']
            id_list = []
            print(len(description), file=sys.stdout)
            for media in attached_media:
                try:
                    path = media[25:]
                    id_list.append(str(Media.query.filter(Media.path.contains(path)).first().id))
                except (TypeError, AttributeError) as e:
                    pass
            id_list = ','.join(id_list)

            if true_if_owner(selected_work, current_user):

                selected_work.title = title
                selected_work.description = description
                selected_work.attached_media = id_list
                db.session.commit()

    return '', 204


def poster_processing(poster_path, duration):

    poster = Image.open(poster_path)
    poster.thumbnail((230, 230), Image.ANTIALIAS)

    # dimensions
    poster_width, poster_height = poster.size
    font = ImageFont.truetype("arial.ttf", 17)
    duration_string = str(timedelta(seconds=round(duration)))
    text_size = font.getsize(duration_string)
    button_size = (text_size[0] + 20, text_size[1] + 20)
    button_img = Image.new('RGBA', button_size, "black")

    # put text on button with 10px margins
    button_draw = ImageDraw.Draw(button_img)
    button_draw.text((5, 0), duration_string, font=font)

    poster.paste(button_img, (poster_width-65, poster_height-20))

    poster.save(poster_path)
    button_img.close()
    poster.close()


@app.route('/upload', methods=['POST'])
@login_required
@cross_origin()
def upload_handler():
    file = request.files['file']

    # Making the filename unique
    n_occurrences = file.filename.count('.')
    split_filename = file.filename.split('.')
    filename = ''
    if n_occurrences:
        for i in range(n_occurrences + 1):
            string = split_filename[i]
            # This is the true extension
            if i == n_occurrences:
                filename += str(current_user.id) + '.' + string
            else:
                filename += string + '_'

    ret = allowed_media(filename)
    upload_flag = ret[0]
    media_type = ret[1]
    save_path = os.path.join(app.config["MEDIA_UPLOADS"], secure_filename(filename)).replace('\\', '/')
    poster_filename = filename.split('.')[0] + '.png'
    poster_save_path = os.path.join(app.config["MEDIA_POSTERS"], secure_filename(poster_filename)).replace('\\', '/')
    if upload_flag:

        current_chunk = int(request.form['dzchunkindex'])
        total_chunks = int(request.form['dztotalchunkcount'])
        upload_size = int(request.form['dztotalfilesize'])

        # If the file already exists it's ok if we are appending to it,
        # but not if it's new file that would overwrite the existing one
        if os.path.exists(save_path) and current_chunk == 0:

            local_size = os.stat(save_path).st_size
            if upload_size > local_size:
                os.remove(save_path)
                return make_response(('Detected an interrupted upload. Please try again', 500))
            else:
                return make_response(('You already uploaded this file', 400))

        try:
            with open(save_path, 'ab') as f:
                f.seek(int(request.form['dzchunkbyteoffset']))
                f.write(file.stream.read())
        except OSError:
            return make_response(("Couldn't write file to disk. Please try again later.", 500))

        if current_chunk + 1 == total_chunks:
            # This was the last chunk, the file should be complete and the size we expect
            if os.path.getsize(save_path) != upload_size:

                return make_response(('Size mismatch. Please try again.', 500))
            else:
                # Success
                if media_type == 2:
                    clip = VideoFileClip(save_path)
                    clip.save_frame(poster_save_path, 0)
                    duration = clip.duration
                    clip.__del__()
                    del clip
                    poster_processing(poster_save_path, duration)
                    new_media = Media(
                        author_id=current_user.id,
                        path=save_path,
                        type=media_type,
                        duration=duration
                    )
                else:
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
            media_list=media_list,
            max_title=max_characters_allowed_work_title,
            max_desc= max_characters_allowed_work_desc)
    else:
        abort(404)


@app.route('/works/new-work', methods=('GET', 'POST'))
@login_required
def new_work():
    form = WorkForm()
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

        return render_template(
            '/works/new-work.html',
            form=form,
            max_title=max_characters_allowed_work_title,
            max_desc=max_characters_allowed_work_desc
        )


@app.route('/works/delete', methods=['POST'])
@login_required
def delete_work():
    work_id = request.get_json()["work_id"]
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
        poster_path = './app/static/media_posters/' + media.path[26:].split('.')[0] + '.png'
        db.session.delete(media)
        db.session.commit()
        print(poster_path, file=sys.stdout)
        print(media.path)
        try:
            os.remove(media.path)
            os.remove(poster_path)
        except FileNotFoundError:
            pass
        except Exception:
            raise

    return '', 204