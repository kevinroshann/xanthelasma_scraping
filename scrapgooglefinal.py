import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import io
from PIL import Image
import time

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


# Assuming chromedriver.exe is in the same directory or your PATH
options = Options()
PATH = "/home/ekn/Downloads/chromedriver-linux64/chromedriver.exe"
service = Service(executable_path=PATH)

wd = webdriver.Chrome(options=options)


def get_images_from_google(wd, delay, max_images):
    def scroll_down(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)

    url = "https://www.google.com/search?q=xanthelasma+images&tbm=isch"
    wd.get(url)

    downloaded_urls_file = "downloaded_urls.txt"  # File to store downloaded URLs
    image_urls = set()

    # Check if downloaded URLs file exists and load them
    if os.path.exists(downloaded_urls_file):
        with open(downloaded_urls_file, "r") as f:
            for line in f:
                image_urls.add(line.strip())

    last_height = wd.execute_script("return document.body.scrollHeight")

    while len(image_urls) < max_images:
        scroll_down(wd)

        # Check if new images loaded after scrolling
        new_height = wd.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            try:
                # Click "Load More" button using XPath (attempt 1)
                load_more_button = wd.find_element(By.XPATH, "//button[text()='Show more results']")
                load_more_button.click()
                time.sleep(delay)
            except:
                try:
                    # Click "Load More" button using partial link text (attempt 2)
                    more_results_link = wd.find_element(By.PARTIAL_LINK_TEXT, "Load more results")
                    more_results_link.click()
                    time.sleep(delay)
                except:
                    pass  # No "Load More" button found, continue scraping

        last_height = new_height

        thumbnails = wd.find_elements(By.CLASS_NAME, "Q4LuWd")

        for img in thumbnails:
            try:
                img.click()
                time.sleep(delay)
            except:
                continue

            images = wd.find_elements(By.CSS_SELECTOR, "img[src*='.jpg']")

            for image in images:
                if image.get_attribute('src') in image_urls:
                    continue

                if image.get_attribute('src') and 'http' in image.get_attribute('src'):
                    image_urls.add(image.get_attribute('src'))
                    print(f"Found {len(image_urls)}")
                    print(image.get_attribute('src'))

                    # Download the image and update downloaded URLs file
                    download_image("imgs/", image.get_attribute('src'), str(len(image_urls)) + ".jpg")
                    with open(downloaded_urls_file, "a") as f:
                        f.write(image.get_attribute('src') + "\n")

    return image_urls


def download_image(download_path, url, file_name):
    try:
        image_content = requests.get(url).content
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file)
        file_path = download_path + file_name

        with open(file_path, "wb") as f:
            image.save(f, "JPEG")

        print("Success")
    except Exception as e:
        print('FAILED -', e)

urls = get_images_from_google(wd, 3, 3000)  # Change max_images to your desired limit

for i, url in enumerate(urls):
    download_image("imgs/", url, str(i) + ".jpg")

wd.quit()
