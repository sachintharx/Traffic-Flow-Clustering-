"""
Streamlit-compatible chatbot module for traffic data analysis
"""
import os
import time
import pandas as pd
import requests
import re
import html
import streamlit as st
from typing import Optional

class TrafficChatbot:
    def __init__(self, csv_path: str, api_key: Optional[str] = None):
        self.csv_path = csv_path
        self.api_key = api_key or "AIzaSyBlnlG-rcCIxAk307OoKNj5fSSkS08hoMM"
        self.model = "gemini-2.0-flash"
        self.last_load_time = 0
        self.data = None
        self.refresh_interval = 3600  # 1 hour
        
    def load_data(self):
        """Load traffic data with caching"""
        now = time.time()
        if self.data is None or (now - self.last_load_time) > self.refresh_interval:
            try:
                self.data = pd.read_csv(self.csv_path)
                self.last_load_time = now
            except Exception as e:
                st.error(f"Error loading data: {str(e)}")
                return None
        return self.data
    
    def clean_html_response(self, response: str) -> str:
        """Clean HTML tags from the response to prevent display artifacts."""
        # Remove common HTML tags that might appear in responses
        cleaned = re.sub(r'</?div[^>]*>', '', response)  # Remove <div> and </div> tags
        cleaned = re.sub(r'</?span[^>]*>', '', cleaned)  # Remove <span> and </span> tags
        cleaned = re.sub(r'</?p[^>]*>', '', cleaned)     # Remove <p> and </p> tags
        cleaned = re.sub(r'</?br[^>]*>', '', cleaned)    # Remove <br> tags
        cleaned = re.sub(r'<[^>]+>', '', cleaned)        # Remove any remaining HTML tags
        return cleaned.strip()
    
    def query_data(self, question: str, df: pd.DataFrame, max_rows=10):
        """
        Simple data querying - returns relevant rows based on question keywords
        """
        question_lower = question.lower()
        cluster_mapping = {0: "Low Traffic", 1: "Medium Traffic", 2: "High Traffic"}

        # Specific segment mentions
        if any(segment in question_lower for segment in ['a0a1', 'a0b0', 'a1a0', 'b1c1']):
            segments = [seg for seg in df['segment'].str.lower() if seg in question_lower]
            if segments:
                filtered_df = df[df['segment'].str.lower().isin(segments)]
                if not filtered_df.empty:
                    return filtered_df.to_string()

        # Traffic level queries
        if 'high traffic' in question_lower or 'highest' in question_lower:
            return df[df['category'] == 'High Traffic'].head(max_rows).to_string()
        if 'low traffic' in question_lower or 'lowest' in question_lower:
            return df[df['category'] == 'Low Traffic'].head(max_rows).to_string()
        if 'medium traffic' in question_lower:
            return df[df['category'] == 'Medium Traffic'].head(max_rows).to_string()

        # Cluster queries
        if 'cluster' in question_lower:
            try:
                cluster_nums = re.findall(r'cluster\s*(\d+)', question_lower)
                if cluster_nums:
                    cluster_id = int(cluster_nums[0])
                    filtered_df = df[df['cluster_id'] == cluster_id]
                    if not filtered_df.empty:
                        header_lines = [
                            "Cluster Analysis:",
                            f"Cluster {cluster_id} corresponds to {cluster_mapping.get(cluster_id, 'Unknown')}",
                            "Cluster -> Traffic Level Mapping:",
                            "0: Low Traffic | 1: Medium Traffic | 2: High Traffic",
                            "",
                        ]
                        return "\n".join(header_lines) + filtered_df.head(max_rows).to_string()
                # General cluster overview
                overview_rows = []
                for cid, level in cluster_mapping.items():
                    subset = df[df['cluster_id'] == cid]
                    if subset.empty:
                        continue
                    count = len(subset)
                    avg = subset['avg_raw_traffic'].mean()
                    overview_rows.append(f"Cluster {cid} ({level}) -> segments: {count}, avg traffic: {avg:.2f}")
                if overview_rows:
                    return "Cluster -> Traffic Level Mapping:\n0: Low Traffic | 1: Medium Traffic | 2: High Traffic\n\n" + "\n".join(overview_rows)
            except Exception:
                pass

        # Summary fallback
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
    
    def ask_gemini(self, question: str, context: str):
        """Call Gemini API for traffic data analysis"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
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
            return self.clean_html_response(ai_response)
        except requests.exceptions.RequestException as e:
            return f"Network error: {str(e)}"
        except Exception as e:
            return f"Error processing response: {str(e)}"
    
    def chat(self, question: str) -> str:
        """Main chat function"""
        try:
            # Handle greetings
            greetings_pattern = r"\b(?:hi|hello|hey|greetings|good\s+morning|good\s+afternoon|good\s+evening)\b"
            user_text = question.strip().lower()
            
            if re.search(greetings_pattern, user_text):
                return "Hello! I'm your traffic data assistant. I can help you analyze road segment traffic data, explain patterns in different clusters, and answer questions about traffic levels. What would you like to know?"
            
            # Load data and generate response
            df = self.load_data()
            if df is None:
                return "Sorry, I'm having trouble accessing the traffic data. Please try again later."
            
            context = self.query_data(question, df)
            answer = self.ask_gemini(question, context)
            return answer
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}. Please try rephrasing your question."

def render_chatbot_widget(csv_path: str):
    """Render the chatbot widget in Streamlit"""
    st.markdown("<h2 class='section-header'>🤖 Traffic Data Assistant</h2>", unsafe_allow_html=True)
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = TrafficChatbot(csv_path)
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize input state
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""
    
    # Chat interface
    with st.container():
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for i, (user_msg, bot_msg) in enumerate(st.session_state.chat_history):
                # User message
                st.markdown(f"""
                <div style='display: flex; justify-content: flex-end; margin-bottom: 10px;'>
                    <div style='background-color: #DCF8C6; padding: 10px; border-radius: 15px; max-width: 70%; color: #000;'>
                        <strong>You:</strong> {user_msg}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Bot message
                st.markdown(f"""
                <div style='display: flex; justify-content: flex-start; margin-bottom: 15px;'>
                    <div style='background-color: #F1F3F5; padding: 10px; border-radius: 15px; max-width: 70%; color: #000;'>
                        <strong>🤖 Assistant:</strong> {html.escape(bot_msg)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Custom CSS for better input alignment
        st.markdown("""
        <style>
        .chat-input-container {
            display: flex;
            gap: 10px;
            align-items: flex-end;
            margin: 20px 0;
        }
        .chat-input-field {
            flex: 1;
        }
        .chat-send-button {
            min-width: 80px;
        }
        div[data-testid="stTextInput"] > div > div > input {
            padding: 12px;
            border-radius: 20px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create form for Enter key handling
        with st.form(key="chat_form", clear_on_submit=True):
            col1, col2 = st.columns([5, 1])
            
            with col1:
                user_input = st.text_input(
                    "Ask me about traffic data...", 
                    placeholder="e.g., 'Which segments have the highest traffic?' or 'Tell me about cluster 2'",
                    key="chat_input_form",
                    label_visibility="collapsed"
                )
            
            with col2:
                # Add some spacing to align with text input
                st.markdown("<br>", unsafe_allow_html=True)
                send_button = st.form_submit_button("Send", type="primary", use_container_width=True)
        
        # Process input when form is submitted (Enter key or Send button)
        if send_button and user_input.strip():
            # Add user message to history
            with st.spinner("🤖 Thinking..."):
                bot_response = st.session_state.chatbot.chat(user_input)
            
            st.session_state.chat_history.append((user_input, bot_response))
            
            # Rerun to update the display and clear form
            st.rerun()
        
        # Quick action buttons
        st.markdown("**Quick Questions:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📈 Highest Traffic", use_container_width=True, key="quick_highest"):
                bot_response = st.session_state.chatbot.chat("Which segments have the highest traffic?")
                st.session_state.chat_history.append(("Which segments have the highest traffic?", bot_response))
                st.rerun()
        
        with col2:
            if st.button("🔍 Cluster Analysis", use_container_width=True, key="quick_cluster"):
                bot_response = st.session_state.chatbot.chat("Explain the different clusters and their characteristics")
                st.session_state.chat_history.append(("Explain the different clusters and their characteristics", bot_response))
                st.rerun()
        
        with col3:
            if st.button("📊 Data Summary", use_container_width=True, key="quick_summary"):
                bot_response = st.session_state.chatbot.chat("Give me an overview of the traffic data")
                st.session_state.chat_history.append(("Give me an overview of the traffic data", bot_response))
                st.rerun()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
