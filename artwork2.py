import os, math
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

image_folder = "filtered_dataset_2"
thumb = 96
cols = 30

# for fn in os.listdie(image_folder): -> loops though images, converts them to RGB + crops them, resizes them to thumbnail size and stores them into numpy array
tiles = []
for fn in os.listdir(image_folder):
    if fn.lower().endswith((".jpg",".jpeg",".png")):
        p = os.path.join(image_folder, fn)
        try:
            im = Image.open(p).convert("RGB")
            w, h = im.size
            m = min(w, h)
            left = (w - m) // 2
            top  = (h - m) // 2
            im = im.crop((left, top, left + m, top + m))
            im = im.resize((thumb, thumb), Image.LANCZOS)
            tiles.append(np.asarray(im))
        except Exception as e:
            print(f"Skip {fn}: {e}")

if not tiles:
    raise SystemExit("No images found.")

#calculating grid size based on tiles and column size
rows = math.ceil(len(tiles) / cols)

# making white background
canvas = np.ones((rows*thumb, cols*thumb, 3), dtype=np.uint8) * 255
# for r in range(rows): -> Loop through each row and column of the grid. places thumbnails from tiles into their correct positions on the canvas
for r in range(rows):
    for c in range(cols):
        if k >= len(tiles): break
        canvas[r*thumb:(r+1)*thumb, c*thumb:(c+1)*thumb, :] = tiles[k]
        k += 1

plt.figure(figsize=(cols*0.35, rows*0.35))
plt.imshow(canvas)
plt.axis("off")
plt.margins(0, 0)
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
plt.savefig("mosaic_uniform.png", dpi=300, bbox_inches="tight", pad_inches=0)
plt.show()