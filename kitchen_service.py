import asyncio
import random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging


logger = logging.getLogger(__name__)


app = FastAPI(title="Kitchen Service")

# Initialize Prometheus metrics instrumentation
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

# Custom metric: Count smoothies ordered by flavor
from prometheus_client import Counter
smoothies_ordered = Counter(
    'smoothies_ordered_total',
    'Total number of smoothies ordered',
    ['flavor']
)
NUM_COOKS = 1
cook_semaphore = asyncio.Semaphore(NUM_COOKS)

class SmoothieOrder(BaseModel):
    flavor: str

@app.post("/prepare")
async def prepare_smoothie(order: SmoothieOrder):
    logger.info(f"Received order to prepare a smoothie with flavor {order.flavor}")

    # Increment the counter for this flavor
    smoothies_ordered.labels(flavor=order.flavor).inc()

    try:
        logger.debug(f"Waiting for a cook to become available")
        await asyncio.wait_for(cook_semaphore.acquire(), timeout=2.0)
    except asyncio.TimeoutError:
        logger.error(f"Can't process the order: {NUM_COOKS} cooks are currently busy. Consider increasing NUM_COOKS.")
        raise HTTPException(status_code=503, detail="All cooks are currently busy")

    try:
        # Prepare the smoothie
        await asyncio.sleep(random.uniform(1.5, 2.5))

        logger.debug(f"Smoothie with flavor {order.flavor} prepared")
        return {"status": "done", "flavor": order.flavor}
    finally:
        cook_semaphore.release()