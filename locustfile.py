import os
import random
import string
import time
import json
import uuid
import base64

from locust import TaskSequence, events, seq_task, Locust, HttpLocust

from additional_handlers import additional_success_handler, additional_failure_handler
from common.kaka_client import KafkaClient

# read kafka brokers from config
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "kafka-10:9092").split(sep=",")
KAFKA_TOPICS = ["company.added.v1", "company.deleted.v1", "company.updated.v1"]

# read other environment variables
QUIET_MODE = False if os.getenv("QUIET_MODE", "true").lower() in ['1', 'true', 'yes'] else True
TASK_DELAY = int(os.getenv("TASK_DELAY", "0"))

# register additional logging handlers
if not QUIET_MODE:
    events.request_success += additional_success_handler
    events.request_failure += additional_failure_handler

class KafkaLocust(Locust):
    client = None

    def __init__(self, *args, **kwargs):
        super(KafkaLocust, self).__init__(*args, **kwargs)
        if not KafkaLocust.client:
            KafkaLocust.client = KafkaClient(KAFKA_BROKERS, KAFKA_TOPICS)


class KafkaBehaviour(TaskSequence):

    def random_message(self, min_length=32, max_length=128):
        return ''.join(random.choice(string.ascii_uppercase) for _ in range(random.randrange(min_length, max_length)))

    def timestamped_message(self):
        return f"{time.time() * 1000}:" + ("kafka" * 24)[:random.randint(32, 128)]

    def company_message(self):

        data = {
            'company_id': 3,
            'user_id': 1
        }
        payload = {
            'Type': 'company.added.v1',
            'Origin': 'locust',
            'RequestID': uuid.uuid4().__str__(),
            'EventID': uuid.uuid4().__str__(),
            'Data': data
        }
        return payload

    def get_headers(self):
        context = {
            "email": "admin@enkya.com",
            "user_id": 1,
            "team_id": "cjcjeoi2w0000rn35c23q98ou"
        }

        external_context = {
            "ip_address": "127.0.0.1",
            "team_id": "cjcjeoi2w0000rn35c23q98ou"
        }

        return {
            "Request-ID": uuid.uuid4().__str__(),
            "Request-Source": "locust",
            "Calling-Service": "locust",
            "enkya-Edge-Context": base64.b64encode(json.dumps(context).encode("utf-8")),
            "enkya-external": base64.b64encode(json.dumps(external_context).encode("utf-8"))
        }
    
    # def on_start(self):
    #     HttpLocust().get('/companies', headers=self.get_headers(), verify=False, catch_response=True)

    @seq_task(1)
    def companyAdded(self):
        self.client.send_event(
            topic="company.added.v1",
            key="company.added",
            message=self.company_message()
        )

    @seq_task(2)
    def companyRenamed(self):
        self.client.send_event(
            topic="company.renamed.v1",
            key="company.renamed",
            message=self.company_message()
        )

    @seq_task(3)
    def companyDeleted(self):
        self.client.send_event(
            topic="company.deleted.v1",
            key="company.deleted",
            message=self.company_message()
        )


class KafkaUser(KafkaLocust):
    """
    Locust user class that pushes messages to Kafka
    """
    task_set = KafkaBehaviour
    min_wait = 40
    max_wait = 100
