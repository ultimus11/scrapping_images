import os
import time
import requests
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import base64

def fetch_image_urls(query, max_links_to_fetch, wd, folder_path, sleep_between_interactions=1):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)
    
    # Build the Google query
    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    
    # Load the page
    wd.get(search_url)
    
    image_urls = set()
    image_count = 0
    results_start = 0
    
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)
        
        # Get all image thumbnail results
        thumbnail_results = wd.find_elements(By.CSS_SELECTOR, "img.Q4LuWd")
        number_results = len(thumbnail_results)
        
        for img in thumbnail_results[results_start:number_results]:
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue
            
            # Extract image URLs
            images = wd.find_elements(By.CSS_SELECTOR, "img.n3VNCb")
            # Get the 'src' attribute which contains the base64 data
            
            for image in images:
                print(image.get_attribute('src'))
                # if image.get_attribute('src') and 'http' in image.get_attribute('src'):
                #     print(image.get_attribute('src'))
                #     image_urls.add(image.get_attribute('src'))
                src_data = image.get_attribute('src')

                # Verify that the src_data contains the base64 string
                if src_data.startswith('data:image/png;base64,'):
                    # Remove the prefix from the base64 string
                    base64_data = src_data.split(',')[1]

                    # Decode the base64 string
                    image_data = base64.b64decode(base64_data)

                    # Define the output file path
                    output_file_path = os.path.join(folder_path, f'{time.time()}.jpg')
                    # output_file_path = 'output_image.png'

                    # Write the decoded image data to a file
                    with open(output_file_path, 'wb') as file:
                        file.write(image_data)
                    print(f"SUCCESS - saved {output_file_path}")
            
            image_count = len(image_urls)
            
            if image_count >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print(f"Found: {len(image_urls)} image links, looking for more...")
            time.sleep(30)
            return
        
        # Move the result startpoint further down
        results_start = len(thumbnail_results)
    # print(image_urls)
    
    return image_count


# def persist_image(folder_path, url):
#     try:
#         image_content = requests.get(url).content

#         with Image.open(BytesIO(image_content)) as img:
#             file_path = os.path.join(folder_path, f'{time.time()}.jpg')
#             img.save(file_path, "JPEG")
#         print(f"SUCCESS - saved {url} - as {file_path}")
#     except Exception as e:
#         print(f"ERROR - Could not save {url} - {e}")

def search_and_download(query, max_images):
    target_folder = os.path.join("images", '_'.join(query.lower().split(' ')))
    
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    
    # Set up the WebDriver
    with webdriver.Chrome(service=Service(ChromeDriverManager().install())) as wd:
        res = fetch_image_urls(query, max_images, wd, target_folder, sleep_between_interactions=0.5)
        
        # for elem in res:
        #     persist_image(target_folder, elem)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python src/scrape_images.py 'search query' number_of_images")
    else:
        search_query = sys.argv[1]
        number_of_images = int(sys.argv[2])
        search_and_download(search_query, number_of_images)
