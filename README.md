# README

* Forked and inspired by [pybites/slackbot](https://github.com/pybites/slackbot).
* Code for article [How to Build a Simple Slack Bot](http://pybit.es/simple-chatbot.html).


## Requirements

* Python 3.6+ (not tested on lower versions) with PIP

### Optional

* Docker with Docker Compose


## Install

1. Clone the repository (or fork and clone).
1. Copy or move **secrets.yml.sample** to **secrets.yml**.

### Setup Slackbot
* **Required:** `slackbot.name`, `slackbot.token`
* **Optional:** `slackbot.id`

1. [Create a new bot user](https://my.slack.com/services/new/bot)
1. Store the bot's username in **secrets.yml** as `slackbot.name`
1. Store the API Token in **secrets.yml** as `slackbot.token`
1. **Note:** `slackbot.id` is optional and will be determined at instantiation
   of NewsSlackBot

### Install with Docker

1. Once you have finished **secrets.yml**, then we just build the image.

    ```sh
    docker-compose build
    ```


### Install with virtualenv
*Not supported*

### Vanilla install

1. Assuming you have Python 3 installed, let's get the environment
   setup:

    ```sh
    pip3 install -r requirements.txt
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

1. Run in the foreground:

    ```sh
    ./run.sh
    ```

    OR background:

    ```sh
    ./run.sh &
    ```
