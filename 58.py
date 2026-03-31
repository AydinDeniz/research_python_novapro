from flask import Flask, request, jsonify, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import psycopg2
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/multi_tenant_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
jwt = JWTManager(app)

# Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    tenant = db.relationship('Tenant', backref=db.backref('users', lazy=True))

class Tenant(db.Model):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    schema_name = db.Column(db.String(150), unique=True, nullable=False)

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(150), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Blueprints
tenant_bp = Blueprint('tenant', __name__, url_prefix='/<tenant_id>')

@tenant_bp.route('/login', methods=['POST'])
def login(tenant_id):
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    tenant = Tenant.query.filter_by(id=tenant_id).first()
    if not tenant:
        return jsonify({'error': 'Tenant not found'}), 404
    
    user = User.query.filter_by(username=username, tenant_id=tenant_id).first()
    if user and user.password == password:
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@tenant_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard(tenant_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or user.tenant_id != int(tenant_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Fetch tenant-specific data (e.g., users, activity logs)
    users = User.query.filter_by(tenant_id=tenant_id).all()
    activity_logs = ActivityLog.query.filter_by(user_id=current_user_id).paginate(page=1, per_page=10)
    
    return jsonify({
        'users': [u.username for u in users],
        'activity_logs': [al.action for al in activity_logs.items]
    }), 200

app.register_blueprint(tenant_bp)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)