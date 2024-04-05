# EMA Screener

This is a screener API that uses the Exponential Moving Average (EMA) to determine if a stock is a buy or sell.

## Quick Setup Guide

- Clone the repository

- Change directory to the repository

- Install the requirements using `pip install -r requirements.txt`

- Copy the config in temp.env to a new file called .env and update the values

- Run migrations using `python manage.py migrate`

- Create a superuser using `python manage.py createsuperuser`

- Run the server using `python manage.py runserver`

- Start Docker, open a new console and start a redis server on port 6379 using

```bash
docker run --rm -p 6379:6379 redis:7
```

Or on a linux terminal (make sure to have redis installed):

```bash
sudo service redis-server start
```

**View API documentation [here](https://documenter.getpostman.com/view/21622102/2sA35G42rH)**

## Connecting to the EMA Record Update Websocket

The EMA record update record websocket route is `ws://be.emascreener.bloombyte.dev/ws/ema-records/update/`
`
In production, ensure that you include a valid API key with your connection request. You can do this by

- Adding a url query param `ws://be.emascreener.bloombyte.dev/ws/ema-records/update/?api_key=<your_api_key>`, or
- Adding the API key to your request headers using the `X-API-KEY` key.

To test your connection, send a JSON message through the connection. If the connection is okay it should piggy-back your message.

>NOTE: The websocket only accepts and returns JSON data

Contact admin to get an API key!
