# Project Setup Guide

Deze handleiding beschrijft hoe je het project lokaal kunt opzetten en gebruiken.

## Vereisten

- **Docker Desktop** (voor PostgreSQL en pgAdmin containers)
- **Python 3.12** of hoger
- **Git** (optioneel, voor version control)

## Stap 0: Software Installeren

### Docker Desktop Installeren

Docker Desktop is nodig om de PostgreSQL en pgAdmin containers te kunnen draaien.

#### Windows

1. Download Docker Desktop voor Windows van [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Voer het installer bestand uit (`Docker Desktop Installer.exe`)
3. Volg de installatie wizard:
   - Accepteer de licentievoorwaarden
   - Kies "Use WSL 2 instead of Hyper-V" (aanbevolen)
4. Start je computer opnieuw op na installatie
5. Start Docker Desktop vanuit het Start menu
6. Wacht tot Docker volledig gestart is (groen icoontje in systray)

**Verificatie:**
```powershell
docker --version
docker-compose --version
```

**Vereisten voor Windows:**
- Windows 10 64-bit: Pro, Enterprise, of Education (Build 19041 of hoger)
- OF Windows 11 64-bit: Home, Pro, Enterprise, of Education
- WSL 2 moet geïnstalleerd zijn (Docker Desktop installeert dit automatisch)

#### macOS

1. Download Docker Desktop voor Mac van [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
2. Open het `.dmg` bestand
3. Sleep Docker naar de Applications folder
4. Start Docker vanuit Applications
5. Geef de benodigde permissies (wachtwoord vereist)

**Verificatie:**
```bash
docker --version
docker-compose --version
```

**Vereisten voor macOS:**
- macOS 11 (Big Sur) of nieuwer
- Apple Silicon (M1/M2) of Intel processor

#### Linux (Ubuntu/Debian)

```bash
# Update package index
sudo apt-get update

# Installeer vereiste packages
sudo apt-get install ca-certificates curl gnupg lsb-release

# Voeg Docker's official GPG key toe
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Setup repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installeer Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Voeg je gebruiker toe aan docker group (om sudo te vermijden)
sudo usermod -aG docker $USER

# Log opnieuw in of herstart je sessie
newgrp docker
```

**Verificatie:**
```bash
docker --version
docker compose version
```

### Python Installeren

#### Windows

**Optie 1: Van python.org**
1. Download Python 3.12 van [python.org/downloads](https://www.python.org/downloads/)
2. Voer het installer bestand uit
3. **Belangrijk:** Vink "Add Python to PATH" aan onderaan het installatie scherm
4. Klik op "Install Now"
5. Wacht tot installatie compleet is

**Optie 2: Via Microsoft Store**
1. Open Microsoft Store
2. Zoek naar "Python 3.12"
3. Klik op "Get" of "Install"

**Verificatie:**
```powershell
python --version
pip --version
```

Als `python` niet werkt, probeer `py`:
```powershell
py --version
py -m pip --version
```

#### macOS

**Optie 1: Via Homebrew (aanbevolen)**
```bash
# Installeer Homebrew eerst (als je het nog niet hebt)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installeer Python
brew install python@3.12
```

**Optie 2: Van python.org**
1. Download Python 3.12 voor macOS van [python.org/downloads](https://www.python.org/downloads/)
2. Open het `.pkg` bestand
3. Volg de installatie wizard

**Verificatie:**
```bash
python3 --version
pip3 --version
```

#### Linux (Ubuntu/Debian)

```bash
# Update package index
sudo apt-get update

# Installeer Python 3.12
sudo apt-get install python3.12 python3.12-venv python3-pip

# Maak python3.12 de standaard (optioneel)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
```

**Verificatie:**
```bash
python3 --version
pip3 --version
```

### Git Installeren (Optioneel)

#### Windows

1. Download Git van [git-scm.com/download/win](https://git-scm.com/download/win)
2. Voer de installer uit
3. Gebruik de standaard instellingen (of pas aan naar voorkeur)
4. Kies een teksteditor naar keuze (bijv. VS Code, Notepad++)

**Verificatie:**
```powershell
git --version
```

#### macOS

**Via Homebrew:**
```bash
brew install git
```

**Via Xcode Command Line Tools:**
```bash
xcode-select --install
```

**Verificatie:**
```bash
git --version
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install git
```

**Verificatie:**
```bash
git --version
```

### Git Configuratie (Eerste keer)

```bash
# Configureer je naam en email
git config --global user.name "Jouw Naam"
git config --global user.email "jouw.email@example.com"

# Verificeer configuratie
git config --list
```

## Stap 1: Docker Containers Opzetten

Het project gebruikt Docker Compose om PostgreSQL (met Apache AGE) en pgAdmin te beheren.

### Docker Compose Starten

Zorg dat je in de project directory bent en start de containers:

```bash
docker-compose up -d
```

Dit start beide containers op de achtergrond met de volgende configuratie:
- **PostgreSQL (Apache AGE):**
  - Container naam: `age-postgres`
  - Port: `5432`
  - Database: `testdb`
  - Gebruiker: `admin`
  - Wachtwoord: `admin1234`
  - Data persistentie via volume `pgdata`

- **pgAdmin:**
  - Container naam: `pgadmin`
  - Port: `8080` (toegankelijk via `http://localhost:8080`)
  - Email: `admin@admin.com`
  - Wachtwoord: `admin1234`

### Containers Verifiëren

Controleer of beide containers draaien:

```bash
docker-compose ps
```

Of gebruik:
```bash
docker ps
```

Je zou twee containers moeten zien: `age-postgres` en `pgadmin`.

### Logs Bekijken

Als je problemen ondervindt, bekijk dan de logs:

```bash
# Alle services
docker-compose logs

# Alleen PostgreSQL
docker-compose logs postgres

# Alleen pgAdmin
docker-compose logs pgadmin

# Follow mode (real-time)
docker-compose logs -f
```

## Stap 2: pgAdmin Configureren

1. Open je browser en ga naar `http://localhost:8080`
2. Log in met:
   - Email: `admin@admin.com`
   - Wachtwoord: `admin1234`
3. Voeg een nieuwe server toe:
   - Rechtermuisklik op "Servers" → "Register" → "Server"
   - **General tab:**
     - Name: `PostgreSQL AGE Local`
   - **Connection tab:**
     - Host: `postgres` (dit is de service naam in docker-compose)
     - Port: `5432`
     - Database: `testdb`
     - Username: `admin`
     - Password: `admin1234`
     - Save password: ✓
4. Klik op "Save"

**Let op:** Omdat beide containers in hetzelfde Docker netwerk draaien (via docker-compose), gebruik je `postgres` als hostname in plaats van `localhost` of `host.docker.internal`.

## Stap 3: Python Environment Opzetten

### Virtual Environment Aanmaken

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Dependencies Installeren

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

De volgende packages worden geïnstalleerd:
- `psycopg2-binary` - PostgreSQL database adapter
- `pandas` - CSV data processing
- `python-dotenv` - Environment variables
- `pytest` - Testing framework
- `unittest-xml-reporting` - Test reporting

## Stap 4: Environment Variabelen Configureren

Maak een `.env` bestand aan in de root van het project:

```bash
# Database configuratie (moet overeenkomen met docker-compose.yml)
DB_USER=admin
DB_PASSWORD=admin1234
DB_HOST=localhost
DB_PORT=5432
DB_NAME=testdb

# CSV directory (absoluut pad of relatief)
CSV_DIR=./csv

# Neo4j (optioneel - laat leeg als je alleen AGE gebruikt)
NEO4J_URI=
NEO4J_USER=
NEO4J_PASSWORD=
```

**Let op:** Deze waarden komen overeen met de configuratie in `docker-compose.yml`. Vanaf je lokale machine (buiten Docker) gebruik je `localhost` als host.

## Stap 5: Database Schema Initialiseren (Optioneel)

Als je het schema handmatig wilt aanmaken (niet nodig voor de import):

```bash
# Via psql command line
docker exec -it age-postgres psql -U admin -d testdb -f schema.sql
```

Of voer het `schema.sql` bestand uit via pgAdmin:
1. Open pgAdmin
2. Navigeer naar je server → Databases → exo_database
3. Open Query Tool
4. Plak de inhoud van `schema.sql` en voer uit

## Stap 6: CSV Import Uitvoeren

### CSV Bestanden Controleren

Zorg dat alle CSV bestanden aanwezig zijn in de `csv/` directory:

```bash
ls csv/
```

Je zou 24 CSV bestanden moeten zien (9 node types en 15 relatie types).

### Import Script Uitvoeren

```bash
python import_csvs.py
```

De import voert de volgende stappen uit:
1. **Bestaande data wissen** - Verwijdert oude AGE graph en PostgreSQL tabellen
2. **Nieuwe graph aanmaken** - Maakt een verse `exo_graph`
3. **FASE 1: Nodes importeren** - Importeert alle entiteiten (Exo, Aim, Dof, etc.)
4. **FASE 2: Edges importeren** - Maakt relaties tussen entiteiten

**Verwachte output:**
```
Clearing AGE graph 'exo_graph'...
AGE graph cleared successfully!
AGE graph 'exo_graph' created successfully!

============================================================
PHASE 1: Creating all nodes
============================================================

Processing file: Aim.csv
Created PostgreSQL table: Aim
Inserting 20 nodes for table: Aim
[OK] Successfully inserted 20 nodes into PostgreSQL and AGE

...

[OK] Imported into AGE successfully!
```

## Stap 7: Data Verifiëren

### Via pgAdmin

1. Open pgAdmin en navigeer naar je database
2. Open Query Tool
3. Voer AGE setup commands uit:

```sql
LOAD 'age';
SET search_path = ag_catalog, "$user", public;
```

### Test Queries

**PostgreSQL tabellen (met individuele kolommen):**
```sql
-- Bekijk alle exoskeletten
SELECT _id, exoName, exoManufacturer, exoActivePassive 
FROM Exo 
LIMIT 5;

-- Tel aantal records
SELECT COUNT(*) FROM Exo;
SELECT COUNT(*) FROM Aim;
SELECT COUNT(*) FROM HAS_AIM;
```

**AGE Graph queries:**
```sql
-- Tel alle nodes in de graph
SELECT * FROM cypher('exo_graph', $$
    MATCH (n)
    RETURN count(n) as node_count
$$) AS (node_count agtype);

-- Vind exoskeletten met hun doelstellingen
SELECT * FROM cypher('exo_graph', $$
    MATCH (e:Exo)-[:HAS_AIM]->(a:Aim)
    RETURN e.exoName, a.aimDescription
    LIMIT 10
$$) AS (exo_name agtype, aim_description agtype);
```

**JOINs tussen PostgreSQL tabellen:**
```sql
-- Exoskeletten met hun doelstellingen
SELECT e.exoName, a."aimDescription"
FROM Exo e
JOIN HAS_AIM ha ON e._id = ha.exoId
JOIN Aim a ON ha.aimId = a._id
LIMIT 10;
```

## Stap 8: Unit Tests Uitvoeren

Het project bevat unit tests om de import te verifiëren:

```bash
python -m pytest test_csv_import.py -v
```

**Verwachte output:**
```
test_csv_import.py::test_database_connection PASSED
test_csv_import.py::test_csv_files_exist PASSED
test_csv_import.py::test_import_script_exists PASSED
...
```

## Troubleshooting

### Docker Container Start Niet

**Probleem:** Port 5432 of 8080 is al in gebruik
```bash
# Bekijk welke containers draaien
docker ps

# Stop conflicterende containers
docker stop <container-name>

# Of wijzig de ports in docker-compose.yml
```
Als je de ports wijzigt in `docker-compose.yml`, update dan ook `DB_PORT` in je `.env` bestand.

### pgAdmin Kan Niet Verbinden met PostgreSQL

**Probleem:** Connection refused

- **Vanuit pgAdmin container:** Gebruik `postgres` als hostname (service naam)
- **Vanuit je lokale machine:** Gebruik `localhost`
- **Controleer of containers in hetzelfde netwerk zitten:**
  ```bash
  docker network inspect test_cicd_mobilab_default
  ```

### Import Script Geeft Errors

**Probleem:** AGE extensie niet geladen
- Zorg dat je de `apache/age` image gebruikt (niet de standaard postgres image)
- Verifieer met: `docker exec -it age-postgres psql -U admin -d testdb -c "SELECT * FROM pg_extension WHERE extname='age';"`

**Probleem:** CSV delimiter errors
- De script detecteert automatisch `;` of `,` als delimiter
- Controleer of CSV bestanden geen mixed delimiters bevatten

### Python Dependencies Installeren Mislukt

**Windows:** Mogelijk probleem met psycopg2
```bash
pip install psycopg2-binary --no-cache-dir
```

## Project Structure

```
test_cicd_mobilab/
├── csv/                          # CSV data bestanden
│   ├── Exo.csv
│   ├── Aim.csv
│   └── ...
├── import_csvs.py                # Hoofdscript voor data import
├── test_csv_import.py            # Unit tests
├── requirements.txt              # Python dependencies
├── schema.sql                    # Database schema (optioneel)
├── .env                          # Environment variables (maak zelf aan)
├── .github/workflows/            # CI/CD configuratie
│   └── import_csv.yml
└── README.md                     # Project documentatie
```

## Handige Docker Compose Commands

```bash
# Containers starten
docker-compose up -d

# Containers stoppen (behoud data)
docker-compose stop

# Containers stoppen en verwijderen (behoud volumes)
docker-compose down

# Containers, netwerken én volumes verwijderen (ALLE DATA WEG!)
docker-compose down -v

# Containers herstarten
docker-compose restart

# Specifieke service herstarten
docker-compose restart postgres

# Status bekijken
docker-compose ps

# Logs bekijken
docker-compose logs
docker-compose logs -f postgres  # follow mode voor specifieke service

# PostgreSQL CLI openen
docker exec -it age-postgres psql -U admin -d testdb

# Container shell openen
docker exec -it age-postgres bash
```

## Database Reset

Als je de database volledig opnieuw wilt opzetten:

### Optie 1: Alleen data wissen (containers behouden)
```bash
# Het import script wist automatisch bestaande data
python import_csvs.py
```

### Optie 2: Volledige reset (containers en volumes verwijderen)
```bash
# Stop en verwijder containers + volumes (ALLE DATA WEG!)
docker-compose down -v

# Start containers opnieuw
docker-compose up -d

# Voer import opnieuw uit
python import_csvs.py
```

### Optie 3: Alleen containers herstarten (data behouden)
```bash
# Herstart services
docker-compose restart

# Of stop en start opnieuw
docker-compose down
docker-compose up -d
```

## Volgende Stappen

- **Query Development:** Ontwikkel complexe graph queries met AGE
- **API Development:** Bouw een REST API bovenop de database
- **Visualisatie:** Gebruik tools zoals Neo4j Browser (als je Neo4j ook gebruikt)
- **CI/CD:** GitHub Actions workflow is al geconfigureerd in `.github/workflows/import_csv.yml`

## Applicatie Flow & Data Transfer

### Visuele Diagrammen

Voor interactieve en kleurrijke diagrammen, zie: **[docs/architecture-diagram.md](docs/architecture-diagram.md)**

De diagrammen bevatten:
- 🎯 **Flow Diagram** - Complete data flow van CSV naar database
- 📊 **Sequence Diagram** - Stap-voor-stap import proces
- 🗄️ **ER Diagram** - Database relaties en structuur
- 🔍 **Query Flow** - Hoe queries worden verwerkt
- 🐳 **Docker Architecture** - Container setup en networking

> **Tip:** Open `docs/architecture-diagram.md` in een Markdown viewer die Mermaid diagrams ondersteunt (zoals GitHub, VS Code met Markdown Preview, of online tools zoals [Mermaid Live Editor](https://mermaid.live/))

### Text-Based Overzicht

Hieronder staat een text-based overzicht van hoe de applicatie en data import werkt:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          PROJECT ARCHITECTURE                            │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   CSV Bestanden  │
│   (csv/ folder)  │
│                  │
│ • Exo.csv        │
│ • Aim.csv        │
│ • Dof.csv        │
│ • HAS_AIM.csv    │
│ • ASSISTS_IN.csv │
│ • ... (24 files) │
└────────┬─────────┘
         │
         │ 1. Read CSV files
         │    (pandas)
         ▼
┌──────────────────┐
│ import_csvs.py   │◄─────── .env (configuratie)
│                  │         • DB_USER=admin
│  Python Script   │         • DB_PASSWORD=admin1234
│                  │         • DB_HOST=localhost
│ • Load .env      │         • DB_NAME=testdb
│ • Connect to DB  │         • CSV_DIR=./csv
│ • Parse CSVs     │
│ • Insert data    │
└────────┬─────────┘
         │
         │ 2. Database Connection
         │    (psycopg2)
         ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                       DOCKER CONTAINERS                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  PostgreSQL + Apache AGE Container (age-postgres)                   │ │
│  │  Port: 5432                                                         │ │
│  │                                                                     │ │
│  │  ┌─────────────────────────────────────────────────────────────┐   │ │
│  │  │                    Database: testdb                         │   │ │
│  │  │                                                             │   │ │
│  │  │  ┌──────────────────────────────────────────────────────┐  │   │ │
│  │  │  │   PostgreSQL Tables (Relational Data)                │  │   │ │
│  │  │  │                                                       │  │   │ │
│  │  │  │   Exo Table:                                         │  │   │ │
│  │  │  │   ┌────┬──────────┬───────────────┬──────────────┐  │  │   │ │
│  │  │  │   │ _id│ exoName  │ exoManufacturer│ exoMaterial │  │  │   │ │
│  │  │  │   ├────┼──────────┼───────────────┼──────────────┤  │  │   │ │
│  │  │  │   │ 40 │CarrySuit │ Auxivo        │ harde mat.  │  │  │   │ │
│  │  │  │   │ 41 │Paexo     │ Ottobock      │ harde mat.  │  │  │   │ │
│  │  │  │   └────┴──────────┴───────────────┴──────────────┘  │  │   │ │
│  │  │  │                                                       │  │   │ │
│  │  │  │   HAS_AIM Table:                                     │  │   │ │
│  │  │  │   ┌────────┬────────┬──────────────┐                │  │   │ │
│  │  │  │   │ exoId  │ aimId  │ aimCategory  │                │  │   │ │
│  │  │  │   ├────────┼────────┼──────────────┤                │  │   │ │
│  │  │  │   │   40   │   1    │  primary     │                │  │   │ │
│  │  │  │   └────────┴────────┴──────────────┘                │  │   │ │
│  │  │  │                                                       │  │   │ │
│  │  │  │   + 22 andere tabellen...                            │  │   │ │
│  │  │  └───────────────────────────────────────────────────────┘  │   │ │
│  │  │                                                             │   │ │
│  │  │  ┌──────────────────────────────────────────────────────┐  │   │ │
│  │  │  │   Apache AGE Graph (exo_graph)                       │  │   │ │
│  │  │  │                                                       │  │   │ │
│  │  │  │        (Exo)──[HAS_AIM]──>(Aim)                      │  │   │ │
│  │  │  │          │                                            │  │   │ │
│  │  │  │          ├─[ASSISTS_IN]──>(Dof)                      │  │   │ │
│  │  │  │          │                                            │  │   │ │
│  │  │  │          ├─[HAS_PROPERTY]──>(ExoProperty)            │  │   │ │
│  │  │  │          │                                            │  │   │ │
│  │  │  │          └─[TRANSFERS_FORCES_TO]──>(Part)            │  │   │ │
│  │  │  │                                                       │  │   │ │
│  │  │  │   Graph voor complexe relationship queries           │  │   │ │
│  │  │  └───────────────────────────────────────────────────────┘  │   │ │
│  │  └─────────────────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  pgAdmin Container (pgadmin)                                        │ │
│  │  Port: 8080                                                         │ │
│  │                                                                     │ │
│  │  Web Interface: http://localhost:8080                              │ │
│  │  • Query Tool                                                      │ │
│  │  • Database Browser                                                │ │
│  │  • Visual Management                                               │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
│  Docker Network: test_cicd_mobilab_default                               │
│  Volume: pgdata (persistent storage)                                     │
└──────────────────────────────────────────────────────────────────────────┘
         │
         │ 3. Query Data
         ▼
┌──────────────────┐
│   Gebruiker      │
│                  │
│ Via pgAdmin:     │
│ • SQL Queries    │
│ • AGE Cypher     │
│ • JOINs          │
│                  │
│ Via Python:      │
│ • psycopg2       │
│ • pandas         │
│ • API calls      │
└──────────────────┘

═══════════════════════════════════════════════════════════════════════════
                            DATA FLOW DETAILS
═══════════════════════════════════════════════════════════════════════════

FASE 1: NODES (Entiteiten)
──────────────────────────
CSV File → pandas DataFrame → Python Dict → PostgreSQL Table + AGE Graph Node

Example: Exo.csv
┌─────────────────────────────────────────────────────┐
│ _id; exoName; exoManufacturer; exoMaterial         │
│  40; CarrySuit; Auxivo; harde materialen            │
└─────────────────────────────────────────────────────┘
                    ↓
         insert_row_postgres()  +  insert_node_age()
                    ↓
┌─────────────────────────────────────────────────────┐
│ PostgreSQL Table: Exo                               │
│ Columns: _id | exoName | exoManufacturer | ...     │
└─────────────────────────────────────────────────────┘
                    +
┌─────────────────────────────────────────────────────┐
│ AGE Graph Node:                                     │
│ (:Exo {_id: 40, exoName: "CarrySuit", ...})        │
└─────────────────────────────────────────────────────┘

FASE 2: EDGES (Relaties)
─────────────────────────
CSV File → pandas DataFrame → Python Dict → PostgreSQL Table + AGE Graph Edge

Example: HAS_AIM.csv
┌──────────────────────────────────────┐
│ exoId; aimId; aimCategory            │
│   40;    1;   primary                │
└──────────────────────────────────────┘
                    ↓
         insert_row_postgres()  +  insert_edge_age()
                    ↓
┌──────────────────────────────────────┐
│ PostgreSQL Table: HAS_AIM            │
│ Columns: exoId | aimId | aimCategory │
└──────────────────────────────────────┘
                    +
┌──────────────────────────────────────┐
│ AGE Graph Edge:                      │
│ (Exo)-[:HAS_AIM {aimCategory: ...}]->(Aim) │
└──────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════
                         QUERY POSSIBILITIES
═══════════════════════════════════════════════════════════════════════════

1. REGULAR SQL (PostgreSQL Tables)
   ↓
   SELECT e.exoName, a.aimDescription
   FROM Exo e
   JOIN HAS_AIM ha ON e._id = ha.exoId
   JOIN Aim a ON ha.aimId = a._id;

2. GRAPH QUERIES (Apache AGE)
   ↓
   SELECT * FROM cypher('exo_graph', $$
       MATCH (e:Exo)-[:HAS_AIM]->(a:Aim)
       RETURN e.exoName, a.aimDescription
   $$) AS (exo_name agtype, aim_description agtype);

3. COMPLEX GRAPH PATTERNS
   ↓
   Find all paths between nodes, shortest paths,
   multi-hop relationships, pattern matching, etc.
```

### Key Points:

1. **Dual Storage:** Data wordt opgeslagen in zowel PostgreSQL tabellen (voor SQL) als AGE graph (voor graph queries)
2. **Single Import:** Het `import_csvs.py` script zorgt voor beide in één keer
3. **Persistent Data:** Docker volume `pgdata` bewaart alle data, zelfs na container restart
4. **Network Isolation:** Containers communiceren via Docker network
5. **Flexible Querying:** Gebruik SQL voor relationele queries, Cypher voor graph patterns

## Support

Voor vragen of problemen, raadpleeg:
- [Apache AGE Documentatie](https://age.apache.org/)
- [PostgreSQL Documentatie](https://www.postgresql.org/docs/)
- [pgAdmin Documentatie](https://www.pgadmin.org/docs/)
