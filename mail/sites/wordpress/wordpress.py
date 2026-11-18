import asyncio
import random
import httpx
import json

# User agents
ua = json.loads('''{"browsers": {"chrome": [
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36"
]}}''')

# Async checker
async def check_wordpress_async(email: str):
    url = f"https://public-api.wordpress.com/rest/v1.1/users/{email}/auth-options"

    headers = {
        'User-Agent': random.choice(ua["browsers"]["chrome"]),
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'DNT': '1',
        'Connection': 'keep-alive',
    }

    params = {
        'http_envelope': '1',
        'locale': 'en',
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers=headers, params=params)
            info = resp.json()

            if "email_verified" in info.get("body", {}):
                return info["body"]["email_verified"]

            if "unknown_user" in str(info) or "email_login_not_allowed" in str(info):
                return False

            return None  # posibil rate limit
    except Exception as e:
        print(f"[ERROR] WordPress: {e}")
        return None


# Sync wrapper
def check_wordpress_email(email: str) -> bool:
    result = asyncio.run(check_wordpress_async(email))
    return result is True


# CLI test
if __name__ == "__main__":
    import sys

    async def main():
        email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ")
        result = await check_wordpress_async(email)
        print("Exists ✅" if result is True else "Doesn't exist ❌" if result is False else "Error / Rate-limited ⚠️")

    asyncio.run(main())
