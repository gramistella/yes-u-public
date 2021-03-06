import os,sys


class Config(object):

    if os.path.exists('debug'):
        print(' * DISABLED COMPRESSION', file=sys.stdout)
        COMPRESSOR_ENABLED = False

    SECRET_KEY = os.environ.get('SECRET_KEY') or '***REMOVED***'

    MYSQL_HOST = '***REMOVED***'
    MYSQL_USER = '***REMOVED***'
    MYSQL_PASSWORD = '***REMOVED***'
    MYSQL_DB = '***REMOVED***'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + MYSQL_USER + ':' + MYSQL_PASSWORD + '@' + MYSQL_HOST \
                              + '/' + MYSQL_DB + '?charset=utf8mb4'
    SQLALCHEMY_POOL_RECYCLE = 120
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RESOURCES = '.\\app\\static\\resources'

    MEDIA_UPLOADS = '.\\app\\static\\user_uploads'
    MEDIA_POSTERS = '.\\app\\static\\media_posters'
    ALLOWED_IMAGE_EXTENSIONS = ['JPEG', 'JPG', 'PNG']
    ALLOWED_VIDEO_EXTENSIONS = ['MP4']
    ALLOWED_PDF_EXTENSIONS = ['PDF']

    SEND_FILE_MAX_AGE_DEFAULT = 600
