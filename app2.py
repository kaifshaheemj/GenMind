import os
import uuid
import logging
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from config.db import db
from routes.users_routes import users_db
from routes.conversation_routes import conversation_blueprint
from gemini import Gemini
from sample_vectordb import file_vectorizing
import search_query
from firebase_admin import firestore

# Flask app initialization
app = Flask(__name__)
app.register_blueprint(users_db, url_prefix="/app")
app.register_blueprint(conversation_blueprint, url_prefix="/app")

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure upload settings
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

logger.info("Application initialized and upload folder configured.")

def allowed_file(filename):
    logger.debug("Checking if the file is allowed: %s", filename)
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_file(file):
    """Handles file saving with additional validation."""
    logger.info("Processing file upload.")
    if not file or not allowed_file(file.filename):
        logger.warning("Invalid file type uploaded: %s", file.filename if file else "No file provided")
        raise ValueError("Invalid file type. Allowed types: " + ", ".join(ALLOWED_EXTENSIONS))
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{str(uuid.uuid4())}_{filename}")
    file.save(file_path)
    logger.info("Saved file to %s", file_path)
    return file_path

def create_new_conversation_document(user_id, conversation_id, query_text=None, file_path=None, gemini_response=None):
    """Creates a Firestore conversation document."""
    logger.info("Creating new conversation document for user_id: %s, conversation_id: %s", user_id, conversation_id)
    conversation_data = {
        "conversation_name": f"Conversation {datetime.now(timezone.utc).isoformat()}",
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc),
        "queries": []
    }

    if query_text or file_path:
        query_id = str(uuid.uuid4())
        query_data = {
            "query_id": query_id,
            "query_text": query_text,
            "file_path": file_path,
            "response": gemini_response,
            "created_at": datetime.now(timezone.utc)
        }
        conversation_data["queries"].append(query_data)

    db.collection("conversations").document(conversation_id).set(conversation_data)
    logger.info("Conversation document created successfully.")
    return conversation_id, conversation_data

@app.route("/app/conversation/new", methods=["POST"])
def create_new_conversation():
    logger.info("Request received to create a new conversation.")
    try:
        user_id = request.form.get("user_id")
        query_text = request.form.get("query")
        file = request.files.get("file")

        if not user_id:
            logger.warning("User ID is missing in the request.")
            return jsonify({"error": "user_id is required"}), 400

        conversation_id = str(uuid.uuid4())
        gemini_response = None
        file_path = None

        # Process file if uploaded
        if file:
            try:
                file_path = process_file(file)
                logger.info("File uploaded and processed successfully: %s", file_path)
                vectordb_response = file_vectorizing(
                    user_id=user_id, 
                    conversation_id=conversation_id, 
                    file_path=file_path
                )
                logger.info("Vectorization completed for file: %s", file_path)

                if query_text:
                    search_results = search_query.search_user_data(
                        query=query_text, 
                        user_id=user_id
                    )
                    logger.info("Search results retrieved for query.")
                    model = Gemini()
                    gemini_response = model.respond(search_results, query_text)
                    logger.info("Gemini response generated.")
            except Exception as e:
                logger.error("Error during file processing: %s", str(e))
                return jsonify({"error": f"File processing error: {str(e)}"}), 400
        
        # If only query text without file
        elif query_text:
            logger.info("Processing query text without file.")
            model = Gemini()
            gemini_response = model.respond(query_text)
            logger.info("Gemini response generated for text query.")

        # Create conversation document
        conversation_id, conversation_data = create_new_conversation_document(
            user_id, conversation_id, query_text, file_path, gemini_response
        )

        logger.info("New conversation created successfully with ID: %s", conversation_id)
        return jsonify({
            "message": "New conversation created successfully.",
            "conversation_id": conversation_id,
            "queries": conversation_data["queries"]
        }), 200

    except Exception as e:
        logger.error("Error creating new conversation: %s", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/app/conversation/<conversation_id>/add", methods=["POST"])
def add_query_to_conversation(conversation_id):
    logger.info("Request received to add a query to conversation ID: %s", conversation_id)
    try:
        query_text = request.form.get("query")
        file = request.files.get("file")
        
        if not query_text and not file:
            logger.warning("Both query text and file are missing.")
            return jsonify({"error": "Either query text or file is required"}), 400

        conversation_ref = db.collection("conversations").document(conversation_id)
        conversation = conversation_ref.get()

        if not conversation.exists:
            logger.warning("Conversation ID %s not found.", conversation_id)
            return jsonify({"error": "Conversation not found"}), 404

        user_id = conversation.to_dict()["user_id"]
        gemini_response = None
        file_path = None

        # Process file if uploaded
        if file:
            try:
                file_path = process_file(file)
                logger.info("File uploaded and processed successfully: %s", file_path)
                vectordb_response = file_vectorizing(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    file_path=file_path
                )
                logger.info("Vectorization completed for file: %s", file_path)

                if query_text:
                    search_results = search_query.search_user_data(
                        query=query_text,
                        user_id=user_id
                    )
                    logger.info("Search results retrieved for query.")
                    model = Gemini()
                    gemini_response = model.respond(search_results, query_text)
                    logger.info("Gemini response generated.")
            except Exception as e:
                logger.error("Error during file processing: %s", str(e))
                return jsonify({"error": f"File processing error: {str(e)}"}), 400
        
        # If only query text without file
        elif query_text:
            logger.info("Processing query text without file.")
            model = Gemini()
            gemini_response = model.respond(retrieved_contents = None,
                            user_input = query_text,
                            history= None)
            logger.info("Gemini response generated for text query.")

        # Add query to conversation
        query_id = str(uuid.uuid4())
        query_data = {
            "query_id": query_id,
            "query_text": query_text,
            "file_path": file_path,
            "response": gemini_response,
            "created_at": datetime.now(timezone.utc)
        }

        conversation_ref.update({
            "queries": firestore.ArrayUnion([query_data])
        })

        logger.info("Query added to conversation ID: %s with query ID: %s", conversation_id, query_id)
        return jsonify({
            "message": "Query added successfully.",
            "query_id": query_id,
            "response": gemini_response
        }), 200

    except Exception as e:
        logger.error("Error adding query to conversation: %s", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logger.info("Starting Flask application.")
    app.run(debug=True)
