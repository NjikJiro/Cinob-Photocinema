from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    session,
    redirect,
    url_for
)
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib
import os

app = Flask(__name__)

SECRET_KEY = 'CINEMA'

client = MongoClient(
    'mongodb+srv://test:sparta@cluster0.w8mhvbo.mongodb.net/?retryWrites=true&w=majority')
db = client.cinobphotocinema

TOKEN_KEY = 'mytoken'


# start halaman user


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET'])
def login():
    msg = request.args.get('msg')
    return render_template('login.html', msg=msg)


@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')


@app.route('/gallery', methods=['GET'])
def gallery():
    return render_template('gallery.html')


@app.route('/faq', methods=['GET'])
def faq():
    return render_template('faq.html')
# akhir halaman user


# start dashboard admin


@app.route('/adminpanel', methods=["GET"])
def dashboard():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({'username': payload.get('id')})
        print(user_info)
        return render_template("adminpanel.html", user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Sesi login kamu telah kadaluwarsa"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="Sepertinya terjadi kesalahan"))


@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get(TOKEN_KEY)
    # try:
    #     payload = jwt.decode(
    #         token_receive,
    #         SECRET_KEY,
    #         algorithms=['HS256']
    #     )
    #     user_info = db.users.find_one({'username': payload.get('id')})
    #     # buat kode input data disini
    # except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
    #     return redirect(url_for('home'))


@app.route('/login_save', methods=['POST'])
def login_save():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({
        'username': username_receive,
        'password': pw_hash
    })
    if result:
        payload = {
            'id': username_receive,
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 1),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({
            "result": "fail",
            "msg": "Kami tidak dapat menemukan pengguna dengan kombinasi id/kata sandi tersebut",
        })


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)