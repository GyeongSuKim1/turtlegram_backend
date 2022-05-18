from functools import wraps
from bson import ObjectId
from flask import Flask, request, jsonify, abort
import json
from flask_cors import CORS
from pymongo import MongoClient
import jwt, hashlib
from datetime import datetime, timedelta

app = Flask(__name__)

cors = CORS(app, resources={r'*': {'origins': '*'}})
client = MongoClient('localhost', 27017)
db = client.dbsparta
SECRET_KEY = 'gyeongsu'


def authorize(f):
    @wraps(f)
    def decorated_function():
        if not 'Authorization' in request.headers:
            abort(401)
        token = request.headers['Authorization']
        try:
            user = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except:
            abort(401)
        return f(user)
    return decorated_function


@app.route("/")
@authorize
def hello_word(user):
    return jsonify({'message':'success'})


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
                return jsonify({'message':'존재하는 이메일'})
            else:
                email = email_receive
        else:
            return jsonify({'message':'메일 주소 확인필요'})
    elif email_receive == '':
        return jsonify({'message':'아무것도 입력 안했네요'})
    else: 
        return jsonify({'message':'이메일 형식으로 확인 바람'})
    
# ㅡㅡㅡㅡㅡ 패스워드 ㅡㅡㅡㅡㅡ
    if password_receive == '':
        return jsonify({'message':'비밀번호 입력해라'})
    elif len(str(password_receive)) >= 8:
        password = password_receive
    else:     
        return jsonify({'message':'비밀번호를 8자리 이상 입력하시오'})
    
# ㅡㅡㅡㅡㅡ 패스워드 해싱 ㅡㅡㅡㅡㅡ
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    doc = {
        'email' : email,
        'password' : password_hash
    }

# ㅡㅡㅡㅡㅡ db에 저장 ㅡㅡㅡㅡㅡ
    db.user_signup.insert_one(doc)
    return jsonify({'message':'저장완료'}), 201


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

    if result is None:
        return jsonify({'message': '일치하지않음'}), 401

    payload = {
        'id': str(result["_id"]),
        'exp': datetime.utcnow() + timedelta(seconds=60*60*24)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return jsonify({'message': 'success', 'token': token})


@app.route("/getuserinfo", methods=["GET"])
@authorize
def get_user_info(user):
    result = db.user_signup.find_one({
        '_id':ObjectId(user["id"])
    })
    
    return jsonify({'message': 'success' , 'email': result['email']})


@app.route("/article", methods=["POST"])
@authorize
def post_article(user):
    data = json.loads(request.data)
    print('125 번', data)
    
    db_user = db.user_signup.find_one({'_id':ObjectId(user.get('id'))})
    
    now = datetime.now().strftime("%H:%M:%S")
    
    doc = {
        'title' : data.get('title',None),
        'content' : data.get('content',None),
        'user' : user['id'],
        'user_email' : db_user['email'],
        'time' : now,
    }
    
    db.article.insert_one(doc)    
    return jsonify({'message':'저장 완료'})


@app.route("/article", methods=["GET"])
def get_article():
    articles = list(db.article.find())
    
    for article in articles:
        article["_id"] = str(article["_id"])
        
    return jsonify({'message': 'success', "articles": articles})

if __name__ =='__main__':
    app.run('0.0.0.0', port=5000, debug=True)