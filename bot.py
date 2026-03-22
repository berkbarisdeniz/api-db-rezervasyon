import requests

cevap = requests.post("http://127.0.0.1:8000/satin_al/4")

print("cevap:",cevap.json())