# create_env_file.py
env_content = """# JOWA USSD APP CONFIGURATION

# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/jowa
DB_HOST=localhost
DB_NAME=jowa
DB_USER=postgres
DB_PASSWORD=postgres
DB_PORT=5432

# Application Settings
DEBUG=True
APP_ENV=development
SECRET_KEY=728495e15b6c5d935285eb079f7c78b99e6c2a7f6571e528aa7c52e0dbf4715d

# USSD Settings
USSD_CODE=*384*531#
COUNTRY_CODE=ZM

# Africa's Talking Configuration
AT_USERNAME=sandbox
AT_API_KEY=atsk_f74b6e4b9e0aa7ea82f7c0058d7315528f829f1993888ac1e696b031adb336daa6385c04

# Application URLs
APP_URL=http://localhost:5000
"""

with open('.env', 'w') as f:
    f.write(env_content)

print("Created .env file successfully")