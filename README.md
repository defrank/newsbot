# README

Forked and inspired by [pybites/slackbot](https://github.com/pybites/slackbot).
Code for article [How to Build a Simple Slack Bot](http://pybit.es/simple-chatbot.html).

## Install

1. Clone the repository (or fork and clone).
1. Copy or move **secrets.env.sample** to **secrets.env**.
1. [Create a new bot user](https://my.slack.com/services/new/bot)
1. Store the bot's username in **secrets.env** as `BOT_NAME`
1. Store the API Token in **secrets.env** as `BOT_TOKEN`
1. Now we need to get the `BOT_ID` by running the following

    ```sh
    docker-compose up -d
    docker exec -it newsbot_slackbot /bin/sh
    python3 get_botid.py
    ```

1. Once you have finished **secrets.env**, then you're good to go.

    ```sh
    docker-compose restart
    ```
