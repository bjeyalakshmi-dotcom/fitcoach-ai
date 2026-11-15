"""
One-time script to index fitness_knowledge.py chunks into Pinecone.

Usage:
    python tools/knowledge_indexer.py

Requires:
    OPENAI_API_KEY and PINECONE_API_KEY set in .env or environment.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from data.fitness_knowledge import KNOWLEDGE_CHUNKS

PINECONE_INDEX = "fitcoach-knowledge"
EMBED_MODEL    = "text-embedding-3-small"
DIMENSION      = 1536
BATCH_SIZE     = 50


def main():
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    # Create index if it does not exist
    existing = [idx.name for idx in pc.list_indexes()]
    if PINECONE_INDEX not in existing:
        print(f"Creating Pinecone index '{PINECONE_INDEX}' ...")
        pc.create_index(
            name=PINECONE_INDEX,
            dimension=DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        # Wait for index to be ready
        while not pc.describe_index(PINECONE_INDEX).status["ready"]:
            print("Waiting for index to be ready...")
            time.sleep(2)
        print("Index ready.")
    else:
        print(f"Index '{PINECONE_INDEX}' already exists.")

    index = pc.Index(PINECONE_INDEX)

    # Embed and upsert in batches
    vectors = []
    print(f"Embedding {len(KNOWLEDGE_CHUNKS)} chunks...")
    for chunk in KNOWLEDGE_CHUNKS:
        response = openai_client.embeddings.create(
            model=EMBED_MODEL,
            input=chunk["text"],
        )
        embedding = response.data[0].embedding
        vectors.append({
            "id":       chunk["id"],
            "values":   embedding,
            "metadata": {**chunk["metadata"], "text": chunk["text"]},
        })
        print(f"  Embedded: {chunk['id']}")

        if len(vectors) >= BATCH_SIZE:
            index.upsert(vectors=vectors)
            print(f"  Upserted batch of {len(vectors)}")
            vectors = []

    if vectors:
        index.upsert(vectors=vectors)
        print(f"  Upserted final batch of {len(vectors)}")

    stats = index.describe_index_stats()
    print(f"\nDone. Pinecone index stats: {stats}")


if __name__ == "__main__":
    main()
