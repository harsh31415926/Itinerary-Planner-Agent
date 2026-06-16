# ◈ Itinerary Planner Agent

A production-oriented multi-agent travel intelligence system built with **LangGraph**, **Groq LLMs**, **Tavily Search**, **AviationStack**, **PostgreSQL**, and **Streamlit**.

The platform employs an agent-based orchestration layer that transforms natural language travel requests into structured travel plans by autonomously extracting trip parameters, gathering external travel intelligence, evaluating accommodation options, analyzing flight routes, and generating comprehensive itineraries.

Unlike conventional travel applications that rely on rigid workflows, this system leverages Agentic AI to coordinate specialized agents capable of reasoning, tool utilization, state persistence, and dynamic decision-making.

--- 

## ◈ Core Capabilities

* Autonomous Travel Planning
* Multi-Agent Orchestration with LangGraph
* Structured Information Extraction
* Real-Time Flight Intelligence
* Intelligent Hotel Discovery
* Dynamic Itinerary Generation
* Persistent State Management
* Interactive Streamlit Interface
* PostgreSQL Checkpointing

---

## ◈ Architecture

```text
User Request
      │
      ▼
Parser Agent
      │
      ▼
Flight Agent
      │
      ▼
Hotel Agent
      │
      ▼
Itinerary Agent
      │
      ▼
Final Planner Agent
      │
      ▼
Travel Report
```

---

## ◈ Technology Stack

| Layer               | Technology             |
| ------------------- | ---------------------- |
| LLM                 | Groq Llama 3.3 70B     |
| Agent Framework     | LangGraph              |
| Search Intelligence | Tavily                 |
| Aviation Data       | AviationStack          |
| Database            | PostgreSQL             |
| Backend             | Python                 |
| Frontend            | Streamlit              |
| State Persistence   | LangGraph Checkpointer |

---

## ◈ Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key

TAVILY_API_KEY=your_tavily_api_key

AVIATION_STACK_API_KEY=your_aviationstack_api_key

DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

---

## ◈ Installation

```bash
git clone https://github.com/harsh31415926/Itinerary-Planner-Agent.git

cd Itinerary-Planner-Agent

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

---

## ◈ Running The Application

### Streamlit Interface

```bash
streamlit run app.py
```

### Terminal Version

```bash
python main.py
```

---

## ◈ Key Engineering Concepts

* Agentic AI Systems
* Workflow Orchestration
* Structured Output Generation
* Tool-Augmented Reasoning
* Stateful Agent Execution
* External API Integration
* Persistent Memory Management
* Human-Centric Itinerary Synthesis

---

## ◈ Future Roadmap

* Multi-City Route Optimization
* Flight Price Forecasting
* Budget Allocation Engine
* Weather-Aware Planning
* Autonomous Booking Agents
* Travel Risk Intelligence
* Recommendation Ranking Models
* Reinforcement-Based Travel Optimization

---

## ◈ License

This project is intended for educational, research, and experimentation purposes involving Agentic AI workflows, multi-agent orchestration, and travel intelligence systems.
