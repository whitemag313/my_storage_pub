import requests
from google_auth_oauthlib import flow

emails_file = 'emails.txt'
aliases_file = 'alias.txt'

# Функция для чтения данных из файла и создания списка пар пользователь-алиас
def create_user_alias_pairs(emails_file, aliases_file):
    user_alias_pairs = []
    with open(emails_file, 'r') as emails, open(aliases_file, 'r') as aliases:
        email_lines = emails.readlines()
        alias_lines = aliases.readlines()
        for email, alias in zip(email_lines, alias_lines):
            email = email.strip()  # Убрать лишние пробелы и символы перевода строки
            alias = alias.strip()
            user_alias_pairs.append({email: alias})
    return user_alias_pairs

# Создать список пар пользователь-алиас
user_alias_pairs = create_user_alias_pairs(emails_file, aliases_file)

# Установка OAuth 2.0 клиента
client_secrets_file = '../user_creation/credentials.json'
flow = flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes=['https://www.googleapis.com/auth/admin.directory.user'])

# Получение учетных данных
credentials = flow.run_local_server()

# Получение access token из учетных данных
access_token = credentials.token

# Заголовки с Authorization и Content-Type
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Проход по списку пар пользователь-алиас и удаление алиаса
for item in user_alias_pairs:
    for user_email, alias_to_delete in item.items():
        # URL для удаления алиаса пользователя
        user_key = user_email  # Для простоты предполагаем, что user_key равен адресу электронной почты
        url = f'https://www.googleapis.com/admin/directory/v1/users/{user_key}/aliases/{alias_to_delete}'

        # Отправка DELETE-запроса для удаления алиаса
        response = requests.delete(url, headers=headers)

        # Проверка статус-кода
        if response.status_code == 204:
            print(f"Алиас '{alias_to_delete}' успешно удален для пользователя '{user_email}'.")
        else:
            print(f"Ошибка при удалении алиаса '{alias_to_delete}' для пользователя '{user_email}'. Код статуса: {response.status_code}")
            print(response.json())
