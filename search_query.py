from config.vector_db import qdrant_client
from model_config.embed_model import model_embedding

def search_user_data(query: str, user_id: str, top_k: int = 5):
    """
    Search vectors for a specific user in the collection.
    
    Args:
        query (str): The search query
        user_id (str): The user ID to filter results
        top_k (int): Number of top results to return
        
    Returns:
        str: Concatenated content from matching documents
    """
    try:
        # Generate query embedding
        query_embedding = model_embedding().embed_query(query)

        # Perform search with user filter
        results = qdrant_client.search(
            collection_name="GenMind_3",
            query_vector=query_embedding,
            query_filter={
                "must": [
                    {
                        "key": "metadata.user_id",
                        "match": {"value": user_id}
                    }
                ]
            },
            limit=top_k
        )

        # Concatenate and return results
        if results:
            return " ".join(
                result.payload.get('page_content', '')
                for result in results
            )
        
        return ""

    except Exception as e:
        raise Exception(f"Error searching user data: {str(e)}")