from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config:

    # clau secreta per a les sessions guardades a les cookies
    SECRET_KEY = environ.get('SECRET_KEY')

    MAIL_SENDER_NAME = environ.get('MAIL_SENDER_NAME')
    MAIL_SENDER_ADDR = environ.get('MAIL_SENDER_ADDR')
    MAIL_SENDER_PASSWORD = environ.get('MAIL_SENDER_PASSWORD')
    MAIL_SMTP_SERVER = environ.get('MAIL_SMTP_SERVER')
    MAIL_SMTP_PORT = int(environ.get('MAIL_SMTP_PORT'))

    CONTACT_ADDR = environ.get('CONTACT_ADDR')

    # debug toolbar
    # https://stackoverflow.com/questions/63116419/evaluate-boolean-environment-variable-in-python
    DEBUG_TB_ENABLED = environ.get('DEBUG_TB_ENABLED', "false").lower() == "true"

    # paràmetre que farà servir SQLAlchemy per a connectar-se
    default_db = "sqlite:///" + basedir + "/sqlite/database.db"
    sqlite_database_uri = environ.get('SQLALCHEMY_DATABASE_URI', default_db)

    # si no hi és el valor a environment, fa servir SQLITE
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI', sqlite_database_uri)

    # mostre als logs les ordres SQL que s'executen
    SQLALCHEMY_ECHO = environ.get('DEBUG_TB_ENABLED', "true").lower() == "true"