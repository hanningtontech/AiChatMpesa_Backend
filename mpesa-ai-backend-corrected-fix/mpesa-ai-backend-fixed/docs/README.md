# Mpesa Agent Documentation

Welcome to the Mpesa Agent documentation! This directory contains comprehensive guides and examples for using the Mpesa AI Agent FastAPI server.

## 📚 Documentation Index

### 🚀 Getting Started
- **[API Examples](api_examples.md)** - Complete API usage examples and endpoints
- **[CLI Demo](cli_demo.md)** - Beautiful CLI interface demonstration

### 🔧 Setup & Configuration
- **[Docker Setup](README-Docker.md)** - Docker deployment instructions
- **[Ngrok Setup](NGROK_SETUP.md)** - Setting up Ngrok for callback URLs

### 💰 M-Pesa Integration
- **[Callback Integration](CALLBACK_INTEGRATION.md)** - M-Pesa callback handling setup
- **[Frictionless Payments](FRICTIONLESS_PAYMENTS.md)** - Real-time payment processing

## 🎯 Quick Start

### CLI Mode
```bash
python app/main.py cli
```

### Server Mode
```bash
python app/main.py
```

### API Endpoints
- **Health Check**: `GET /health`
- **Create Session**: `POST /sessions`
- **List Sessions**: `GET /sessions`
- **Run Agent**: `POST /run`

## 🏗️ Architecture

The Mpesa Agent consists of:

1. **FastAPI Server** - REST API for session management and agent interaction
2. **CLI Interface** - Beautiful command-line interface for direct interaction
3. **SQLite Database** - Simple session persistence
4. **M-Pesa Integration** - Real-time payment processing with callback support
5. **Google ADK Agent** - AI-powered conversation handling

## 🔗 Related Files

- **Main Application**: `../app/main.py`
- **Agent Implementation**: `../app/mpesa_agent/agent.py`
- **M-Pesa Tools**: `../app/mpesa_agent/mpesa_tools.py`
- **Requirements**: `../requirements.txt`

## 📞 Support

For issues or questions, please refer to the specific documentation files or check the main README in the project root.
