from flask import render_template, Blueprint

app_home = Blueprint('app_home', __name__, template_folder='templates')


@app_home.route('/home')
def home_page():
    return render_template('home_page.html')
