import requests
from bs4 import BeautifulSoup
import json

def fetch_motion_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def analyze_motion_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Look for vote-related sections
    vote_sections = []

    # Find all divs that might contain votes
    for div in soup.find_all('div'):
        text = div.get_text().lower()
        if any(keyword in text for keyword in ['stemming', 'voor', 'tegen', 'onthouding', 'vote', 'resultaat']):
            vote_sections.append({
                'tag': 'div',
                'classes': div.get('class'),
                'id': div.get('id'),
                'text': div.get_text()[:500]  # First 500 chars
            })

    # Find tables
    tables = []
    for table in soup.find_all('table'):
        text = table.get_text().lower()
        if any(keyword in text for keyword in ['stemming', 'voor', 'tegen', 'onthouding', 'vote']):
            tables.append({
                'classes': table.get('class'),
                'text': table.get_text()[:500]
            })

    # Look for specific vote patterns
    vote_data = {}
    # Try to find party vote counts
    for element in soup.find_all(['span', 'div', 'td']):
        text = element.get_text().strip()
        # Look for patterns like "VVD: 25 voor, 5 tegen"
        if ':' in text and any(word in text.lower() for word in ['voor', 'tegen', 'onthouding']):
            vote_data[text] = element.get_text()

    return {
        'vote_sections': vote_sections,
        'tables': tables,
        'vote_data': vote_data,
        'title': soup.find('title').get_text() if soup.find('title') is not None else 'No title'
    }

def main():
    # Test with the first motion
    url = "https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2025Z13886&did=2025D31484"

    print(f"Fetching {url}")
    html = fetch_motion_page(url)
    if html:
        analysis = analyze_motion_html(html)
        print(json.dumps(analysis, indent=2, ensure_ascii=False))

        # Save HTML for manual inspection
        with open('temp/motion_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("Saved HTML to temp/motion_page.html")

if __name__ == "__main__":
    main()