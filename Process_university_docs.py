import os
import json
from unstructured.partition.pdf import partition_pdf


os.environ['UNSTRUCTURED_CACHE_DIR'] = 'model_cache'
os.environ['HF_HOME'] = 'model_cache'
# ==================== THE GUARANTEED FIX ====================
# Ensure these paths are correct for your system.
poppler_bin_path = r"C:\Program Files\poppler-24.08.0\Library\bin"
tesseract_bin_path = r"C:\Program Files\Tesseract-OCR"

# Add these paths to the environment variable for this script only.
os.environ["PATH"] += os.pathsep + poppler_bin_path
os.environ["PATH"] += os.pathsep + tesseract_bin_path
# =============================================================

# --- CONFIGURATION ---
PDF_INPUT_DIR = "University_Knowledge_base"
JSON_OUTPUT_FILE = "extracted_university_data.json" # Define the output filename
CATEGORIES_TO_IGNORE = ["Header", "Footer", "PageNumber"]

def process_all_pdfs(input_dir):
    """
    Processes all PDFs in a directory, handling text and tables,
    and returns a clean list of chunks for RAG ingestion.
    """
    if not os.path.isdir(input_dir):
        print(f"❌ ERROR: Input directory '{input_dir}' not found.")
        return []

    all_final_chunks = []
    
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print(f"⚠️ WARNING: No PDF files found in '{input_dir}'.")
        return []

    print(f"Found {len(pdf_files)} PDF(s) to process. Starting...")

    for filename in pdf_files:
        pdf_path = os.path.join(input_dir, filename)
        print(f"\nProcessing file: {filename}")
        
        try:
            elements = partition_pdf(
                filename=pdf_path,
                strategy="hi_res",
                # Attempt to get high-quality tables
                infer_table_structure=True,
                # Don't save images, but get text from them
                extract_images_in_pdf=False,
                languages=["eng"]
            )

            # --- Process and clean the extracted elements ---
            for element in elements:
                if element.category in CATEGORIES_TO_IGNORE:
                    continue

                if element.category == "Table":
                    content = element.metadata.text_as_html
                    element_type = "Table"
                    if not content: continue
                else:
                    content = element.text
                    element_type = element.category
                    if not content.strip(): continue

                chunk = {
                    "content": content,
                    "metadata": {
                        "source_file": filename,
                        "page_number": element.metadata.page_number,
                        "element_type": element_type
                    }               
                }
                all_final_chunks.append(chunk)

            print(f"✅ Successfully processed and chunked '{filename}'.")

        except Exception as e:
            print(f"❌ ERROR processing '{filename}': {e}")
            continue

    return all_final_chunks

def save_chunks_to_json(chunks, output_file):
    """Saves a list of chunks to a JSON file."""
    if not chunks:
        print("No data to save.")
        return

    print(f"\n💾 Saving {len(chunks)} chunks to '{output_file}'...")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Use indent=4 for a human-readable, pretty-printed JSON file
            json.dump(chunks, f, indent=4, ensure_ascii=False)
        print("✅ Successfully saved data.")
    except Exception as e:
        print(f"❌ ERROR saving to JSON: {e}")

if __name__ == "__main__":
    # 1. Run the main processing function
    all_chunks = process_all_pdfs(PDF_INPUT_DIR)

    if all_chunks:
        # 2. Save the extracted chunks to the specified JSON file
        save_chunks_to_json(all_chunks, JSON_OUTPUT_FILE)
        
        print("\n========================================================")
        print(f"🎉 Pipeline complete! Total chunks extracted: {len(all_chunks)}")
        print(f"   Data saved in '{JSON_OUTPUT_FILE}'")
        print("========================================================")

    else:
        print("\nNo data was extracted. Please check the error messages above.")