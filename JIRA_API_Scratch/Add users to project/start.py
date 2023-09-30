import requests
from requests.auth import HTTPBasicAuth
import json
import cred_api  # create file with credentials

api_token = cred_api.api_token
email_auth = cred_api.email

my_domain = '<YOUR DOMENI HERE>'
project_id = '<PID HERE>'
role_id = '<ROLE ID>'

def get_account_ids():
    with open("emails.txt", "r") as file:
        emails = [line.strip() for line in file]
    # Initialize an empty list to store account IDs
    account_ids = []

    for email in emails:
        url = f"https://{my_domain}.atlassian.net/rest/api/3/user/search"

        auth = HTTPBasicAuth(email_auth, api_token)

        headers = {
            "Accept": "application/json"
        }

        query = {
            'query': email
        }

        response = requests.get(url, headers=headers, params=query, auth=auth)

        if response.status_code == 200:
            data = response.json()
            users = data
            if users:
                for user in users:
                    account_id = user.get("accountId")
                    if account_id:
                        account_ids.append(account_id)

    return account_ids



def add_user_to_project():
    url = f"https://{my_domain}.atlassian.net/rest/api/3/project/{project_id}/role/{role_id}"

    auth = HTTPBasicAuth(email_auth, api_token)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = json.dumps({
        "user":
            account_ids

    })

    response = requests.request(
        "POST",
        url,
        data=payload,
        headers=headers,
        auth=auth
    )


    if response.status_code == 200:
        print("Users added to the project role successfully.")
    else:
        print(f"Error: {response.status_code} - {response.text}")


#START SCRIPT
if __name__ == '__main__':
    account_ids = get_account_ids()
    add_user_to_project()