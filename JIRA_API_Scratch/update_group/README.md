### Instruction for script
1. [Install python](https://www.python.org/downloads/)

2. Create API token [here](https://id.atlassian.com/manage-profile/security/api-tokens)

The token will be visible only once, save it in a safe place (1Password for example)

- Insert your token and email in file “cred_api.py“.

3. Insert groupID and group name in file “start.py”.
  - You can obtain the groupID from here - https://{YOUR DOMAIN}.atlassian.net/wiki/rest/api/group/by-name?name={name}
  - Replace `{name}` with the actual group name.


### With this script you can do 3 options:

| Option                                                          | Description                                                         |
|-----------------------------------------------------------------|---------------------------------------------------------------------|
| 1. Modify users in group, add and delete from group automatically | Fill the file "[modify_members.txt](modify_members.txt)" with the emails |
| 2. Only add users in group                                      | Fill the file "[only_add.txt](only_add.txt)"                        |
| 3. Only delete users from group                                 | Fill the file "[only_delete.txt](only_delete.txt)"                              |
  

When you fill the file, make sure that:
* Every new email starts on a **new** line.
* **No blank lines** at the end of the file.


If all is done, start the script with the following command in the terminal:

    python3 start.sh