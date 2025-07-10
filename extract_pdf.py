from pypdf import PdfReader, PdfWriter

# Load the original PDF
reader = PdfReader("University_Knowledge_base/Prospectus.pdf") 
writer = PdfWriter()

for i in range(30, 47): 
    writer.add_page(reader.pages[i])

# Save to a new PDF
with open("University_Knowledge_base/extracted_prospectus.pdf", "wb") as output_pdf:
    writer.write(output_pdf)

print("Pages extracted and saved to extracted_pages.pdf")

