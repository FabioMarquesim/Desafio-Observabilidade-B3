import logging
import random
import threading
import time
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_music_api")

app = FastAPI(title="Mock Music Database API")

FAILURE_CHANCE = 0.05

_active_requests = 0
_active_requests_lock = threading.Lock()


@contextmanager
def track_active_request():
    global _active_requests
    with _active_requests_lock:
        _active_requests += 1
        current = _active_requests
    try:
        yield current
    finally:
        with _active_requests_lock:
            _active_requests -= 1


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/track-metadata")
def track_metadata(artist: str, title: str):
    with track_active_request() as active_requests:
        network_jitter_ms = random.randint(5, 50)
        load_delay_ms = active_requests * 2
        time.sleep((network_jitter_ms + load_delay_ms) / 1000)

        if random.random() < FAILURE_CHANCE:
            logger.error(f"track lookup failed artist={artist} title={title} active_requests={active_requests}")
            raise HTTPException(status_code=503, detail="music database temporarily unavailable")

        seed = sum(ord(c) for c in f"{artist}{title}")
        rng = random.Random(seed)
        bpm = rng.randint(80, 180)

        if bpm >= 140:
            energy_level = "High"
            visual_preset = "strobes_and_lasers"
        elif bpm >= 100:
            energy_level = "Medium"
            visual_preset = "color_wash"
        else:
            energy_level = "Low"
            visual_preset = "ambient_glow"

        metadata = {
            "bpm": bpm,
            "energy_level": energy_level,
            "visual_preset": visual_preset,
        }

        logger.info(f"track lookup responded artist={artist} title={title} active_requests={active_requests} metadata={metadata}")

        return metadata
