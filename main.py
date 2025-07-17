from fastapi import FastAPI
import uvicorn
from solders.keypair import Keypair # type: ignore
import asyncio
from agentipy.tools.rugcheck import RugCheckManager
import base58
import os
import json
import time
import requests
from solders.message import Message
from solders.signature import Signature
from solders.hash import Hash
from solders.system_program import TransferParams, transfer
from solders.transaction import Transaction
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()
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
async def rug_check(input: str):
    try:
        rugcheck = RugCheckManager(api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTI5MTcxMTksImlkIjoiOWM5NjFqSEJkOFhOVXpEMVlXYlhCRGhqV1BDNmY1SFpXZmtpOFRwNHhqNmsifQ.IuUffQdjtX_zsLpVjIHDxbFRE5u9Afk8yCeNnIfOVD8")
        report_task = rugcheck.fetch_token_report_summary(input)
        lockers_task = rugcheck.fetch_token_lp_lockers(input)
        report, lockers = await asyncio.gather(report_task, lockers_task)
        return {"report": report.to_user_friendly_string(), "lockers": lockers.to_user_friendly_string()}
    except Exception as e:
        return {"error": str(e), "message": "Error fetching rug check data"}
    
@app.get("/rug_check_scan")
async def rug_check_scan(input: str, chain: str):
    try:
        rugcheck = RugCheckManager(api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTI5MTcxMTksImlkIjoiOWM5NjFqSEJkOFhOVXpEMVlXYlhCRGhqV1BDNmY1SFpXZmtpOFRwNHhqNmsifQ.IuUffQdjtX_zsLpVjIHDxbFRE5u9Afk8yCeNnIfOVD8")
        report_task = rugcheck.fetch_token_report_summary(input)
        report = await report_task
        return {"report": report.to_user_friendly_string()}
    except Exception as e:
        return {"error": str(e), "message": "Error fetching rug check data"}

# Load private key from environment variable
PRIVATE_KEY = os.getenv("SOLANA_PRIVATE_KEY")
if not PRIVATE_KEY:
    raise ValueError("Please set the SOLANA_PRIVATE_KEY environment variable.")

# Create a wallet (Keypair) from the private key
wallet: Keypair = Keypair.from_base58_string(PRIVATE_KEY)

def sign_message(wallet: Keypair, message: str) -> dict:
    message_bytes = message.encode("utf-8")
    signature = wallet.sign_message(message_bytes)
    signature_base58 = str(signature)
    signature_data = list(base58.b58decode(signature_base58))
    return {
        "data": signature_data,
        "type": "ed25519",
    }

@app.post("/login_rugcheck")
async def login_rugcheck():
    message_data = {
        "message": "Sign-in to Rugcheck.xyz",
        "timestamp": int(time.time() * 1000),
        "publicKey": str(wallet.pubkey()),
    }
    message_json = json.dumps(message_data, separators=(',', ':'))
    signature = sign_message(wallet, message_json)
    payload = {
        "signature": signature,
        "wallet": str(wallet.pubkey()),
        "message": message_data,
    }
    try:
        response = requests.post(
            "https://api.rugcheck.xyz/auth/login/solana",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
        )
        if response.status_code == 200:
            response_data = response.json()
            return {"success": True, "data": response_data}
        else:
            return {"success": False, "status_code": response.status_code, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
