import httpx
import json


BASE_URL = "http://localhost:8000/api/v1"


# login 

resp = httpx.post(F"{BASE_URL}/auth/login",json = {
    "email": "user3@example.com",
    "password": "User123@"
})


token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

DOC_ID = "68532dc7-f2e9-44f3-9883-46b124c177bc"


print("streaming repsonse : \n")




# Stream
with httpx.stream(
    "POST",
    f"{BASE_URL}/chat/{DOC_ID}/stream",
    headers=headers,
    json={"query": "Summarize this document", "document_id": DOC_ID},
    timeout=60,
) as response:
    for line in response.iter_lines():
        if line.startswith("data: "):
            event = json.loads(line[6:])

            if event["type"] == "sources":
                print(f"\n[Sources found: {len(event['data'])}]")
            elif event["type"] == "token":
                print(event["data"], end="", flush=True)
            elif event["type"] == "done":
                print(f"\n\n[Done — session: {event['data']['session_id']}]")
            elif event["type"] == "error":
                print(f"\n[Error: {event['data']}]")