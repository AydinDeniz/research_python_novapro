from flask import Flask, request, jsonify, g
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with your actual secret key

def encode_auth_token(user_id):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    except Exception as e:
        return e

def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'

def token_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_token = request.headers.get('Authorization')
        if not auth_token:
            return jsonify(message='Token is missing.'), 403
        user_id = decode_auth_token(auth_token)
        if isinstance(user_id, str):
            return jsonify(message=user_id), 403
        g.user_id = user_id
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
def login():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify(message='User ID is required.'), 400
    auth_token = encode_auth_token(user_id)
    return jsonify(auth_token=auth_token.decode()), 200

@app.route('/protected', methods=['GET'])
@token_required
def protected():
    return jsonify(user_id=g.user_id), 200

if __name__ == '__main__':
    app.run(debug=True)