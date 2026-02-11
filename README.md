# LLM-Powered Conversational AI Data Analyst with Power BI Integration

## 🎯 Problem Statement

Organizations struggle to extract meaningful insights from their data and Power BI dashboards. Data analysts spend significant time answering repetitive questions about metrics, trends, and KPIs. This project solves this by creating an AI-powered conversational data analyst that:

1. **Automatically analyzes datasets** with comprehensive EDA
2. **Generates human-readable insights** using LLMs
3. **Answers natural language questions** about data and dashboards
4. **Explains Power BI KPIs** in business terms
5. **Provides data-driven recommendations** instantly

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE (Streamlit)                   │
│              Upload Data → Analyze → Chat → Insights            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CONVERSATIONAL AI ENGINE                       │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ Intent       │  │ Context      │  │ Response           │   │
│  │ Classifier   │  │ Retriever    │  │ Generator (LLM)    │   │
│  │              │  │ (RAG-style)  │  │                    │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
┌─────────────────────────┐   ┌──────────────────────────────┐
│  DATA ANALYSIS ENGINE   │   │  POWER BI INTEGRATION        │
│  • Data Loader          │   │  • Metadata Parser           │
│  • EDA Engine           │   │  • KPI Analyzer              │
│  • Insight Generator    │   │  • Dashboard Explainer       │
│  • Statistical Analysis │   │                              │
└───────────┬─────────────┘   └──────────────┬───────────────┘
            │                                 │
            ▼                                 ▼
┌─────────────────────────┐   ┌──────────────────────────────┐
│  CSV/Excel Dataset      │   │  Power BI Metadata (JSON)    │
└─────────────────────────┘   └──────────────────────────────┘
```

## 🚀 Key Features

### 1. Automated Data Analysis
- **Data Loading**: Supports CSV and Excel files
- **Comprehensive EDA**: Descriptive statistics, correlations, distributions
- **Anomaly Detection**: Identifies outliers using IQR and Z-score methods
- **Trend Analysis**: Detects temporal patterns and trends
- **Missing Value Analysis**: Categorizes data quality issues

### 2. LLM-Powered Insights
- **Executive Summaries**: High-level overview of findings
- **Root Cause Analysis**: Explains why patterns exist
- **Business Recommendations**: Actionable next steps
- **Statistical Explanations**: Translates stats into business language

### 3. Conversational AI Chatbot
- **Intent Classification**: Understands user questions
- **Context-Aware Responses**: Uses RAG-style retrieval
- **Multiple Intent Types**:
  - Trend analysis
  - Comparisons
  - Explanations
  - KPI queries
  - Dashboard summaries
  - Anomaly detection
- **Conversation Memory**: Maintains chat history

### 4. Power BI Integration
- **Metadata-Based**: No UI scraping required
- **KPI Explanations**: Natural language KPI descriptions
- **Performance Analysis**: Compares actual vs. target
- **Dashboard Summaries**: Comprehensive overviews
- **Related Metrics**: Finds connected KPIs

## 📁 Project Structure

```
llm_data_analyst/
├── app.py                          # Streamlit UI application
├── requirements.txt                # Python dependencies
├── .env.template                   # Environment variables template
├── README.md                       # This file
│
├── config/
│   └── settings.py                 # Application configuration
│
├── src/
│   ├── analysis/
│   │   ├── data_loader.py         # Dataset loading and validation
│   │   ├── eda_engine.py          # Exploratory Data Analysis
│   │   └── insight_generator.py   # Converts EDA to insights
│   │
│   ├── chatbot/
│   │   ├── intent_classifier.py   # Classifies user queries
│   │   ├── context_retriever.py   # RAG-style context retrieval
│   │   └── chatbot_engine.py      # Main conversational AI
│   │
│   ├── powerbi/
│   │   └── metadata_parser.py     # Power BI integration
│   │
│   └── utils/
│       └── llm_client.py           # LLM client (OpenAI/Anthropic/Mock)
│
├── prompts/
│   └── templates.py                # LLM prompt templates
│
├── data/
│   ├── sample_sales_data.csv      # Sample dataset
│   └── powerbi_metadata.json      # Sample Power BI metadata
│
└── outputs/                        # Generated reports and analyses
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd llm_data_analyst
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment** (Optional - for real LLM)
```bash
cp .env.template .env
# Edit .env and add your API keys
```

## 🎮 Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Quick Start Guide

#### 1. **Load Your Data**
   - Navigate to "📁 Load Data"
   - Upload a CSV or Excel file
   - View data preview and metadata

#### 2. **Run Analysis**
   - Go to "🔍 Analysis"
   - Click "Run Full Analysis"
   - Review generated insights

#### 3. **Load Power BI Metadata** (Optional)
   - Navigate to "📊 Power BI"
   - Upload your Power BI metadata JSON
   - View KPI summaries

#### 4. **Chat with the AI Analyst**
   - Go to "💬 Chatbot"
   - Ask questions in natural language
   - Get instant, data-driven answers

### Example Questions to Ask

```
General Analysis:
- "What are the main trends in the data?"
- "Which variables are strongly correlated?"
- "Show me the top 5 insights"

Specific Queries:
- "Explain the outliers in Sales_Amount"
- "Why is revenue increasing?"
- "Compare Northeast vs Southeast regions"

KPI Questions:
- "What is the current Customer Satisfaction Score?"
- "Why is Total Revenue below target?"
- "Explain the Marketing ROI metric"

Dashboard:
- "Summarize the dashboard"
- "Which KPIs need attention?"
- "Show me all underperforming metrics"
```

## 🔧 Technical Details

### Data Analysis Pipeline

1. **Data Loading**
   - Validates file format
   - Checks data quality
   - Generates metadata

2. **EDA Engine**
   - Descriptive statistics (mean, median, std, etc.)
   - Correlation analysis (Pearson correlation matrix)
   - Distribution analysis (normality tests, skewness)
   - Outlier detection (IQR method, Z-scores)
   - Trend detection (linear regression)
   - Missing value analysis

3. **Insight Generation**
   - Prioritizes findings by importance
   - Generates business recommendations
   - Categorizes insights (data quality, trends, relationships)

### Chatbot Architecture

1. **Intent Classification**
   - Regex-based pattern matching
   - Confidence scoring
   - Entity extraction

2. **Context Retrieval (RAG)**
   - Retrieves relevant EDA results
   - Filters insights by intent
   - Fetches Power BI metadata
   - Maintains conversation history

3. **Response Generation**
   - Uses structured prompts
   - Incorporates context
   - Generates natural language
   - Cites specific data points

### Power BI Integration

The system integrates with Power BI through **metadata-based approach**:

**Export from Power BI** (Manual Process):
1. Identify key KPIs and their current values
2. Note trends, targets, and performance indicators
3. Export as JSON in the required format

**Metadata Structure**:
```json
{
  "dashboard_name": "Dashboard Name",
  "kpis": [
    {
      "name": "KPI Name",
      "value": 12345,
      "target": 10000,
      "trend": {
        "direction": "increasing",
        "value": 7.2
      }
    }
  ],
  "filters": {...},
  "visualizations": [...]
}
```

### LLM Integration

The system supports three LLM modes:

1. **Mock LLM** (Default)
   - No API key required
   - Deterministic responses
   - Perfect for development/demo

2. **OpenAI**
   - Set `USE_MOCK_LLM=false` in `.env`
   - Add `OPENAI_API_KEY` to `.env`
   - Uses GPT-4 Turbo

3. **Anthropic Claude**
   - Set `USE_MOCK_LLM=false` in `.env`
   - Add `ANTHROPIC_API_KEY` to `.env`
   - Uses Claude 3 Sonnet

## 📊 Sample Data

The project includes sample data in `data/`:

- **sample_sales_data.csv**: 10 days of sales data across regions and product categories
- **powerbi_metadata.json**: Sample Power BI dashboard with 7 KPIs

## 🎓 For Interview Explanation

### "Walk me through your approach"

**Problem Identification:**
"Organizations have vast amounts of data in Excel files and Power BI dashboards, but extracting insights requires manual analysis. I built an AI system that automatically analyzes data, generates insights, and answers questions conversationally."

**Solution Architecture:**
"The system has three main components:

1. **Data Analysis Engine**: Performs comprehensive EDA - descriptive stats, correlations, outlier detection, trend analysis. It's built with pandas, scipy, and scikit-learn.

2. **LLM Integration**: Uses prompt engineering to convert statistical findings into business insights. I created structured prompts for different tasks - executive summaries, trend explanations, KPI descriptions.

3. **Conversational AI**: Implements RAG (Retrieval-Augmented Generation) - classifies user intent, retrieves relevant context from the analysis, and generates responses using the LLM."

**Key Technical Decisions:**

*Why metadata-based Power BI integration?*
"Scraping Power BI UI would be fragile and violate terms of service. Metadata-based approach is clean, maintainable, and allows users to control exactly what data is shared with the AI."

*Why RAG instead of fine-tuning?*
"RAG provides current, accurate answers without requiring model retraining. The context retriever ensures responses are grounded in actual data, preventing hallucinations."

*Why support Mock LLM?*
"Makes the system testable and demonstrable without API costs. Shows I think about development workflows and production concerns."

**Challenges Solved:**

1. **Context Management**: Limited token windows required smart context retrieval - only relevant insights/data for each query
2. **Intent Classification**: Regex patterns with confidence scoring handle ambiguous queries
3. **Statistical Explanation**: Prompt templates translate technical findings into business language

**Production Considerations:**

- Modular design allows easy swapping of LLM providers
- Configuration-driven (no hardcoded values)
- Error handling throughout
- Extensible architecture for adding new analysis types

### "How would you scale this?"

1. **Database Backend**: Replace CSV loading with database connections
2. **Async Processing**: Use Celery for long-running EDA tasks
3. **Caching**: Cache analysis results to avoid recomputation
4. **Multi-tenancy**: Add user authentication and data isolation
5. **Real Power BI API**: Integrate with Power BI REST API for live data
6. **Embedding-based RAG**: Replace regex with semantic search using embeddings

## 🧪 Testing

```python
# Test data loading
python -c "from src.analysis.data_loader import DataLoader; loader = DataLoader(); loader.load_file('data/sample_sales_data.csv')"

# Test EDA
python -c "from src.analysis.eda_engine import EDAEngine; import pandas as pd; data = pd.read_csv('data/sample_sales_data.csv'); eda = EDAEngine(data); results = eda.run_full_analysis(); print(results.keys())"

# Test chatbot
python -c "from src.chatbot.chatbot_engine import DataAnalystChatbot; bot = DataAnalystChatbot(use_mock=True); print(bot.chat('What are the key insights?'))"
```

## 📝 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

This is a portfolio project. For improvements or questions, please open an issue.

## 📧 Contact

For questions about this project or interview discussions, please contact the developer.

---

**Built with:** Python, Streamlit, Pandas, OpenAI/Anthropic APIs, Power BI Integration
