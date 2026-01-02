from qdrant_client import QdrantClient
import os

client = QdrantClient(
    url="https://c299fd03-1832-4dc4-8e2e-af6b0fd684f7.us-east4-0.gcp.cloud.qdrant.io:6333",
    api_key=os.getenv("QDRANT_API_KEY"),
    check_compatibility=False
)

print(client.get_collections())