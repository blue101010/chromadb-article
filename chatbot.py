import chromadb
import uuid

# --- Phase d'indexation ---
client = chromadb.Client()
collection = client.create_collection(
    name="policies"
)

with open("policies.txt", "r", encoding="utf-8") as f:
    policies = f.read().splitlines()

collection.add(
    ids=[str(uuid.uuid4()) for _ in policies],
    documents=policies,
    metadatas=[{"line": i} for i in range(len(policies))],
)

# --- Phase de récupération ---
queries = [
    "Can I return swimwear?",
    "Do you ship internationally?",
    "What about carbon emissions?",
]

for q in queries:
    results = collection.query(
        query_texts=[q], n_results=3
    )
    print(f"\nQuery: {q}")
    for doc, dist, meta in zip(
        results["documents"][0],
        results["distances"][0],
        results["metadatas"][0],
    ):
        print(f"  [{dist:.4f}] (ligne {meta['line']}) "
              f"{doc[:70]}...")
