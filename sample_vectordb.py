# from langchain.vectorstores import Qdrant
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.document_loaders import PyPDFLoader
# from config.vector_db import qdrant_client
# from model_config.embed_model import model_embedding


# def file_vectorizing(user_id, conversation_id, file_path):
#     # loader = PyPDFLoader(r"E:\\Attention is all you need.pdf")  # Replace with your PDF path
#     loader = PyPDFLoader(file_path)
#     documents = loader.load()

#     #Split documents into chunks
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
#     texts = text_splitter.split_documents(documents)

#     # user_id = "fWHF2iGfYYmFAz62Kp85" 
#     # Add user_id to the metadata of each text chunk
#     for text in texts:
#         if "metadata" not in text:
#             text.metadata = {}
#         text.metadata["user_id"] = user_id
#         text.metadata["conversation_id"] = conversation_id

#     # Step 6: Create the Qdrant vector database
#     qdrant = Qdrant.from_documents(
#         texts,
#         model_embedding(),
#         url="https://23d3e77b-82ee-4929-8efe-5291110b98b9.europe-west3-0.gcp.cloud.qdrant.io:6333",
#         prefer_grpc=False,
#         collection_name="GenMind_3",  # Shared collection for all users
#         api_key="dq8OJwrHsyk6IVMFGpufuBC1PHDzSQjICQrV0Y9EDsT2olTsvIp5bg"
#     )

#     return {
#         "message": "User-specific vectors added successfully!",
#         "user_id": user_id,
#         "conversation_id": conversation_id,
#         "file_path": file_path,
#         "collection_name": "GenMind_3"
#     }

from langchain.vectorstores import Qdrant
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    UnstructuredImageLoader
)
from config.vector_db import qdrant_client
from model_config.embed_model import model_embedding
import os

def get_document_loader(file_path):
    """Returns appropriate document loader based on file extension."""
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        return PyPDFLoader(file_path)
    elif file_extension == '.txt':
        return TextLoader(file_path)
    elif file_extension in ['.doc', '.docx']:
        return Docx2txtLoader(file_path)
    elif file_extension in ['.png', '.jpg', '.jpeg']:
        return UnstructuredImageLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def file_vectorizing(user_id, conversation_id, file_path):
    """Vectorizes file content and stores in Qdrant."""
    try:
        # Get appropriate loader
        loader = get_document_loader(file_path)
        documents = loader.load()

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        texts = text_splitter.split_documents(documents)

        # Add metadata to each chunk
        for text in texts:
            if not hasattr(text, 'metadata'):
                text.metadata = {}
            text.metadata.update({
                "user_id": user_id,
                "conversation_id": conversation_id,
                "file_path": file_path
            })

        # Create Qdrant vector database
        qdrant = Qdrant.from_documents(
            texts,
            model_embedding(),
            url="https://23d3e77b-82ee-4929-8efe-5291110b98b9.europe-west3-0.gcp.cloud.qdrant.io:6333",
            prefer_grpc=False,
            collection_name="GenMind_3",
            api_key="dq8OJwrHsyk6IVMFGpufuBC1PHDzSQjICQrV0Y9EDsT2olTsvIp5bg"
        )

        return {
            "message": "User-specific vectors added successfully!",
            "user_id": user_id,
            "conversation_id": conversation_id,
            "file_path": file_path,
            "collection_name": "GenMind_3"
        }
        
    except Exception as e:
        raise Exception(f"Error vectorizing file: {str(e)}")