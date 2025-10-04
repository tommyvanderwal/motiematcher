import requests

# Simple website check for voting results

def check_website_votes():
    urls = [
        'https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2025Z18621&did=2025D43264',
        'https://www.tweedekamer.nl/kamerstukken/moties/detail?id=2025Z18608&did=2025D43239'
    ]

    for url in urls:
        print(f"🌐 Checking: {url.split('id=')[1].split('&')[0]}")

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                content = response.text.lower()

                # Look for voting indicators
                if 'stemming' in content or 'vote' in content or 'voor' in content or 'tegen' in content:
                    print("   ✅ Website contains voting-related content")

                    # Try to extract some vote info
                    if 'verworpen' in content:
                        print("   📊 Shows: VERWORPEN")
                    elif 'aangenomen' in content:
                        print("   📊 Shows: AANGENOMEN")
                    else:
                        print("   📊 Vote result not clearly visible in HTML")
                else:
                    print("   ⚠️  No clear voting content found")
            else:
                print(f"   ❌ HTTP {response.status_code}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        print()

if __name__ == "__main__":
    check_website_votes()