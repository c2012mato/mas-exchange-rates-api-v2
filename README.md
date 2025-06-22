# mas-exchange-rates-api-v2


## Flow Diagram
```mermaid

graph TD
    style StartNode fill:#3498db,stroke:#333,stroke-width:2px;
    style EndNode fill:#3498db,stroke:#333,stroke-width:2px;
    style ConfigNode fill:#95a5a6,stroke:#333,stroke-width:2px;
    style BQNode fill:#e74c3c,stroke:#333,stroke-width:2px;
    style FetchNode fill:#f39c12,stroke:#333,stroke-width:2px;
    style LoopNode fill:#95a5a6,stroke:#333,stroke-width:2px;
    style DataNode fill:#95a5a6,stroke:#333,stroke-width:2px;
    style PipelineNode fill:#95a5a6,stroke:#333,stroke-width:2px;
    style ErrorNode fill:#e74c3c,stroke:#333,stroke-width:2px;

    A[Start]:::StartNode --> B[Load Config Values]:::ConfigNode
    B --> C[Create BigQuery Client]:::BQNode
    C --> D([Get Max Date from BigQuery]):::BQNode
    D --> E[Set Start and End Dates]:::ConfigNode
    E --> F[Initialize API Fetcher]:::FetchNode
    F --> G[Start Pipeline]:::PipelineNode
    G --> H{Loop: For Each Date in Range}:::LoopNode
    H --> I([Fetch Data from MAS API]):::FetchNode
    I --> J([Process & Normalize Data]):::DataNode
    J --> K([Upload Data to BigQuery]):::BQNode
    K --> L{More Dates?}:::LoopNode
    L -- Yes --> I
    L -- No --> M[Pipeline Completed]:::EndNode
    M --> N[End]:::EndNode
    H -- Error --> X[Log/Handle Error]:::ErrorNode
    X --> L

    %% Styling for main nodes
    classDef StartNode fill:#3498db,stroke:#333,stroke-width:2px;
    classDef EndNode fill:#3498db,stroke:#333,stroke-width:2px;
    classDef ConfigNode fill:#95a5a6,stroke:#333,stroke-width:2px;
    classDef BQNode fill:#e74c3c,stroke:#333,stroke-width:2px;
    classDef FetchNode fill:#f39c12,stroke:#333,stroke-width:2px;
    classDef DataNode fill:#95a5a6,stroke:#333,stroke-width:2px;
    classDef PipelineNode fill:#95a5a6,stroke:#333,stroke-width:2px;
    classDef LoopNode fill:#95a5a6,stroke:#333,stroke-width:2px;
    classDef ErrorNode fill:#e74c3c,stroke:#333,stroke-width:2px;


