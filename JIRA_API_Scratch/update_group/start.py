import requests
from requests.auth import HTTPBasicAuth
import json
import cred_api

#CHANGE VALUE HERE
group_id = "<ENTER GROUP ID HERE>"  #Enter group ID here (https://{YOUR DOMAIN}.atlassian.net/wiki/rest/api/group/by-name?name={name})
group_name = "<ENTER GROUP NAME HERE>"  #Enter group name


# global value
base_url = 'https://<YOUR DOMAIN>.atlassian.net'
my_dom = "<YOUR DOMAIN>"
api_token = cred_api.api_token
email_auth = cred_api.email
users_new = open("modify_members.txt").read().splitlines()  #for modify group, add & delete members
only_add_members = open("only_add.txt").read().splitlines() #for only add members in group
only_delete_members = open("only_delete.txt").read().splitlines() #for only add members in group


# start step one / dump users from group, create email+accontID list
def step_one(base_url, group_id, email_auth, api_token):
    url = f"{base_url}/rest/api/3/group/member"
    auth = HTTPBasicAuth(email_auth, api_token)
    headers = {
        "Accept": "application/json"
    }
    params = {
        'groupId': group_id,
        'limit': 100,  # Set the desired limit per page (maximum is 100)
        'startAt': 0  # Start at the first page
    }

    users_g = []
    has_more = True

    while has_more:
        response = requests.get(url, headers=headers, params=params, auth=auth)

        if response.status_code == 200:
            data = response.json()
            members = data.get('values', [])

            for member in members:
                member_info = {
                    'emailAddress': member.get('emailAddress', ''),
                    'accountId': member.get('accountId', '')
                }
                users_g.append(member_info)

            total = data.get('total', 0)
            start_at = data.get('startAt', 0)
            max_results = data.get('maxResults', 0)

            if start_at + max_results >= total:
                has_more = False
            else:
                params['startAt'] = start_at + max_results
        else:
            print(f"Failed to retrieve members from the group. Status code: {response.status_code}")
            print(response.text)
            break

    return users_g
# create dict with email + accountID for users_new
def get_id(users_new):
    url_getid = f"https://{base_url}/rest/api/3/user/search"
    auth = HTTPBasicAuth(email_auth, api_token)

    new_users_id = {}

    for email in users_new:
        url = f"{url_getid}?query={email}"

        response = requests.get(url, auth=auth)

        if response.status_code == 200:
            user_data = json.loads(response.text)
            if user_data:
                item = user_data[0]  # Assuming the first user in the response is the desired one
                account_id = item.get("accountId")
                if account_id:
                    new_users_id[email] = account_id
            else:
                print(f"No user found for email: {email}")
        else:
            print(f"Failed to retrieve user data for email: {email}. Error: {response.text}")

    new_users_id_list = []

    for email, account_id in new_users_id.items():
        new_dict = {
            "emailAddress": email,
            "accountId": account_id
        }
        new_users_id_list.append(new_dict)

    return new_users_id_list

# compare "user_g" and "new_users_id_list"
def compare_lists(users_g, new_users_id_list):

    #not in new_users_id_list NEED DELETE FROM GROUP
    not_in_new_users = []

    new_users_id_account_ids = {user['accountId'] for user in new_users_id_list}

    for user in users_g:
        if user['accountId'] not in new_users_id_account_ids:
            not_in_new_users.append(user)

    #not in users_g NEED TO ADD TO GROUP
    not_in_users_g = []
    user_g_account_ids = {user['accountId'] for user in users_g}

    for user in new_users_id_list:
        if user['accountId'] not in user_g_account_ids:
            not_in_users_g.append(user)

    return not_in_users_g, not_in_new_users

def add_users_to_group(not_in_users_g, group_name, base_url, email_auth, api_token):
    add_status = []
    headers = {'Content-Type': 'application/json'}

    for user in not_in_users_g:
        payload = {'accountId': user['accountId']}
        response = requests.post(f"{base_url}/rest/api/2/group/user?groupname={group_name}",
                                 data=json.dumps(payload), headers=headers,
                                 auth=HTTPBasicAuth(email_auth, api_token))
        add_status.append((user['accountId'], response.status_code))

    return add_status

def remove_users_from_group(not_in_new_users, group_name, base_url, email_auth, api_token):
    remove_status = []

    for user in not_in_new_users:
        response = requests.delete(
            f"{base_url}/rest/api/2/group/user?groupname={group_name}&accountId={user['accountId']}",
            auth=HTTPBasicAuth(email_auth, api_token))
        remove_status.append((user['accountId'], response.status_code))

    return remove_status

def modify_group():
    users_g = step_one(base_url, group_id, email_auth, api_token)
    print("\nUSERS IN GROUP:\n", users_g)

    print("TOTAL users in group", len(users_g))

    new_users_id_list = get_id(users_new)
    print("\nUSERS IN LIST\n", new_users_id_list)
    print("Total users: ", len(new_users_id_list))

    not_in_users_g, not_in_new_users = compare_lists(users_g, new_users_id_list)

    print("\nADD TO GROUP:\n", not_in_users_g)
    print("\nDELETE FROM GROUP:\n", not_in_new_users)

    confirmation = input("Do you want to continue? (Y/N): ")
    if confirmation.lower() == "y":
        # Modify group
        add_users_to_group(not_in_users_g, group_name, base_url, email_auth, api_token)
        remove_users_from_group(not_in_new_users, group_name, base_url, email_auth, api_token)

    else:
        print("Operation canceled.")

def only_add(only_add_members, email_auth, api_token, group_id):

    base_url = f"https://{my_dom}.atlassian.net/rest/api/3/user/search"
    group_add_url = f'https://{my_dom}.atlassian.net/rest/api/3/group/user'

    auth = HTTPBasicAuth(email_auth, api_token)

    new_users_id = {}
    print(only_add_members)

    for email in only_add_members:
        url = f"{base_url}?query={email}"

        response = requests.get(url, auth=auth)

        if response.status_code == 200:
            user_data = json.loads(response.text)
            if user_data:
                item = user_data[0]  # Assuming the first user in the response is the desired one
                account_id = item.get("accountId")
                if account_id:
                    new_users_id[email] = account_id
            else:
                print(f"No user found for email: {email}")
        else:
            print(f"Failed to retrieve user data for email: {email}. Error: {response.text}")

    only_add_members_list = []

    for email, account_id in new_users_id.items():
        new_dict = {
            "emailAddress": email,
            "accountId": account_id
        }
        only_add_members_list.append(new_dict)

    print("\nADD MEMBERS:\n", only_add_members_list)

    confirmation = input("Do you want to continue? (Y/N): ")
    if confirmation.lower() == "y":
        # add users:
        add_status = []

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        for user in only_add_members_list:
            print(user['accountId'])

            body_data = {
                'accountId': user['accountId']
            }

            response = requests.post(f'{group_add_url}?groupId={group_id}', json=body_data, headers=headers, auth=auth)
            add_status.append((user['accountId'], response.status_code))
            #print(f"Status code: {response.status_code}, Response: {response.text}")

        return add_status, only_add_members_list

    else:
        print("Operation canceled.")

def only_delete(only_delete_members, email_auth, api_token):
    base_url = f"https://{my_dom}.atlassian.net/rest/api/3/user/search"
    group_del_url = f"https://{my_dom}.atlassian.net/rest/api/3/group/user"
    auth = HTTPBasicAuth(email_auth, api_token)

    new_users_id = {}

    for email in only_delete_members:
        url = f"{base_url}?query={email}"

        response = requests.get(url, auth=auth)

        if response.status_code == 200:
            user_data = json.loads(response.text)
            if user_data:
                item = user_data[0]  # Assuming the first user in the response is the desired one
                account_id = item.get("accountId")
                if account_id:
                    new_users_id[email] = account_id
            else:
                print(f"No user found for email: {email}")
        else:
            print(f"Failed to retrieve user data for email: {email}. Error: {response.text}")

    only_delete_members_list = []

    for email, account_id in new_users_id.items():
        new_dict = {
            "emailAddress": email,
            "accountId": account_id
        }
        only_delete_members_list.append(new_dict)

    print("\nDELETE MEMBERS:\n", only_delete_members_list)

    confirmation = input("Do you want to continue? (Y/N): ")
    if confirmation.lower() == "y":
        #delete users:
        remove_status = []

        for user in only_delete_members_list:
            print(user['accountId'])

            body_data = {
                'groupId': group_id,
                'accountId': user['accountId']
            }

            response = requests.delete(group_del_url, params=body_data, auth=auth)
            remove_status.append((user['accountId'], response.status_code))
            print(f"Status code: {response.status_code}, Response: {response.text}")

        return remove_status

    else:
        print("Operation canceled.")


####################
####START SCRIPT####
####################
if __name__ == '__main__':
    while True:
        print(" 1. Modify group with list\n 2. Only add members to group \n 3. Only delete members from group \n")
        user_input = input("Enter 1, 2, or 3 to select an option (or any other key to exit): ")

        if user_input == "1":
            # Option 1 - MODIFY
            print("Option 1 selected.")
            modify_group()
            print("You are welcome!\n")
            break

        elif user_input == "2":
            # Option 2 - ADD
            print("Option 2 selected.")
            only_add(only_add_members, email_auth, api_token, group_id)
            print("You are welcome!\n")
            break

        elif user_input == "3":
            # Option 3 - DELETE
            print("Option 3 selected.")
            only_delete(only_delete_members, email_auth, api_token, base_url)
            print("You are welcome!\n")
            break

        else:
            # Break the loop for any other input
            print("Exiting the program.")
            break