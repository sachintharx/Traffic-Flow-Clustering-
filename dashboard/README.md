# 🚦 Road Segment Traffic Analysis Dashboard

A comprehensive dashboard for analyzing road segment traffic data with AI-powered chatbot assistance.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Option 1: One-Click Setup (Recommended)
1. **Clone/Download** this project to your computer
2. **Double-click** `run.bat` (Windows) or run `./run.sh` (Mac/Linux)
3. **Open** your browser to `http://localhost:8501`

### Option 2: Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the dashboard
streamlit run app.py

# 3. Run the chatbot server (optional)
python chatbot_server.py
```

## 📁 Project Structure
```
dashboard/
├── app.py                  # Main Streamlit dashboard
├── traffic_chatbot.py      # Chatbot integration module
├── chatbot_server.py       # Standalone FastAPI chatbot server
├── run.bat                 # Windows quick-start script
├── run.sh                  # Mac/Linux quick-start script
├── requirements.txt        # Python dependencies
├── data/
│   └── road_segment_traffic_clusters.csv  # Traffic data
└── README.md              # This file
```

## 🖥️ Available Interfaces

### 1. Streamlit Dashboard (Main Interface)
- **URL**: `http://localhost:8501`
- **Features**: Interactive visualizations, filters, AI chatbot
- **Best for**: Data exploration and analysis

### 2. FastAPI Chatbot Server (Optional)
- **URL**: `http://localhost:8000`
- **Features**: Standalone chatbot API with web interface
- **Best for**: API integration or standalone chatbot use

## 📊 Dashboard Features

### Overview Tab
- Traffic category distribution (pie chart)
- Average traffic by category
- Traffic distribution histogram

### Cluster Analysis Tab
- Traffic distribution by cluster (box plots)
- Segment count by cluster
- Detailed cluster statistics

### Segment Details Tab
- Interactive scatter plot of all segments
- Top segments by traffic volume
- Customizable rankings

### Geospatial View Tab
- Simulated map view of segments
- Traffic intensity visualization
- Interactive hover details

### Data Explorer Tab
- Filtered data table with styling
- Export functionality (CSV download)
- Real-time filtering

### AI Assistant Tab
- Conversational chatbot interface
- Natural language queries about traffic data
- Quick action buttons for common questions

## 🔧 Configuration

### API Key Setup (Optional)
For enhanced AI responses, set your Gemini API key:

**Windows:**
```cmd
set GEMINI_API_KEY=your_api_key_here
```

**Mac/Linux:**
```bash
export GEMINI_API_KEY=your_api_key_here
```

Or edit the API key directly in `chatbot_server.py` and `traffic_chatbot.py`

### Filters Available
- **Cluster Selection**: Filter by cluster IDs (0, 1, 2)
- **Traffic Category**: Low, Medium, High traffic
- **Segment Search**: Search for specific road segments
- **Traffic Range**: Slider to filter by traffic values

## 💬 Chatbot Usage Examples

Try these questions with the AI assistant:

- "Which segments have the highest traffic?"
- "Tell me about cluster 2"
- "What are the traffic patterns?"
- "Show me segments with low traffic"
- "Compare traffic between clusters"
- "What's the average traffic in each category?"

## 🛠️ Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Kill processes on ports 8501 or 8000
taskkill /f /im python.exe  # Windows
pkill -f streamlit          # Mac/Linux
```

**2. Module Not Found**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**3. Data File Not Found**
Ensure `data/road_segment_traffic_clusters.csv` exists in the project directory

**4. API Connection Issues**
- Check internet connection
- Verify API key if using Gemini AI
- Chatbot works offline with basic data analysis

### Performance Tips
- **Large datasets**: Adjust `max_rows` parameter in query functions
- **Slow responses**: Consider caching data with longer refresh intervals
- **Memory usage**: Restart the application periodically for long sessions

## 📋 System Requirements

### Minimum Requirements
- **RAM**: 2GB available
- **Storage**: 100MB free space
- **Python**: 3.8+
- **Internet**: Required for AI features (optional for basic dashboard)

### Recommended
- **RAM**: 4GB+ available
- **CPU**: Multi-core processor
- **Browser**: Chrome, Firefox, Safari (latest versions)

## 🔄 Updates and Maintenance

### Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### Clean Cache and Temporary Files
```bash
# Windows
cleanup.bat

# Mac/Linux
./cleanup.sh
```

### Restart Services
```bash
# Stop all Python processes
taskkill /f /im python.exe  # Windows
pkill python                # Mac/Linux

# Restart dashboard
streamlit run app.py
```

## 📈 Data Format

The dashboard expects CSV data with these columns:
- `segment`: Road segment identifier (e.g., "A0A1")
- `cluster_id`: Cluster assignment (0, 1, 2)
- `category`: Traffic level ("Low Traffic", "Medium Traffic", "High Traffic")
- `avg_raw_traffic`: Numerical traffic value

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all dependencies are installed correctly
3. Ensure data files are in the correct location
4. Check Python version compatibility

## 📄 License

This project is for educational purposes as part of EE7260 Advanced Artificial Intelligence coursework.
