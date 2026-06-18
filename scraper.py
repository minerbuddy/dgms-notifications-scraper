import requests

url = "https://www.dgms.gov.in/UserView/index?mid=1603"

r = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=20
)

print("STATUS:", r.status_code)
print("TIME:", r.elapsed)
print(r.text[:200])
