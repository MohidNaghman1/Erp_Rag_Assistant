import json
import chromadb
from sentence_transformers import SentenceTransformer

def load_final_chunks(file_path):
    """Loads the final, chunked data from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ ERROR: The file '{file_path}' was not found.")
        return None

def build_vector_store(chunks, collection_name, embedding_model_name):
    """Creates embeddings and stores them in a ChromaDB collection."""
    if not chunks:
        print("No chunks to process.")
        return

    print("Initializing ChromaDB client...")
    # Create a persistent client that saves to disk
    client = chromadb.PersistentClient(path="./university_db1")
    
    # Load the embedding model
    print(f"Loading embedding model: {embedding_model_name}")
    # This will download the model the first time it's run
    embedding_model = SentenceTransformer(embedding_model_name, trust_remote_code=True)
    
    print(f"Creating or getting collection: {collection_name}")
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"} # Use cosine similarity
    )

    print(f"Processing {len(chunks)} chunks to add to the vector store...")
    
    # Prepare data for ChromaDB
    documents = [chunk['content'] for chunk in chunks]
    metadatas = [chunk['metadata'] for chunk in chunks]
    ids = [f"chunk_{i}" for i in range(len(chunks))] # Create a unique ID for each chunk

    # Generate embeddings for all documents in batches
    print("Generating embeddings for all documents... (This may take a while)")
    embeddings = embedding_model.encode(documents, show_progress_bar=True)
    
    # Add to ChromaDB collection
    print("Adding documents, embeddings, and metadata to ChromaDB...")
    collection.add(
        embeddings=embeddings.tolist(), # ChromaDB needs a list
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print("\n✅ Vector store built successfully!")
    print(f"   Database saved in './university_db' directory.")
    print(f"   Total documents in collection: {collection.count()}")

if __name__ == "__main__":
    input_file = "final_chunked_data.json"
    # A good, free, and small embedding model to start with
    model_name = 'all-MiniLM-L6-v2' 
    collection_name = "university_handbook"
    
    final_chunks = load_final_chunks(input_file)
    if final_chunks:
        build_vector_store(final_chunks, collection_name, model_name)