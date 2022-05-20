#!/usr/bin/env python

import collections
import paho.mqtt.client as mqtt


class MqttController:
    mqtt_client = None
    is_connected = False

    topic_handlers = None

    def __init__(self, host, port):
        self.topic_handlers = collections.defaultdict(set)
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.__on_connect
        self.mqtt_client.on_message = self.__on_message

        try:
            self.mqtt_client.connect(host, port, 60)

        except Exception as e:
            print(e)
            print("MQTT-Error - try to connect to local mqtt-server...")
            self.mqtt_client.connect("localhost", 1883, 60)

        self.mqtt_client.loop_start()

    def subscribe_to_topic(self, topic, callback):
        print(topic)
        self.topic_handlers[topic].add(callback)
        self.mqtt_client.subscribe(topic)

    def __on_connect(self, mqttc, userdata, flags, rc):
        print("Connected to mqtt client with result code " + str(rc))

    def __on_message(self, mqttc, userdata, msg):
        for handler in self.topic_handlers.get(msg.topic, []):
            handler(msg.payload)

