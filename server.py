from flask import Flask, Response, request
from flask.ext.login import LoginManager, UserMixin, login_required
from uuid import uuid4
import json

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    # proxy for a database of users
    user_database = {"JohnDoe": {"username": "JohnDoe", "password": "John", "current_token": ""}}

    def __init__(self, username, password):
        self.id = username
        self.password = password
        self.current_token = ""

    @classmethod
    def get_by_id(cls, id):
        return cls.user_database.get(id)

    @classmethod
    def get_by_token(cls, token):
        return cls.user_database.get(token)


@login_manager.request_loader
def load_user(request):
    token = request.headers.get('Authorization')
    if token is None:
        return Response(response="Invalid token", status=401)

    user_from_db = User.get_by_token(token)
    if user_from_db:
        return user_from_db
    return None

@app.route('/login', methods=['POST'])
def login():
    data = json.loads(request.data)
    username = data['username']
    password = data['password']
    user = User.get_by_id(username)
    if not user:
        return Response(response="Username not found", status=404)
    print user
    if password != user["password"]:
        return Response(response="Password is incorrect", status=401)
    token = uuid4()
    user['current_token'] = token
    return Response(response=json.dumps({'token': str(user['current_token'])}), status=200)

@app.route("/test",methods=["GET"])
def index():
    return Response(response='dope shit',status=200)

@app.route("/protected/",methods=["GET"])
@login_required
def protected():
    return Response(response="Hello Protected World!", status=200)


if __name__ == '__main__':
    app.config["SECRET_KEY"] = "ITSASECRET"
    app.run(port=5000,debug=True)
