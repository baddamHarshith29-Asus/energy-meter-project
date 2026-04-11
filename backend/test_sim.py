import requests

url = "http://127.0.0.1:5000/api/simulate-unified"

res = requests.post(url, json={
    "input": {
        "machines": 5,
        "machineRuntime": 8,
        "monthlyUnits": 700,
        "costPerUnit": 8
    },
    "scenario": {
        "reduceRuntime": 20,
        "reduceHours": 2
    }
})

print(res.text)
