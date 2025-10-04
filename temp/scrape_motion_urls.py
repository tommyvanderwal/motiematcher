import requests
from bs4 import BeautifulSoup
import re

# Scrape recent motions from Tweede Kamer website
url = 'https://www.tweedekamer.nl/kamerstukken/moties'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find motion links - look for links containing 'moties' and numbers
motion_links = []
for link in soup.find_all('a', href=True):
    href = link['href']
    if 'moties' in href and re.search(r'\d{4}Z\d+', href):
        full_url = f"https://www.tweedekamer.nl{href}" if href.startswith('/') else href
        title = link.get_text().strip()
        if title and len(motion_links) < 5:  # Get first 5
            motion_links.append((full_url, title))

print(f"Found {len(motion_links)} motion links:")
for i, (url, title) in enumerate(motion_links, 1):
    print(f"{i}. {title[:60]}...")
    print(f"   URL: {url}")

# Save for manual checking
with open('temp/motion_urls.txt', 'w', encoding='utf-8') as f:
    for url, title in motion_links:
        f.write(f"{url}\t{title}\n")

print("\nURLs saved to temp/motion_urls.txt for manual verification")