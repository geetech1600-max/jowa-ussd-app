#!/bin/bash

# setup_git.sh - Initialize git repository for JOWA project

echo "🚀 Setting up Git repository for JOWA USSD App..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Initialize git repository
echo "📁 Initializing git repository..."
git init

# Add all files
echo "📦 Adding files to git..."
git add .

# Show what will be committed
echo "📋 Files to be committed:"
git status

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Complete JOWA USSD application

- Complete Flask USSD application with Africa's Talking integration
- PostgreSQL database with Supabase configuration  
- Modular structure with services, models, and utilities
- Comprehensive testing suite
- Production deployment configuration
- Environment configuration with secure credentials
- Database initialization scripts
- Docker support for containerization
- USSD job matching platform for Zambia"

echo "✅ Git repository initialized successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Create a repository on GitHub: https://github.com/new"
echo "2. Add remote origin: git remote add origin https://github.com/your-username/jowa-ussd-app.git"
echo "3. Push to GitHub: git push -u origin main"
echo ""
echo "🌐 To deploy to Render.com:"
echo "1. Push your code to GitHub"
echo "2. Connect your GitHub repo to Render.com"
echo "3. Set environment variables in Render dashboard"
echo "4. Deploy automatically"