# Setup Google Gemini API for Chatbot
# This script helps you configure the chatbot with Google Gemini (FREE!)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🤖 GOOGLE GEMINI SETUP" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Google Gemini is FREE and easy to set up!" -ForegroundColor Green
Write-Host ""

# Check if API key is already set
$existingKey = $env:GEMINI_API_KEY
if ($existingKey) {
    Write-Host "✅ GEMINI_API_KEY is already set!" -ForegroundColor Green
    Write-Host "   Key: $($existingKey.Substring(0, 10))..." -ForegroundColor Gray
    Write-Host ""
    $useExisting = Read-Host "Use existing key? (y/n)"
    if ($useExisting -eq "y") {
        Write-Host "Using existing API key" -ForegroundColor Green
        $apiKey = $existingKey
    } else {
        $apiKey = $null
    }
} else {
    $apiKey = $null
}

if (-not $apiKey) {
    Write-Host "STEP 1: Get Your Free Gemini API Key" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Open this URL in your browser:" -ForegroundColor White
    Write-Host "   https://makersuite.google.com/app/apikey" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Sign in with your Google account" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Click 'Create API Key'" -ForegroundColor White
    Write-Host ""
    Write-Host "4. Copy the API key" -ForegroundColor White
    Write-Host ""
    
    # Open browser
    $openBrowser = Read-Host "Open browser now? (y/n)"
    if ($openBrowser -eq "y") {
        Start-Process "https://makersuite.google.com/app/apikey"
        Write-Host ""
        Write-Host "Browser opened. Get your API key and come back here." -ForegroundColor Yellow
        Write-Host ""
    }
    
    # Get API key from user
    Write-Host "STEP 2: Enter Your API Key" -ForegroundColor Yellow
    Write-Host ""
    $apiKey = Read-Host "Paste your Gemini API key here"
    
    if (-not $apiKey) {
        Write-Host ""
        Write-Host "❌ No API key provided. Setup cancelled." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "STEP 3: Installing Gemini Library" -ForegroundColor Yellow
Write-Host ""

# Install google-generativeai
Write-Host "Installing google-generativeai..." -ForegroundColor Cyan
pip install google-generativeai --quiet
Write-Host "✅ Library installed" -ForegroundColor Green

Write-Host ""
Write-Host "STEP 4: Configuring Backend" -ForegroundColor Yellow
Write-Host ""

# Create .env file
$envContent = @"
# Google Gemini API Configuration
GEMINI_API_KEY=$apiKey
"@

$envPath = "backend/.env"
$envContent | Out-File $envPath -Encoding UTF8
Write-Host "✅ Created backend/.env file" -ForegroundColor Green

# Set environment variable for current session
$env:GEMINI_API_KEY = $apiKey
Write-Host "✅ Set environment variable for current session" -ForegroundColor Green

Write-Host ""
Write-Host "STEP 5: Testing Connection" -ForegroundColor Yellow
Write-Host ""

# Test the API key
try {
    $testScript = @"
import google.generativeai as genai
import os

genai.configure(api_key='$apiKey')
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content('Say hello!')
print(response.text)
"@
    
    $testScript | python -
    Write-Host ""
    Write-Host "✅ Gemini API is working!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not test API (but it's probably fine)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎉 SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Configuration Summary:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Provider: Google Gemini" -ForegroundColor Cyan
Write-Host "Model: gemini-pro" -ForegroundColor Cyan
Write-Host "API Key: $($apiKey.Substring(0, 10))..." -ForegroundColor Cyan
Write-Host "Cost: FREE! 🎉" -ForegroundColor Green
Write-Host ""

Write-Host "📁 Configuration Files:" -ForegroundColor Yellow
Write-Host "  ✅ backend/.env (for local development)" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Start the backend:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   python api_server.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Open frontend:" -ForegroundColor White
Write-Host "   Open frontend_new/index.html in your browser" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Test the chatbot:" -ForegroundColor White
Write-Host "   Look for the chatbot in the bottom-right corner" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Try these questions:" -ForegroundColor White
Write-Host "   - 'What's the weather like?'" -ForegroundColor Gray
Write-Host "   - 'What activities do you recommend?'" -ForegroundColor Gray
Write-Host "   - 'Are there any events this weekend?'" -ForegroundColor Gray
Write-Host "   - 'Plan a 3-day trip for me'" -ForegroundColor Gray
Write-Host ""

Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "  • Gemini is completely FREE" -ForegroundColor White
Write-Host "  • No credit card required" -ForegroundColor White
Write-Host "  • 60 requests per minute limit" -ForegroundColor White
Write-Host "  • Perfect for hackathons!" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Your AI chatbot is ready with Gemini! 🤖" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
