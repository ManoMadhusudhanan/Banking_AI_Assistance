from qdrant_client import QdrantClient
import os

client = QdrantClient(
    url="Your QDRANT_UI",
    api_key=os.getenv("QDRANT_API_KEY"),
    check_compatibility=False
)


print(client.get_collections())
