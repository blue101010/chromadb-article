import chromadb
import uuid

client = chromadb.Client()

collection = client.create_collection(name="policies")

with open("policies.txt", "r", encoding="utf-8") as f:
    policies: list[str] = f.read().splitlines()


collection.add(
    ids=[str(uuid.uuid4()) for _ in policies],
    documents=policies,
    metadatas=[{"line": line} for line in range(len(policies))],
)

print(collection.peek())