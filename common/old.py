from locust import HttpLocust, TaskSet
from common.kaka_client import KafkaClient
import uuid
import base64
import json

def login(l):
    l.client.post("/login", {"username":"ellen_key", "password":"education"})

def logout(l):
    l.client.post("/logout", {"username":"ellen_key", "password":"education"})

def index(l):
    l.client.send("/companies", )

def companies(l):
    l.client.get("/companies")

class UserBehavior(TaskSet):
    tasks = {index: 2, companies: 1}

    def on_start(self):
        login(self)

    def on_stop(self):
        logout(self)

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 1000
    max_wait = 1000

