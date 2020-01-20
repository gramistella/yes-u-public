from flask import render_template, flash, url_for, redirect, request, send_from_directory
from app import app, db
import os, sys
from app.forms import LoginForm
from app.models import Schools, Media
from flask_login import current_user, login_user, logout_user

from werkzeug.urls import url_parse


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/schools/index')
def school_index():
    return render_template('/schools/index.html', title='Schools')



@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.ico')

@app.route('/schools/user-page')
def user_page():
    if current_user.is_authenticated:

        return populate_school_template(current_user, is_school_owner=1)


def populate_school_template(school_obj, is_school_owner=0):

    header_img_filename = 'resources/' + school_obj.header_img

    images = Media.query.filter_by(type=1, author_id=current_user.id).all()
    images_path = []
    for image_row in images:
        path = image_row.path
        path = path[5:]
        images_path.append(path)

    if school_obj.description is not None and len(school_obj.description) < 1:
        description = 'You can write whatever you want here!'
    else:
        description = school_obj.description

    return render_template('/schools/school-template.html',
                           user=school_obj,
                           description=description,
                           header_img_filename=header_img_filename,
                           is_school_owner=is_school_owner,
                           images=images_path)

@app.route('/schools/Sandnes-videregående-skole')
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
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/backend', methods=['POST','GET'])
def handle_request():

    max_characters_allowed = 190
    if request.method == 'GET':
        return '', 200

    if request.method == 'POST':
        content = request.get_json(silent=True)
        request_type = content['type']

        # Edit school description
        if request_type == 1:
            description = content['description']
            description = (description[:max_characters_allowed]) \
                if len(description) > max_characters_allowed else description

            if current_user.description.split() != description.split():
                current_user.description = description
                #print(len(description), file=sys.stdout)
                db.session.commit()
            return '', 204
        if request_type == 2:
            image = request.files['image']

            image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))

    return '', 204


@app.route('/upload', methods=['POST'])
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


@app.route('/work-test')
def work_test_page():

    title = 'This is an amazing title!'
    description = 'This is the magical description <br> You can describe your work and add multimedia content.'
    return render_template('/works/work.html', title=title, description=description)
