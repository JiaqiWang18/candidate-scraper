import requests
import csv
import validators
import os
from pathlib import Path
from PIL import Image, UnidentifiedImageError


def crop_square_from_top(img):
    img_width, img_height = img.size
    side_len = min(img_width, img_height)
    if img_width > img_height:
        offset = (img_width - img_height)//2
        return img.crop((offset, 0, side_len+offset, side_len))
    return img.crop((0, 0, side_len, side_len))


def google_search_img(query):
    link = f"https://www.googleapis.com/customsearch/v1?key={os.environ.get('GOOGLE_SEARCH_KEY')}&q={query}&searchType=image&imgColorType=color&num=1&fileType=jpg"
    print(link)
    req = requests.get(link, timeout=(5, 10))
    print(req.json()["items"][0]["link"])
    return req.json()["items"][0]["link"]


def main():
    INPUT_DIR = "ballotpedia_out"
    OUTPUT_DIR = "new_photos"
    GOOGLE_DIR = os.path.join(OUTPUT_DIR,"google")
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    Path(GOOGLE_DIR).mkdir(parents=True, exist_ok=True)
    directory = os.path.join(INPUT_DIR)
    search_log = open(os.path.join(OUTPUT_DIR, "search_log.csv"), 'w')
    search_log_writer = csv.writer(search_log)
    search_log_writer.writerow(["Name", "Photo URL", "Photo File Name"])
    for root, dirs, files in os.walk(directory):
        progress = 0
        for file in files:
            print(file)
            if file.endswith(".csv"):
                with open(os.path.join(INPUT_DIR, file), newline='') as csvfile:
                    tracer = csv.reader(csvfile)
                    next(tracer, None)
                    for row in tracer:
                        file_name = row[0]
                        img_link = row[12]
                        file_path = os.path.join(OUTPUT_DIR, f'{file_name}.jpg')
                        if not validators.url(img_link):
                            search_term = row[0]+" "+row[6]
                            print(f"{row[0]} does not have photo, search on google")
                            img_link = google_search_img(search_term)
                            file_path = os.path.join(GOOGLE_DIR, f'{file_name}.jpg')
                            search_log_writer.writerow([row[0], img_link, file_path])
                        else:
                            print(f"{row[0]} has photo")
                        try:
                            img_data = requests.get(img_link, timeout=(5, 10)).content
                        except Exception as e:
                            print(e)
                            continue
                        with open(file_path, 'wb') as img_writer:
                            img_writer.write(img_data)
                        try:
                            im = Image.open(file_path).convert("RGB")
                            im_cropped = crop_square_from_top(im)
                            im_cropped.save(file_path)
                        except UnidentifiedImageError as e:
                            print(e)
                        print("Written")
            progress += 1
            print(f"{progress}/{len(files)} files done")
    search_log.close()


if __name__ == '__main__':
    main()