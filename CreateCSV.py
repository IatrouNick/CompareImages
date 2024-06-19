import os
import cv2
import numpy as np
import csv
from keras.applications.vgg16 import VGG16, preprocess_input
from keras.preprocessing import image
from keras.models import Model
import datetime
import os

# Get the directory of the currently executing script
script_dir = os.path.dirname(__file__)

# Load the VGG16 model pre-trained on ImageNet
base_model = VGG16(weights='imagenet')
# Remove the top layer (softmax layer) to get the features from the last convolutional layer
model = Model(inputs=base_model.input, outputs=base_model.get_layer('fc1').output)

def extract_features(img_path):
    # Load the image with the target size of 224x224
    img = image.load_img(img_path, target_size=(224, 224))
    # Convert the image to array
    img_data = image.img_to_array(img)
    # Expand the dimensions to match the model input
    img_data = np.expand_dims(img_data, axis=0)
    # Preprocess the image
    img_data = preprocess_input(img_data)
    # Get the features
    features = model.predict(img_data)
    return features

def calculate_similarity(features1, features2):
    # Calculate the cosine similarity between the features
    similarity = np.dot(features1, features2.T) / (np.linalg.norm(features1) * np.linalg.norm(features2))
    similarity = similarity[0][0]  # Extract the value from the matrix
    return similarity

if __name__ == "__main__":
    photos_folder_path = os.path.join(script_dir, 'Photos/')
    test_folder_path = os.path.join(script_dir, 'PDFimages/')
    
    #photos_folder_path = 'C:/Users/iatro/Desktop/PhotoCheck/Photos/'  # Folder containing the photos to compare
    #test_folder_path = 'C:/Users/iatro/Desktop/PhotoCheck/PDFimages/'  # Folder containing the images to compare against

    # Initialize a dictionary to store the similarity scores for each image
    similarities_dict = {}

    # Extract features for all images in the Photos folder
    photos_features_dict = {}
    for filename in os.listdir(photos_folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(photos_folder_path, filename)
            photos_features_dict[filename] = extract_features(file_path)

    # Extract features for all images in the Test folder
    test_features_dict = {}
    for filename in os.listdir(test_folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(test_folder_path, filename)
            test_features_dict[filename] = extract_features(file_path)

    # Compare each image in the Photos folder with every image in the Test folder
    for photo_image, photo_features in photos_features_dict.items():
        similarities_dict[photo_image] = []
        for test_image, test_features in test_features_dict.items():
            similarity = calculate_similarity(photo_features, test_features)
            similarities_dict[photo_image].append((photo_image, test_image, similarity))

    # Write the similarities to a CSV file
    csv_file_path = os.path.join(script_dir, 'similarities.csv')
    #csv_file_path = 'C:/Users/iatro/Desktop/PhotoCheck/similarities.csv'
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Photo Image', 'Test Image', 'Similarity'])

        for photo_image, similarities in similarities_dict.items():
            # Sort the similarities for the current photo image in descending order
            similarities.sort(key=lambda x: x[2], reverse=True)
            for similarity in similarities:
                writer.writerow(similarity)

    print(f"Similarities have been written to {csv_file_path}")
