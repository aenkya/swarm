from locust import events, HttpLocust
from kafka import KafkaProducer, KafkaConsumer
import time
import json

class KafkaClient:
    httpClient = None

    def __init__(self, kafka_brokers=None, topics=None):

        if kafka_brokers is None:
            kafka_brokers = ["kafka-10:9092"]
        self.producer = KafkaProducer(
                                        bootstrap_servers=kafka_brokers,
                                        acks="all",
                                        value_serializer=lambda m: json.dumps(m).encode('utf-8'))
        if topics:
            self.consumer = KafkaConsumer(
                                        bootstrap_servers=kafka_brokers,
                                        group_id="eventbus-user-tools"
                                        )
            self.consumer.subscribe(topics=topics)


    def __handle_success(self, *arguments, **kwargs):
        end_time = time.time()
        elapsed_time = int((end_time - kwargs["start_time"]) * 1000)
        try:
            record_metadata = kwargs["future"].get(timeout=1)

            request_data = dict(request_type="ENQUEUE",
                                name=record_metadata.topic,
                                response_time=elapsed_time,
                                response_length=record_metadata.serialized_value_size)

            self.__fire_success(**request_data)
        except Exception as ex:
            raise  ValueError("Logging the exception : {0}".format(ex))

    def __handle_failure(self, *arguments, **kwargs):
        end_time = time.time()
        elapsed_time = int((end_time - kwargs["start_time"]) * 1000)

        request_data = dict(request_type="ENQUEUE", name=kwargs["topic"], response_time=elapsed_time,
                            exception=arguments[0])

        self.__fire_failure(**request_data)

    def __fire_failure(self, **kwargs):
        events.request_failure.fire(**kwargs)

    def __fire_success(self, **kwargs):
        events.request_success.fire(**kwargs)

    def send_event(self, topic, key=None, message=None):
        start_time = time.time()
        future = self.producer.send(topic, key=key.encode() if key else None,
                                    value=message if message else None)
        future.add_callback(self.__handle_success, start_time=start_time, future=future)
        future.add_errback(self.__handle_failure, start_time=start_time, topic=topic)
    
    def createHttpClient(self):
        self.httpClient = HttpLocust()

    def finalize(self):
        print("flushing the messages")
        self.producer.flush(timeout=5)
        print("flushing finished")
