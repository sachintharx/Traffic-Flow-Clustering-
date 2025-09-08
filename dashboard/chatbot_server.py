#!/usr/bin/env python3
"""
Standalone FastAPI Traffic Data Chatbot Server
Combines all functionality from chatbot_SDVN folder into a single file
"""
import os
import time
import pandas as pd
import requests
import re
import uvicorn
import html
from pathlib import Path
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# ==========================
# CONFIGURATION
# ==========================
class Settings:
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    WORKERS: int = int(os.getenv("WORKERS", 1))
    
    # Application Configuration
    API_KEY: str = os.getenv("GEMINI_API_KEY", "AIzaSyBlnlG-rcCIxAk307OoKNj5fSSkS08hoMM")
    MODEL: str = "gemini-2.0-flash"
    CSV_FILE: str = os.getenv("CSV_FILE", "data/road_segment_traffic_clusters.csv")
    REFRESH_INTERVAL: int = int(os.getenv("REFRESH_INTERVAL", 3600))
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def csv_path(self) -> str:
        return str(self.BASE_DIR / self.CSV_FILE)

settings = Settings()

# ==========================
# DATA LOADER
# ==========================
last_load_time = 0
data = None

def load_data():
    """Load traffic data with caching"""
    global last_load_time, data
    now = time.time()
    if data is None or (now - last_load_time) > settings.REFRESH_INTERVAL:
        try:
            data = pd.read_csv(settings.csv_path)
            last_load_time = now
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    return data

# ==========================
# QUERY ENGINE
# ==========================
def clean_html_response(response: str) -> str:
    """Clean HTML tags from the response to prevent display artifacts."""
    # Remove common HTML tags that might appear in responses
    cleaned = re.sub(r'</?div[^>]*>', '', response)  # Remove <div> and </div> tags
    cleaned = re.sub(r'</?span[^>]*>', '', cleaned)  # Remove <span> and </span> tags
    cleaned = re.sub(r'</?p[^>]*>', '', cleaned)     # Remove <p> and </p> tags
    cleaned = re.sub(r'</?br[^>]*>', '', cleaned)    # Remove <br> tags
    cleaned = re.sub(r'<[^>]+>', '', cleaned)        # Remove any remaining HTML tags
    return cleaned.strip()

def query_data(question: str, df: pd.DataFrame, max_rows=10):
    """
    Simple data querying - returns relevant rows based on question keywords
    """
    question_lower = question.lower()
    # Static mapping of cluster IDs to human-readable traffic levels
    cluster_mapping = {0: "Low Traffic", 1: "Medium Traffic", 2: "High Traffic"}
    
    # Check for specific segment mentions
    if any(segment in question_lower for segment in ['a0a1', 'a0b0', 'a1a0', 'b1c1']):
        # Extract segment names from question
        segments = [seg for seg in df['segment'].str.lower() if seg in question_lower]
        if segments:
            filtered_df = df[df['segment'].str.lower().isin(segments)]
            if not filtered_df.empty:
                return filtered_df.to_string()
    
    # Check for traffic level queries
    if 'high traffic' in question_lower or 'highest' in question_lower:
        return df[df['category'] == 'High Traffic'].head(max_rows).to_string()
    elif 'low traffic' in question_lower or 'lowest' in question_lower:
        return df[df['category'] == 'Low Traffic'].head(max_rows).to_string()
    elif 'medium traffic' in question_lower:
        return df[df['category'] == 'Medium Traffic'].head(max_rows).to_string()
    
    # Check for cluster queries
    if 'cluster' in question_lower:
        try:
            # Extract cluster number from question
            cluster_nums = re.findall(r'cluster\s*(\d+)', question_lower)
            if cluster_nums:
                cluster_id = int(cluster_nums[0])
                filtered_df = df[df['cluster_id'] == cluster_id]
                if not filtered_df.empty:
                    header = [
                        "Cluster Analysis:",
                        f"Cluster {cluster_id} corresponds to {cluster_mapping.get(cluster_id, 'Unknown')}.",
                        "Cluster -> Traffic Level Mapping:",
                        "0: Low Traffic | 1: Medium Traffic | 2: High Traffic",
                        "",  # blank line
                    ]
                    return "\n".join(header) + filtered_df.head(max_rows).to_string()
            else:
                # General cluster overview request
                cluster_overview = []
                for cid, level in cluster_mapping.items():
                    count = (df['cluster_id'] == cid).sum()
                    avg = df.loc[df['cluster_id'] == cid, 'avg_raw_traffic'].mean()
                    cluster_overview.append(f"Cluster {cid} ({level}) -> segments: {count}, avg traffic: {avg:.2f}")
                overview_text = "Cluster -> Traffic Level Mapping:\n0: Low Traffic | 1: Medium Traffic | 2: High Traffic\n\n" + "\n".join(cluster_overview)
                return overview_text
        except:
            pass
    
    # Default: return summary statistics and top segments
    summary = f"""
    Dataset Summary:
    Total segments: {len(df)}
    Traffic categories: {df['category'].value_counts().to_dict()}
    Clusters: {sorted(df['cluster_id'].unique())}
    Cluster -> Traffic Level Mapping: 0: Low Traffic | 1: Medium Traffic | 2: High Traffic
    
    Top 5 highest traffic segments:
    {df.nlargest(5, 'avg_raw_traffic')[['segment', 'avg_raw_traffic', 'category']].to_string()}
    """
    return summary

# ==========================
# GEMINI API CALL
# ==========================
def ask_gemini(question: str, context: str):
    """Call Gemini API for traffic data analysis"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.MODEL}:generateContent?key={settings.API_KEY}"

    prompt = f"""
    You are a traffic data assistant for road segment analysis.
    Answer the question ONLY using this CSV data context:
    {context}

    Important: Use the following fixed mapping from cluster IDs to traffic levels:
    Cluster 0 = Low Traffic
    Cluster 1 = Medium Traffic
    Cluster 2 = High Traffic

    Guidelines:
    - Be specific and provide numerical data when available
    - Mention segment names, traffic values, and categories
    - If asked about trends, compare different segments or clusters
    - Keep responses concise but informative
    - If the data doesn't contain enough information, say so clearly

    Question: {question}
    """

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            return f"API Error: {response.status_code} - {response.text}"

        data = response.json()
        ai_response = data["candidates"][0]["content"]["parts"][0]["text"]
        return clean_html_response(ai_response)
    except requests.exceptions.RequestException as e:
        return f"Network error: {str(e)}"
    except Exception as e:
        return f"Error processing response: {str(e)}"

# ==========================
# PYDANTIC MODELS
# ==========================
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    status: str = "success"

# ==========================
# FASTAPI APP
# ==========================
app = FastAPI(
    title="Traffic Data Chatbot",
    description="AI-powered chatbot for traffic data analysis",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# API ENDPOINTS
# ==========================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Simple HTML interface for the chatbot"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Traffic Data Chatbot</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f8f9fa; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .chat-box { border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 8px; background: #fff; }
            .input-container { display: flex; gap: 10px; align-items: center; margin: 15px 0; }
            input[type="text"] { 
                flex: 1; 
                padding: 12px 15px; 
                border: 2px solid #e9ecef; 
                border-radius: 25px; 
                font-size: 16px;
                outline: none;
                transition: border-color 0.3s;
            }
            input[type="text"]:focus { border-color: #007bff; }
            button { 
                padding: 12px 25px; 
                background: #007bff; 
                color: white; 
                border: none; 
                border-radius: 25px; 
                cursor: pointer; 
                font-size: 16px;
                transition: background-color 0.3s;
                min-width: 80px;
            }
            button:hover { background: #0056b3; }
            button:disabled { background: #6c757d; cursor: not-allowed; }
            .response { 
                background: #f8f9fa; 
                padding: 20px; 
                margin: 15px 0; 
                border-radius: 8px; 
                white-space: pre-wrap; 
                border-left: 4px solid #007bff;
                min-height: 50px;
            }
            .thinking { color: #6c757d; font-style: italic; }
            .title { color: #007bff; text-align: center; margin-bottom: 10px; }
            .subtitle { color: #6c757d; text-align: center; margin-bottom: 30px; }
            .examples { background: #e7f3ff; padding: 15px; border-radius: 8px; margin: 20px 0; }
            .examples h3 { margin-top: 0; color: #007bff; }
            .examples li { margin: 5px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="title">🚦 Traffic Data Chatbot</h1>
            <p class="subtitle">Ask questions about traffic data, road segments, clusters, and patterns.</p>
            
            <div class="chat-box">
                <div class="input-container">
                    <input type="text" id="questionInput" placeholder="e.g., Which segments have the highest traffic?" />
                    <button onclick="askQuestion()" id="sendButton">Send</button>
                </div>
                <div id="response" class="response" style="display:none;"></div>
            </div>
            
            <div class="examples">
                <h3>💡 Example Questions:</h3>
                <ul>
                    <li>"Which segments have the highest traffic?"</li>
                    <li>"Tell me about cluster 2"</li>
                    <li>"What are the traffic patterns?"</li>
                    <li>"Show me low traffic segments"</li>
                    <li>"Compare traffic between clusters"</li>
                    <li>"What's the average traffic in each category?"</li>
                </ul>
            </div>
            
            <p><strong>🔗 API Endpoints:</strong></p>
            <ul>
                <li><a href="/docs">📚 Interactive API Documentation</a></li>
                <li><a href="/health">❤️ Health Check</a></li>
            </ul>
        </div>
        
        <script>
            async function askQuestion() {
                const questionInput = document.getElementById('questionInput');
                const question = questionInput.value.trim();
                const responseDiv = document.getElementById('response');
                const sendButton = document.getElementById('sendButton');
                
                if (!question) {
                    alert('Please enter a question');
                    questionInput.focus();
                    return;
                }
                
                // Disable button and show thinking state
                sendButton.disabled = true;
                sendButton.textContent = '...';
                responseDiv.style.display = 'block';
                responseDiv.innerHTML = '<span class="thinking">🤖 Thinking...</span>';
                responseDiv.scrollIntoView({ behavior: 'smooth' });
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ question: question })
                    });
                    
                    const data = await response.json();
                    responseDiv.innerHTML = data.answer.replace(/&lt;/g, '<').replace(/&gt;/g, '>');
                    
                    // Clear input field after successful response
                    questionInput.value = '';
                    
                } catch (error) {
                    responseDiv.innerHTML = '❌ Error: ' + error.message;
                } finally {
                    // Re-enable button
                    sendButton.disabled = false;
                    sendButton.textContent = 'Send';
                    questionInput.focus();
                }
            }
            
            // Handle Enter key press
            document.getElementById('questionInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    askQuestion();
                }
            });
            
            // Focus on input when page loads
            window.addEventListener('load', function() {
                document.getElementById('questionInput').focus();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    df = load_data()
    return {
        "status": "healthy",
        "data_loaded": df is not None,
        "total_segments": len(df) if df is not None else 0,
        "api_configured": bool(settings.API_KEY and settings.API_KEY != "YOUR_API_KEY_HERE")
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint"""
    try:
        # Handle greetings
        greetings_pattern = r"\b(?:hi|hello|hey|greetings|good\s+morning|good\s+afternoon|good\s+evening)\b"
        if re.search(greetings_pattern, request.question.lower()):
            return ChatResponse(
                answer="Hello! I'm your traffic data assistant. I can help you analyze road segment traffic data, explain patterns in different clusters, and answer questions about traffic levels. What would you like to know?"
            )
        
        # Load data
        df = load_data()
        if df is None:
            return ChatResponse(
                answer="Sorry, I'm having trouble accessing the traffic data. Please try again later.",
                status="error"
            )
        
        # Get context and generate response
        context = query_data(request.question, df)
        answer = ask_gemini(request.question, context)
        
        # If API call fails, return the data context directly
        if "API Error" in answer or "Network error" in answer or "Error:" in answer:
            answer = f"📊 **Traffic Data Analysis:**\n\n{context}\n\n*Note: AI service unavailable, showing raw data analysis.*"
        
        return ChatResponse(answer=answer)
        
    except Exception as e:
        return ChatResponse(
            answer=f"Sorry, I encountered an error: {str(e)}. Please try rephrasing your question.",
            status="error"
        )

@app.get("/chat")
async def chat_get(question: str = Query(..., description="Question about traffic data")):
    """GET endpoint for simple chat queries"""
    request = ChatRequest(question=question)
    response = await chat_endpoint(request)
    return response

# ==========================
# SERVER RUNNER
# ==========================
if __name__ == "__main__":
    print("🚀 Starting Traffic Data Chatbot Server...")
    print(f"📍 Server will be available at: http://localhost:{settings.PORT}")
    print(f"🔧 Workers: {settings.WORKERS}")
    print(f"📁 Working directory: {settings.BASE_DIR}")
    print(f"📊 Data file: {settings.csv_path}")
    
    # Start the server
    uvicorn.run(
        "chatbot_server:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        log_level="info",
        access_log=True,
        reload=False
    )
