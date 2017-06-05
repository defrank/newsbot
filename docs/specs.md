# Specifications

## Overview
A Slackbot that fetches relevant news about any given topic.  Periodically
updates a channel it is subscribed to with news updates.  The channel is
responsible for the news topic and update frequency.  News is fetched from a
dynamic set of sources.

Future support will include commands the bot will accept to deliver news
on-demand.


## Table of Contents
1. [Overview](#overview)
1. [Slackbot](#slackbot)
    1. [API](#slack-api)
    1. [Channels](#channels)
    1. [Commands](#commands)
1. [News Clients](#news-clients)
    1. [Twitter](#twitter-client)
        1. [API](#twitter-api)

## Slackbot

### Slack API
* [Slack Bot Users API](https://api.slack.com/bot-users)
* [Slack RTM API](https://api.slack.com/rtm)
* [Slack Python RTM API](https://slackapi.github.io/python-slackclient/real_time_messaging.html#rtm-events)

### Channels

#### Requirements
* slackbot must be a member

#### Topic
Should specify the news topic (e.g. *developer news*, *political news*, etc.),
otherwise general will be assumed.

#### Purpose
Used to specify specific settings such as frequency of news updates.

##### Options
* topic: can specify more than once
* **frequency:** polling number in minutes
    * default is *60*
* **limit:** maximum number of articles
    * default is *2*
* **keywords:** additional keywords used to prioritize in search
* **exclude:** keywords used to exclude articles
* **language:** restrict articles to language specified by
  [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) format
    * default is *en* (English)

Example:
```
frequency: 30
limit: 5
language: english
```

### Commands
*TODO*

## News Clients
All clients must provide the following interface:
* Implement `_fetch` method that accepts a topic and limit, then returns
  an iterable of strings (preferably a generator despite below example).

    ```python
    def _fetch(self, topic, limit):
        return ['Article 1', 'Article 2']
    ```

* News topic must be certain that either the API searches related
  topics or that synonyms are included in the search.

### Twitter Client

#### Twitter API
* [Twitter Search API](https://dev.twitter.com/rest/public/search)
* [Tweepy Search API](https://tweepy.readthedocs.io/en/v3.5.0/api.html#API.search)
