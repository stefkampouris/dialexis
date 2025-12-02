import urllib.request
import urllib.error

url = "http://localhost:7860/"
endpoints = ["/offer", "/sdp", "/signaling/offer"]

print("--- PROBE START ---")
for ep in endpoints:
    full_url = f"{url.rstrip('/')}{ep}"
    try:
        req = urllib.request.Request(full_url, method="POST")
        with urllib.request.urlopen(req) as response:
            print(f"FOUND: {ep} -> {response.status}")
    except urllib.error.HTTPError as e:
        print(f"MISS: {ep} -> {e.code}")
    except Exception as e:
        print(f"ERR: {ep} -> {e}")
print("--- PROBE END ---")
