#  AI Code Review & Rewrite Agent

> Intelligent code review and automated code refactoring powered by Groq + Llama 3.3 70B

## Overview

An AI-powered web application that reviews your code for bugs, performance issues, security vulnerabilities, and best practices—and then **automatically rewrites it** to fix all identified issues. Perfect for developers who want instant feedback without waiting for code review cycles.

## Features

###### Code Review
- 🔍 **Multi-language support**: Python, JavaScript, TypeScript, Java, C++, Go, Rust, PHP
- 🎯 **Customizable focus areas**: Bugs, Performance, Security, Best Practices
- 📊 **Severity breakdown**: Categorizes issues into Critical, High, Medium, and Low priority
- 💡 **Actionable suggestions**: Provides specific, line-by-line improvements with examples
- ⚡ **Lightning-fast analysis**: Real-time reviews using Groq's ultra-fast LLM inference

### Code Rewriting
- ✨ **Automatic fixes**: Rewrites code to address all identified issues
- 🔧 **Production-ready**: Generated code is clean, well-commented, and follows best practices
- 📋 **Detailed explanations**: Explains exactly what changed and why
- 🎯 **Key improvements list**: Highlights specific enhancements made
- 📋 **Copy-ready**: One-click copy for rewritten code

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Groq API** - Ultra-fast LLM inference (Llama 3.3 70B)
- **Python** - Backend logic and parsing

### Frontend
- **HTML5 + Tailwind CSS** - Responsive, beautiful UI
- **Vanilla JavaScript** - Interactive features
- **Marked.js** - Markdown rendering
- **Highlight.js** - Code syntax highlighting

## Installation

### Prerequisites
- Python 3.8+
- Groq API Key (free tier available at https://console.groq.com)

### Setup

1. **Clone the repository**

2. **Create virtual environment**

3. **Install dependencies**

4. **Set up environment variables**

5. **Run the server**

6. **Access the app**
Open http://localhost:8000 in your browser

## Usage

### Review Code
1. Paste your code into the editor
2. Select programming language
3. Choose focus areas (bugs, performance, security, best practices)
4. Click "🚀 Review Code"
5. View severity breakdown and detailed feedback

### Rewrite Code
1. After reviewing code, click "✨ Fix & Rewrite"
2. AI automatically refactors the code
3. See side-by-side comparison in "Rewritten Code" tab
4. Copy the improved code with one click

## Example Use Cases

- 🎓 **Learning**: Understand code improvements and best practices
- 🔍 **Code Quality**: Catch bugs and security issues before production
- ⚡ **Performance**: Optimize slow algorithms automatically
- 🚀 **Onboarding**: Help junior developers improve their code
- 📚 **Knowledge Sharing**: Learn from AI-generated improvements

## API Endpoints

### POST `/api/review`
Reviews code and returns detailed feedback with severity breakdown

### POST `/api/rewrite`
Rewrites code to fix all issues identified in review

### GET `/api/models`
Lists available LLM models for code review

## Performance

- ⚡ **Average review time**: 2-5 seconds
- 🔄 **Rewrite time**: 3-7 seconds
- 💰 **Cost**: Free (uses Groq's free tier API)
- 🌐 **Works offline**: After initialization

## Browser Support

- Chrome/Chromium ✅
- Firefox ✅
- Safari ✅
- Edge ✅

## Roadmap

- [ ] GitHub integration for PR reviews
- [ ] VS Code extension
- [ ] Support for more languages (Kotlin, Swift, Ruby)
- [ ] Team collaboration features
- [ ] Custom rules and linting preferences
- [ ] Export reports (PDF, JSON)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Author

Built with ❤️ using Groq + Llama 3.3

---

**Star this project if you find it helpful!** ⭐
