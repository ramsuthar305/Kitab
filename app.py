from flask import Flask,request
from flask_pymongo import PyMongo
# from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object("config.Config")
mongo = PyMongo(app)
# csrf = CSRFProtect(app)

from admin.views import admin
from portal.views import portal

app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(portal, url_prefix='')


if __name__ == '__main__':
    app.run(debug=True)



