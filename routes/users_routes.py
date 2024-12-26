import os
import re
from flask import Flask, request, jsonify, Blueprint
from flask_bcrypt import Bcrypt
from datetime import datetime, timezone
from db.users_db import (
    create_user,
    get_all_users,
    get_user_by_email_or_phone,
    get_user_by_id,
    update_user,
    delete_user
)

# Initialize Blueprint and bcrypt
users_db = Blueprint('users', __name__)
bcrypt = Bcrypt()

# Validation functions
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))

def is_valid_password(password):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
    return bool(re.match(pattern, password))

def is_valid_phone(phone):
    pattern = r'^[0-9]{10,15}$'
    return bool(re.match(pattern, str(phone)))

# Routes
@users_db.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    required_fields = ['user_name', 'email', 'password', 'phone_number']
    if not all(field in data for field in required_fields):
        return jsonify({'msg': 'All fields are required.'}), 400

    name, email, password, phone_number = (
        data['user_name'], 
        data['email'], 
        data['password'], 
        data['phone_number']
    )

    if not is_valid_email(email):
        return jsonify({'msg': 'Invalid email format'}), 400
    if not is_valid_password(password):
        return jsonify({'msg': 'Invalid password format'}), 400
    if not is_valid_phone(phone_number):
        return jsonify({'msg': 'Invalid phone number format'}), 400

    if get_user_by_email_or_phone(email=email) or get_user_by_email_or_phone(phone_number=phone_number):
        return jsonify({'msg': 'User with this email or phone already exists'}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user_id = create_user(name, email, hashed_password, phone_number)
    return jsonify({'user_id': user_id}), 201

@users_db.route('/api/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def user_operations(user_id):
    if request.method == 'GET':
        user = get_user_by_id(user_id)
        return jsonify(user) if user else jsonify({'msg': 'User not found'}), 404

    if request.method == 'PUT':
        data = request.get_json()
        if 'email' in data and not is_valid_email(data['email']):
            return jsonify({'msg': 'Invalid email format'}), 400
        if 'password' in data:
            if not is_valid_password(data['password']):
                return jsonify({'msg': 'Invalid password format'}), 400
            data['password'] = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        if 'phone_number' in data and not is_valid_phone(data['phone_number']):
            return jsonify({'msg': 'Invalid phone number format'}), 400
        update_user(user_id, data)
        return jsonify({'msg': 'User updated successfully'}), 200

    if request.method == 'DELETE':
        delete_user(user_id)
        return jsonify({'msg': 'User deleted successfully'}), 200

@users_db.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    if not data:
        return jsonify({'msg': 'Invalid request payload'}), 400

    identifier, password = data.get('identifier'), data.get('password')
    if not identifier or not password:
        return jsonify({'msg': 'Identifier and password are required'}), 400

    
    phone = identifier if type(identifier) == int else None
    email = None if phone else identifier if '@' in identifier else None
    # email = identifier if '@' in identifier else None
    # phone = None if email else identifier
    print("Phone:", phone)
    print("Email:", email)
    
    user = get_user_by_email_or_phone(email=email, phone_number=phone)

    if user and bcrypt.check_password_hash(user['password'], password):
        user_id = user['_id']
        login_time = datetime.now(timezone.utc)
        update_user(user_id, {'last_login': login_time})
        return jsonify({'user_id': user_id, 'login_time': login_time.isoformat()}), 200

    return jsonify({'msg': 'Invalid identifier or password'}), 401

@users_db.route('/api/users', methods=['GET'])
def fetch_all_users():
    users = get_all_users()
    return jsonify({'users': users}), 200
