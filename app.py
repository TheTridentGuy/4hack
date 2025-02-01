from flask import Flask, request, render_template, redirect, session
from prisma import Prisma
import flask
import secrets
import hashlib
import datetime


from config import HOST, PORT, DEBUG, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASS_HASH, DEFAULT_BOARD_NAME, DEFAULT_BOARD_DESC


app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
db = Prisma()
db.connect()


admins =  db.user.find_many(where={"role": "ADMIN"})
if not admins:
    db.user.create(data={
        "username": DEFAULT_ADMIN_USERNAME,
        "pass_hash": DEFAULT_ADMIN_PASS_HASH,
        "role": "ADMIN",
        "display_name": "Admin",
        "bio": "Default admin user"
    })
boards = db.board.find_first()
if not boards:
    db.board.create(data={
        "name": DEFAULT_BOARD_NAME,
        "desc": DEFAULT_BOARD_DESC
    })


def verify_session(user_id, session_id):
    if user_id and session_id:
        session_obj = db.session.find_first(where={"user_id": user_id, "session_id": session_id})
        if datetime.datetime.now().astimezone(datetime.timezone.utc) < session_obj.expires:
            return user_id
    return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/client")
def client():
    if verify_session(session.get("user_id"), session.get("session_id")):
        boards = db.board.find_many(where={"private": False})
        boards_list = [(board.board_id, board.name) for board in boards]
        return render_template("client.html", boards=boards_list)
    else:
        return redirect("/auth/login")

@app.route("/auth/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.values.get("username")
        password = request.values.get("password")
        print(username, password)
        if username and password:
            # TODO: update hash algorithm
            user = db.user.find_first(where={"username": username, "pass_hash": hashlib.sha256(password.encode()).hexdigest()})
            session_obj = db.session.create(data={"user_id": user.user_id, "expires": datetime.datetime.now().astimezone(datetime.timezone.utc) + datetime.timedelta(days=1), "session_id": secrets.token_hex(32)})
            session["user_id"] = user.user_id
            session["session_id"] = session_obj.session_id
            if user:
                return redirect("/client")
            return "Invalid credentials"
    return render_template("login.html")


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
