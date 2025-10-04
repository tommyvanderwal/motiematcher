import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_motion_links(url, max_motions=20):
    """Scrape motion links from the search page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find motion links - looking for links to detail pages
    motion_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/kamerstukken/moties/detail?' in href and 'id=' in href:
            # Extract id and did from URL
            full_url = f"https://www.tweedekamer.nl{href}"
            motion_links.append(full_url)
            if len(motion_links) >= max_motions:
                break

    return motion_links

def scrape_motion_votes(motion_url):
    """Scrape voting information from a motion detail page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(motion_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching motion page {motion_url}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Try to find voting section - this might need adjustment based on actual HTML
    votes = {}

    # Look for voting tables or sections
    vote_tables = soup.find_all('table')
    for table in vote_tables:
        if 'stem' in table.get_text().lower() or 'vote' in table.get_text().lower():
            # Parse table rows
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cols = row.find_all('td')
                if len(cols) >= 2:
                    party = cols[0].get_text().strip()
                    vote = cols[1].get_text().strip()
                    votes[party] = vote

    # If no table found, look for other structures
    if not votes:
        # Look for divs with voting info
        for div in soup.find_all('div'):
            classes = div.get('class')
            if classes and any('stem' in cls.lower() or 'vote' in cls.lower() for cls in classes):
                text = div.get_text()
                # This is a simple extraction - might need refinement
                votes['raw_text'] = text

    title_tag = soup.find('title')
    title = title_tag.get_text() if title_tag else 'Unknown'

    return {
        'url': motion_url,
        'votes': votes,
        'title': title
    }

def main():
    search_url = "https://www.tweedekamer.nl/kamerstukken/moties?qry=%2A&fld_tk_categorie=Kamerstukken&fld_prl_kamerstuk=Moties&srt=date%3Adesc%3Adate&page=70"

    print("Fetching motion links...")
    motion_links = scrape_motion_links(search_url, max_motions=20)

    print(f"Found {len(motion_links)} motion links")

    results = []
    for i, link in enumerate(motion_links[:10]):  # Limit to 10 for testing
        print(f"Scraping motion {i+1}: {link}")
        vote_data = scrape_motion_votes(link)
        if vote_data:
            results.append(vote_data)
        time.sleep(1)  # Be respectful

    # Save results
    with open('temp/scraped_motion_votes.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(results)} motion vote data to temp/scraped_motion_votes.json")

if __name__ == "__main__":
    main()