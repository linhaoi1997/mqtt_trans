import datetime
import json
import time
from threading import Thread

import paho.mqtt.client as mqtt
from models import LxsData
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


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
    with open("./info.yaml") as f:
        data = yaml.safe_load(f)["mqtt"]
    while True:
        print("尝试重连")
        try:
            client.connect(data["host"], data["port"], keepalive=10)
            client.subscribe(data["topic"], qos=0)
            break
        except Exception as e:
            print(e)
        time.sleep(5)


def subscribe(client_):
    with open("./info.yaml") as f:
        data = yaml.safe_load(f)["mqtt"]
    # client = mqtt.Client()
    client_.username_pw_set(data["user"], data["password"])
    client_.on_connect = on_connect
    client_.on_message = on_message
    client_.on_disconnect = on_disconnect

    client_.connect(data["host"], data["port"], keepalive=10)
    client_.subscribe(data["topic"], qos=0)
    client_.loop_forever()
    return client


def start_loop(loop):
    asyncio.set_event_loop(loop)
    print("start loop", time.time())
    loop.run_forever()


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    t = Thread(target=start_loop, args=(loop,))
    t.start()
    client = mqtt.Client()
    subscribe(client)
