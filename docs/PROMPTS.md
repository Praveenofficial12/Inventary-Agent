# 🧠 AI Agent Prompt Reference Guide

This document provides a comprehensive reference for all LLM system prompts used in the **Nexus AI Inventory Management System**. Each agent is a specialized LangChain-powered module targeting Google Gemini 1.5 Pro (with OpenAI GPT-4 Turbo as fallback).

---

## Prompt File Locations

| Agent | Prompt File |
|---|---|
| Analysis Agent | `docs/prompts/analysis_agent.txt` |
| Assistant Agent | `docs/prompts/assistant_agent.txt` |
| Recommendation Agent | `docs/prompts/recommendation_agent.txt` |
| Report Agent | `docs/prompts/report_agent.txt` |

All agents dynamically load their prompts at runtime. If a prompt file is missing, agents fall back to embedded rule-based logic — ensuring 100% uptime.

---

## Agent 1: Analysis Agent (`analysis_agent.txt`)

**Class**: `backend/app/ai/agents/analysis_agent.py`
**Endpoint**: `GET /agents/alerts`
**Role**: Inventory Health Scanner & Risk Detector

### What it does:
- Scans ALL products and detects stock anomalies
- Classifies alerts by severity: `critical` → `high` → `medium` → `low`
- Detects dead stock (zero movement) and projects future stockouts
- Returns structured JSON with `alerts[]` and `summary`

### LangChain Chain:
```
ChatPromptTemplate → Gemini LLM → JsonOutputParser
```

### Input to LLM:
```
"Analyze this data: Products: [{...}], Logs: [{...}]"
```

### Output Schema:
```json
{
  "alerts": [
    {
      "type": "critical_out_of_stock | low_stock | dead_stock | predicted_shortage",
      "product_name": "MacBook Pro 14",
      "sku": "LAP-MBP-14",
      "message": "MacBook Pro 14 quantity (5) is at reorder threshold (10). Reorder recommended.",
      "severity": "medium",
      "quantity": 5,
      "threshold": 10
    }
  ],
  "summary": "3 products analyzed. 2 alerts detected (1 critical, 1 medium)."
}
```

### Rule-Based Fallback Logic:
When LLM is unavailable, the agent applies deterministic rules:
- `quantity == 0` → severity: `high`, type: immediate reorder
- `0 < quantity <= threshold` → severity: `medium`, type: reorder soon

---

## Agent 2: Assistant Agent (`assistant_agent.txt`)

**Class**: `backend/app/ai/agents/assistant_agent.py`
**Endpoint**: `POST /chat/message`
**Role**: Conversational Inventory Q&A & Natural Language Interface

### What it does:
- Provides a natural language interface to the live inventory database
- Dynamically fetches ALL products, categories, and suppliers before each response
- Builds a structured inventory context and injects it into the LLM prompt
- Optionally enriches responses with RAG-retrieved policy documents
- Maintains conversation history per `session_id` in MongoDB

### Context Building Flow:
```
User Message
    ↓
Fetch all products from DB (with category & supplier names resolved)
    ↓
Build inventory context string (out-of-stock, low-stock, healthy summaries)
    ↓
Query ChromaDB RAG for relevant policy documents (threshold: 0.3 similarity)
    ↓
Compose: [System Prompt] + [Inventory Context] + [Policy Docs] + [User Input]
    ↓
Gemini LLM → Natural Language Response
```

### LangChain Chain:
```
ChatPromptTemplate(system, user) → Gemini LLM → response.content
```

### Rule-Based Fallback (15+ intent categories):
The agent has an intelligent rule-based fallback covering:
- `out of stock` queries
- `low stock / reorder / alert` queries
- `total value / valuation` queries
- `stock level for specific product` queries
- `expensive / top products` queries
- `category breakdown` queries
- `supplier overview` queries
- Greetings & help intents
- Generic fallback with inventory snapshot

---

## Agent 3: Recommendation Agent (`recommendation_agent.txt`)

**Class**: `backend/app/ai/agents/recommendation_agent.py`
**Endpoint**: `GET /agents/recommendations`
**Role**: Supply Chain Optimization & Procurement Strategist

### What it does:
- Analyzes stock levels against thresholds and supplier data
- Generates prioritized reorder recommendations with suggested quantities
- Identifies consolidation opportunities (same supplier, multiple low-stock items)
- Flags dead stock for liquidation consideration
- Returns JSON with `recommendations[]`, `insights[]`, and `summary`

### LangChain Chain:
```
ChatPromptTemplate → Gemini LLM → JsonOutputParser
```

### Input to LLM:
```
"Inventory Data: [{products}], Suppliers: [{suppliers}]"
```

### Output Schema:
```json
{
  "recommendations": [
    {
      "priority": "critical",
      "action": "Urgent Reorder — Wireless Mouse (SKU: MOU-01)",
      "rationale": "Product has 0 units in stock. Active revenue loss. Assign to TechCorp.",
      "targeted_products": ["MOU-01"],
      "supplier": "TechCorp",
      "suggested_order_quantity": 45,
      "estimated_cost": 810.00
    }
  ],
  "insights": ["2 products from TechCorp need restocking — consolidate PO for cost savings."],
  "summary": "Supply chain status: 2 critical items, 1 high-priority item requiring immediate attention."
}
```

### Suggested Quantity Formula:
- Out of stock: `reorder_threshold × 3` (replenish + buffer)
- Low stock: `reorder_threshold × 2` (standard buffer)

---

## Agent 4: Report Agent (`report_agent.txt`)

**Class**: `backend/app/ai/agents/report_agent.py`
**Endpoint**: `GET /reports/generate`
**Role**: Executive Intelligence Report Generator

### What it does:
- Generates complete executive-level inventory reports from live data
- Calculates advanced financial metrics (gross margin potential, cost basis, valuation)
- Produces per-category breakdowns and risk-level assessments
- Returns board-ready JSON report with 5 structured sections

### LangChain Chain:
```
ChatPromptTemplate → Gemini LLM → JsonOutputParser
```

### Input to LLM:
```
"Data: [{products}]"
```

### Output Schema:
```json
{
  "title": "Nexus AI Inventory Intelligence Report — 2026-07-05",
  "generated_at": "2026-07-05T06:30:00Z",
  "risk_level": "Medium",
  "summary": "Executive summary paragraph...",
  "key_metrics": {
    "total_products": 3,
    "total_inventory_value": 13835.00,
    "total_cost_basis": 10980.00,
    "gross_margin_potential_pct": 20.6,
    "healthy_stock_count": 1,
    "low_stock_count": 1,
    "out_of_stock_count": 1,
    "top_category": "Electronics"
  },
  "sections": [
    { "heading": "Executive Summary", "content": "..." },
    { "heading": "Stock Alert Analysis", "content": "..." },
    { "heading": "Valuation Analysis", "content": "..." },
    { "heading": "Category Breakdown", "content": "..." },
    { "heading": "Action Plan", "content": "..." }
  ],
  "recommendations": [...]
}
```

---

## RAG Pipeline (Retrieval-Augmented Generation)

**File**: `backend/app/ai/rag_pipeline.py`
**Vector Store**: ChromaDB (local persistent store)
**Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384-dim vectors)

### How it works:

1. **Document Ingestion** (`POST /upload/document`):
   - User uploads a PDF or TXT policy document
   - Text is extracted and split into 500-token chunks (50-token overlap)
   - Each chunk is embedded via `all-MiniLM-L6-v2`
   - Embeddings stored in ChromaDB `company_policies` collection

2. **Query at Chat Time**:
   - User message is embedded with the same model
   - ChromaDB performs cosine similarity search (top-5 results)
   - Results filtered by relevance threshold: `score >= 0.3`
   - Filtered documents injected into the Assistant Agent's context

### Ingestion Code Flow:
```
PDF/TXT File → PyPDF/text extraction → RecursiveCharacterTextSplitter
    → HuggingFaceEmbeddings (all-MiniLM-L6-v2) → ChromaDB.add_texts()
```

### Query Code Flow:
```
User Query → embed query → ChromaDB.similarity_search_with_relevance_scores()
    → filter(score >= 0.3) → return Document objects → inject into LLM context
```

---

## LLM Provider Abstraction

**File**: `backend/app/ai/llm_provider.py`

The system uses a provider pattern to support multiple LLM backends:

```python
get_llm_provider(provider_name=None) → LLM Instance

# provider = "gemini"  →  ChatGoogleGenerativeAI(model="gemini-1.5-pro")
# provider = "openai"  →  ChatOpenAI(model="gpt-4-turbo-preview")
```

Switch providers by updating `LLM_PROVIDER` in `.env`:
```env
LLM_PROVIDER=gemini     # Default (free tier available)
LLM_PROVIDER=openai     # Requires paid OpenAI API key
```

---

## Prompt Engineering Principles Applied

| Principle | Implementation |
|---|---|
| **Role Assignment** | Each prompt opens with a clear expert persona definition |
| **Structured Output** | All agent prompts enforce strict JSON output schemas |
| **Anti-Hallucination** | Explicit "NO HALLUCINATION" / "NEVER FABRICATE" instructions |
| **Grounding** | Prompts instruct the LLM to derive all figures from input data |
| **Fallback Safety** | Rule-based Python fallback for every agent (LLM-agnostic) |
| **Context Injection** | Live DB data injected at runtime into the prompt context |
| **Output Parsing** | `JsonOutputParser` validates and parses LLM JSON responses |
