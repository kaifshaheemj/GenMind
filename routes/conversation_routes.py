from flask import jsonify, Blueprint, request
from datetime import datetime, timezone
from config.db import db
import logging
from firebase_admin import firestore

# Blueprint for conversation routes
conversation_blueprint = Blueprint('conversation', __name__, url_prefix='/app')
conversations_collection = db.collection('conversations')
users_collection = db.collection('users')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_user_conversations(user_id, conversation_id):
    """
    Updates the user's list of conversation IDs with a new conversation ID.
    """
    try:
        user_ref = users_collection.document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            logger.error("User with user_id %s not found.", user_id)
            return

        user_data = user_doc.to_dict()
        conversation_ids = user_data.get("conversation_ids", [])

        if conversation_id not in conversation_ids:
            conversation_ids.append(conversation_id)
            user_ref.update({"conversation_ids": conversation_ids})
            logger.info("Updated user %s with new conversation_id %s", user_id, conversation_id)
    except Exception as e:
        logger.error("Error updating user's conversation_ids: %s", str(e))

@conversation_blueprint.route('/api/create_conversation/<user_id>', methods=['POST'])
def create_conversation(user_id):
    """
    Creates a new conversation for a given user.
    """
    try:
        user_ref = users_collection.document(user_id)
        if not user_ref.get().exists:
            return jsonify({"status": "error", "message": "User not found"}), 404

        new_conversation = {
            "user_id": user_id,
            "conversation_name": request.json.get('conversation_name', "Unnamed Conversation"),
            "queries": [],
            "created_at": datetime.utcnow()
        }

        conversation_ref = conversations_collection.add(new_conversation)
        conversation_id = conversation_ref[1].id

        user_ref.update({
            "conversation_ids": firestore.ArrayUnion([conversation_id])
        })

        return jsonify({"status": "success", "conversation_id": conversation_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@conversation_blueprint.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """
    Retrieves a specific conversation by its ID.
    """
    try:
        if not conversation_id:
            return jsonify({"status": "error", "message": "Invalid conversation ID"}), 400

        conversation_ref = conversations_collection.document(conversation_id)
        conversation = conversation_ref.get()

        if not conversation.exists:
            return jsonify({"status": "error", "message": "Conversation not found"}), 404

        return jsonify({
            "status": "success",
            "conversation_id": conversation_id,
            "conversation_data": conversation.to_dict()
        }), 200
    except Exception as e:
        logger.error("Error retrieving conversation: %s", str(e))
        return jsonify({"status": "error", "message": "An error occurred while retrieving the conversation"}), 500

@conversation_blueprint.route('/api/conversation_ids/<user_id>', methods=['GET'])
def get_conversation_ids(user_id):
    """
    Retrieves all conversation IDs for a given user.
    """
    try:
        user_ref = users_collection.document(user_id)
        user = user_ref.get()

        if not user.exists:
            return jsonify({"status": "error", "message": "User not found"}), 404

        conversation_ids = user.to_dict().get('conversation_ids', [])

        return jsonify({
            "status": "success",
            "user_id": user_id,
            "conversation_ids": conversation_ids
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@conversation_blueprint.route('/api/conversation_name/<user_id>', methods=['GET'])
def get_conversations(user_id):
    """
    Retrieves all conversation names and IDs for a given user.
    """
    try:
        user_ref = users_collection.document(user_id)
        user = user_ref.get()

        if not user.exists:
            return jsonify({"status": "error", "message": "User not found"}), 404

        conversation_ids = user.to_dict().get('conversation_ids', [])
        conversations = []

        for conversation_id in conversation_ids:
            conversation_ref = conversations_collection.document(conversation_id)
            conversation = conversation_ref.get()

            if conversation.exists:
                conversation_data = conversation.to_dict()
                conversation_name = conversation_data.get("conversation_name", "Unnamed Conversation")
                conversations.append({
                    "conversation_id": conversation_id,
                    "conversation_name": conversation_name
                })

        return jsonify({
            "status": "success",
            "user_id": user_id,
            "conversations": conversations
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
