import requests
from requests.auth import HTTPBasicAuth
import json
import cred

# Global values
email_auth = cred.email
api_token = cred.api_token
access_token = cred.access_token
auth = HTTPBasicAuth(email_auth, api_token)
base_url = "https://<YOUR DOMAIN HERE>.atlassian.net"

def find_account_id_by_email(email_to_find):
    url = f"{base_url}/rest/api/3/user/search"
    headers = {
        "Accept": "application/json",
    }
    query = {
        'query': email_to_find
    }

    response = requests.get(url, headers=headers, params=query, auth=auth)

    if response.status_code == 200:
        user_data = json.loads(response.text)
        if user_data and len(user_data) > 0:
            return user_data[0]['accountId']
    return None


# Function to update a user's name using their account ID
def update_user_name(account_id, new_name):
    url = f"https://api.atlassian.com/users/{account_id}/manage/profile"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    payload = json.dumps({
        "name": new_name,
    })

    response = requests.request(
        "PATCH",
        url,
        data=payload,
        headers=headers
    )

    if response.status_code == 200:
        print(f"User updated successfully. Account ID: {account_id}"
              f"\nNew Name: {new_name}")
    else:
        print(f"Failed to update user. Account ID: {account_id}")
        print(f"Response: {response.text}")

# Start script
with open("list.txt", "r") as file, open("error.txt", "w") as error_file:
    for line in file:
        parts = line.strip().split("\t")
        if len(parts) == 2:
            email, new_name = parts
            account_id = find_account_id_by_email(email)
            if account_id:
                update_user_name(account_id, new_name)
            else:
                error_message = f"ERROR: User not found for email: {email}"
                print(error_message)
                error_file.write(error_message + "\n")
        else:
            error_message = f"ERROR: Invalid format in line: {line}"
            print(error_message)
            error_file.write(error_message + "\n")

