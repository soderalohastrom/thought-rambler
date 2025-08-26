#!/bin/bash

# Backend Setup Script for Thought Ramble Parser

echo "Setting up Thought Ramble Parser Backend..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "Downloading spaCy English model..."
python -m spacy download en_core_web_sm

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please update .env file with your API keys"
fi

echo "Backend setup complete!"
echo "To start the server, run: uvicorn app:app --reload --host 0.0.0.0 --port 8000"
