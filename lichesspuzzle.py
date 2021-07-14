from typing import Any, Dict
from zulip_bots.lib import BotHandler
import requests
import json
import configparser
import re
import zulip
import schedule, time
import threading
import datetime

def get_content():
     r = requests.get('https://lichess.org/training/daily', headers={'Accept': 'application/vnd.lichess.v5+json'})
     c = r.content
     o = json.loads(c)
     url = "https://lichess.org/training/" + str(o['puzzle']['realId'])
     imgurl = "https://lichess1.org/training/export/gif/thumbnail/" + str(o['puzzle']['realId']) + ".gif"
     return ("[Solve the daily puzzle](" + url + ")" + "[:](" + imgurl + ")")

def run_continuously(interval=1):
    cease_continuous_run = threading.Event()
    class ScheduleThread(threading.Thread):
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)
    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run

class LichessPuzzleHandler:

    def reschedule(self):
        schedule.clear()
        time = self.read_config("time")
        split = time.split(":")
        now = datetime.datetime.now(datetime.timezone.utc)
        offset = now.astimezone().tzinfo.utcoffset(now)
        local_time = (datetime.datetime.combine(datetime.date.today(), datetime.time(int(split[0]), int(split[1]))) + offset).strftime("%H:%M")
        print("Scheduling daily puzzle for " + time + " UTC / " + local_time + " local time")
        schedule.every().day.at(local_time).do(self.job)
        all_jobs = schedule.get_jobs()
        print(all_jobs)


    def job(self):
        stream = self.read_config("stream")
        if stream == None:
            print("ERROR: No stream set in " + self.bot_config_file)
            return
        topic = self.read_config("topic")
        if topic == None:
            print("ERROR: No topic set in " + self.bot_config_file)
            return
        request = {
            "type": "stream",
            "to": stream,
            "topic": topic,
            "content": get_content(),
        }
        result = self.client.send_message(request)
        if result["result"] == "error":
            print ("ERROR: " + result["msg"])
    
    
    def initialize(self, bot_handler: BotHandler) -> None:
        self.bot_config_file = "lichesspuzzle.conf"
        self.zuliprc_config_file = "zuliprc"
        self.configparser = configparser.ConfigParser()
        self.client = zulip.Client(config_file = self.zuliprc_config_file)
        self.reschedule()
        stop_run_continuously = run_continuously()
        print("Initialized!")

    def usage(self) -> str:
        return """
This is the Lichess Daily Puzzle App. I will post the daily Lichess puzzle to a specific stream and topic every day at a specific time. I support the following commands:

**set time** *HH:MM* - Sets the time for when I will post the daily puzzle (24-hour format, UTC)
**get time** - Returns the time for when I will post the daily puzzle (24-hour format, UTC)
**set stream** *stream_name* - Sets the stream name I will post to (do not include a leading #)
**get stream** - Returns the stream name I will post to
**set topic** *topic_name* - Sets the topic name I will post to
**get topic** - Returns the topic name I will post to
**puzzle** - I will reply to your message with the daily puzzle
        """

    def read_config(self, key) -> str:
        try:
            with open(self.bot_config_file) as f:
                self.configparser.read_file(f)
                value = self.configparser.get("lichesspuzzle", key)
        except configparser.NoOptionError:
            return None
        return value
    
    def set_config(self, key, value):
        self.configparser.set("lichesspuzzle", key, value)
        with open(self.bot_config_file, "w") as config:
            self.configparser.write(config)
        print("Set " + key + " to " + value)
        
    def handle_message(self, message: Dict[str, Any], bot_handler: BotHandler) -> None:
        split = message["content"].split()
        if split[0] == "get" and split[1] in ["time", "stream", "topic"]:
            value = self.read_config(split[1])
            bot_handler.send_reply(message, split[1] + " is currently set to " + value)
        elif split[0] == "set" and split[1] == "time":
            if not re.match("^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$", split[2]):
                bot_handler.send_reply(message, "Expected HH:MM")
                return
            self.set_config("time", split[2])
            self.reschedule()
            bot_handler.send_reply(message, "Time set to " + split[2])
        elif split[0] == "set" and split[1] in ["stream", "topic"]:
            value = " ".join(split[2:])
            self.set_config(split[1], value)
            bot_handler.send_reply(message, split[1] + " has been set to " + value)
        elif split[0] == "puzzle":
            bot_handler.send_reply(message, get_content()) 
        else:
            bot_handler.send_reply(message, self.usage()) 
        return

handler_class = LichessPuzzleHandler
