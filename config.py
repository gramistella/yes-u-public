import os,sys


class Config(object):

    if os.path.exists('debug'):
        print('DEBUG MODE ENABLED', file=sys.stdout)
        COMPRESSOR_ENABLED = False

    SECRET_KEY = os.environ.get('SECRET_KEY') or '***REMOVED***'

    MYSQL_HOST = 'ls-f809ec4120ad2052b087d2bc11aac70f15665ef4.c8vqvp1pkij4.eu-central-1.rds.amazonaws.com'
    MYSQL_USER = '***REMOVED***'
    MYSQL_PASSWORD = 'zO4NU1A83g6c(7iD#H0u+B:4lyIol&Aq'
    MYSQL_DB = '***REMOVED***'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + MYSQL_USER + ':' + MYSQL_PASSWORD + '@' + MYSQL_HOST \
                              + '/' + MYSQL_DB + '?charset=utf8mb4'
    SQLALCHEMY_POOL_RECYCLE = 120
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MEDIA_UPLOADS = '.\\app\\static\\user_uploads'
    ALLOWED_IMAGE_EXTENSIONS = ['JPEG', 'JPG', 'PNG']
    ALLOWED_VIDEO_EXTENSIONS = ['MP4']
    ALLOWED_PDF_EXTENSIONS = ['PDF']

    SEND_FILE_MAX_AGE_DEFAULT = 600
