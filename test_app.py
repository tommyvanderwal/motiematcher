import requests
from bs4 import BeautifulSoup
import sys
import re

def run_test():
    """
    Runs a full user simulation test on the Motiematcher app.
    1. Starts a session.
    2. Clicks through and votes on all motions.
    3. Verifies that each page only shows one unique motion.
    """
    base_url = "http://127.0.0.1:8000"
    
    try:
        with requests.Session() as s:
            # 1. Start the session by visiting the start page and submitting the form
            print("--- Step 1: Starting Session ---")
            start_page = s.get(base_url)
            if start_page.status_code != 200:
                print(f"FAIL: Could not load start page. Status: {start_page.status_code}")
                return False
            
            # Find the form action and submit it to get the redirect
            soup = BeautifulSoup(start_page.content, 'html.parser')
            form = soup.find('form')
            start_action = form['action']
            
            response = s.post(f"{base_url}{start_action}", allow_redirects=True)
            print(f"Session started. Redirected to: {response.url}")

            # 2. Loop through motions, vote, and check for duplicates
            print("\n--- Step 2: Voting and Verifying Motions ---")
            
            seen_motion_subjects = set()
            current_url = response.url

            while "/results" not in current_url:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find motion subject
                subject_tag = soup.find('h5')
                if not subject_tag:
                    print(f"FAIL: Could not find motion subject on page {current_url}")
                    return False
                subject = subject_tag.text.strip()
                
                # --- Verification ---
                if subject in seen_motion_subjects:
                    print(f"FAIL: Duplicate motion found! Subject: '{subject}'")
                    return False
                seen_motion_subjects.add(subject)
                print(f"PASS: Motion '{subject}' is unique.")

                # --- Simulate Voting ---
                vote_form = soup.find('form')
                if not vote_form:
                    print(f"FAIL: Could not find vote form on page {current_url}")
                    return False
                
                vote_action = vote_form['action']
                motion_id = vote_form.find('input', {'name': 'motion_id'})['value']
                
                # Vote 'Voor' by default
                vote_data = {'motion_id': motion_id, 'vote': 'Voor'}
                response = s.post(f"{base_url}{vote_action}", data=vote_data, allow_redirects=True)
                current_url = response.url
                print(f"Voted. Redirected to: {current_url}")

            print("\n--- Step 3: Reached Results Page ---")
            if response.status_code == 200 and "/results" in current_url:
                print("SUCCESS: Successfully voted on all unique motions and reached the results page.")
                return True
            else:
                print(f"FAIL: Did not correctly land on results page. Final URL: {current_url}")
                return False

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the test: {e}")
        return False

if __name__ == "__main__":
    if not run_test():
        print("\n--- TEST FAILED ---")
        sys.exit(1)
    print("\n--- TEST PASSED ---")
    sys.exit(0)
