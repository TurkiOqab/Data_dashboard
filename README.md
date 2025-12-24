# Data Dashboard - AI-Powered Slide Intelligence

An intelligent dashboard that ingests PowerPoint presentations and enables natural language queries over slide content, including text, tables, and visual charts.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      STREAMLIT FRONTEND                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ File Upload │  │    Chat     │  │  Slide/Chart Viewer     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PROCESSING LAYER                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │ PPTX Processor  │  │ Vision Analyzer │  │ Query Engine   │  │
│  │ (python-pptx)   │  │ (Claude Vision) │  │ (ChromaDB)     │  │
│  └─────────────────┘  └─────────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      STORAGE LAYER                              │
│  ┌─────────────────────────┐  ┌──────────────────────────────┐ │
│  │ ChromaDB Vector Store   │  │ Local File Storage           │ │
│  │ (semantic embeddings)   │  │ (slides, images, metadata)   │ │
│  └─────────────────────────┘  └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack Decisions

### Why Python over Node.js?

| Criteria | Python | Node.js |
|----------|--------|---------|
| **PowerPoint Parsing** | `python-pptx` - mature, full-featured | Limited libraries, less reliable |
| **AI/ML Ecosystem** | Native home for AI (LangChain, transformers) | Requires Python bridges |
| **Vision Models** | First-class Anthropic/OpenAI SDK support | Wrapper libraries |
| **Data Processing** | Pandas, NumPy - industry standard | Not designed for data work |
| **Visualization** | Plotly, Matplotlib - interactive & static | Chart.js - less flexible |

**Verdict**: Python is the natural choice for AI + data processing workloads.

### Why Streamlit over React?

| Criteria | Streamlit | React |
|----------|-----------|-------|
| **Development Speed** | Hours to prototype | Days to prototype |
| **AI Integration** | Native Python, zero context switch | API layer required |
| **Built-in Components** | File upload, chat, charts included | Must build or install |
| **Maintenance** | Single codebase | Frontend + backend repos |
| **Production Ready** | Yes (with caching) | Yes |

**Verdict**: Streamlit provides 80% of React's capability with 20% of the effort for this use case.

### Why Claude Vision for Chart Analysis?

1. **Semantic Understanding**: Doesn't just OCR text - understands what charts *mean*
2. **Data Extraction**: Can approximate data points from bar/line/pie charts
3. **Context Awareness**: Understands chart in context of slide content
4. **Single API**: Same model handles text queries and visual analysis

Alternative considered: Custom OCR + chart detection pipelines - rejected due to complexity and lower accuracy on varied chart styles.

### Why ChromaDB for Vector Search?

1. **Local-first**: No external infrastructure needed
2. **Embedding Native**: Built for semantic search use cases
3. **Lightweight**: Runs in-process, no separate server
4. **Fuzzy by Design**: Semantic similarity naturally handles imperfect queries

## Core Features

### 1. Unstructured Data Ingestion
- Extracts text from all slide elements
- Parses tables into structured format
- Converts slides to images for visual analysis
- Uses Claude Vision to describe charts and graphics

### 2. Fuzzy Query Engine
- Embeds all slide content into vector space
- Semantic search finds relevant content even with imprecise queries
- LLM interprets user intent and reformulates queries
- Returns ranked results with confidence scores

### 3. Data Visualization
- Shows original slides when relevant
- Re-generates interactive Plotly charts from extracted data
- Highlights specific content regions

## Project Structure

```
Data_dashboard/
├── app/
│   ├── main.py                 # Streamlit entry point
│   ├── components/
│   │   ├── chat.py             # Chat interface
│   │   ├── upload.py           # File upload handler
│   │   └── visualizer.py       # Chart/slide display
│   ├── services/
│   │   ├── pptx_processor.py   # PowerPoint extraction
│   │   ├── vision_analyzer.py  # Claude Vision integration
│   │   ├── embeddings.py       # Text embedding service
│   │   └── query_engine.py     # Semantic search
│   └── utils/
│       └── helpers.py          # Utility functions
├── data/
│   ├── uploads/                # Raw uploaded files
│   └── processed/              # Extracted content
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Run the Application
```bash
streamlit run app/main.py
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Claude API key for vision and chat | Yes |
| `CHROMA_PERSIST_DIR` | ChromaDB storage path | No (default: `./data/chroma`) |

## Usage

1. **Upload**: Drag and drop a `.pptx` file
2. **Wait**: System extracts text, tables, and analyzes charts
3. **Ask**: Type natural language questions about your slides
4. **View**: See relevant slides or regenerated visualizations

## Example Queries

- "What were Q3 sales numbers?"
- "Show me the revenue trend chart"
- "Which slide talks about market expansion?"
- "Summarize the key findings"
- "What's the comparison between regions?"

## Future Enhancements

- [ ] Multi-file support with cross-document search
- [ ] PDF and Word document support
- [ ] Export regenerated charts
- [ ] Collaboration features
- [ ] Fine-tuned embeddings for domain-specific content
