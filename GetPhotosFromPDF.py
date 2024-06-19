import fitz  # PyMuPDF
from PIL import Image
import io
import os

# Get the directory of the currently executing script
script_dir = os.path.dirname(__file__)

# Open the PDF
pdf_document = "PhotoPDF.pdf"
doc = fitz.open(pdf_document)

folder_to_save = os.path.join(script_dir, 'PDFimages/')
if not os.path.exists(folder_to_save):
    os.makedirs(folder_to_save)

# List to hold names of images to delete
images_to_delete = []

for page_number in range(len(doc)):
    page = doc.load_page(page_number)
    images = page.get_images(full=True)
    
    for img_index, img in enumerate(images):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        image = Image.open(io.BytesIO(image_bytes))
        image_filename = f"page_{page_number + 1}_image_{img_index + 1}.{image_ext}"
        image_path = os.path.join(folder_to_save, image_filename)
        image.save(image_path)
        print(f"Saved: {image_filename}")
        
        # Check if the image name contains 'image_1'
        if 'image_1' in image_filename:
            images_to_delete.append(image_path)

print("Done extracting images.")

# Delete images containing 'image_1' in their names
for image_path in images_to_delete:
    if os.path.exists(image_path):
        os.remove(image_path)
        print(f"Deleted: {image_path}")
    else:
        print(f"File not found: {image_path}")

print("Done deleting images.")
