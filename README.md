# xp-users
VM IP: 192.168.78.9
VM PORT: 18000
URL: http://192.168.78.9:18000

- Auth
- Internal, base user model
- Wallet module
- KYC flows

# References
- [Wallet ERD](https://dbdiagram.io/d/xp-wallet-6577e03456d8064ca0d6edba)

# Database creation
- Install PostgreSQL; make sure to download
a version compatible with the Django version you are using: https://www.postgresql.org/download/
- Create database via PgAdmin or `psql`:
   `CREATE DATABASE xp_wallet;`
- Create or connect default user via PgAdmin or `psql`:
   `CREATE USER xp_wallet WITH PASSWORD 'xp_wallet';`
- Grant privileges to user via PgAdmin or `psql`:
   `GRANT ALL PRIVILEGES ON DATABASE xp_wallet TO xp_wallet;`
- Connect to database via PgAdmin or `psql`:
   `\c xp_wallet`
- Initialize database
   `python manage.py loaddata apps/wallet/fixtures/initialize.yaml`

# Installation and Setup
- Clone the repository

  `git clone https://github.com/todoxp/xp-users.git`
- Install dependencies

  `pip install -r requirements.txt`
- Inside the 'logs' folder, create a new file for the logs
    - Go to "logs" and create a new file called "django.log"

       `cd logs && touch django.log`

    - Duplicate env.example, change the file name

        `cp env.example .env`
        - Update the .env file with the appropriate values for the
        database connection and the log file name.

- Run migrations

    `python manage.py migrate`
- Run the server

    `python manage.py runserver`

- Run the tests

    `python manage.py test`

## pre-commit

A framework for managing and maintaining multi-language pre-commit hooks.
https://pre-commit.com/index.html

- install pre-commit hooks: `pre-commit install` (will run them on every commit)
- it's recommended to run all pre-commit hooks before push to avoid errors in the CI/CD pipeline.
    - `pre-commit run --all-files`
