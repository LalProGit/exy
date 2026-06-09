```mermaid
graph TD
    %% EXTERNAL INTERFACES
    subgraph Clients [External Interfaces]
        Discord[Discord App]
        Web[Web UI / WebSocket]
    end

    %% API GATEWAY LAYER
    subgraph Server [FastAPI Gateway]
        Adapters[Platform Adapters In/Out]
        Router{Intent Router}
        Adapters -->|ExyPayload| Router
        Router -.->|Rate-limited Stream| Adapters
    end

    %% LOCAL STORAGE & EPHEMERAL RAG SYSTEM
    subgraph HotMemory [SQLite + sqlite-vec Layer]
        SemCache[Semantic Chat Cache]
        ToolDB[Dynamic Tool Manifests]
        EphRAG[Ephemeral Vector Index <br> JIT Context Distillation]
    end

    %% ORCHESTRATION & EXECUTION
    subgraph Engine [Agent Core]
        Orch[pydantic-ai Orchestrator]
        
        subgraph Tools [Execution Layer]
            REST[Generic REST Driver]
            Script[Python Script Runner]
            Browser[Playwright Engine]
        end
    end

    %% EXTERNAL APIS
    LLM[OpenRouter: Llama-3.3-70b]
    Notion[(Notion: Cold Storage)]

    %% ROUTING LOGIC
    Clients <--> Adapters
    Router -->|Standard Chat| SemCache
    Router -->|Direct Slash Commands| Tools
    
    %% JIT EXECUTION & CACHING
    SemCache -->|Cache Miss| Orch
    ToolDB -->|Inject only relevant tools| Orch
    
    Orch <-->|Prompt / Stream| LLM
    Orch -->|Trigger| Tools
    
    %% EPHEMERAL RAG PIPELINE FLOW
    Browser -->|1. Extract & Strip Markdown| EphRAG
    EphRAG -->|2. Precision Chunk Retrieval| Orch
    
    Tools <-->|Updates| ToolDB
    
    %% ASYNC DB WRITES
    Orch -.->|Async Background Task| Notion
    ```