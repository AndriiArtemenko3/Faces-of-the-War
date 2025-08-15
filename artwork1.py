import os
import matplotlib.pyplot as plt
from PIL import Image

image_folder = "filtered_dataset_2"

images_per_row = 25
thumb_size = (64, 64)

all_images = []
for filename in os.listdir(image_folder):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        img_path = os.path.join(image_folder, filename)
        # opens image from the source folder, convert to RGB, and resize to defined thumbnail size (thumb_size) -> in pixels
        try:
            img = Image.open(img_path).convert("RGB")
            img = img.resize(thumb_size)
            all_images.append(img)
        except Exception as e:
            print(f"Error loading {filename}: {e}")

# calculates number of rows for the artwork. total images in the source foulder divided by images_per_row variable + 1
rows = (len(all_images) // images_per_row) + 1
# makes a matplotlib grid for the artwork
fig, axes = plt.subplots(rows, images_per_row, figsize=(images_per_row, rows))
# set the spaces between the images
fig.subplots_adjust(wspace=0, hspace=0)

# for r in range(rows): -> loops through each row on the grid and displays images accordingly
idx = 0
for r in range(rows):
    for c in range(images_per_row):
        ax = axes[r, c] if rows > 1 else axes[c]
        ax.axis("off")
        if idx < len(all_images):
            ax.imshow(all_images[idx])
            idx += 1

plt.show()