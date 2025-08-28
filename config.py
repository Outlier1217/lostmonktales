import os

DATABASE_URI = os.getenv('DATABASE_URI')
if not DATABASE_URI:
    raise ValueError("DATABASE_URI environment variable is not set.")