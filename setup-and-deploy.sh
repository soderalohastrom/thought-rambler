#!/bin/bash

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Installing Vercel CLI..."
    npm install -g vercel
else
    echo "✅ Vercel CLI is already installed"
fi

# Initialize git repository
echo "Initializing git repository..."
git init

# Add all files
echo "Adding files to git..."
git add .

# Create initial commit
echo "Creating initial commit..."
git commit -m "Initial commit: Thought Ramble Parser - Ready for Vercel deployment"

# Check git status
echo "Git status:"
git status

echo ""
echo "🚀 Ready for Vercel deployment!"
echo "Next steps:"
echo "1. Push to GitHub: git remote add origin <your-repo-url> && git push -u origin main"
echo "2. Deploy to Vercel: vercel --prod"
echo ""
echo "Or deploy directly from local:"
echo "vercel --prod"