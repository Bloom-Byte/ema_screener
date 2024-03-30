# EMA Screener

This is a screener API that uses the Exponential Moving Average (EMA) to determine if a stock is a buy or sell.

## Quick Setup Guide

- Clone the repository

- Change directory to the repository

- Install the requirements using `pip install -r requirements.txt`

- Setup the environment variables:
  - To change djsm related configs, see djsm docs [here](https://github.com/ti-oluwa/djsm#)
  - If necessary, Change the `DB_NAME`, `DB_HOST`, `DB_PORT` variables to point to your database name, host and port respectively.

- Set up your database credentials using djsm:
  - Run `python manage.py update_secrets "DB_USER" "<your_db_user>"`
  - Run `python manage.py update_secrets "DB_PASSWORD" "<your_db_password>"`

- Run migrations using `python manage.py migrate`

- Create a superuser using `python manage.py createsuperuser`

- Run the server using `python manage.py runserver`

**View API documentation [here](https://documenter.getpostman.com/view/21622102/2sA35G42rH)**
