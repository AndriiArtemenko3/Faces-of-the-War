import praw
import time
import requests
import cv2
import numpy as np
import os
import pickle

from utils.create_token import create_token

POST_SEARCH_AMOUNT = 500 # number of posts to search through 
QUERY = [ # my keywords
    # common keywords to document war crimes
    "kill* OR injure* OR civilian OR murder* OR drone* OR terror*",
    # keywords to document attacks on civil/residential infrastracture
    "Kyiv OR Odessa OR Kharkiv OR Donetsk OR Kherson OR Sumy"
    # more rare but useful 
    "prisoner OR cover OR aftermath OR attack OR children OR family"
]
IMAGE_RESIZE_DIMS = (224, 224)

def create_folder(image_path):
    '''
    Create a folder at the given path if it does not already exist
    '''
    CHECK_FOLDER = os.path.isdir(image_path)
    if not CHECK_FOLDER:
        os.makedirs(image_path)


dir_path = os.path.dirname(os.path.realpath(__file__))
image_path = os.path.join(dir_path, "images/")
ignore_path = os.path.join(dir_path, "ignore_images/")
create_folder(image_path)

if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
else:
    creds = create_token()
    pickle_out = open("token.pickle","wb")
    pickle.dump(creds, pickle_out)

reddit = praw.Reddit(client_id=creds['client_id'], 
                    client_secret=creds['client_secret'],
                    user_agent=creds['user_agent'],
                    username=creds['username'],
                    password=creds['password'])

def fetch_all_posts(subreddit, query, limit):
    '''
    Fetch unique Reddit posts from a given subreddit using multiple search modes.

    This function runs searches using the Reddit API (via PRAW) for a given
    query, attempting 'top', 'new', and 'hot' sorting to maximize coverage.
    It uses a helper function to ensure no duplicate posts are added.
    '''
    seen_ids = set()
    results = []

    def add_unique(posts):
        '''
        Append posts to the results list if they have not already been seen.
        '''
        for post in posts:
            if post.id not in seen_ids:
                seen_ids.add(post.id)
                results.append(post)

    try:
        add_unique(subreddit.search(query, sort="top", time_filter="all", syntax="lucene", limit=limit, params={"include_over_18": "on"}))
    except Exception as e:
        print(f"Search failed in {subreddit.display_name}: {e}")

    try:
        add_unique(subreddit.search(query, sort="new", time_filter="month", syntax="lucene", limit=limit, params={"include_over_18": "on"}))
        add_unique(subreddit.search(query, sort="hot", time_filter="all", syntax="lucene", limit=limit, params={"include_over_18": "on"}))
    except Exception as e:
        print(f"Fallback fetch failed in {subreddit.display_name}: {e}")

    return results

ignore_paths = []
for dirpath, _, filenames in os.walk(ignore_path):
    ignore_paths.extend([os.path.join(dirpath, file) for file in filenames])

ignore_images = []
for path in ignore_paths:
    img = cv2.imread(path)
    if img is not None:
        img_resized = cv2.resize(img, IMAGE_RESIZE_DIMS)
        ignore_images.append(img_resized)
f_final = open("sub_list.csv", "r")
img_notfound = cv2.imread('imageNF.png')
# for line in f_final: -> loop iterates over each subreddit in sub_list.csv file
for line in f_final:
    sub = line.strip()
    subreddit = reddit.subreddit(sub)

    print(f"Loading {sub}!")
    count = 0
    results = []
    # for query in QUERY: -> loop runs each search query for the current subreddit
    for query in QUERY: 
        print(f"Running query batch: '{query}'")
        query_results = fetch_all_posts(subreddit, query, POST_SEARCH_AMOUNT)
        results.extend(query_results)
        time.sleep(0.8) #i run on 1, takes ages. 0.5s seems better
        print(f"Total fetched: {len(results)} posts from r/{sub}")
        print(f"Total fetched: {len(results)} posts from r/{sub}")
    # for submission in results: loop processes and filters fetched posts
    for submission in results:
        time.sleep(0.4) #0.2 is near optimal but might actually remove it altogether
        if submission.score < 100: #for top/hot i run on 50, returns higher quality but when running for new posts can be tricky. for new best is 10+, 20+
            continue
        url = submission.url.lower()
        if "jpg" in url or "png" in url:
            try:
                print(f"Checking: {submission.title} → {submission.url}")
                resp = requests.get(url, stream=True).raw
                image = np.asarray(bytearray(resp.read()), dtype="uint8")
                if image is None:
                    continue
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)
                # check images for duplicate
                compare_image = cv2.resize(image,(224,224))
                ignore_flag = False
                for ignore in ignore_images:
                    difference = cv2.subtract(ignore, compare_image)
                    b, g, r = cv2.split(difference)
                    total_difference = cv2.countNonZero(b) + cv2.countNonZero(g) + cv2.countNonZero(r)
                    if total_difference == 0:
                        ignore_flag = True
                        break
                # save image if not flagged as a duplicate
                if not ignore_flag:
                    cv2.imwrite(f"{image_path}{sub}-{submission.id}.png", image)
                count += 1
            except Exception as e:
                print(f"Image failed: {submission.url.lower()}")
                print(e)
        