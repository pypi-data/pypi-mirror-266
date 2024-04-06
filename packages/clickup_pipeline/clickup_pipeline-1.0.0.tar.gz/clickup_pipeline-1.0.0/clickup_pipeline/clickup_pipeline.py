import requests
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


def fetch_clickup_data(clickup_api_token, clickup_space_id):
    clickup_api_token = os.getenv('CLICKUP_API_TOKEN')
    clickup_space_id = os.getenv('CLICKUP_SPACE_ID')
    url = f"https://api.clickup.com/api/v2/space/{clickup_space_id}/task"
    headers = {'Authorization': clickup_api_token}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data


def transform_data(data):
    return data


def upload_data_to_postgres(data):
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        # port=os.getenv('POSTGRES_PORT'),
        database=os.getenv('POSTGRES_DATABASE'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')

    )
    cur = conn.cursor()

    for task in data['tasks']:
        cur.execute("INSERT INTO tasks (id, name, status) VALUES (%s, %s, %s)",
                    (task['id'], task['name'], task['status']))

    conn.commit()
    cur.close()
    conn.close()