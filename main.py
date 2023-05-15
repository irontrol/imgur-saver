import string
import time
import math
import json
import random
import os
from pathlib import Path
from multiprocessing import Pool

json_file = 'properties.json'

try:
    import requests
    import cv2
    from PIL import Image
except ModuleNotFoundError:
    os.system('pip install requests')
    os.system('pip install opencv-python')
    os.system('pip install pillow')
    import requests
    import cv2
    from PIL import Image

def init():
    load_json()
    create_folders()
    change_extensions()

def load_json():
    content = json.load(open(json_file))
    global IMAGE_TYPE, OUTPUT, EXCLUDE
    IMAGE_TYPE = content['image_type']
    OUTPUT = content['output']
    EXCLUDE = content['exclude']

def create_folders():
    Path(OUTPUT).mkdir(exist_ok=True)
    Path(EXCLUDE).mkdir(exist_ok=True)

def change_extensions():
    name = ''
    for i in range(2):
        j = 0
        for file in Path(EXCLUDE).iterdir():
            if file.suffix == '.txt':
                continue
            if i == 1:
                name = 'exclude_'
            file.rename(Path(EXCLUDE) / (name + str(j) + '.' + IMAGE_TYPE))
            j += 1

def generate_id():
    characters = '0123456789' + string.ascii_lowercase
    return ''.join(random.sample(characters, 6))

def save_image(url, image):
    try:
        with open(str(image), 'wb') as f:
            res = requests.get(url, timeout=5)
            f.write(res.content)
    except requests.exceptions.RequestException:
        print(f"    Error saving image {image.name} (ID: {image.stem})")
        print("    Generating new ID...")

def check_empty(image):
    img = cv2.imread(str(image))
    return img is None

def check_exclude(image):
    img = Image.open(str(image))

    for file in Path(EXCLUDE).iterdir():
        if file.suffix == '.txt':
            continue
        example = Image.open(file)
        if list(img.getdata()) == list(example.getdata()):
            return True

    return False

def download_image(i):
    id = generate_id()

    url = 'https://i.imgur.com/' + id + '.jpg'

    directory = Path(OUTPUT) / (str(i + 1) + '_' + str(id) + '.' + IMAGE_TYPE)

    save_image(url, directory)
        
    if directory.exists() and not (check_empty(directory) or check_exclude(directory)):
        print(f"    Saved image #{i + 1} (ID: {id})")
        return True
    else:
        directory.unlink()
        return False

def main():
    init()

    print("Started saving images:")
    start_time = time.time()

    pool = Pool()

    i = 0
    while True:
        results = pool.map(download_image, range(i, i + 1000))
        i += 1000

        success_count = sum(results)

        if success_count == 0:
            break

    pool.close()
    pool.join()

    print("Finished saving images.")
    end_time = time.time()

    time_passed = end_time - start_time
    print(f"Time: {math.floor(time_passed / 60):02}:{round(time_passed % 60):02}")

main()
