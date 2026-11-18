import httpx
import json
import time

# List of Chrome user agents
ua = json.loads('''{
    "browsers": {
        "chrome": [
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36"
        ]
    }
}''')["browsers"]["chrome"]

def check_twitter_email(email):
    url = "https://api.twitter.com/i/users/email_available.json"
    params = {"email": email}

    for user_agent in ua:
        headers = {"User-Agent": user_agent}

        try:
            with httpx.Client(headers=headers, timeout=10) as client:
                response = client.get(url, params=params)

                if response.status_code != 200:
                    print(f"[Twitter] UA: {user_agent[:40]}... | Status {response.status_code} for {email}")
                    continue

                data = response.json()

                if "taken" in data:
                    print(f"[Twitter] Email '{email}' taken: {data['taken']} (UA: {user_agent[:40]}...)")
                    return data["taken"]  # True = registered, False = not registered

                print(f"[Twitter] Unexpected structure: {data} (UA: {user_agent[:40]}...)")

        except Exception as e:
            print(f"[Twitter] Exception with UA {user_agent[:40]}...: {e}")
            time.sleep(1)  # brief pause before next try

    print(f"[Twitter] All attempts failed for {email}")
    return False
