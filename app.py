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


@app.route('/gallery/2', methods=['GET'])
def gallery2():
    return render_template('gallery2.html')


@app.route('/adminpanel/register', methods=['GET'])
def register():
    return render_template('register.html')


@app.route('/gallery/2/detail-<title>', methods=['GET'])
def gallery_detail(title):
    post = db.product.find_one({'title': title}, {'_id': False})
    post_num = post.get('num')

    if post_num:
        num_folder = post.get('folder')

        detail = list(db.product_detail.find(
            {'folder': num_folder}, {'_id': False}))

    return render_template('detail-user.html', post=post, detail=detail)


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
        db.product_detail.delete_many({'folder': post.get('folder')})
        return jsonify({'msg': 'hapus berhasil!'})
    else:
        return jsonify({'msg': 'post tidak ditemukan'})


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

        DBfile = f'img/{detail}/{title_receive}.{extension}'

        count = db.product.count_documents({})
        num = count + 1

        doc = {
            'num': num,
            'username': user_info.get('username'),
            'title': title_receive,
            'file': DBfile,
            'folder': detail,
            'layout': layout_receive,  # Simpan jenis layout
            #  'url':
        }
        db.product.insert_one(doc)
        return jsonify({'msg': 'data telah ditambahkan', 'result': 'success'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('dashboard'))


@app.route('/adminpanel/update-posting/<int:num>', methods=['POST'])
def update_posting(num):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )

        title = request.form.get('title')
        layout = request.form.get('layout')

        if "file_give" in request.files:
            new_image = request.files['file_give']

            old_post = db.product.find_one({'num': num})
            old_image_path = old_post.get('file')

            if new_image:
                # Lakukan penyimpanan file gambar yang baru
                extension = new_image.filename.split(
                    '.')[-1]  # Ambil ekstensi dengan benar
                filename = f'static/img/detail-{num}/{title}.{extension}'
                new_image.save(filename)

                new_image_path = f'img/detail-{num}/{title}.{extension}'
                db.product.update_one({'num': num}, {
                                      '$set': {'title': title, 'layout': layout, 'file': new_image_path}})

                # Hapus gambar yang lama
                if old_image_path:
                    old_image_file = os.path.join('static', old_image_path)
                    if os.path.exists(old_image_file):
                        os.remove(old_image_file)

        else:
            # Jika tidak ada file yang diunggah, tetap perbarui title dan layout
            db.product.update_one(
                {'num': num}, {'$set': {'title': title, 'layout': layout}})

        return jsonify({'result': 'success', 'msg': 'Data telah diperbarui'})

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


@app.route('/adminpanel/get-posting/<int:num>', methods=['GET'])
def get_posting(num):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )

        post = db.product.find_one({'num': num}, {'_id': False})

        if posting:
            return jsonify({'result': 'success', 'post': post})
        else:
            return jsonify({'result': 'error', 'msg': 'Posting tidak ditemukan'}), 404

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


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
        num_folder = post.get('folder')
        post_detail = list(db.product_detail.find(
            {'folder': num_folder}, {'_id': False}))
        count = 1
        return render_template('detail.html', post_detail=post_detail, post=post, count=count, user_info=user_info)

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


@app.route('/adminpanel/posting/<int:num>', methods=['POST'])
def detail_posting(num):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        post = db.product.find_one({'num': num}, {'_id': False})

        # data input
        count = db.product_detail.count_documents({})
        num = count + 1
        title_receive = request.form.get('title_give')
        file = request.files['file_give']
        layout_receive = request.form.get('layout_give')
        num_folder = post.get('folder')

        directory = f'static/img/{num_folder}'
        os.makedirs(directory, exist_ok=True)

        extension = file.filename.split('.')[1]
        filename = f'{directory}/{title_receive}.{extension}'
        file.save(filename)

        DBfile = f'img/{num_folder}/{title_receive}.{extension}'

        doc = {
            'num': num,
            'title': title_receive,
            'file': DBfile,
            'folder': post.get('folder'),
            'layout': layout_receive,
        }
        db.product_detail.insert_one(doc)
        return jsonify({'msg': 'data telah ditambahkan', 'result': 'success'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


@app.route('/adminpanel/delete-post-detail/<int:num>', methods=['POST'])
def delete_post_detail(num):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        detail = db.product_detail.find_one({'num': num})

        if detail:
            file_path = os.path.join('static', detail['file'])

            if os.path.exists(file_path):
                os.remove(file_path)

            db.product_detail.delete_one({'num': num})

            return jsonify({'msg': 'File detail telah dihapus', 'result': 'success'})
        else:
            return jsonify({'msg': 'File detail tidak ditemukan', 'result': 'error'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('home'))


@app.route('/register-save', methods=['POST'])
def register_save():
    username_receive = request.form.get('username_give')
    password_receive = request.form.get('password_give')
    password_hash = hashlib.sha256(
        password_receive.encode('utf-8')).hexdigest()

    count = db.product.count_documents({})
    num = count + 1

    doc = {
        'num': num,
        'username': username_receive,
        'password': password_hash
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
