import asyncio
import random
import httpx
from bs4 import BeautifulSoup
import json

# User agents
ua = json.loads('''{"browsers": {"chrome": [
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36"
]}}''')

# Async function
async def check_amazon_async(email: str):
    headers = {"User-agent": random.choice(ua["browsers"]["chrome"])}

    url = (
        "https://www.amazon.com/ap/signin?"
        "openid.pape.max_auth_age=0&"
        "openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3F_encoding%3DUTF8%26ref_%3Dnav_ya_signin&"
        "openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&"
        "openid.assoc_handle=usflex&"
        "openid.mode=checkid_setup&"
        "openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&"
        "openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&"
    )

    async with httpx.AsyncClient(follow_redirects=True, timeout=20) as client:
        try:
            req = await client.get(url, headers=headers)
            body = BeautifulSoup(req.text, 'html.parser')
            data = {
                x["name"]: x.get("value", "")
                for x in body.select('form input') if "name" in x.attrs
            }
            data["email"] = email

            req = await client.post("https://www.amazon.com/ap/signin/", data=data, headers=headers)
            body = BeautifulSoup(req.text, 'html.parser')

            if body.find("div", {"id": "auth-password-missing-alert"}):
                return True  # Email exists
            else:
                return False  # Email does not exist

        except Exception:
            return None  # Rate limited or error


# Sync wrapper for use in non-async environments
def check_amazon_email(email: str) -> bool:
    result = asyncio.run(check_amazon_async(email))
    return result is True  # Only return True if email exists

# At the end of amazon.py
check_amazon_email = check_amazon_async

# CLI test
if __name__ == "__main__":
    import sys

    async def main():
        email = sys.argv[1] if len(sys.argv) > 1 else input("Email: ")

        attempts = 70
        for i in range(attempts):
            result = await check_amazon_async(email)
            if result:
                print(True)
                return
        print(False)

    asyncio.run(main())
