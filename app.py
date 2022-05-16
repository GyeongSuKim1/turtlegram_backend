import email
import json
from msilib.schema import ODBCAttribute
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
cors = CORS(app, resources={r'*': {'origins': '*'}})
client = MongoClient('localhost', 27017)
db = client.dbsparta


@app.route("/")
def hello_word():
    return jsonify({'mseege':'success'})


@app.route("/signup", methods=["POST"])
def sign_up():

    data = json.loads(request.data)
    print(data.get('email'))
    print(data['password'])
    
    doc = {
        'email' : data.get('email'),
        'password' : data.get('password')
    }
    
    db.user_signup.insert_one(doc)
    return jsonify({'mseege':'success'})



if __name__ =='__main__':
    app.run('0.0.0.0', port=5000, debug=True)