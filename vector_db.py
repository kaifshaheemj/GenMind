# from langchain.vectorstores import Qdrant
# from langchain.embeddings import HuggingFaceBgeEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.document_loaders import PyPDFLoader
# from qdrant_client import QdrantClient

# # Initialize QdrantClient for cloud instance
# qdrant_client = QdrantClient(
#     url="https://23d3e77b-82ee-4929-8efe-5291110b98b9.europe-west3-0.gcp.cloud.qdrant.io:6333",
#     api_key="dq8OJwrHsyk6IVMFGpufuBC1PHDzSQjICQrV0Y9EDsT2olTsvIp5bg"
# )

# # Print available collections to verify connection
# print(qdrant_client.get_collections())

# # Load PDF document
# loader = PyPDFLoader("E:\Attention is all you need.pdf")
# documents = loader.load()

# # Split documents into chunks
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
# texts = text_splitter.split_documents(documents)

# # Load the embedding model
# model_name = "BAAI/bge-large-en"
# model_kwargs = {'device': 'cpu'}
# encode_kwargs = {'normalize_embeddings': False}
# embeddings = HuggingFaceBgeEmbeddings(
#     model_name=model_name,
#     model_kwargs=model_kwargs,
#     encode_kwargs=encode_kwargs
# )

# # Initialize Qdrant vector database for cloud
# qdrant = Qdrant.from_documents(
#     texts,
#     embeddings,
#     url="https://23d3e77b-82ee-4929-8efe-5291110b98b9.europe-west3-0.gcp.cloud.qdrant.io:6333",
#     prefer_grpc=False,
#     collection_name="GenMind",
#     api_key="dq8OJwrHsyk6IVMFGpufuBC1PHDzSQjICQrV0Y9EDsT2olTsvIp5bg"
# )

# print("Vector DB Successfully Created!")



# import uuid
# from langchain.vectorstores import Qdrant
# from langchain.embeddings import HuggingFaceBgeEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.document_loaders import PyPDFLoader
# from qdrant_client.models import PointStruct
# from qdrant_client import QdrantClient

# # Initialize QdrantClient for the cloud instance
# qdrant_client = QdrantClient(
#     url="https://23d3e77b-82ee-4929-8efe-5291110b98b9.europe-west3-0.gcp.cloud.qdrant.io:6333",
#     api_key="dq8OJwrHsyk6IVMFGpufuBC1PHDzSQjICQrV0Y9EDsT2olTsvIp5bg"
# )

# # Verify the connection by listing existing collections
# print(qdrant_client.get_collections())

# # Load a PDF document
# loader = PyPDFLoader("E:\\Attention is all you need.pdf")
# documents = loader.load()

# # Split the document into chunks
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
# texts = text_splitter.split_documents(documents)

# # Load the embedding model
# model_name = "BAAI/bge-large-en"
# model_kwargs = {'device': 'cpu'}
# encode_kwargs = {'normalize_embeddings': False}
# embeddings = HuggingFaceBgeEmbeddings(
#     model_name=model_name,
#     model_kwargs=model_kwargs,
#     encode_kwargs=encode_kwargs
# )

# # Specify the user_id for this operation
# user_id = "fWHF2iGfYYmFAz62Kp85"  # Replace this dynamically based on the authenticated user

# # Prepare data points with user-specific metadata
# points = [
#     texts,
#     PointStruct(
#         id=str(uuid.uuid4()),  # Generate a unique UUID for each point
#         vector=embeddings.embed_query(text.page_content),  # Vector for the text chunk
#         payload={"user_id": user_id, "metadata": {"page_number": text.metadata.get("page_number", None)}}
#     )
#     for text in texts  # Loop through the text chunks
# ]

# # Upsert points into the single Qdrant collection with metadata
# qdrant_client.upsert(
#     collection_name="GenMind",  # Single collection name
#     points=points
# )

# print("User-specific vectors added successfully!")

# # Function to query user-specific data
# def search_user_data(query: str, user_id: str, top_k: int = 5):
#     """
#     Search vectors for a specific user in the collection.
#     """
#     results = qdrant_client.search(
#         collection_name="GenMind",  # Use the single shared collection
#         query_vector=embeddings.embed_query(query),  # Embed the query text
#         query_filter={
#             "must": [{"key": "user_id", "match": {"value": user_id}}]  # Filter by user_id
#         },
#         top=top_k  # Number of top results to return
#     )
#     return results

# # Example search query
# search_query = "Attention mechanism in neural networks"
# search_results = search_user_data(search_query, user_id="user_123")

# # Print search results
# print("Search Results:")
# for result in search_results:
#     print(f"Document ID: {result.id}, Score: {result.score}, Payload: {result.payload}")

# print("Search completed successfully!")


from langchain.vectorstores import Qdrant
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from qdrant_client import QdrantClient


# # Load PDF document
# loader = PyPDFLoader("E:\\Attention is all you need.pdf")
# documents = loader.load()

# # Split documents into chunks
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
# texts = text_splitter.split_documents(documents)

# # Specify user ID
# user_id = "kaif_17"  # Replace this with the authenticated user's ID

# # Add user_id to the metadata of each text chunk
# for text in texts:
#     if "metadata" not in text:
#         text.metadata = {}
#     text.metadata["user_id"] = user_id

# Load the embedding model
model_name = "BAAI/bge-large-en"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

# Initialize QdrantClient for cloud instance
qdrant_client = QdrantClient(
    url="https://23d3e77b-82ee-4929-8efe-5291110b98b9.europe-west3-0.gcp.cloud.qdrant.io:6333",
    api_key="dq8OJwrHsyk6IVMFGpufuBC1PHDzSQjICQrV0Y9EDsT2olTsvIp5bg"
)

# # Create the Qdrant vector database
# qdrant = Qdrant.from_documents(
#     texts,
#     embeddings,
#     url="https://23d3e77b-82ee-4929-8efe-5291110b98b9.europe-west3-0.gcp.cloud.qdrant.io:6333",
#     prefer_grpc=False,
#     collection_name="GenMind",
#     api_key="dq8OJwrHsyk6IVMFGpufuBC1PHDzSQjICQrV0Y9EDsT2olTsvIp5bg"
# )

# print("User-specific vectors added successfully!")

# Function to query user-specific data
def search_user_data(query: str, user_id: str, top_k: int = 5):
    """
    Search vectors for a specific user in the collection.
    """
    results = qdrant_client.search(
        collection_name="GenMind",  # Use the single shared collection
        query_vector=embeddings.embed_query(query),  # Embed the query text
        query_filter={
            "must": [{"key": "user_id", "match": {"value": user_id}}]  # Filter by user_id
        },
        limit=top_k  # Number of top results to return
    )
    return results

# Example search query
query_text = "About Abstract of Attention is all you need"
search_results = search_user_data(query=query_text, user_id="kaif_17")

# Print the results
print("Search Results:", search_results)


