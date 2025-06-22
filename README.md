# mas-exchange-rates-api-v2
this is a complete guide on how to extract daily fx rates from MAS GOV API by the Monetary Authority of Singapore (MAS).
## Requirements
1. GOV API KEY : https://eservices.mas.gov.sg/apimg-portal/api-catalog-details/10485
2. Set up Bigquery and create service account https://cloud.google.com/bigquery/docs/use-service-accounts
3. Use the API key and service account credentials specifically for this project.

Note: If you are running your scripts on GCP-managed platforms such as Cloud Run, Cloud Functions, Compute Engine (GCE), or Composer, you do not need to export or provide a JSON service account file. These platforms handle authentication for you, which is much safer.

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


