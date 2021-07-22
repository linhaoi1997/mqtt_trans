import json

import paho.mqtt.client as mqtt
import yaml
from functools import partial


def on_connect(topic, client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(topic)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


def on_message_and_trans(trans_client, client, userdata, msg):
    # print(msg.topic + " " + str(msg.payload))
    try:
        trans_client.publish(msg.payload)
    except Exception as e:
        print(e)
        trans_client.connect(trans_client.config.get("target_host"), trans_client.config.get("target_port"))


def on_publish(client, userdata, mid):
    pass
    # print("mid", str(mid), sep=" ,")


class Config:

    def __init__(self, path):
        with open(path, "r") as f:
            self.info = yaml.safe_load(f)

    def get(self, key, default=""):
        return self.info.get(key, default)


class TransClient():

    def __init__(self, config_path):
        self.config = Config(config_path)
        self.client = mqtt.Client()
        self.client.connect(self.config.get("target_host"), self.config.get("target_port"))
        self.client.username_pw_set(self.config.get("target_user"), self.config.get("target_password"))
        self.client.on_connect = partial(on_connect, self.config.get("target_topic"))
        self.client.on_publish = on_publish
        self.time_stamp = None

    def publish(self, data):
        time_stamp = json.loads(data)["meta"]["t"]
        if self.time_stamp != time_stamp:
            self.client.publish(self.config.get("target_topic"), data)
        self.time_stamp = time_stamp


class ListenClient():

    def __init__(self, config_path, trans_client):
        self.config = Config(config_path)
        self.listen_client = mqtt.Client()
        self.listen_client.connect(self.config.get("source_host"), self.config.get("source_port"))
        self.listen_client.username_pw_set(self.config.get("source_user"), self.config.get("source_password"))
        self.listen_client.on_connect = partial(on_connect, self.config.get("source_topic"))
        self.listen_client.on_message = partial(on_message_and_trans, trans_client)
        self.listen_client.on_publish = on_publish

    def loop(self):
        self.listen_client.loop_forever()


class Trans:

    def __init__(self, config_path):
        self.trans_client = TransClient(config_path)
        self.listen_client = ListenClient(config_path, self.trans_client)


if __name__ == '__main__':
    Trans("./info.yaml").listen_client.loop()
