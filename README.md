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
  - Run

  ```bash
  python manage.py update_secrets "DB_USER" "<your_db_user>"
  ```

  - And
  
  ```bash
  python manage.py update_secrets "DB_PASSWORD" "<your_db_password>"
  ```

- Run migrations using `python manage.py migrate`

- Create a superuser using `python manage.py createsuperuser`

- Run the server using `python manage.py runserver`

- Open a new console and start a redis server on port 6379 using

```bash
docker run --rm -p 6379:6379 redis:7
```

**View API documentation [here](https://documenter.getpostman.com/view/21622102/2sA35G42rH)**

## Connecting to the EMA Record Update Websocket

The EMA record update record websocket route is `/ws/ema-records/update/`

In production, ensure that you include a valid API key with your connection request. You can do this by

- Adding a url query param `/ws/ema-records/update/?api_key=<your_api_key>`, or
- Adding the API key to your request headers using the `X-API-KEY` key.

To test your connection, send a JSON message through the connection. If the connection is okay it should piggy-back your message.

>NOTE: The websocket only accepts and returns JSON data

Contact admin to get an API key!
