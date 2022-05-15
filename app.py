from crypt import methods
from flask import Flask, jsonify
from requests import request

app = Flask(__name__)





@app.route("/")
def hello_word():
    return jsonify({'mseege':'success'})


@app.route("/singup", methods=["POST"])
def sign_up():
    print(request)
    
    return jsonify({'mseege':'success'})



if __name__ =='__main__':
    app.run('0.0.0.0', port=5000, debug=True)