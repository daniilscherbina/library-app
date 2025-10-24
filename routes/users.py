from flask import Blueprint, request, jsonify
from models.base import db
from models.user import User

users_bp = Blueprint('users', __name__)

@users_bp.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@users_bp.route('/api/users/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        role=data.get('role', 'reader')
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@users_bp.route('/api/users/login', methods=['POST'])
def login():
    # Basic implementation - in production use proper authentication
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user:
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401
