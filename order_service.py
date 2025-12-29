import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Order Service")

class Order(BaseModel):
    flavor: str

@app.post("/order")
async def create_order(order: Order):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8001/prepare",
                json={"flavor": order.flavor}
            )
            response.raise_for_status()
            return {"status": "completed", "kitchen_response": response.json()}
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Kitchen failed to process order")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Kitchen unavailable")
