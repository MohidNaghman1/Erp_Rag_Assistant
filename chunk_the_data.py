import json
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_data(file_path):
    """Loads the extracted data from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ ERROR: The file '{file_path}' was not found.")
        return None

def chunk_data(chunks):
    """
    Applies a second layer of chunking to long text elements,
    while leaving tables and short elements intact.
    """
    if not chunks:
        return []

    # Initialize the text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # The max size of a chunk (in characters)
        chunk_overlap=150,  # The overlap between chunks to maintain context
        length_function=len
    )

    final_chunks = []
    
    for chunk in chunks:
        element_type = chunk['metadata']['element_type']
        content = chunk['content']
        
        # We only want to split long text elements.
        # Tables, titles, and other short elements are kept as-is.
        if element_type in ["NarrativeText", "Text", "UncategorizedText"] and len(content) > text_splitter._chunk_size:
            print(f"Splitting a long '{element_type}' chunk from {chunk['metadata']['source_file']}...")
            
            # Split the long text
            sub_chunks = text_splitter.split_text(content)
            
            # Create a new chunk for each sub-chunk, preserving metadata
            for i, sub_chunk_content in enumerate(sub_chunks):
                final_chunks.append({
                    "content": sub_chunk_content,
                    "metadata": {
                        **chunk['metadata'], # Inherit original metadata
                        "chunk_index": i + 1 # Add which part of the split it is
                    }
                })
        else:
            # If the chunk is a table or short text, add it directly
            final_chunks.append(chunk)
            
    return final_chunks

if __name__ == "__main__":
    input_file = "extracted_university_data.json"
    output_file = "final_chunked_data.json"
    
    # 1. Load the data extracted by our first script
    initial_chunks = load_data(input_file)
    
    if initial_chunks:
        # 2. Apply the second layer of chunking
        final_chunks = chunk_data(initial_chunks)
        
        print(f"\nOriginal chunk count: {len(initial_chunks)}")
        print(f"Final chunk count after splitting: {len(final_chunks)}")
        
        # 3. Save the final, ready-to-embed data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_chunks, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Final, chunked data saved to '{output_file}'")