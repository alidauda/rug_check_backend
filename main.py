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
        return {"succ ess": False, "error": str(e)}

@app.get("/parse_report")
async def parse_report():
    """Parse the report.json file and return structured analysis"""
    try:
        with open("report.json", "r") as f:
            data = json.load(f)
        
     
        analysis = {
            "token_info": {
                "name": data.get("tokenMeta", {}).get("name"),
                "symbol": data.get("tokenMeta", {}).get("symbol"),
                "mint": data.get("mint"),
                "creator": data.get("creator"),
                "supply": data.get("token", {}).get("supply"),
                "decimals": data.get("token", {}).get("decimals")
            },
            "risk_indicators": {
                "creator_balance": data.get("creatorBalance", 0),
                "top_holder_percentage": data.get("topHolders", [{}])[0].get("pct", 0) if data.get("topHolders") else 0,
                "total_holders": len(data.get("topHolders", [])),
                "insider_holders": len([h for h in data.get("topHolders", []) if h.get("insider", False)])
            },
            "top_holders": data.get("topHolders", [])[:10],  
            "rug_score": calculate_rug_score(data)
        }
        
        return analysis
    except Exception as e:
        return {"error": str(e), "message": "Error parsing report"}

def calculate_rug_score(data):
    """Calculate a simple rug score based on various factors"""
    score = 0
    reasons = []
    
    # Creator balance check
    creator_balance = data.get("creatorBalance", 0)
    if creator_balance > 1000000000:  # More than 1B tokens
        score += 30
        reasons.append("High creator balance")
    
    # Top holder concentration
    top_holders = data.get("topHolders", [])
    if top_holders:
        top_holder_pct = top_holders[0].get("pct", 0)
        if top_holder_pct > 20:
            score += 25
            reasons.append("High top holder concentration")
        elif top_holder_pct > 10:
            score += 15
            reasons.append("Moderate top holder concentration")
    
    # Insider holders
    insider_count = len([h for h in top_holders if h.get("insider", False)])
    if insider_count > 0:
        score += insider_count * 5
        reasons.append(f"{insider_count} insider holders detected")
    
    # Supply distribution
    total_supply = data.get("token", {}).get("supply", 0)
    if total_supply > 0:
        distributed_supply = sum(h.get("amount", 0) for h in top_holders[:10])
        distribution_ratio = distributed_supply / total_supply
        if distribution_ratio > 0.5:
            score += 20
            reasons.append("Poor supply distribution")
    
    return {
        "score": min(score, 100),
        "risk_level": "HIGH" if score > 70 else "MEDIUM" if score > 40 else "LOW",
        "reasons": reasons
    }

@app.get("/analyze_report")
async def analyze_report():
    """Detailed analysis of the report.json file with insights"""
    try:
        with open("report.json", "r") as f:
            data = json.load(f)
        
        # Deep analysis
        analysis = {
            "summary": {
                "token_name": data.get("tokenMeta", {}).get("name"),
                "token_symbol": data.get("tokenMeta", {}).get("symbol"),
                "total_supply": data.get("token", {}).get("supply"),
                "creator_balance": data.get("creatorBalance"),
                "holder_count": len(data.get("topHolders", []))
            },
            "concentration_analysis": analyze_concentration(data),
            "insider_analysis": analyze_insiders(data),
            "supply_analysis": analyze_supply_distribution(data),
            "recommendations": generate_recommendations(data)
        }
        
        return analysis
    except Exception as e:
        return {"error": str(e), "message": "Error analyzing report"}

def analyze_concentration(data):
    """Analyze token concentration among top holders"""
    top_holders = data.get("topHolders", [])
    if not top_holders:
        return {"error": "No holder data available"}
    
    total_concentration = sum(h.get("pct", 0) for h in top_holders[:10])
    return {
        "top_10_concentration": total_concentration,
        "top_holder_percentage": top_holders[0].get("pct", 0),
        "concentration_risk": "HIGH" if total_concentration > 50 else "MEDIUM" if total_concentration > 30 else "LOW",
        "holder_distribution": [{"rank": i+1, "percentage": h.get("pct", 0)} for i, h in enumerate(top_holders[:10])]
    }

def analyze_insiders(data):
    """Analyze insider holdings"""
    top_holders = data.get("topHolders", [])
    insiders = [h for h in top_holders if h.get("insider", False)]
    
    return {
        "insider_count": len(insiders),
        "insider_percentage": sum(h.get("pct", 0) for h in insiders),
        "insider_addresses": [h.get("address") for h in insiders],
        "risk_level": "HIGH" if len(insiders) > 3 else "MEDIUM" if len(insiders) > 0 else "LOW"
    }

def analyze_supply_distribution(data):
    """Analyze supply distribution patterns"""
    creator_balance = data.get("creatorBalance", 0)
    total_supply = data.get("token", {}).get("supply", 0)
    creator_percentage = (creator_balance / total_supply * 100) if total_supply > 0 else 0
    
    return {
        "creator_percentage": creator_percentage,
        "creator_balance": creator_balance,
        "total_supply": total_supply,
        "distribution_risk": "HIGH" if creator_percentage > 20 else "MEDIUM" if creator_percentage > 10 else "LOW"
    }

def generate_recommendations(data):
    """Generate recommendations based on analysis"""
    recommendations = []
    
    creator_balance = data.get("creatorBalance", 0)
    if creator_balance > 1000000000:
        recommendations.append("⚠️ High creator balance detected - potential dump risk")
    
    top_holders = data.get("topHolders", [])
    if top_holders and top_holders[0].get("pct", 0) > 20:
        recommendations.append("⚠️ High concentration in top holder - limited liquidity")
    
    insiders = [h for h in top_holders if h.get("insider", False)]
    if len(insiders) > 0:
        recommendations.append(f"⚠️ {len(insiders)} insider holders detected")
    
    if len(recommendations) == 0:
        recommendations.append("✅ Token appears to have healthy distribution")
    
    return recommendations

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
