import os
from dotenv import load_dotenv, dotenv_values

load_dotenv('.env.develop')

key = os.getenv('DB_PASSWORD_LOCAL')
print(key)