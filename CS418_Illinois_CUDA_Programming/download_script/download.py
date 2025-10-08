
# Lu Thanh Thien
# Jul 14 2024

import re, os, shutil
import json
import requests
import subprocess
from pathlib import Path
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


options = Options()
options.add_argument('--headless=new')
urls_json = Path("urls.json")
urls_json_old = Path("urls.old.json")

def sanitize_filename(filename):
    # Define a regex pattern for characters that are not allowed in filenames
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def check_exist(path_name, url=None):
    if (urls_json.exists()):
        shutil.copy(src=urls_json, dst=urls_json_old)
        # TODO: check if the download url same as exist downloaded file url
    if os.path.exists(path_name): 
            print(f"{path_name} has already exist!")
            return True
    return False

def download_video(url, path):
    try:
        path_name = path / (sanitize_filename(url["name"]) + ".mp4")
        if (check_exist(path_name)): return

        driver = webdriver.Chrome(options=options)
        driver.get(url["url"])

        wait = WebDriverWait(driver, 10)
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")

        iframe = driver.find_element(By.ID, "kplayer_ifp")
        driver.switch_to.frame(iframe)

        # Now find the video element inside the iframe
        video = driver.find_element(By.TAG_NAME, "video")
        src_video = video.get_attribute("src")
        print(f"[Video] Downloading {src_video}")

        driver.quit()
        
        command = ["yt-dlp", "-f", "bestvideo/best", src_video, "-o", path_name]
        subprocess.run(command)

        print("Download complete, saved video in: ", path_name)
    except Exception as e:
        print(f"Error while download video from {url}: {e}")

def download_slides(url, path):
    try:
        path_name = path / (sanitize_filename(url["name"]) + ".pdf")
        if (check_exist(path_name)): return
        print(f"[Slide] Downloading {path_name}")
        response = requests.get(url["url"])
        with open(path_name, 'wb') as f:
            f.write(response.content)
    except Exception as e:
        print(f"Error while download slide from {url}: {e}")

def get_urls():
    url = "https://lumetta.web.engr.illinois.edu/408-Sum24/"
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    
    lis = driver.find_elements(
        by=By.TAG_NAME, value="li"
    )
    print("Getting urls...")
    urls = []
    for li in lis:
        elements = li.get_attribute("innerHTML")
        if "</a>" in elements:
            a = li.find_element(by=By.TAG_NAME, value="a")
            name = a.text
            if (name in [url["name"] for url in urls]):
                name = name + "_1"
            url = a.get_attribute("href")
            if url.endswith(".pdf") and ("slide" in name.lower()):
                urls.append({"url": url, "name": name, "type": "pdf"})
            elif url.endswith(".pdf"):
                urls.append({"url": url, "name": name, "type": "exam"})
            elif url.__contains__("mediaspace.illinois.edu/media/"):
                urls.append({"url": url, "name": name, "type": "video"})

    driver.quit()

    print("Total videos: {}, total slides: {}, total exams: {}".format(
        len([url for url in urls if url["type"] == "video"]),
        len([url for url in urls if url["type"] == "pdf"]),
        len([url for url in urls if url["type"] == "exam"])
    ))

    with open(urls_json, "w") as f:
        json.dump(urls, f, indent=4)
    return urls

if __name__ == "__main__":
    print("Start downloading...")
    lecture_path = Path("lectures")
    lecture_path.mkdir(exist_ok=True)
    video_path = Path("videos")
    video_path.mkdir(exist_ok=True)
    exam_path = Path("exams")
    exam_path.mkdir(exist_ok=True)
    
    # urls = get_urls()
    urls = [
        {"url": "https://mediaspace.illinois.edu/media/t/1_er1kns9y", "name": "Lecture 93", "type": "video"},
        {"url": "https://mediaspace.illinois.edu/media/t/1_hweutm4x", "name": "Lecture 94", "type": "video"}
    ]

    # Download pdf files first, then videos
    order = {'pdf': 0, 'exam': 1, 'video': 2}
    urls.sort(key=lambda x: order[x["type"]])

    total_pdf = len([url for url in urls if (url["type"] == "pdf") or (url["type"] == "exam") ])
    total_videos = len([url for url in urls if (url["type"] == "video")])
    pdf_count = 0
    video_count = 0
    for url in urls:
        if url["type"] == "pdf":
            download_slides(url, lecture_path)
            pdf_count += 1
            print(f"Finish download {pdf_count}/{total_pdf} lectures/exam files")
        if url["type"] == "video":
            download_video(url, video_path)
            video_count += 1
            print(f"Finish download {video_count}/{total_videos} videos")
        if url["type"] == "exam":
            download_slides(url, exam_path)
            pdf_count += 1
            print(f"Finish download {pdf_count}/{total_pdf} lectures/exam files")