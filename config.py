import os

# Database configuration
DATABASE_URI = os.getenv('DATABASE_URI', 'postgresql://postgres:root@localhost/arch_db')