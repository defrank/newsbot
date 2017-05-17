# README

* Forked and inspired by [pybites/slackbot](https://github.com/pybites/slackbot).
* Code for article [How to Build a Simple Slack Bot](http://pybit.es/simple-chatbot.html).


## Requirements

* Python 3.6+ (not tested on lower versions) with PIP

### Optional

* Docker with Docker Compose


## Install

1. Clone the repository (or fork and clone).
1. Copy or move **secrets.env.sample** to **secrets.env**.
1. [Create a new bot user](https://my.slack.com/services/new/bot)
1. Store the bot's username in **secrets.env** as `BOT_NAME`
1. Store the API Token in **secrets.env** as `BOT_TOKEN`

### Install with Docker

1. Now we need to get the `BOT_ID`:

    ```sh
    docker-compose up -d
    docker-compose exec slackbot python3 get_botid.py
    ```

1. Store the bot ID in **secrets.env**.
1. Once you have finished **secrets.env**, then you're good to go.

    ```sh
    docker-compose restart
    ```


### Install with virtualenv
*Not supported*

### Vanilla install

1. Assuming you have Python 3 installed, let's get the environment
   setup:

    ```sh
    pip install -r requirements.txt
    source secrets.env
    export $(cut -d= -f1 secrets.env)
    ```

1. Now we need to get the `BOT_ID`:

    ```sh
    python3 get_botid.py
    ```

1. Store the bot ID in **secrets.env**.
1. Possibly a good idea to source **secrets.env** in you startup config
   file (e.g., .bashrc).  Add the following lines:

   ```sh
   bot_secretsfile="path/to/your/secrets.env"
   source "${bot_secretsfile}"
   export $(cut -d= -f1 "${bot_secretsfile}")
   ```

1. Logout, login, then verify your environment:

    ```sh
    echo $BOT_NAME $BOT_TOKEN $BOT_ID
    ```


## Run

1. Be sure to setup the environment in [Install](#Install) first.

### Run with Docker

1. Launch the container:

    ```sh
    docker-compose up -d
    ```

### Run with virtualenv
*Not supported*

### Vanilla run

1. If you did not source **secrets.env** in your startup config file,
   then we need to source it:

    ```sh
    source secrets.env
    export $(cut -d= -f1 secrets.env)
    ```

1. Run in the foreground:

    ```sh
    ./run.sh
    ```

    OR background:

    ```sh
    ./run.sh &
    ```
