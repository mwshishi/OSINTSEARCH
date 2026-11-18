import httpx
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

def check_spotify_email(email):
    url = "https://spclient.wg.spotify.com/signup/public/v1/account"

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "DNT": "1",
        "Connection": "keep-alive",
    }

    params = {
        "validate": "1",
        "email": email
    }

    try:
        response = httpx.get(url, headers=headers, params=params, timeout=10)
        data = response.json()

        if "status" in data:
            if data["status"] == 20:
                return True  # Email is registered on Spotify
            elif data["status"] == 1:
                return False  # Email is not registered

        return None  # Unexpected API response

    except Exception as e:
        print(f"Spotify API error: {e}")
        return None  # API error
