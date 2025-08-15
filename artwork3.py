import os, math
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import random

image_folder = "filtered_dataset_2"
MASK_PATH = "ukraine_map.jpeg" #a path to the mask image
OUTPUT = "mosaic_ukraine.png"

TILE = 64
COLS = 80
BG_COLOR = (255, 255, 255)
FILL_WHERE = "black"
RANDOMIZE_IMAGES = True

def load_tiles(folder, tile_px):
    '''
    Loads images from a folder, center-crops to squares, and resizes to fixed tiles.

    - Supports .jpg, .jpeg, .png
    - Converts images to RGB, crops a centered square, resizes with LANCZOS, and appends to the returned list.
    - If `RANDOMIZE_IMAGES` is True, shuffles the tiles in-place.
    - Files that cannot be opened/processed are skipped

    '''
    tiles = []
    for fn in os.listdir(folder):
        if fn.lower().endswith((".jpg",".jpeg",".png")):
            path = os.path.join(folder, fn)
            try:
                im = Image.open(path).convert("RGB")
                w, h = im.size
                m = min(w, h)
                im = im.crop(((w-m)//2, (h-m)//2, (w+m)//2, (h+m)//2))
                im = im.resize((tile_px, tile_px), Image.LANCZOS)
                tiles.append(np.asarray(im))
            except Exception as e:
                print(f"Skip {fn}: {e}")
    if RANDOMIZE_IMAGES:
        random.shuffle(tiles)
    return tiles

tiles = load_tiles(image_folder, TILE)
if not tiles:
    raise SystemExit("No images found in image_folder")

# loads the mask image in grayscale and calculates its aspect ratio (height/width)
mask_img = Image.open(MASK_PATH).convert("L")
mask_w, mask_h = mask_img.size
aspect = mask_h / mask_w

# calculates canvas size based on columns, tile size, and mask aspect ratio
canvas_w = COLS * TILE
canvas_h = int(round(canvas_w * aspect / TILE)) * TILE
rows = canvas_h // TILE

# resizes mask to match canvas dimensions and convert to NumPy array for pixel check
mask = mask_img.resize((canvas_w, canvas_h), Image.BILINEAR)
mask_np = np.asarray(mask)

# decides that only black pixels will count as inside_bool
if FILL_WHERE.lower() == "black":
    inside_bool = mask_np < 128
else:
    inside_bool = mask_np >= 128

# gets grid cell coordinates that fall inside the mask shape
inside_cells = []
for r in range(rows):
    for c in range(COLS):
        y = r*TILE + TILE//2
        x = c*TILE + TILE//2
        if inside_bool[y, x]:
            inside_cells.append((r, c))

canvas = np.full((rows*TILE, COLS*TILE, 3), BG_COLOR, dtype=np.uint8)

# places tiles into the cells inside the mask
k = 0
n_tiles = len(tiles)
for (r, c) in inside_cells:
    tile = tiles[k % n_tiles]
    canvas[r*TILE:(r+1)*TILE, c*TILE:(c+1)*TILE] = tile
    k += 1

plt.figure(figsize=(COLS*0.25, rows*0.25))
plt.imshow(canvas)
plt.axis("off")
plt.margins(0, 0)
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
plt.savefig(OUTPUT, dpi=300, bbox_inches="tight", pad_inches=0)
plt.show()

print(f"Saved: {OUTPUT}")