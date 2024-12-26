from config.db import db
from datetime import datetime
from firebase_admin import firestore
from datetime import datetime, timezone 

# Firestore users collection reference
users_collection = db.collection('users')

def create_user(name, email, hashed_password, phone_number):
    """
    Creates a new user in the Firestore 'users' collection.
    """
    user_data = {
        'name': name.lower(),
        'email': email,
        'password': hashed_password,
        'phone_number': phone_number,
        'created_at': datetime.now(timezone.utc)
    }
    result = users_collection.add(user_data)
    print("Creation result:", result)
    print("Generated User ID:", result[1])
    return result[1].id

def get_all_users():
    """
    Retrieves all users from the Firestore 'users' collection.
    """
    users = []
    for doc in users_collection.stream():
        user = doc.to_dict()
        user['_id'] = doc.id
        user['name'] = user['name'].lower()  # Optional: Normalize name to lowercase
        users.append(user)
    return users

def get_user_by_id(user_id):
    """
    Fetches a user document by its ID.
    """
    try:
        doc = users_collection.document(user_id).get()
        print("Fetched user:", doc.to_dict())
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        raise ValueError("Invalid User ID") from e

def update_user(user_id, update_data):
    """
    Updates an existing user document.
    """
    try:
        users_collection.document(user_id).update(update_data)
    except Exception as e:
        raise ValueError("Invalid User ID") from e

def get_user_by_email_or_phone(email=None, phone_number=None):
    """
    Fetches a user document by email, phone number, or both.
    """
    query = None
    if email and phone_number:
        query = users_collection.where('email', '==', email).where('phone_number', '==', phone_number)
    elif email:
        query = users_collection.where('email', '==', email)
    elif phone_number:
        query = users_collection.where('phone_number', '==', phone_number)

    if query:
        results = []
        for doc in query.stream():
            user_data = doc.to_dict()
            user_data['_id'] = doc.id  # Include the document ID
            results.append(user_data)
        return results[0] if results else None

    return None

def delete_user(user_id):
    """
    Deletes a user document by its ID.
    """
    try:
        users_collection.document(user_id).delete()
    except Exception as e:
        raise ValueError("Invalid User ID") from e
