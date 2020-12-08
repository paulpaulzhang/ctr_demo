from flask import Flask
from web_home import app_home
from web_login import app_login
from web_query import app_query

app = Flask(__name__)
app.register_blueprint(app_home)
app.register_blueprint(app_login)
app.register_blueprint(app_query)

app.secret_key = 'super secret key'
if __name__ == '__main__':
    app.debug = True
    app.run(debug=True)
