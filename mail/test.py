import httpx

def check_twitter_email(email):
    url = "https://api.twitter.com/i/users/email_available.json"
    params = {"email": email}
    
    try:
        response = httpx.get(url, params=params, timeout=10)
        data = response.json()

        if "taken" in data:
            return f"Email {email} {'is registered' if data['taken'] else 'is available'}"
        else:
            return "Unexpected response from Twitter API"
    
    except Exception as e:
        return f"Error: {e}"

# Example usage
email_to_check = "ralucamanea02@gmail.com"
print(check_twitter_email(email_to_check))
