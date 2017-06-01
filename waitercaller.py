
import config
from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from user import User
from flask_login import LoginManager
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_manager
from flask_login import current_user
from mockdbhelper import MockDBHelper as DBHelper
from passwordhelper import PasswordHelper



DB = DBHelper()
PH = PasswordHelper()
app = Flask(__name__)
login_manager = LoginManager(app)
app.secret_key = 'tPXJY3X37Qybz4QykV+hOyUxVQeEXf1Ao2C8upz+fGQXKsM'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    # user_password = DB.get_user(email)
    # if user_password and user_password == password:
    #     user = User(email)
    #     login_user(user, remember=True)
    #     return redirect(url_for('account'))
    stored_user = DB.get_user(email)
    if stored_user and PH.validate_password(password, stored_user['salt'], stored_user['hashed']):
        user = User(email)
        login_user(user, remember=True)
        return redirect(url_for('account'))
    return home()

@app.route('/account')
@login_required
def account():
    tables = DB.get_tables(current_user.get_id())
    return render_template('account.html', tables=tables)

@login_manager.user_loader
def load_user(user_id):
    user_password = DB.get_user(user_id)
    if user_password:
        return User(user_id)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    pw1 = request.form.get('password')
    pw2 = request.form.get('password2')
    if not pw1 == pw2:
        return redirect(url_for('home'))
    if DB.get_user(email):
        return redirect(url_for('home'))
    salt = PH.get_salt()
    hashed = PH.get_hash(pw1 + salt)
    DB.add_user(email, salt, hashed)
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/account/createtable', methods=['POST'])
@login_required
def account_createtable():
    tablename = request.form.get('tablenumber')
    tableid = DB.add_table(tablename, current_user.get_id())
    new_url = config.base_url + 'newrequest/' + tableid
    DB.update_table(tableid, new_url)
    return redirect(url_for('account'))

@app.route('/account/deletetable')
@login_required
def account_deletetable():
    tableid = request.args.get('tableid')
    DB.delete_table(tableid)
    return redirect(url_for('account'))

if __name__ == '__main__':
    app.run(port=5000, debug=True)