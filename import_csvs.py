import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from neo4j import GraphDatabase
import sys
from datetime import datetime

# === Log everything printed to terminal ===
log_filename = f"import_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

class Tee(object):
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()

log_file = open(log_filename, "w", encoding="utf-8")
sys.stdout = Tee(sys.stdout, log_file)
sys.stderr = Tee(sys.stderr, log_file)

load_dotenv()

# === Database configuration ===
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME')
CSV_DIR = os.getenv('CSV_DIR')

# === Neo4j config ===
neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

# === Try to connect to Neo4j (optional) ===
neo4j_available = False
neo4j_driver = None

if neo4j_uri and neo4j_user and neo4j_password:
    try:
        neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        print("Clearing Neo4j database...")
        with neo4j_driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("Neo4j database cleared successfully!")
        neo4j_available = True
    except Exception as e:
        print(f"⚠ Warning: Could not connect to Neo4j: {e}")
        print("Continuing with AGE only...")
        neo4j_driver = None
else:
    print("⚠ Neo4j credentials not configured. Continuing with AGE only...")

# === Connect to PostgreSQL/AGE ===
conn = psycopg2.connect(
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port,
    database=db_name,
    sslmode='disable',
    connect_timeout=10
)
cur = conn.cursor()

# === Enable AGE and check if graph exists ===
cur.execute("LOAD 'age';")
cur.execute("SET search_path = ag_catalog, \"$user\", public;")
cur.execute("SELECT count(*) FROM ag_catalog.ag_graph WHERE name = %s;", ('exo_graph',))
row = cur.fetchone()
graph_exists = bool(row and row[0])

# === Clear AGE graph if it exists ===
if graph_exists:
    print("Clearing AGE graph 'exo_graph'...")
    cur.execute("SELECT drop_graph('exo_graph', true);")
    conn.commit()
    print("AGE graph cleared successfully!")

# === Create fresh graph ===
cur.execute("SELECT create_graph('exo_graph');")
conn.commit()
print("AGE graph 'exo_graph' created successfully!")

# === Helpers ===
MAIN_TABLES = [
    "Aim", "AimType", "Dof", "Exo", "ExoProperty", "JointT", 
    "Part", "StructureKinematicName", "StructureKinematicNameType"
]
INTERMEDIATE_TABLES = [
    "ASSISTS_IN", "DOESNT_GO_WITH", "GIVES_POSTURAL_SUPPORT_IN", 
    "GIVES_RESISTANCE_IN", "HAS_AIM", "HAS_AIM_SKN", "HAS_AIMTYPE", 
    "HAS_AS_MAIN_DOF", "HAS_DOF", "HAS_PROPERTY", "HAS_SKNTYPE", 
    "IS_CONNECTED_WITH", "LIMITS_IN", "TRANSFERS_FORCES_FROM", 
    "TRANSFERS_FORCES_TO"
]

# === AGE insert ===
def insert_node_age(table_name, row):
    props = ', '.join([f"{k}: {format_age_value(v)}" for k, v in row.items()])
    cypher = f"SELECT * FROM cypher('exo_graph', $$ CREATE (:{table_name} {{{props}}}) $$) AS (n agtype);"
    cur.execute(cypher)

def format_age_value(value):
    """Format value for AGE Cypher query - handle None, numbers, and strings properly."""
    if pd.isna(value) or value == '' or value is None:
        return 'null'
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        # Escape single quotes in strings and wrap in quotes
        return f"'{str(value).replace(chr(39), chr(92)+chr(39))}'"

def insert_edge_age(table_name, row):
    """Insert an edge based on foreign keys in AGE."""
    DEBUG = False  # Set to True to see generated queries
    
    try:
        if table_name == "GIVES_POSTURAL_SUPPORT_IN":
            cypher = f"""
            MATCH (e:Exo), (d:Dof)
            WHERE e._id = {format_age_value(row['exoId'])} AND d._id = {format_age_value(row['dofId'])}
            CREATE (e)-[:GIVES_POSTURAL_SUPPORT_IN {{aim: {format_age_value(row.get('aim'))}, adjustable: {format_age_value(row.get('adjustable'))}, mechanism: {format_age_value(row.get('mechanism'))}, direction: {format_age_value(row.get('direction'))}}}]->(d)
            """
        elif table_name == "TRANSFERS_FORCES_FROM":
            cypher = f"""
            MATCH (e:Exo), (p:Part)
            WHERE e._id = {format_age_value(row['exoId'])} AND p._id = {format_age_value(row['partId'])}
            CREATE (e)-[:TRANSFERS_FORCES_FROM]->(p)
            """
        elif table_name == "TRANSFERS_FORCES_TO":
            cypher = f"""
            MATCH (e:Exo), (p:Part)
            WHERE e._id = {format_age_value(row['exoId'])} AND p._id = {format_age_value(row['partId'])}
            CREATE (e)-[:TRANSFERS_FORCES_TO]->(p)
            """
        elif table_name == "HAS_AIM":
            cypher = f"""
            MATCH (e:Exo), (a:Aim)
            WHERE e._id = {format_age_value(row['exoId'])} AND a._id = {format_age_value(row['aimId'])}
            CREATE (e)-[:HAS_AIM {{aimCategory: {format_age_value(row.get('aimCategory'))}}}]->(a)
            """
        elif table_name == "HAS_AIM_SKN":
            cypher = f"""
            MATCH (e:Exo), (s:StructureKinematicName)
            WHERE e._id = {format_age_value(row['exoId'])} AND s._id = {format_age_value(row['sknId'])}
            CREATE (e)-[:HAS_AIM_SKN {{structureKinematicNameCategory: {format_age_value(row.get('structureKinematicNameCategory'))}}}]->(s)
            """
        elif table_name == "HAS_PROPERTY":
            cypher = f"""
            MATCH (e:Exo), (p:ExoProperty)
            WHERE e._id = {format_age_value(row['exoId'])} AND p._id = {format_age_value(row['exoPropertyId'])}
            CREATE (e)-[:HAS_PROPERTY {{exoPropertyValue: {format_age_value(row.get('exoPropertyValue'))}}}]->(p)
            """
        elif table_name == "ASSISTS_IN":
            cypher = f"""
            MATCH (e:Exo), (d:Dof)
            WHERE e._id = {format_age_value(row['exoId'])} AND d._id = {format_age_value(row['dofId'])}
            CREATE (e)-[:ASSISTS_IN {{aim: {format_age_value(row.get('aim'))}, rangeAdjustable: {format_age_value(row.get('rangeAdjustable'))}, lowerBoundMinAngle: {format_age_value(row.get('lowerBoundMinAngle'))}, lowerBoundMaxAngle: {format_age_value(row.get('lowerBoundMaxAngle'))}, upperBoundMinAngle: {format_age_value(row.get('upperBoundMinAngle'))}, upperBoundMaxAngle: {format_age_value(row.get('upperBoundMaxAngle'))}, sizeAdjustable: {format_age_value(row.get('sizeAdjustable'))}, direction: {format_age_value(row.get('direction'))}}}]->(d)
            """
        elif table_name == "DOESNT_GO_WITH":
            cypher = f"""
            MATCH (e:Exo), (s:StructureKinematicName)
            WHERE e._id = {format_age_value(row['exoId'])} AND s._id = {format_age_value(row['sknId'])}
            CREATE (e)-[:DOESNT_GO_WITH]->(s)
            """
        elif table_name == "GIVES_RESISTANCE_IN":
            cypher = f"""
            MATCH (e:Exo), (d:Dof)
            WHERE e._id = {format_age_value(row['exoId'])} AND d._id = {format_age_value(row['dofId'])}
            CREATE (e)-[:GIVES_RESISTANCE_IN {{aim: {format_age_value(row.get('aim'))}, rangeAdjustable: {format_age_value(row.get('rangeAdjustable'))}, lowerBoundMinAngle: {format_age_value(row.get('lowerBoundMinAngle'))}, lowerBoundMaxAngle: {format_age_value(row.get('lowerBoundMaxAngle'))}, upperBoundMinAngle: {format_age_value(row.get('upperBoundMinAngle'))}, upperBoundMaxAngle: {format_age_value(row.get('upperBoundMaxAngle'))}, sizeAdjustable: {format_age_value(row.get('sizeAdjustable'))}, direction: {format_age_value(row.get('direction'))}}}]->(d)
            """
        elif table_name == "HAS_AIMTYPE":
            cypher = f"""
            MATCH (a:Aim), (at:AimType)
            WHERE a._id = {format_age_value(row['aimId'])} AND at._id = {format_age_value(row['aimTypeId'])}
            CREATE (a)-[:HAS_AIMTYPE]->(at)
            """
        elif table_name == "HAS_AS_MAIN_DOF":
            cypher = f"""
            MATCH (e:Exo), (d:Dof)
            WHERE e._id = {format_age_value(row['exoId'])} AND d._id = {format_age_value(row['dofId'])}
            CREATE (e)-[:HAS_AS_MAIN_DOF]->(d)
            """
        elif table_name == "HAS_DOF":
            cypher = f"""
            MATCH (j:JointT), (d:Dof)
            WHERE j._id = {format_age_value(row['jointTId'])} AND d._id = {format_age_value(row['dofId'])}
            CREATE (j)-[:HAS_DOF]->(d)
            """
        elif table_name == "HAS_SKNTYPE":
            cypher = f"""
            MATCH (s:StructureKinematicName), (st:StructureKinematicNameType)
            WHERE s._id = {format_age_value(row['sknId'])} AND st._id = {format_age_value(row['sknTypeId'])}
            CREATE (s)-[:HAS_SKNTYPE]->(st)
            """
        elif table_name == "IS_CONNECTED_WITH":
            cypher = f"""
            MATCH (j:JointT), (p:Part)
            WHERE j._id = {format_age_value(row['jointTId'])} AND p._id = {format_age_value(row['partId'])}
            CREATE (j)-[:IS_CONNECTED_WITH]->(p)
            """
        elif table_name == "LIMITS_IN":
            cypher = f"""
            MATCH (e:Exo), (d:Dof)
            WHERE e._id = {format_age_value(row['exoId'])} AND d._id = {format_age_value(row['dofId'])}
            CREATE (e)-[:LIMITS_IN {{aim: {format_age_value(row.get('aim'))}, maxAngle: {format_age_value(row.get('maxAngle'))}, minAngle: {format_age_value(row.get('minAngle'))}, adjustable: {format_age_value(row.get('adjustable'))}, direction: {format_age_value(row.get('direction'))}}}]->(d)
            """
        else:
            return
        
        if DEBUG:
            print(f"DEBUG Query: SELECT * FROM cypher('exo_graph', $$ {cypher} $$) AS (r agtype);")
        
        full_query = f"SELECT * FROM cypher('exo_graph', $$ {cypher} $$) AS (r agtype);"
        cur.execute(full_query)
        
        # Note: CREATE queries may not return data, which is normal behavior
        # The edge is created successfully as long as no exception is raised
            
    except Exception as e:
        print(f"✗ ERROR creating edge for {table_name}: {e}")
        print(f"   Row data: {row}")
        print(f"   Query: {cypher if 'cypher' in locals() else 'Query not generated'}")
        raise

# === Neo4j insert ===
def insert_node_neo4j(table_name, row):
    props = {k: (None if pd.isna(v) else v) for k, v in row.items()}
    prop_str = ", ".join([f"{k}: ${k}" for k in props])

    cypher = f"CREATE (n:{table_name} {{ {prop_str} }})"
    
    with neo4j_driver.session() as session:
        session.run(cypher, **props)

def insert_edge_neo4j(table_name, row):
    r = {k: (None if pd.isna(v) else v) for k, v in dict(row).items()}

    if table_name == "GIVES_POSTURAL_SUPPORT_IN":
        cypher = """
        MATCH (e:Exo {_id: $exoId}), (d:Dof {_id: $dofId})
        CREATE (e)-[:GIVES_POSTURAL_SUPPORT_IN {
            aim: $aim,
            adjustable: $adjustable,
            mechanism: $mechanism,
            direction: $direction
        }]->(d)
        """
    elif table_name == "TRANSFERS_FORCES_FROM":
        cypher = """
        MATCH (e:Exo {_id: $exoId}), (p:Part {_id: $partId})
        CREATE (e)-[:TRANSFERS_FORCES_FROM]->(p)
        """
    elif table_name == "TRANSFERS_FORCES_TO":
        cypher = """
        MATCH (e:Exo {_id: $exoId}), (p:Part {_id: $partId})
        CREATE (e)-[:TRANSFERS_FORCES_TO]->(p)
        """
    elif table_name == "HAS_AIM":
        cypher = """
        MATCH (e:Exo {_id: $exoId}), (a:Aim {_id: $aimId})
        CREATE (e)-[:HAS_AIM {aimCategory: $aimCategory}]->(a)
        """
    elif table_name == "HAS_AIM_SKN":
        cypher = """
        MATCH (e:Exo {_id: $exoId}), (s:StructureKinematicName {_id: $sknId})
        CREATE (e)-[:HAS_AIM_SKN {structureKinematicNameCategory: $structureKinematicNameCategory}]->(s)
        """
    elif table_name == "HAS_PROPERTY":
        cypher = """
        MATCH (e:Exo {_id: $exoId}), (p:ExoProperty {_id: $exoPropertyId})
        CREATE (e)-[:HAS_PROPERTY {exoPropertyValue: $exoPropertyValue}]->(p)
        """
    elif table_name == "ASSISTS_IN":
        cypher = """
        MATCH (e:Exo {_id: $exoId}), (d:Dof {_id: $dofId})
        CREATE (e)-[:ASSISTS_IN {
            aim: $aim,
            rangeAdjustable: $rangeAdjustable,
            lowerBoundMinAngle: $lowerBoundMinAngle,
            lowerBoundMaxAngle: $lowerBoundMaxAngle,
            upperBoundMinAngle: $upperBoundMinAngle,
            upperBoundMaxAngle: $upperBoundMaxAngle,
            sizeAdjustable: $sizeAdjustable,
            direction: $direction
        }]->(d)
        """
    elif table_name == "DOESNT_GO_WITH":
        cypher = """
        MATCH (e:Exo {_id: $exoId}), (s:StructureKinematicName {_id: $sknId})
        CREATE (e)-[:DOESNT_GO_WITH]->(s)
        """
    elif table_name == "GIVES_RESISTANCE_IN":
        cypher = """
        MATCH (e:Exo {_id: $exoId}), (d:Dof {_id: $dofId})
        CREATE (e)-[:GIVES_RESISTANCE_IN {
            aim: $aim,
            rangeAdjustable: $rangeAdjustable,
            lowerBoundMinAngle: $lowerBoundMinAngle,
            lowerBoundMaxAngle: $lowerBoundMaxAngle,
            upperBoundMinAngle: $upperBoundMinAngle,
            upperBoundMaxAngle: $upperBoundMaxAngle,
            sizeAdjustable: $sizeAdjustable,
            direction: $direction
        }]->(d)
        """
    elif table_name == "HAS_AIMTYPE":
        cypher = """
        MATCH (a:Aim {_id: $aimId}), (at:AimType {_id: $aimTypeId})
        CREATE (a)-[:HAS_AIMTYPE]->(at)
        """
    elif table_name == "HAS_AS_MAIN_DOF":
        cypher = """
        MATCH (e:Exo {_id: $exoId}), (d:Dof {_id: $dofId})
        CREATE (e)-[:HAS_AS_MAIN_DOF]->(d)
        """
    elif table_name == "HAS_DOF":
        cypher = """
        MATCH (j:JointT {_id: $jointTId}), (d:Dof {_id: $dofId})
        CREATE (j)-[:HAS_DOF]->(d)
        """
    elif table_name == "HAS_SKNTYPE":
        cypher = """
        MATCH (s:StructureKinematicName {_id: $sknId}), (st:StructureKinematicNameType {_id: $sknTypeId})
        CREATE (s)-[:HAS_SKNTYPE]->(st)
        """
    elif table_name == "IS_CONNECTED_WITH":
        cypher = """
        MATCH (j:JointT {_id: $jointTId}), (p:Part {_id: $partId})
        CREATE (j)-[:IS_CONNECTED_WITH]->(p)
        """
    elif table_name == "LIMITS_IN":
        cypher = """
        MATCH (e:Exo {_id: $exoId}), (d:Dof {_id: $dofId})
        CREATE (e)-[:LIMITS_IN {
            aim: $aim,
            maxAngle: $maxAngle,
            minAngle: $minAngle,
            adjustable: $adjustable,
            direction: $direction
        }]->(d)
        """
    else:
        return

    with neo4j_driver.session() as session:
        result = session.run(cypher, **r)
        summary = result.consume()
        if summary.counters.relationships_created == 0:
            print(f"⚠ WARNING: Neo4j edge creation failed for {table_name}")
            print(f"   Row data: {r}")


# === Main loop - Process nodes first, then edges ===
csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith(".csv")]

# Separate node files from edge files
node_files = [f for f in csv_files if os.path.splitext(f)[0] in MAIN_TABLES]
edge_files = [f for f in csv_files if os.path.splitext(f)[0] in INTERMEDIATE_TABLES]

# Process all node files first
print("\n" + "="*60)
print("PHASE 1: Creating all nodes")
print("="*60)
for file in sorted(node_files):
    table_name = os.path.splitext(file)[0]
    csv_path = os.path.join(CSV_DIR, file)
    
    print(f"\n{'='*60}")
    print(f"Processing file: {file}")
    print(f"Table name: {table_name}")
    print(f"{'='*60}")
    
    # Auto-detect delimiter by reading first line
    with open(csv_path, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        delimiter = ',' if ',' in first_line and ';' not in first_line else ';'
    
    # Read CSV with error handling for inconsistent columns
    df = pd.read_csv(csv_path, sep=delimiter, quotechar='"', escapechar="'", 
                    skipinitialspace=True, engine='python', on_bad_lines='warn')

    print(f"Columns in {table_name}: {list(df.columns)}")
    
    # Check for ID column and print first few rows for debugging
    id_column = None
    for col in df.columns:
        if col.lower() in ['id', '_id', f'{table_name.lower()}id']:
            id_column = col
            break
    
    if id_column:
        print(f"Found ID column: '{id_column}'")
        print(f"Sample IDs: {df[id_column].head(3).tolist()}")
    else:
        print(f"WARNING: No ID column found in {table_name}!")
        print(f"First row: {df.iloc[0].to_dict() if len(df) > 0 else 'No data'}")
    
    print(f"Inserting {len(df)} nodes for table: {table_name}")
    
    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        # Filter out unnamed columns (from trailing delimiters)
        row_dict = {k: v for k, v in row_dict.items() if not str(k).startswith('Unnamed')}
        insert_node_age(table_name, row_dict)
        if neo4j_available:
            insert_node_neo4j(table_name, row_dict)
    print(f"[OK] Successfully inserted {len(df)} nodes")

# Commit nodes before creating edges
conn.commit()
print("\n✓ All nodes committed to database")

# Process all edge files after nodes are created
print("\n" + "="*60)
print("PHASE 2: Creating all edges")
print("="*60)
for file in sorted(edge_files):
    table_name = os.path.splitext(file)[0]
    csv_path = os.path.join(CSV_DIR, file)
    
    print(f"\n{'='*60}")
    print(f"Processing file: {file}")
    print(f"Table name: {table_name}")
    print(f"{'='*60}")
    
    # Auto-detect delimiter by reading first line
    with open(csv_path, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        delimiter = ',' if ',' in first_line and ';' not in first_line else ';'
    
    # Read CSV with error handling for inconsistent columns
    df = pd.read_csv(csv_path, sep=delimiter, quotechar='"', escapechar="'", 
                    skipinitialspace=True, engine='python', on_bad_lines='warn')

    print(f"Columns in {table_name}: {list(df.columns)}")
    print(f"Inserting {len(df)} edges for table: {table_name}")
    skipped_rows = 0
    successful_rows = 0
    
    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        # Filter out unnamed columns (from trailing delimiters)
        row_dict = {k: v for k, v in row_dict.items() if not str(k).startswith('Unnamed')}
        
        # Check if any critical ID columns are missing/NaN
        has_missing_ids = False
        for key, value in row_dict.items():
            if 'Id' in key and pd.isna(value):
                has_missing_ids = True
                break
        
        if has_missing_ids:
            skipped_rows += 1
            continue
        
        try:
            insert_edge_age(table_name, row_dict)
            if neo4j_available:
                insert_edge_neo4j(table_name, row_dict)
            successful_rows += 1
        except Exception as e:
            print(f"✗ Error at row {idx + 2} (line {idx + 2} in CSV): {e}")
            print(f"  Available columns: {list(row_dict.keys())}")
            print(f"  Row data: {row_dict}")
            skipped_rows += 1
    
    if skipped_rows > 0:
        print(f"[WARN] Skipped {skipped_rows} rows due to errors or missing values")
    print(f"[OK] Successfully inserted {successful_rows} edges")
    
    # Commit after each edge file
    conn.commit()

conn.commit()

cur.close()
conn.close()
if neo4j_driver:
    neo4j_driver.close()

if neo4j_available:
    print("\n[OK] Imported into AGE + Neo4j successfully!")
else:
    print("\n[OK] Imported into AGE successfully! (Neo4j was not available)")