# Solana Backend API

A FastAPI-based backend service for Solana blockchain operations including wallet generation and rug checking functionality.

## Features

- 🔐 **Wallet Generation**: Generate new Solana keypairs with public/private key pairs
- 🔍 **Rug Check**: Analyze Solana tokens for potential rug pull indicators
- ⚡ **Fast API**: Built with FastAPI for high performance and automatic API documentation
- 🐍 **Modern Python**: Uses UV for fast package management and Python 3.12+

## Prerequisites

- Python 3.12 or higher
- [UV](https://github.com/astral-sh/uv) package manager

## Installation

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd backend
```

2. **Install dependencies using UV:**
```bash
uv sync
```

3. **Set up environment variables (optional):**
```bash
# Create .env file
echo "RUGCHECK_API_KEY=your_api_key_here" > .env
echo "SOLANA_PRIVATE_KEY=your_private_key_here" >> .env
```

4. **Activate the virtual environment (optional):**
```bash
uv venv
# On Windows: .venv\Scripts\activate
# On Unix: source .venv/bin/activate
```

## Running the Application

### Development Mode (with hot reload)
```bash
uv run uvicorn main:app --reload
```

### Production Mode
```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`

## API Endpoints

### `GET /`
Health check endpoint that returns a welcome message.

**Response:**
```json
{
  "message": "Hello from backend!"
}
```

### `GET /generate_wallet`
Generates a new Solana wallet with public and private keys.

**Response:**
```json
{
  "public_key": "11111111111111111111111111111112",
  "private_key": "base58_encoded_private_key"
}
```

### `GET /rug_check`
Analyzes a Solana token for potential rug pull indicators.

**Parameters:**
- `public_key` (string): The public key to analyze
- `private_key` (string): The private key for authentication

**Response:**
```json
{
  "message": "Rug check!"
}
```

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications
- **Solders**: Python bindings for Solana's Rust libraries
- **Base58**: Base58 encoding/decoding for Solana addresses
- **Agentipy**: Additional utilities for blockchain operations

## Project Structure

```
backend/
├── main.py              # Main FastAPI application
├── pyproject.toml       # Project configuration and dependencies
├── README.md           # This file
├── .python-version     # Python version specification
├── .gitignore          # Git ignore rules
└── .venv/              # Virtual environment (created after uv venv)
```

## Development

### Adding New Dependencies
```bash
uv add <package-name>
```

### Adding Development Dependencies
```bash
uv add --dev <package-name>
```

### Running Tests
```bash
uv run pytest
```

## Security Notes

⚠️ **Important**: Never expose private keys in production environments. The current implementation is for development/testing purposes only.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license information here]
