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
    'mongodb+srv://ragdoll:smkm@cluster0.emf0knj.mongodb.net/?retryWrites=true&w=majority')
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


@app.route('/team', methods=['GET'])
def team():
    return render_template('team.html')


@app.route('/gallery2', methods=['GET'])
def gallery2():
    return render_template('gallery2.html')


@app.route('/faq', methods=['GET'])
def faq():
    return render_template('faq.html')


# Halaman detail gallery
# A
@app.route('/detailA', methods=['GET'])
def detailA():
    return render_template('detailA.html')

# B


@app.route('/detailB', methods=['GET'])
def detailB():
    return render_template('detailB.html')

# C


@app.route('/detailC', methods=['GET'])
def detailC():
    return render_template('detailC.html')

# D


@app.route('/detailD', methods=['GET'])
def detailD():
    return render_template('detailD.html')

# E


@app.route('/detailE', methods=['GET'])
def detailE():
    return render_template('detailE.html')

# F


@app.route('/detailF', methods=['GET'])
def detailF():
    return render_template('detailF.html')

# G


@app.route('/detailG', methods=['GET'])
def detailG():
    return render_template('detailG.html')

# H


@app.route('/detailH', methods=['GET'])
def detailH():
    return render_template('detailH.html')

# I


@app.route('/detailI', methods=['GET'])
def detailI():
    return render_template('detailI.html')

# J


@app.route('/detailJ', methods=['GET'])
def detailJ():
    return render_template('detailJ.html')
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


@app.route('/get-posts', methods=['GET'])
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


@app.route('/adminpanel/posting', methods=['POST'])
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
        layout_receive = request.form.get('layout_give')  # Ambil jenis layout

        # Validasi jenis layout
        if not layout_receive:
            return jsonify({'msg': 'Mohon pilih jenis layout'}), 400

        # Mencari nomor folder terakhir
        last_folder = db.product.find_one(
            sort=[('folder', -1)], projection={'folder': 1})
        if last_folder and 'folder' in last_folder:
            last_number = int(last_folder['folder'].replace('detail-', ''))
            detail = f"detail-{last_number + 1}"
        else:
            detail = "detail-1"

        directory = f'static/img/{detail}'
        os.makedirs(directory, exist_ok=True)

        # akhir kode cari folder

        extension = file.filename.split('.')[1]
        filename = f'{directory}/{title_receive}.{extension}'
        file.save(filename)

        count = db.product.count_documents({})
        num = count + 1

        doc = {
            'num': num,
            'username': user_info.get('username'),
            'title': title_receive,
            'file': filename,
            'folder': detail,
            'layout': layout_receive  # Simpan jenis layout
        }
        db.product.insert_one(doc)
        return jsonify({'msg': 'data telah ditambahkan', 'result': 'success'})
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
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({
            "result": "fail",
            "msg": "Kami tidak dapat menemukan pengguna dengan kombinasi id/kata sandi tersebut",
        })


@app.route('/adminpanel/delete-post', methods=['POST'])
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


@app.route('/adminpanel/posting/<int:num>', methods=['GET'])
def detail_post(num):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({'username': payload.get('id')})
        post = db.product.find_one({'num': num}, {'_id': False})
        return render_template("detail.html", post=post, user_info=user_info)

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
