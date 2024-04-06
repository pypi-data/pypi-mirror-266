import requests
import threading
import time
from typing import Union, List, Dict, Optional

write_key = None
api_url = "http://api.dawnai.com/"
buffer_size = 50
buffer_timeout = 5
buffer = []
flush_timer = None
debug_logs = False


def identify(user_id: str, traits: Dict[str, Union[str, int, bool, float]]) -> None:
    data = {"user_id": user_id, "traits": traits}
    save_to_buffer({"type": "identify", "data": data})


def track(
    user_id: str,
    event: str,
    properties: Optional[Dict[str, Union[str, int, bool, float]]] = None,
) -> None:
    data = {"user_id": user_id, "event": event, "properties": properties}
    save_to_buffer({"type": "track", "data": data})

def track_ai(
    user_id: str,
    event: str,
    model: Optional[str] = None,
    user_input: Optional[str] = None,
    output: Optional[str] = None,
    convo_id: Optional[str] = None,
    properties: Optional[Dict[str, Union[str, int, bool, float]]] = None,
) -> None:
    data = {
        "user_id": user_id,
        "event": event,
        "properties": properties or {},
        "ai_data": {
            "model": model,
            "input": user_input,
            "output": output,
            "convo_id": convo_id,
        },
    }

    save_to_buffer({"type": "track-ai", "data": data})


def save_to_buffer(event: Dict[str, Union[str, Dict]]) -> None:
    global buffer, flush_timer

    if debug_logs:
        print(f"Added to buffer: {event}")

    buffer.append(event)

    if len(buffer) >= buffer_size:
        flush()
    elif flush_timer is None:
        flush_timer = threading.Timer(buffer_timeout, flush)
        flush_timer.start()


def flush() -> None:
    global buffer, flush_timer

    if flush_timer is not None:
        flush_timer.cancel()
        flush_timer = None

    if not buffer:
        return

    current_buffer = buffer
    buffer = []

    grouped_events = {}

    for event in current_buffer:
        endpoint = event["type"]
        data = event["data"]
        if endpoint not in grouped_events:
            grouped_events[endpoint] = []
        grouped_events[endpoint].append(data)

    for endpoint, events_data in grouped_events.items():
        send_request(endpoint, events_data)


def send_request(endpoint: str, dataEntries: List[Dict[str, Union[str, Dict]]]) -> None:
    if write_key is None:
        raise ValueError("write_key is not set")

    url = f"{api_url}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {write_key}",
    }

    response = requests.post(url, json=dataEntries, headers=headers)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {response.text}")
        raise e
