#!/bin/bash
# Quick setup for Meme Culture Radar
echo "🎭 Setting up Meme Culture Radar..."

# Clone Bitget Wallet Skill (dependency)
if [ ! -d "bitget-wallet-skill" ]; then
    echo "📦 Cloning Bitget Wallet Skill..."
    git clone https://github.com/bitget-wallet-ai-lab/bitget-wallet-skill.git
fi

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install requests

echo "✅ Setup complete! Run: python3 radar.py --help"
