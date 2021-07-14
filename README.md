# Lichess Daily Puzzle bot for Zulip

## About

The purpose of this Zulip bot is to automatically post the daily chess puzzle from lichess.org in a specfic topic in a specific stream at a specific time of day every day. [Read more about Lichess here.](https://lichess.org/about)


## Setup

1) In your Zulip client, go to Settings -> Your bots, and add a new Generic bot
2) Download its `zuliprc` file and put it at the root of this folder
3) Download the `zulip_bots` Python package using `pip3 install zulip_bots`
4) Place the contents of this folder into `/python-zulip-api/zulip_bots/zulip_bots/bots/lichesspuzzle/`
5) Start the bot with: `zulip-run-bot lichesspuzzle --config-file zuliprc`

## Usage

In these examples, I'll assume you've named your bot `puzzlebot`.

- @puzzlebot **set time** *HH:MM* - Sets the time for when the bot will post the daily puzzle (24-hour format, UTC)
- @puzzlebot **get time** - Returns the time for when the bot will post the daily puzzle (24-hour format, UTC)
- @puzzlebot **set stream** *stream_name* - Sets the stream name the bot will post to (do not include a leading #)
- @puzzlebot **get stream** - Returns the stream name the bot will post to
- @puzzlebot **set topic** *topic_name* - Set the topic name the bot will post to
- @puzzlebot **get topic** - Returns the topic name the bot will post to
- @puzzlebot **puzzle** - The bot will reply to your message with the daily puzzle
