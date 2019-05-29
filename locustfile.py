from locust import HttpLocust, TaskSet

def login(l):
    l.client.post("/login", {"username":"ellen_key", "password":"education"})

def logout(l):
    l.client.post("/logout", {"username":"ellen_key", "password":"education"})

def index(l):
    l.client.get("/")

def companies(l):
    l.client.get("/companies")

class UserBehavior(TaskSet):
    tasks = {index: 2, companies: 1}

    def on_start(self):
        pass
        # login(self)

    def on_stop(self):
        pass
        # logout(self)

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 1000
    max_wait = 1000