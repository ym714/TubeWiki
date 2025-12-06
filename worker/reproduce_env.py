from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).parent / '.env'
print(f"Loading .env from: {env_path}")
print(f"File exists: {env_path.exists()}")

if env_path.exists():
    with open(env_path, 'r') as f:
        print("--- File Content ---")
        print(f.read())
        print("--------------------")

load_dotenv(dotenv_path=env_path, verbose=True)

print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"QSTASH_CURRENT_SIGNING_KEY: {os.getenv('QSTASH_CURRENT_SIGNING_KEY')}")
print(f"GROQ_API_KEY: {os.getenv('GROQ_API_KEY')}")
