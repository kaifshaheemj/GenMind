# from langchain.vectorstores import Qdrant
# from langchain.embeddings import HuggingFaceBgeEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.document_loaders import PyPDFLoader
# from qdrant_client import QdrantClient

# # Step 1: Initialize Qdrant Client for cloud instance
# qdrant_client = QdrantClient(
#     url="https://23d3e77b-82ee-4929-8efe-5291110b98b9.europe-west3-0.gcp.cloud.qdrant.io:6333",
#     api_key="dq8OJwrHsyk6IVMFGpufuBC1PHDzSQjICQrV0Y9EDsT2olTsvIp5bg"
# )

# # Step 2: Load PDF document
# loader = PyPDFLoader(r"E:\\Attention is all you need.pdf")  # Replace with your PDF path
# documents = loader.load()

# # Step 3: Split documents into chunks
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
# texts = text_splitter.split_documents(documents)

# # Step 4: Specify user ID
# user_id = "fWHF2iGfYYmFAz62Kp85"  # Replace with authenticated user's ID

# # Add user_id to the metadata of each text chunk
# for text in texts:
#     if "metadata" not in text:
#         text.metadata = {}
#     text.metadata["user_id"] = user_id

# # Step 5: Load the embedding model
# model_name = "BAAI/bge-large-en"
# model_kwargs = {'device': 'cpu'}
# encode_kwargs = {'normalize_embeddings': False}
# embeddings = HuggingFaceBgeEmbeddings(
#     model_name=model_name,
#     model_kwargs=model_kwargs,
#     encode_kwargs=encode_kwargs
# )

# # Step 6: Create the Qdrant vector database
# qdrant = Qdrant.from_documents(
#     texts,
#     embeddings,
#     url="https://23d3e77b-82ee-4929-8efe-5291110b98b9.europe-west3-0.gcp.cloud.qdrant.io:6333",
#     prefer_grpc=False,
#     collection_name="GenMind_1",  # Shared collection for all users
#     api_key="dq8OJwrHsyk6IVMFGpufuBC1PHDzSQjICQrV0Y9EDsT2olTsvIp5bg"
# )

# print("User-specific vectors added successfully!")

# # Step 7: Define function to query user-specific data
# def search_user_data(query: str, user_id: str, top_k: int = 5):
#     """
#     Search vectors for a specific user in the collection.
#     """
#     results = qdrant_client.search(
#         collection_name="GenMind_1",  # Shared collection
#         query_vector=embeddings.embed_query(query),  # Embed the query text
#         query_filter={
#             "must": [{"key": "user_id", "match": {"value": user_id}}]  # Filter by user_id
#         },
#         limit=top_k  # Number of top results to return
#     )
#     return results

# # Step 8: Example search query
# query_text = "About Abstract of Attention is all you need"
# print("Query_vector:", embeddings.embed_query(query_text))
# search_results = search_user_data(query=query_text, user_id="fWHF2iGfYYmFAz62Kp85")

# # Step 9: Print the search results
# print("Search Results:")
# for result in search_results:
#     print(f"Score: {result.score}, Payload: {result.payload}")


from langchain.vectorstores import Qdrant
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from qdrant_client import QdrantClient

# Step 1: Initialize Qdrant Client for cloud instance
qdrant_client = QdrantClient(
    url="https://23d3e77b-82ee-4929-8efe-5291110b98b9.europe-west3-0.gcp.cloud.qdrant.io:6333",
    api_key="dq8OJwrHsyk6IVMFGpufuBC1PHDzSQjICQrV0Y9EDsT2olTsvIp5bg"
)

# Step 2: Load PDF document
loader = PyPDFLoader(r"E:\\Attention is all you need.pdf")  # Replace with your PDF path
documents = loader.load()

# Step 3: Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = text_splitter.split_documents(documents)

# Step 4: Specify user ID
user_id = "fWHF2iGfYYmFAz62Kp85"  # Replace with authenticated user's ID

# Add user_id to the metadata of each text chunk
for text in texts:
    if "metadata" not in text:
        text.metadata = {}
    text.metadata["user_id"] = user_id

# Verify metadata before insertion
for text in texts:
    print("Metadata before insertion:", text.metadata)

# Step 5: Load the embedding model
model_name = "BAAI/bge-large-en"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

# Step 6: Create the Qdrant vector database
qdrant = Qdrant.from_documents(
    texts,
    embeddings,
    url="https://23d3e77b-82ee-4929-8efe-5291110b98b9.europe-west3-0.gcp.cloud.qdrant.io:6333",
    prefer_grpc=False,
    collection_name="GenMind_1",  # Shared collection for all users
    api_key="dq8OJwrHsyk6IVMFGpufuBC1PHDzSQjICQrV0Y9EDsT2olTsvIp5bg"
)

print("User-specific vectors added successfully!")

# Step 7: Check collection info
collection_info = qdrant_client.get_collection(collection_name="GenMind_1")
print("Collection Info:", collection_info)

# Step 8: Test search without user filter
query_text = "About Abstract of Attention is all you need"
results_no_filter = qdrant_client.search(
    collection_name="GenMind_1",
    query_vector=embeddings.embed_query(query_text),
    limit=5
)
print("Results without user filter:", results_no_filter)

# Step 9: Test stored metadata
vectors = qdrant_client.scroll(collection_name="GenMind_1", limit=5)
for vector in vectors[0]:
    print("Stored Vector Metadata:", vector.payload)

# Step 10: Define function to query user-specific data
def search_user_data(query: str, user_id: str, top_k: int = 5):
    """
    Search vectors for a specific user in the collection.
    """
    results = qdrant_client.search(
        collection_name="GenMind_1",  # Shared collection
        query_vector=embeddings.embed_query(query),  # Embed the query text
        query_filter={
            "must": [{"key": "user_id", "match": {"value": user_id}}]  # Filter by user_id
        },
        limit=top_k  # Number of top results to return
    )
    return results

# Step 11: Example search query
search_results = search_user_data(query=query_text, user_id="fWHF2iGfYYmFAz62Kp85")

# Step 12: Print the search results
print("Search Results:")
if not search_results:
    print("No results found.")
else:
    for result in search_results:
        print(f"Score: {result.score}, Payload: {result.payload}")
