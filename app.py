from __future__ import division, print_function
import sys
import os
import glob
import re
import numpy as np


# Keras
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.models import load_model
from keras.preprocessing import image
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# Flask utils
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, login_required, \
    UserMixin, RoleMixin
from flask_security.utils import hash_password


# flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECURITY_PASSWORD_SALT'] = 'thisisasecretsalt'

db = SQLAlchemy(app)

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean)
    confirmed_at = db.Column(db.DateTime)
    roles = db.relationship(
        'Role', 
        secondary=roles_users, 
        backref=db.backref('users', lazy='dynamic')
    )

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    description = db.Column(db.String(255))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)



# Load model
MODEL_PATH = 'bento_nodrop.h5'
model = load_model(MODEL_PATH)   
print('Model loaded. Check http://127.0.0.1:5000/')

# label
lab = {0 : 'ALAP-ALAP KAWAH', 1 : 'ANGSA-BATU CHRISTMAS', 2 : 'ANGSA-BATU TOPENG', 3 : 'BELIBIS TOTOL', 4 : 'BIRU-LAUT EKOR-BLOROK', 5 : 'BOHA WASUR', 6 : 'BUNTUT-SATE PUTIH', 7 : 'BURUNG-KUCING TUTUL', 8 : 'CAMAR-ANGGUK COKELAT', 9 : 'CAMAR-KEJAR POMARIN', 10 : 'CEREK BESAR', 11 : 'CIKALANG BESAR', 12 : 'CINENEN GUNUNG', 13 : 'DARA-LAUT KASPIA', 14 : 'ELANG TIRAM', 15 : 'GAJAHAN PENGGALA', 16 : 'IBIS ROKOROKO', 17 : 'JUNAI EMAS', 18 : 'KAREO PADI', 19 : 'KASUARI GELAMBIR-GANDA', 20 : 'KEDIDI LEHER-MERAH', 21 : 'KEDIDIR BELANG', 22 : 'LAYANG-LAYANG ASIA', 23 : 'PECUK-ULAR AUSTRALASIA', 24 : 'PERKICI PELANGI', 25 : 'PERKUTUT JAWA', 26 : 'PIPIT BENGGALA', 27 : 'SERAK JAWA', 28 : 'TAK DIKETAHUI', 29 : 'TIKUSAN ALIS-PUTIH', 30 : 'TRULEK TOPENG'}

# predict funtion
def model_predict(img_path, model):
    img = load_img(img_path, target_size=(224, 224))

    # Preprocessing image
    x = img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x, mode='caffe')

    preds = model.predict(x)
    return preds


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict(file_path, model)

        # Process result
        pred_class = preds.argmax(axis=-1)
        print(pred_class)
        y = " ".join(str(x) for x in pred_class)
        y = int(y)
        result = lab[y]
        print(result)
        return result
    return None


@app.route('/')

# @login_required 
# i swithced the project path on my computer and login is not working for me anymore. 
# TypeError: LoginForm.validate() got an unexpected keyword argument 'extra_validators'

def profile():
    # must login
    return render_template('index.html')

@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    # register page
    if request.method == 'POST':
        user_datastore.create_user(
            email=request.form.get('email'),
            password=hash_password(request.form.get('password'))
        )
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/burung')
def burung():
    # burung page
    return render_template('burung.html')

if __name__ == '__main__':
    app.run(debug=True, threaded=False)


# env\Scripts\activate.bat



