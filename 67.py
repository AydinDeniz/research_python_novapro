from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import os
import subprocess
import redis
import rq
from sqlalchemy.dialects.postgresql import JSONB

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://username:password@localhost/dbname"
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
app.config["REDIS_URL"] = "redis://localhost"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
jwt = JWTManager(app)

redis_conn = redis.from_url(app.config["REDIS_URL"])
queue = rq.Queue("job-queue", connection=redis_conn)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("jobs", lazy=True))
    script = db.Column(db.Text, nullable=False)
    environment = db.Column(JSONB, nullable=True)
    input_files = db.Column(JSONB, nullable=True)
    stdout = db.Column(db.Text, nullable=True)
    stderr = db.Column(db.Text, nullable=True)
    exit_code = db.Column(db.Integer, nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        login_user(user)
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad username or password"}), 401

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"msg": "logout successful"}), 200

@app.route("/upload", methods=["POST"])
@jwt_required()
def upload_script():
    user_id = get_jwt_identity()
    user = User.query.filter_by(username=user_id).first()
    script = request.files["script"].read().decode("utf-8")
    environment = request.form.get("environment", None)
    input_files = request.form.get("input_files", None)
    job = Job(user_id=user.id, script=script, environment=environment, input_files=input_files)
    db.session.add(job)
    db.session.commit()
    queue.enqueue("app.execute_script", job.id)
    return jsonify({"job_id": job.id}), 201

def execute_script(job_id):
    job = Job.query.get(job_id)
    user = job.user
    working_dir = f"/tmp/{user.username}/{job_id}"
    os.makedirs(working_dir, exist_ok=True)
    
    with open(f"{working_dir}/script.py", "w") as f:
        f.write(job.script)
    
    if job.environment:
        env = dict(os.environ, **job.environment)
    else:
        env = os.environ
    
    process = subprocess.run(
        ["python", f"{working_dir}/script.py"],
        cwd=working_dir,
        env=env,
        capture_output=True,
        text=True
    )
    
    job.stdout = process.stdout
    job.stderr = process.stderr
    job.exit_code = process.returncode
    db.session.commit()

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)