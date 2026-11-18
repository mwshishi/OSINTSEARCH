import json, os, httpx, random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15"
]

def check_username_all_sites(username):
    results = {}
    path = os.path.join(os.path.dirname(__file__), "sites.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    for site, info in data.items():
        url = info["url"].format(username)
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive",
        }

        try:
            with httpx.Client(follow_redirects=True, timeout=10) as client:
                resp = client.get(url, headers=headers)

            error_type = info.get("errorType")
            found = False

            if error_type == "status_code":
                found = resp.status_code in [200, 301, 302, 403]
                print(f"[DEBUG] [{site}] Status Code: {resp.status_code} → {'FOUND' if found else 'NOT FOUND'}")

            elif error_type == "message":
                error_msg = info.get("errorMsg", "").lower()
                found = error_msg not in resp.text.lower()
                snippet = resp.text.lower()
                print (snippet)
                print(f"[DEBUG] [{site}] Message check → Looking for: \"{error_msg}\"")
                print(f"[DEBUG] [{site}] Found: {'NO' if error_msg in snippet else 'YES'}")

            else:
                print(f"[DEBUG] [{site}] Unknown errorType '{error_type}'")

        except Exception as e:
            print(f"[ERROR] [{site}] Exception: {e}")
            found = False

        results[site] = (url, found)

    return results
