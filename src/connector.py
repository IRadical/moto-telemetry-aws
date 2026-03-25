import os
import json
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
from dotenv import load_dotenv

load_dotenv()

class AWSConnector:
    def __init__(self):
        self.endpoint = os.getenv("AWS_ENDPOINT")
        self.client_id = os.getenv("CLIENT_ID")
        self.cert_filepath = os.getenv("CERT_PATH")
        self.pri_key_filepath = os.getenv("KEY_PATH")
        self.ca_filepath = os.getenv("CA_PATH")
        
        self.topic = f"telemetry/{self.client_id}"

        self.event_loop_group = io.EventLoopGroup(1)
        self.host_resolver = io.DefaultHostResolver(self.event_loop_group)
        self.client_bootstrap = io.ClientBootstrap(self.event_loop_group, self.host_resolver)

        self.mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=self.endpoint,
            cert_filepath=self.cert_filepath,
            pri_key_filepath=self.pri_key_filepath,
            client_bootstrap=self.client_bootstrap,
            ca_filepath=self.ca_filepath,
            client_id=self.client_id,
            clean_session=False,
            keep_alive_secs=30
        )

    def connect(self):
        print(f"Connecting to AWS IoT Core at {self.endpoint}...")
        connect_future = self.mqtt_connection.connect()
        connect_future.result() 
        print("Connected successfully to AWS IoT Core!")

    def publish_telemetry(self, payload):
        message = json.dumps(payload)
        self.mqtt_connection.publish(
            topic=self.topic,
            payload=message,
            qos=mqtt.QoS.AT_LEAST_ONCE
        )
        print(f"Published to [{self.topic}]")

    def disconnect(self):
        print("Disconnecting...")
        disconnect_future = self.mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected completely.")

    def publish(self, topic, payload):
        """Envía datos a AWS IoT Core usando un tópico específico."""
        message = json.dumps(payload)
        self.mqtt_connection.publish(
            topic=topic,
            payload=message,
            qos=mqtt.QoS.AT_LEAST_ONCE
        )
        print(f"Published to [{topic}]")