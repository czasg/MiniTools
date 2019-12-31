import requests

print(requests.get("http://127.0.0.1:8866/scheduler/jobs").text)

# print(requests.post("http://127.0.0.1:8866/scheduler/jobs", json={
#     "func": "async_scheduler:async_scheduler",
#     "id": "cza_test",
#     "trigger": "interval",
#     "seconds": 3,
# }).text)

# print(requests.post("http://127.0.0.1:8866/scheduler/jobs/cza_test/pause").text)


# print(requests.post("http://127.0.0.1:8866/scheduler/jobs/cza_test/resume").text)