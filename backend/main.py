from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Load environment variables
load_dotenv()
app = FastAPI(title="AI Code Review Agent")

app = FastAPI(title="AI Code Review Agent")

@app.get("/favicon.ico")
async def favicon():
    return {}

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize Groq client
api_key = os.getenv("GROQ_API_KEY")
print(f"✅ GROQ_API_KEY loaded: {bool(api_key)}")

client = Groq(api_key=api_key)

class CodeReviewRequest(BaseModel):
    code: str
    language: str
    focus_areas: list[str] = ["bugs", "performance", "security", "best_practices"]


class CodeReviewResponse(BaseModel):
    review: str
    issues_found: int
    severity_breakdown: dict
    suggestions: list[dict]


class CodeRewriteRequest(BaseModel):
    code: str
    language: str
    review: str


class CodeRewriteResponse(BaseModel):
    original_code: str
    rewritten_code: str
    explanation: str
    improvements: list[str]


def parse_review_response(review_text: str) -> dict:
    """Parse the LLM response to extract structured data"""
    
    critical_section = re.search(r'### 🔴 Critical Issues.*?(?=###|\Z)', review_text, re.DOTALL)
    high_section = re.search(r'### 🟠 High Priority.*?(?=###|\Z)', review_text, re.DOTALL)
    medium_section = re.search(r'### 🟡 Medium Priority.*?(?=###|\Z)', review_text, re.DOTALL)
    low_section = re.search(r'### 🟢 Low Priority.*?(?=###|\Z)', review_text, re.DOTALL)
    
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0
    
    if critical_section:
        critical_text = critical_section.group(0)
        critical_count = len(re.findall(r'^\s*[-*]\s', critical_text, re.MULTILINE))
        if critical_count == 0:
            critical_count = len([p for p in critical_text.split('\n') if p.strip() and not p.strip().startswith('#')])
    
    if high_section:
        high_text = high_section.group(0)
        high_count = len(re.findall(r'^\s*[-*]\s', high_text, re.MULTILINE))
        if high_count == 0:
            high_count = len([p for p in high_text.split('\n') if p.strip() and not p.strip().startswith('#')])
    
    if medium_section:
        medium_text = medium_section.group(0)
        medium_count = len(re.findall(r'^\s*[-*]\s', medium_text, re.MULTILINE))
        if medium_count == 0:
            medium_count = len([p for p in medium_text.split('\n') if p.strip() and not p.strip().startswith('#')])
    
    if low_section:
        low_text = low_section.group(0)
        low_count = len(re.findall(r'^\s*[-*]\s', low_text, re.MULTILINE))
        if low_count == 0:
            low_count = len([p for p in low_text.split('\n') if p.strip() and not p.strip().startswith('#')])
    
    severity_breakdown = {
        "critical": max(critical_count, 1) if critical_section else 0,
        "high": max(high_count, 1) if high_section else 0,
        "medium": max(medium_count, 1) if medium_section else 0,
        "low": max(low_count, 1) if low_section else 0
    }
    
    suggestions = []
    suggestion_section = re.search(r'## 🔧 Suggested Improvements.*?(?=##|\Z)', review_text, re.DOTALL)
    
    if suggestion_section:
        suggestion_text = suggestion_section.group(0)
        suggestion_items = re.split(r'^\s*\d+\.\s|^\s*[-*]\s', suggestion_text, flags=re.MULTILINE)
        
        for item in suggestion_items[1:]:
            item_clean = item.strip()
            if len(item_clean) > 20:
                description = item_clean[:200] + "..." if len(item_clean) > 200 else item_clean
                suggestions.append({"description": description})
    
    total_issues = severity_breakdown["critical"] + severity_breakdown["high"] + severity_breakdown["medium"] + severity_breakdown["low"]
    
    return {
        "issues_found": total_issues,
        "severity_breakdown": severity_breakdown,
        "suggestions": suggestions[:10]
    }




# ==================== LOGIN ROUTES (NEW) ====================


@app.get("/", response_class=HTMLResponse)
async def serve_login():
    """Serve login page"""
    try:
        with open(os.path.join(FRONTEND_DIR, "login.html"), "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>❌ login.html not found</h1>")



@app.get("/app", response_class=HTMLResponse)
async def serve_tool():
    """Serve the tool page after login"""
    try:
        with open(os.path.join(FRONTEND_DIR, "index.html"), "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>❌ index.html not found</h1>")


# ============================================================




@app.post("/api/review", response_model=CodeReviewResponse)
async def review_code(request: CodeReviewRequest):
    """Review code and provide suggestions using Groq API"""
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    
    focus_str = ", ".join(request.focus_areas)
    
    # Properly format the prompt with the code - FIX: Include the actual code with triple backticks
    prompt = f"""You are an expert code reviewer with 15+ years of experience. Analyze this {request.language} code and provide a detailed review.

Focus on: {focus_str}

Code to review:
```{request.language}
{request.code}
```

Provide your review in this format:

## 🎯 Overall Assessment
[Brief summary of code quality]

## 🔍 Issues Found

### 🔴 Critical Issues (Must Fix)
- [List each critical bug or security vulnerability as separate bullet point]
- [Another critical issue if exists]

### 🟠 High Priority
- [List high priority items as separate bullet points]
- [Another high priority item if exists]

### 🟡 Medium Priority
- [List medium priority items as separate bullet points]
- [Another medium priority item if exists]

### 🟢 Low Priority
- [List low priority items as separate bullet points]
- [Another low priority item if exists]

## ✅ Strengths
[What's done well]

## 🔧 Suggested Improvements
1. [Specific suggestion 1]
2. [Specific suggestion 2]
3. [Specific suggestion 3]

Be specific, cite line numbers when relevant, and provide code snippets for fixes."""



    try:
        print(f"\n{'='*60}")
        print(f"📝 CODE REVIEW REQUEST")
        print(f"{'='*60}")
        print(f"Language: {request.language}")
        print(f"Code length: {len(request.code)} chars")
        print(f"Code preview: {request.code[:100]}...")
        print(f"Focus areas: {focus_str}")
        print(f"Calling Groq API...")
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior software engineer specialized in code review. Provide detailed, actionable feedback. Always use bullet points (-) for each issue in the severity sections. You MUST analyze the provided code."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=2000,
            top_p=0.9
        )
        
        review_text = chat_completion.choices[0].message.content
        print(f"✅ Review generated successfully!")
        print(f"Review length: {len(review_text)} chars")
        print(f"{'='*60}\n")
        
        parsed_data = parse_review_response(review_text)
        
        return CodeReviewResponse(
            review=review_text,
            issues_found=parsed_data["issues_found"],
            severity_breakdown=parsed_data["severity_breakdown"],
            suggestions=parsed_data["suggestions"]
        )
        
    except Exception as e:
        print(f"\n❌ ERROR in review_code:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        raise HTTPException(status_code=500, detail=f"Error during code review: {str(e)}")





@app.post("/api/rewrite", response_model=CodeRewriteResponse)
async def rewrite_code(request: CodeRewriteRequest):
    """Rewrite code to fix issues and improve quality"""
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    
    # FIX: Include the actual code with triple backticks
    prompt = f"""You are an expert {request.language} developer. Rewrite this code to fix all issues, improve performance, security, and follow best practices.

Original Code:
```{request.language}
{request.code}
```

Previous Review:
{request.review}

Provide your response in this exact format:

## ✨ Rewritten Code
```{request.language}
[Your rewritten code here]
```

## 📝 Explanation
[Explain what you changed and why, in 2-3 sentences]

## 🎯 Key Improvements
- Improvement 1: [Detail]
- Improvement 2: [Detail]
- Improvement 3: [Detail]
- Improvement 4: [Detail]

Make sure the rewritten code is production-ready, well-commented, and addresses all the issues mentioned in the review."""



    try:
        print(f"\n{'='*60}")
        print(f"🔧 CODE REWRITE REQUEST")
        print(f"{'='*60}")
        print(f"Language: {request.language}")
        print(f"Calling Groq API for rewrite...")
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert software developer. Rewrite code to be production-ready, fixing all issues, improving performance, security, and maintainability. Always wrap the rewritten code in triple backticks with the language identifier."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=2000,
            top_p=0.9
        )
        
        rewrite_text = chat_completion.choices[0].message.content
        print(f"✅ Rewrite generated successfully!")
        print(f"Response length: {len(rewrite_text)} chars")
        
        # Extract rewritten code - try multiple patterns
        rewritten_code = None
        
        # Try pattern 1: ```language\n code \n```
        code_match = re.search(r'```[\w]*\n(.*?)\n```', rewrite_text, re.DOTALL)
        if code_match:
            rewritten_code = code_match.group(1).strip()
            print(f"DEBUG: Extracted code using pattern 1 (language-specific)")
        
        # Try pattern 2: ``` code ```
        if not rewritten_code:
            code_match = re.search(r'```\n(.*?)\n```', rewrite_text, re.DOTALL)
            if code_match:
                rewritten_code = code_match.group(1).strip()
                print(f"DEBUG: Extracted code using pattern 2 (generic)")
        
        # Try pattern 3: Look for code between specific markers
        if not rewritten_code:
            code_match = re.search(r'## ✨ Rewritten Code\n```[\w]*\n(.*?)\n```', rewrite_text, re.DOTALL)
            if code_match:
                rewritten_code = code_match.group(1).strip()
                print(f"DEBUG: Extracted code using pattern 3 (with header)")
        
        # If still not found, extract the largest code block
        if not rewritten_code:
            all_code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', rewrite_text, re.DOTALL)
            if all_code_blocks:
                rewritten_code = max(all_code_blocks, key=len).strip()
                print(f"DEBUG: Extracted code using pattern 4 (largest block)")
        
        # Fallback
        if not rewritten_code:
            rewritten_code = "# Could not extract rewritten code. Here's the full response:\n\n" + rewrite_text
            print(f"DEBUG: Using fallback - could not extract code")
        
        print(f"DEBUG: Final code length: {len(rewritten_code)} chars")
        print(f"{'='*60}\n")
        
        # Extract explanation
        explanation_match = re.search(r'## 📝 Explanation\n(.*?)(?=##|\Z)', rewrite_text, re.DOTALL)
        explanation = explanation_match.group(1).strip() if explanation_match else "Code has been rewritten with improvements."
        
        # Extract improvements
        improvements = []
        improvements_match = re.search(r'## 🎯 Key Improvements\n(.*?)(?=##|\Z)', rewrite_text, re.DOTALL)
        if improvements_match:
            improvements_text = improvements_match.group(1)
            improvement_items = re.findall(r'- (.*?)(?:\n|$)', improvements_text)
            improvements = [item.strip() for item in improvement_items if item.strip()][:5]
        
        if not improvements:
            improvements = ["Code refactored for better quality", "Error handling improved", "Performance optimized", "Best practices applied"]
        
        return CodeRewriteResponse(
            original_code=request.code,
            rewritten_code=rewritten_code,
            explanation=explanation,
            improvements=improvements
        )
        
    except Exception as e:
        print(f"\n❌ ERROR in rewrite_code:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        raise HTTPException(status_code=500, detail=f"Error during code rewrite: {str(e)}")




@app.get("/api/models")
async def get_available_models():
    """Get list of available Groq models for code review"""
    return {
        "models": [
            {
                "id": "llama-3.3-70b-versatile",
                "name": "Llama 3.3 70B Versatile",
                "description": "Best for code review & rewrite (Recommended)",
                "speed": "Very Fast",
                "recommended": True
            },
            {
                "id": "mixtral-8x7b-32768",
                "name": "Mixtral 8x7B",
                "description": "Great for code analysis",
                "speed": "Very Fast",
                "recommended": False
            },
            {
                "id": "llama-3.1-8b-instant",
                "name": "Llama 3.1 8B Instant",
                "description": "Fastest option",
                "speed": "Ultra Fast",
                "recommended": False
            }
        ]
    }




@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "api_key_set": bool(os.getenv("GROQ_API_KEY"))}




if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🤖 AI Code Review & Rewrite Agent")
    print("="*60)
    print("✅ Login Page: http://localhost:8000")
    print("✅ Tool Page: http://localhost:8000/app")
    print("="*60 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)



