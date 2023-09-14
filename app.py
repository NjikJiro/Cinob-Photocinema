from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    url_for
)
from pymongo import MongoClient
import os


app = Flask(__name__)

client = MongoClient(
    'mongodb+srv://test:sparta@cluster0.w8mhvbo.mongodb.net/?retryWrites=true&w=majority')
db = client.cinobphotocinema


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login')
def login():
    test = ""


@app.route('/gallery')
def gallery():
    card = list(db.card.find({}, {'_id': False}))
    return jsonify({'card': card})


@app.route('/adminpanel', methods=["POST"])
def save_card():
    title_receive = request.form.get('title_give')
    file = request.files['file_give']

    directory = f'static/image/{title_receive}'
    os.makedirs(directory, exist_ok=True)

    extension = file.filename.split('.')[1]
    filename = f'{directory}/{title_receive}.{extension}'
    file.save(filename)

    doc = {
        'title': title_receive,
        'file': filename,
    }
    db.produk.insert_one(doc)
    return jsonify({'pesan': 'data telah ditambahkan'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
