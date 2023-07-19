from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_uploads import IMAGES, UploadSet, configure_uploads
import os
from werkzeug.utils import secure_filename
from flask_msearch import Search
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_admin import Admin
from flask_wtf.csrf import CSRFProtect
from flask_toastr import Toastr

#basedir for our uploads
basedir = os.path.abspath(os.path.dirname(__file__))

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cl_mall.db"
app.config["SECRET_KEY"] = "kshghf2732654skskjs6"
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

csrf = CSRFProtect()
csrf.init_app(app)


#initialize Toastr
toastr = Toastr(app)

# initialize the app with the extension
db.init_app(app)
bcrypt = Bcrypt(app)
search = Search()
search.init_app(app)
migrate = Migrate(app, db)
with app.app_context():
    if db.engine.url.drivername == "sqlite":
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)

admin = Admin()
admin.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='customerLogin'
login_manager.needs_refresh_message_category = 'danger'
login_manager.login_message = u'Please login first'
csrf = CSRFProtect()
csrf.init_app(app)


from cl_mall.customers import routes
from cl_mall.products import routes
from cl_mall.admin import routes
from cl_mall.carts import carts