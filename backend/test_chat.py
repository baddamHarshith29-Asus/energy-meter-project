import requests

url = "http://127.0.0.1:5000/api/chat"

print("Sending chat 1...")
res1 = requests.post(url, json={
    "query": "Hello", 
    "history": []
})
print("Res 1:", res1.json())
history = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": res1.json().get('response', '')}]

print("Sending chat 2...")
res2 = requests.post(url, json={
    "query": "How are you?", 
    "history": history
})
print("Res 2:", res2.json())
history.extend([{"role": "user", "content": "How are you?"}, {"role": "assistant", "content": res2.json().get('response', '')}])

print("Sending chat 3...")
res3 = requests.post(url, json={
    "query": "What is 2+2?", 
    "history": history
})
print("Res 3:", res3.json())
