import datetime
import json
import time
from threading import Thread

import paho.mqtt.client as mqtt
from save_to_db.models import LxsData
import asyncio
import yaml


async def save(topic, data, time_stamp):
    await LxsData.create(
        device_id=data["device_id"],
        topic=topic,
        timestamp=time_stamp,
        data={i["name"]: i["value"] for i in data["values"]}
    ).save()


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

    for i in json.loads(msg.payload):
        asyncio.run_coroutine_threadsafe(save(msg.topic, i, datetime.datetime.fromtimestamp(i["ts"] / 1000)), loop)


def subscribe():
    with open("./info.yaml") as f:
        data = yaml.safe_load(f)["mqtt"]
    client = mqtt.Client()
    client.username_pw_set(data["user"], data["password"])
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(data["host"], data["port"])
    client.subscribe(data["topic"], qos=0)
    client.loop_forever()
    return client


def start_loop(loop):
    asyncio.set_event_loop(loop)
    print("start loop", time.time())
    loop.run_forever()


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    t = Thread(target=start_loop, args=(loop,))
    t.start()
    client = subscribe()
