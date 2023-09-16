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
import shutil

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

@app.route('/login', methods=['GET'])
def login():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({'username': payload.get('id')})
        return redirect(url_for('dashboard', user_info=user_info))
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        msg = request.args.get('msg')
        return render_template('login.html', msg=msg)


@app.route('/get_posts', methods=['GET'])
def get_posts():
    card = list(db.product.find({}, {'_id': False}))
    return jsonify({'card': card})


@app.route('/adminpanel', methods=["GET"])
def dashboard():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.users.find_one({'username': payload.get('id')})
        return render_template("adminpanel.html", user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Sesi login kamu telah kadaluwarsa"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="Sepertinya terjadi kesalahan"))


@app.route('/posting', methods=['POST'])
def posting():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({'username': payload.get('id')})
        # buat kode input data disini
        title_receive = request.form.get('title_give')
        file = request.files['file_give']

        # Mencari nomor folder terakhir
        last_folder_number = list(
            db.product.find().sort([('folder', -1)]).limit(1))
        if len(last_folder_number) == 0 or 'folder' not in last_folder_number[0]:
            detail = "detail 1"
        else:
            last_number = int(
                last_folder_number[0]['folder'].replace('detail', ''))
            detail = f"detail {last_number + 1}"

        directory = f'static/img/{detail}'
        os.makedirs(directory, exist_ok=True)
        # akhir kode cari folder

        extension = file.filename.split('.')[1]
        filename = f'{directory}/{title_receive}.{extension}'
        file.save(filename)

        count = db.bucket.count_documents({})
        num = count + 1

        doc = {
            'num': num,
            'username': user_info.get('username'),
            'title': title_receive,
            'file': filename,
            'folder': detail,
        }
        db.product.insert_one(doc)
        return jsonify({'msg': 'data telah ditambahkan'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('dashboard'))


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


@app.route('/adminpanel/delete_post', methods=['POST'])
def delete_post():
    num_receive = request.form['num_give']

    # Temukan post yang akan dihapus
    post = db.product.find_one({'num': int(num_receive)})

    if post:
        # Hapus folder terkait beserta isinya
        folder_to_delete = post['folder']
        folder_path = os.path.join('static', 'img', folder_to_delete)

        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)  # Hapus folder dan isinya

        # Hapus post dari database
        db.product.delete_one({'num': int(num_receive)})
        return jsonify({'msg': 'hapus berhasil!'})
    else:
        return jsonify({'msg': 'post tidak ditemukan'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
