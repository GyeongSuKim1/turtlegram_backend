from bson import ObjectId
from flask import Flask, request, jsonify
import datetime
import email
import hashlib
import json
from unittest import result
from flask_cors import CORS
from pymongo import MongoClient
import jwt, datetime, hashlib

app = Flask(__name__)

cors = CORS(app, resources={r'*': {'origins': '*'}})
client = MongoClient('localhost', 27017)
db = client.dbsparta
SECRET_KEY = 'gyeongsu'


@app.route("/")
def hello_word():
    return jsonify({'mseege':'success'})


@app.route("/signup", methods=["POST"])
def sign_up():
    
# ㅡㅡㅡㅡㅡ 변수선언 ㅡㅡㅡㅡㅡ
    data = json.loads(request.data)
    email_receive  = data.get('email')
    password_receive = data.get('password')
    
    domain = ['naver.com', 'gmail.com']
        
# ㅡㅡㅡㅡㅡ 이메일 ㅡㅡㅡㅡㅡ
    if '@' in email_receive:
        if email_receive.split('@')[1] in domain:
            if db.user_signup.find_one({'email':email_receive}):
                return jsonify({'mseege':'존재하는 이메일'})
            else:
                email = email_receive
        else:
            return jsonify({'mseege':'메일 주소 확인필요'})
    elif email_receive == '':
        return jsonify({'mseege':'아무것도 입력 안했네요'})
    else: 
        return jsonify({'mseege':'이메일 형식으로 확인 바람'})
    
# ㅡㅡㅡㅡㅡ 패스워드 ㅡㅡㅡㅡㅡ
    if password_receive == '':
        return jsonify({'mseege':'비밀번호 입력해라'})
    elif len(str(password_receive)) >= 8:
        password = password_receive
    else:     
        return jsonify({'mseege':'비밀번호를 8자리 이상 입력하시오'})
    
# ㅡㅡㅡㅡㅡ 패스워드 해싱 ㅡㅡㅡㅡㅡ
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    doc = {
        'email' : email,
        'password' : password_hash
    }

# ㅡㅡㅡㅡㅡ db에 저장 ㅡㅡㅡㅡㅡ
    print(doc)
    db.user_signup.insert_one(doc)
    print(doc)
    return jsonify({'mseege':'저장완료'}), 201


@app.route("/login", methods=["POST"])
def log_in():

    data = json.loads(request.data)
    email = data.get("email")
    password = data.get("password")
    
    # ㅡㅡㅡㅡㅡ 비밀번호 해싱 ㅡㅡㅡㅡㅡ
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    result = db.user_signup.find_one({
        'email' : email,
        'password' : password_hash           
    })
    print(result)

    if result is None:
        return jsonify({'messge': '일치하지않음'}), 401

    payload = {
        'id': str(result["_id"]),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=60*60*24)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    print(token)
    return jsonify({'messge': 'success', 'token': token})


#     # else:
#     #     return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})
    
#     # print(data.get('email'))
#     # print(data["password"])

@app.route("/getuserinfo", methods=["GET"])
def get_user_info():
    token = request.headers.get("Authorization")
    print(token)
    
    user = jwt.decode(token, SECRET_KEY, algorithm=['HS256'])
    print (user)
    result = db.user_signup.find_one({
        '_id':ObjectId(user["id"])
    })
    
    print(result)
    
    return jsonify({'messge': 'success'})
# , 'email': result['email']
if __name__ =='__main__':
    app.run('0.0.0.0', port=5000, debug=True)