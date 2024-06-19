import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pandas as pd
import os
import shutil

# Get the directory of the currently executing script
script_dir = os.path.dirname(__file__)

# Load the CSV file
csv_file_path = os.path.join(script_dir, 'similarities.csv')
df = pd.read_csv(csv_file_path)

# Define relative paths based on the script's directory
photos_dir = os.path.join(script_dir, 'Photos/')
pdf_images_dir = os.path.join(script_dir, 'PDFimages/')
found_photos_dir = os.path.join(photos_dir, 'found/')
found_pdf_images_dir = os.path.join(pdf_images_dir, 'found/')

# Create the destination directories if they do not exist
if not os.path.exists(found_photos_dir):
    os.makedirs(found_photos_dir)
if not os.path.exists(found_pdf_images_dir):
    os.makedirs(found_pdf_images_dir)

# Helper function to load images
def load_image(image_path, max_size=(400, 400)):
    img = Image.open(image_path)
    img.thumbnail(max_size)
    return ImageTk.PhotoImage(img)

# Function to handle "Yes" button click
def on_yes():
    global df

    if len(df) == 0:
        messagebox.showwarning("Warning", "No image pair is currently loaded.")
        return

    photo_image = df.iloc[0]['Photo Image']
    test_image = df.iloc[0]['Test Image']

    # Move the photo image to the 'found_photos_dir' directory if it exists in photos_dir
    photo_image_path = os.path.join(photos_dir, photo_image)
    if os.path.exists(photo_image_path):
        shutil.move(photo_image_path, os.path.join(found_photos_dir, photo_image))
        #messagebox.showinfo("Moved", f"Moved '{photo_image}' to 'found' directory in Photos.")
    else:
        messagebox.showwarning("Warning", f"Photo Image '{photo_image}' not found in directory.")

    # Move the test image to the 'found_pdf_images_dir' directory if it exists in pdf_images_dir
    test_image_path = os.path.join(pdf_images_dir, test_image)
    if os.path.exists(test_image_path):
        shutil.move(test_image_path, os.path.join(found_pdf_images_dir, test_image))
        #messagebox.showinfo("Moved", f"Moved '{test_image}' to 'found' directory in PDFimages.")
    else:
        messagebox.showwarning("Warning", f"Test Image '{test_image}' not found in directory.")

    # Prepare the data for results.csv
    result_row = {
        'image ': test_image
    }

    result_file_path = os.path.join(script_dir, 'results.csv')
    result_exists = os.path.exists(result_file_path)

    # Write to results.csv without empty lines
    result_exists = os.path.exists(result_file_path)
    mode = 'a' if result_exists else 'w'

    with open(result_file_path, mode, newline='') as f:
        if not result_exists:
            pd.DataFrame([result_row]).to_csv(f, header=True, index=False)
        else:
            pd.DataFrame([result_row]).to_csv(f, header=False, index=False)
    # Remove all rows containing both 'Photo Image' and 'Test Image' from original CSV
    df = df[~((df['Photo Image'] == photo_image) | (df['Test Image'] == test_image))]

    # Save the updated DataFrame back to the original CSV file
    df.to_csv(csv_file_path, index=False)

    # Always show the image from the first row
    show_first_image()

# Function to handle "No" button click
def on_no():
    global df

    if len(df) == 0:
        messagebox.showwarning("Warning", "No image pair is currently loaded.")
        return

    # Drop the current row (first row)
    df = df.drop(index=df.index[0]).reset_index(drop=True)

    # Save the updated DataFrame back to the original CSV file
    df.to_csv(csv_file_path, index=False)

    # Show the next image pair
    show_first_image()

# Function to handle "Skip" button click
def on_skip():
    global df

    if len(df) == 0:
        messagebox.showwarning("Warning", "No image pair is currently loaded.")
        return

    photo_image = df.iloc[0]['Photo Image']

    # Remove all rows containing 'Photo Image' from original CSV
    df = df[df['Photo Image'] != photo_image]

    # Save the updated DataFrame back to the original CSV file
    df.to_csv(csv_file_path, index=False)

    # Show the next image pair
    show_first_image()

# Function to display the first image pair
def show_first_image():
    global df

    # If DataFrame is empty, show message and exit
    if len(df) == 0:
        messagebox.showinfo("Info", "No more image pairs to show.")
        root.quit()
        return

    # Load the first pair of images
    photo_image_name = df.iloc[0]['Photo Image']
    test_image_name = df.iloc[0]['Test Image']

    # Determine the paths for display
    photo_image_path = os.path.join(photos_dir, photo_image_name)
    test_image_path = os.path.join(pdf_images_dir, test_image_name)

    # Check if the image paths exist
    if not os.path.exists(photo_image_path):
        messagebox.showwarning("Warning", f"Photo Image '{photo_image_name}' not found in directory.")
        return
    if not os.path.exists(test_image_path):
        messagebox.showwarning("Warning", f"Test Image '{test_image_name}' not found in directory.")
        return

    # Load images and update labels
    photo_img = load_image(photo_image_path)
    test_img = load_image(test_image_path)

    # Update the images and labels in the UI
    photo_label.config(text=photo_image_name)
    photo_image_label.config(image=photo_img)
    photo_image_label.image = photo_img
    test_label.config(text=test_image_name)
    test_image_label.config(image=test_img)
    test_image_label.image = test_img

# Create the main window
root = tk.Tk()
root.title("Image Similarity Checker")

# Create frames for the images and labels
photo_frame = tk.Frame(root)
photo_frame.pack(side="left", padx=20, pady=20)

test_frame = tk.Frame(root)
test_frame.pack(side="right", padx=20, pady=20)

# Create labels to display the image filenames
photo_label = tk.Label(photo_frame, text="")
photo_label.pack()

test_label = tk.Label(test_frame, text="")
test_label.pack()

# Create labels to display the images
photo_image_label = tk.Label(photo_frame)
photo_image_label.pack()

test_image_label = tk.Label(test_frame)
test_image_label.pack()

# Create Yes, No, and Skip buttons
yes_button = tk.Button(root, text="Yes", command=on_yes, bg="green", fg="white")
yes_button.pack(side="left", padx=20, pady=20)

no_button = tk.Button(root, text="No", command=on_no, bg="red", fg="white")
no_button.pack(side="right", padx=20, pady=20)

skip_button = tk.Button(root, text="Skip", command=on_skip, bg="blue", fg="white")
skip_button.pack(side="top", pady=20)

# Always show the image from the first row initially
show_first_image()

# Start the main loop
root.mainloop()
