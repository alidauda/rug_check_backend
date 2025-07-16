from fastapi import FastAPI
import uvicorn
from solders.keypair import Keypair # type: ignore

import base58

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello from backend!"}


@app.get("/generate_wallet")
def generate_wallet():
    keypair = Keypair()
    private_key_bytes = bytes(keypair)
    private_key_str = base58.b58encode(private_key_bytes).decode("utf-8")
    return {
        "public_key": str(keypair.pubkey()),
        "private_key": private_key_str,
    }

@app.get("/rug_check")
def rug_check(public_key: str, private_key: str):
    keypair = Keypair.from_base58_string(private_key)  # type: ignore
    public_key = str(keypair.pubkey())

    
    return {"message": "Rug check!", }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
