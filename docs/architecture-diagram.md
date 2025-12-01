# Application Architecture Diagram

## Complete Flow Diagram

```mermaid
graph TD
    A[📁 CSV Bestanden in csv/ folder] --> B[💾 Push naar GitHub Repository]
    B --> C[⚡ GitHub Action Triggered<br/>import_csv.yml]
    C --> D[🧪 Run Unit Tests<br/>pytest test_csv_import.py]
    D --> E{Tests<br/>Passed?}
    E -->|❌ Failed| F[🛑 Stop Workflow<br/>Send Notification]
    E -->|✅ Passed| G[🐍 Run import_csvs.py]
    G --> H[📊 Create PostgreSQL Tables<br/>Individual Columns]
    G --> I[🕸️ Create AGE Graph Nodes<br/>exo_graph]
    H --> J[(🐘 PostgreSQL Database<br/>testdb)]
    I --> J
    J --> K[📈 Data in Both Formats:<br/>- SQL Tables<br/>- Graph Nodes & Edges]
    K --> L[🔍 Query via pgAdmin<br/>localhost:8080]
    K --> M[💻 Query via Python Scripts<br/>psycopg2]
    
    style A fill:#e1f5ff,stroke:#333,stroke-width:2px
    style B fill:#d4edda,stroke:#333,stroke-width:2px
    style C fill:#fff3cd,stroke:#333,stroke-width:2px
    style D fill:#ffeaa7,stroke:#333,stroke-width:2px
    style E fill:#fab1a0,stroke:#333,stroke-width:2px
    style F fill:#ff7675,stroke:#333,stroke-width:2px
    style G fill:#74b9ff,stroke:#333,stroke-width:2px
    style H fill:#a29bfe,stroke:#333,stroke-width:2px
    style I fill:#fd79a8,stroke:#333,stroke-width:2px
    style J fill:#55efc4,stroke:#333,stroke-width:2px
    style K fill:#00b894,stroke:#333,stroke-width:2px
    style L fill:#fdcb6e,stroke:#333,stroke-width:2px
    style M fill:#e17055,stroke:#333,stroke-width:2px
```

## Local Development Flow

```mermaid
graph TD
    A[👨‍💻 Developer Werkt Lokaal] --> B[🐳 Docker Compose Up<br/>Start Containers]
    B --> C1[📦 PostgreSQL + AGE Container<br/>age-postgres:5432]
    B --> C2[🖥️ pgAdmin Container<br/>pgadmin:8080]
    C1 --> D[💾 Docker Volume: pgdata<br/>Persistent Storage]
    A --> E[⚙️ Configure .env File<br/>DB credentials]
    E --> F[🐍 Run import_csvs.py<br/>Locally]
    F --> G[📁 Read CSV Files<br/>from csv/ folder]
    G --> H[🔄 Process with pandas<br/>Parse & Transform Data]
    H --> I1[💾 Insert into PostgreSQL Tables<br/>insert_row_postgres]
    H --> I2[🕸️ Insert into AGE Graph<br/>insert_node_age/insert_edge_age]
    I1 --> C1
    I2 --> C1
    C1 --> J[✅ Data Available for Queries]
    J --> K[🔍 Query via pgAdmin UI]
    J --> L[💻 Query via Python]
    J --> M[📊 SQL Queries on Tables]
    J --> N[🕸️ Cypher Queries on Graph]
    
    style A fill:#dfe6e9,stroke:#333,stroke-width:2px
    style B fill:#74b9ff,stroke:#333,stroke-width:2px
    style C1 fill:#55efc4,stroke:#333,stroke-width:2px
    style C2 fill:#ffeaa7,stroke:#333,stroke-width:2px
    style D fill:#fd79a8,stroke:#333,stroke-width:2px
    style F fill:#a29bfe,stroke:#333,stroke-width:2px
    style J fill:#00b894,stroke:#333,stroke-width:2px
```

## Detailed Data Flow

```mermaid
graph LR
    subgraph Input["📥 Input"]
        A1[Exo.csv]
        A2[Aim.csv]
        A3[HAS_AIM.csv]
        A4[24 CSV Files]
    end
    
    subgraph Processing["⚙️ Processing"]
        B1[Read CSV<br/>pandas.read_csv]
        B2[Parse Delimiter<br/>; or ,]
        B3[Create DataFrame]
        B4[Filter Columns<br/>Remove Unnamed]
        B5[Convert Types<br/>Format Values]
    end
    
    subgraph Database["💾 Database Layer"]
        C1[Create Table<br/>IF NOT EXISTS]
        C2[Insert PostgreSQL Row<br/>INSERT INTO]
        C3[Create AGE Node<br/>CREATE node:Label]
        C4[Create AGE Edge<br/>MATCH + CREATE]
    end
    
    subgraph Storage["🗄️ Storage"]
        D1[(PostgreSQL Tables<br/>Relational Data)]
        D2[(AGE Graph<br/>Graph Data)]
        D3[Docker Volume<br/>pgdata]
    end
    
    subgraph Output["📤 Query Interface"]
        E1[SQL Queries]
        E2[Cypher Queries]
        E3[Python API]
        E4[pgAdmin UI]
    end
    
    Input --> B1
    B1 --> B2
    B2 --> B3
    B3 --> B4
    B4 --> B5
    B5 --> C1
    C1 --> C2
    C1 --> C3
    B5 --> C4
    C2 --> D1
    C3 --> D2
    C4 --> D2
    D1 --> D3
    D2 --> D3
    D1 --> E1
    D2 --> E2
    D1 --> E3
    D2 --> E3
    E4 --> E1
    E4 --> E2
    
    style Input fill:#e1f5ff,stroke:#333,stroke-width:2px
    style Processing fill:#fff3cd,stroke:#333,stroke-width:2px
    style Database fill:#ffeaa7,stroke:#333,stroke-width:2px
    style Storage fill:#55efc4,stroke:#333,stroke-width:2px
    style Output fill:#a29bfe,stroke:#333,stroke-width:2px
```

## Data Import Process

```mermaid
sequenceDiagram
    participant CSV as CSV Files
    participant Script as import_csvs.py
    participant Pandas as pandas
    participant PG as PostgreSQL
    participant AGE as Apache AGE
    participant Vol as Docker Volume

    Note over CSV,Vol: Phase 1: Node Import
    CSV->>Script: Read CSV files
    Script->>Pandas: Parse with pandas
    Pandas->>Script: Return DataFrame
    
    loop For each node CSV
        Script->>PG: Create table (if not exists)
        Script->>PG: INSERT INTO table
        Script->>AGE: CREATE (node:Label {...})
    end
    
    PG->>Vol: Persist data
    AGE->>Vol: Persist graph
    
    Note over CSV,Vol: Phase 2: Edge Import
    
    loop For each edge CSV
        Script->>PG: Create relationship table
        Script->>PG: INSERT INTO table
        Script->>AGE: MATCH + CREATE edge
    end
    
    PG->>Vol: Persist relationships
    AGE->>Vol: Persist graph edges
    
    Note over Script,Vol: Import Complete!
```

## Database Structure

```mermaid
erDiagram
    Exo ||--o{ HAS_AIM : "has"
    Exo ||--o{ ASSISTS_IN : "assists in"
    Exo ||--o{ HAS_PROPERTY : "has"
    Exo ||--o{ TRANSFERS_FORCES_TO : "transfers to"
    Exo ||--o{ TRANSFERS_FORCES_FROM : "transfers from"
    Exo ||--o{ HAS_AIM_SKN : "has"
    Exo ||--o{ LIMITS_IN : "limits"
    Exo ||--o{ GIVES_RESISTANCE_IN : "gives resistance"
    Exo ||--o{ GIVES_POSTURAL_SUPPORT_IN : "supports"
    
    Aim ||--o{ HAS_AIM : "is aim of"
    Aim ||--o{ HAS_AIMTYPE : "has type"
    
    Dof ||--o{ ASSISTS_IN : "is assisted"
    Dof ||--o{ LIMITS_IN : "is limited"
    Dof ||--o{ GIVES_RESISTANCE_IN : "has resistance"
    Dof ||--o{ GIVES_POSTURAL_SUPPORT_IN : "is supported"
    Dof ||--o{ HAS_DOF : "belongs to"
    
    JointT ||--o{ HAS_DOF : "has"
    JointT ||--o{ IS_CONNECTED_WITH : "connected to"
    
    Part ||--o{ TRANSFERS_FORCES_TO : "receives force"
    Part ||--o{ TRANSFERS_FORCES_FROM : "gives force"
    Part ||--o{ IS_CONNECTED_WITH : "connects to"
    
    StructureKinematicName ||--o{ HAS_AIM_SKN : "has aim"
    StructureKinematicName ||--o{ HAS_SKNTYPE : "has type"
    
    ExoProperty ||--o{ HAS_PROPERTY : "property of"
    AimType ||--o{ HAS_AIMTYPE : "type of"
    StructureKinematicNameType ||--o{ HAS_SKNTYPE : "type of"
    
    Exo {
        int _id PK
        string exoName
        string exoManufacturer
        string exoMaterial
        string exoActivePassive
        string exoDescription
    }
    
    Aim {
        int _id PK
        string aimDescription
    }
    
    Dof {
        int _id PK
        string dofDescription
    }
    
    HAS_AIM {
        int exoId FK
        int aimId FK
        string aimCategory
    }
    
    ASSISTS_IN {
        int exoId FK
        int dofId FK
        string aim
        string direction
        string rangeAdjustable
    }
```

## Query Flow

```mermaid
graph LR
    subgraph UserQueries["User Queries"]
        A1[SQL Query]
        A2[Cypher Query]
        A3[Python Script]
    end
    
    subgraph pgAdmin["pgAdmin Interface"]
        B1[Query Tool]
    end
    
    subgraph Database["PostgreSQL Database"]
        C1[PostgreSQL Tables]
        C2[AGE Graph]
    end
    
    subgraph Results["Query Results"]
        D1[Tabular Data]
        D2[Graph Patterns]
        D3[JSON/Dict]
    end
    
    A1 --> B1
    A2 --> B1
    A3 --> C1
    A3 --> C2
    
    B1 --> C1
    B1 --> C2
    
    C1 --> D1
    C2 --> D2
    A3 --> D3
    
    style UserQueries fill:#e1f5ff
    style pgAdmin fill:#fff3cd
    style Database fill:#f8d7da
    style Results fill:#d4edda
```

## Docker Compose Architecture

```mermaid
graph TB
    subgraph DockerHost["Docker Host Machine"]
        subgraph Network["Docker Network: test_cicd_mobilab_default"]
            subgraph PG["Container: age-postgres"]
                PG1[PostgreSQL Server<br/>Port 5432]
                PG2[Apache AGE Extension]
                PG3[Database: testdb]
            end
            
            subgraph PA["Container: pgadmin"]
                PA1[pgAdmin Web Server<br/>Port 80]
                PA2[Connected to postgres:5432]
            end
        end
        
        subgraph Volumes["Docker Volumes"]
            V1[(pgdata<br/>Persistent Storage)]
        end
        
        subgraph Ports["Port Mapping"]
            P1[Host:5432 → Container:5432]
            P2[Host:8080 → Container:80]
        end
    end
    
    subgraph External["External Access"]
        E1[localhost:5432<br/>PostgreSQL]
        E2[localhost:8080<br/>pgAdmin]
        E3[Python Scripts]
    end
    
    PG --> PA
    PG3 --> V1
    
    P1 --> PG1
    P2 --> PA1
    
    E1 --> P1
    E2 --> P2
    E3 --> E1
    
    style PG fill:#cfe2ff
    style PA fill:#f8d7da
    style Volumes fill:#d1ecf1
    style External fill:#d4edda
```

