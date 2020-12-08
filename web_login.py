from flask import render_template, request, session, Blueprint

app_login = Blueprint('app_login', __name__, template_folder='templates')


@app_login.route('/', methods=['GET'])
def login_page():
    return render_template('login_page.html')


@app_login.route('/user_login', methods=['POST'])
def user_login():
    # username = request.form['username']
    # password = request.form['password']
    # print(username, password)
    # db = connect()
    # cursor = db.cursor()
    # cursor.execute('SELECT username FROM user WHERE username= %s', username)
    # username_ = cursor.fetchone()
    # if username_:
    #     cursor.execute('SELECT password FROM user WHERE username= %s', username)
    #     password_ = cursor.fetchone()[0]
    #     db.close()
    #     if password == password_:
    #         session['user'] = username
    #         return 'ok'
    #     else:
    #         return '用户名或密码错误'
    # else:
    #     db.close()
    #     return '用户名不存在'
    return 'ok'
