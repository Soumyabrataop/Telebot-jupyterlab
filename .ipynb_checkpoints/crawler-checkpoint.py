import os
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = "https://help.telebotcreator.com"
OUTPUT_DIR = "telebot_docs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

visited = set()

def sanitize_filename(path):
    path = path.strip('/')
    if not path:
        return "index"
    return re.sub(r'[^a-zA-Z0-9_-]', '_', path)

def get_links_from_page(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('mailto:') or href.startswith('tel:'):
                continue
            if href.startswith('/'):
                full_url = urljoin(BASE_URL, href)
            elif href.startswith(BASE_URL):
                full_url = href
            else:
                continue
            parsed = urlparse(full_url)
            clean_url = parsed.scheme + "://" + parsed.netloc + parsed.path
            if clean_url.startswith(BASE_URL):
                links.add(clean_url)
        return list(links)
    except:
        return []

def download_markdown(url):
    if url in visited:
        return
    visited.add(url)

    md_url = url.rstrip('/') + ".md"
    try:
        response = requests.get(md_url)
        if response.status_code != 200:
            return
        filename = sanitize_filename(urlparse(url).path) + ".md"
        filepath = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(filepath):
            return  # already exists, skip

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(response.text)
    except:
        pass

def crawl():
    to_visit = [BASE_URL]
    while to_visit:
        current = to_visit.pop()
        if current in visited:
            continue
        download_markdown(current)
        links = get_links_from_page(current)
        for link in links:
            if link not in visited:
                to_visit.append(link)

if __name__ == "__main__":
    crawl()
