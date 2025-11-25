# CSV to Graph Database Import Script Documentation

## Overview

This Python script imports CSV data into both Apache AGE (PostgreSQL extension) and Neo4j graph databases. It creates a graph structure with nodes and relationships (edges) from CSV files containing information about exoskeletons, their properties, and relationships.

## Prerequisites

- Python 3.x
- PostgreSQL with Apache AGE extension installed
- Neo4j database (optional)
- Required Python packages: `psycopg2`, `pandas`, `python-dotenv`, `neo4j`

## Environment Configuration

The script uses environment variables loaded from a `.env` file:

### PostgreSQL/AGE Configuration
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password
- `DB_HOST` - Database host address
- `DB_PORT` - Database port (defaults to 5432)
- `DB_NAME` - Database name
- `CSV_DIR` - Directory containing CSV files to import

### Neo4j Configuration (Optional)
- `NEO4J_URI` - Neo4j connection URI
- `NEO4J_USER` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password

## Database Connection Flow

### 1. Neo4j Connection (Optional)
- Attempts to connect to Neo4j if credentials are provided
- Clears existing data using `MATCH (n) DETACH DELETE n`
- If connection fails, continues with AGE only
- Sets `neo4j_available` flag for conditional imports

### 2. PostgreSQL/AGE Connection
- Connects to PostgreSQL database
- Loads the AGE extension
- Sets search path to include `ag_catalog`
- Checks if `exo_graph` already exists
- Drops existing graph if present
- Creates a fresh `exo_graph`

## Data Structure

### Node Types (Main Tables)
The script processes 9 types of nodes:

1. **Aim** - Goals/objectives of exoskeletons
2. **AimType** - Categories of aims
3. **Dof** - Degrees of Freedom (movement capabilities)
4. **Exo** - Exoskeleton devices
5. **ExoProperty** - Properties of exoskeletons
6. **JointT** - Joint types
7. **Part** - Body parts
8. **StructureKinematicName** - Kinematic structure names
9. **StructureKinematicNameType** - Types of kinematic structures

### Relationship Types (Intermediate Tables)
The script creates 15 types of relationships:

1. **ASSISTS_IN** - Exo assists in a degree of freedom
2. **DOESNT_GO_WITH** - Incompatibility between exo and structure
3. **GIVES_POSTURAL_SUPPORT_IN** - Exo provides postural support
4. **GIVES_RESISTANCE_IN** - Exo provides resistance
5. **HAS_AIM** - Exo has a specific aim
6. **HAS_AIM_SKN** - Exo has kinematic structure aim
7. **HAS_AIMTYPE** - Aim has a type
8. **HAS_AS_MAIN_DOF** - Exo's main degree of freedom
9. **HAS_DOF** - Joint has a degree of freedom
10. **HAS_PROPERTY** - Exo has a property
11. **HAS_SKNTYPE** - Structure has a type
12. **IS_CONNECTED_WITH** - Joint is connected with a part
13. **LIMITS_IN** - Exo limits movement in a DOF
14. **TRANSFERS_FORCES_FROM** - Exo transfers forces from a part
15. **TRANSFERS_FORCES_TO** - Exo transfers forces to a part

## Core Functions

### `format_age_value(value)`
Formats Python values for AGE Cypher queries:
- Converts `None`, empty strings, and NaN to `null`
- Returns numbers as strings
- Escapes single quotes in strings and wraps them in quotes

### `insert_node_age(table_name, row)`
Creates nodes in AGE:
- Builds property list from row dictionary
- Generates Cypher CREATE query
- Executes query through PostgreSQL cursor

### `insert_edge_age(table_name, row)`
Creates relationships in AGE:
- Uses pattern matching to find source and target nodes
- Creates edges with properties specific to each relationship type
- Handles different property sets for each edge type
- Includes error handling with detailed logging

### `insert_node_neo4j(table_name, row)`
Creates nodes in Neo4j:
- Converts row to property dictionary
- Uses parameterized Cypher queries
- Only executes if Neo4j is available

### `insert_edge_neo4j(table_name, row)`
Creates relationships in Neo4j:
- Pattern matches source and target nodes by `_id`
- Creates typed relationships with properties
- Validates successful creation by checking relationship count
- Only executes if Neo4j is available

## Import Process

### Phase 1: Node Creation

1. **File Detection**
   - Lists all CSV files in the specified directory
   - Separates node files from edge files based on table names

2. **Delimiter Detection**
   - Reads first line of each CSV
   - Auto-detects comma (`,`) or semicolon (`;`) delimiter

3. **CSV Parsing**
   - Uses pandas with error handling for inconsistent columns
   - Skips malformed lines with warnings
   - Filters out unnamed columns from trailing delimiters

4. **Node Insertion**
   - Processes each row in the CSV
   - Inserts into AGE
   - Inserts into Neo4j (if available)
   - Prints progress information

5. **Commit**
   - Commits all nodes to database before proceeding to edges

### Phase 2: Edge Creation

1. **File Processing**
   - Processes edge CSV files in sorted order
   - Same delimiter detection and CSV parsing as Phase 1

2. **Data Validation**
   - Checks for missing ID columns
   - Skips rows with missing critical foreign keys

3. **Edge Insertion**
   - Creates relationships between existing nodes
   - Uses MATCH queries to find source/target nodes by ID
   - Inserts properties specific to each relationship type
   - Tracks successful and skipped rows

4. **Error Handling**
   - Catches and logs exceptions with row data
   - Continues processing after errors
   - Reports skipped rows at the end

5. **Commit**
   - Commits after each edge file is processed

## Edge Property Handling

Different edge types have different properties:

### Simple Edges (No Properties)
- TRANSFERS_FORCES_FROM
- TRANSFERS_FORCES_TO
- DOESNT_GO_WITH
- HAS_AIMTYPE
- HAS_AS_MAIN_DOF
- HAS_DOF
- HAS_SKNTYPE
- IS_CONNECTED_WITH

### Complex Edges (With Properties)

**ASSISTS_IN / GIVES_RESISTANCE_IN**
- `aim`, `rangeAdjustable`, `lowerBoundMinAngle`, `lowerBoundMaxAngle`
- `upperBoundMinAngle`, `upperBoundMaxAngle`, `sizeAdjustable`, `direction`

**GIVES_POSTURAL_SUPPORT_IN**
- `aim`, `adjustable`, `mechanism`, `direction`

**HAS_AIM**
- `aimCategory`

**HAS_AIM_SKN**
- `structureKinematicNameCategory`

**HAS_PROPERTY**
- `exoPropertyValue`

**LIMITS_IN**
- `aim`, `maxAngle`, `minAngle`, `adjustable`, `direction`

## Output Messages

### Success Messages
- `[OK] Successfully inserted X nodes/edges` - Successful data insertion
- `✓ All nodes committed to database` - Phase 1 completion
- `[OK] Imported into AGE + Neo4j successfully!` - Full completion with both databases
- `[OK] Imported into AGE successfully! (Neo4j was not available)` - AGE-only completion

### Warning Messages
- `⚠ Warning: Could not connect to Neo4j: <error>` - Neo4j unavailable
- `⚠ Neo4j credentials not configured` - Missing Neo4j environment variables
- `[WARN] Skipped X rows due to errors or missing values` - Data validation issues
- Parser warnings for CSV files with inconsistent field counts

### Error Messages
- `✗ ERROR creating edge for <table>: <error>` - Edge creation failure with details
- `WARNING: No ID column found in <table>!` - Missing ID column in node CSV

## Database Queries

### Node Creation Query Pattern
```cypher
CREATE (:<Label> {property1: value1, property2: value2, ...})
```

### Edge Creation Query Pattern
```cypher
MATCH (source:<SourceLabel>), (target:<TargetLabel>)
WHERE source._id = <sourceId> AND target._id = <targetId>
CREATE (source)-[:<RELATIONSHIP_TYPE> {property: value, ...}]->(target)
```

## Debugging

Set `DEBUG = True` in the `insert_edge_age()` function to see:
- Generated Cypher queries
- Query execution details

## Common Issues and Solutions

### CSV Parsing Warnings
**Issue**: "Expected X fields, saw Y"
**Cause**: Extra commas/semicolons or unescaped quotes in CSV data
**Solution**: Clean CSV data or ignored if non-critical rows

### Missing ID Columns
**Issue**: "WARNING: No ID column found"
**Cause**: CSV missing `_id` or `id` column
**Solution**: Add ID column to CSV file

### Edge Creation Failures
**Issue**: Edges not created despite no errors
**Cause**: Source or target nodes don't exist (wrong IDs)
**Solution**: Verify node IDs exist before creating edges

### Neo4j Connection Failures
**Issue**: "Unable to retrieve routing information"
**Cause**: Neo4j not running or wrong credentials
**Impact**: Script continues with AGE only

## Performance Considerations

- Nodes are committed in batch after all insertions
- Edges are committed after each file to prevent memory issues
- Large CSV files may take significant time to process
- Each row requires a separate database query (no bulk insert optimization)

## Final Database State

After successful execution:
- AGE contains a complete graph in `exo_graph`
- Neo4j contains identical data (if available)
- 145 nodes across 9 types
- 464 relationships across 15 types (based on sample data)

## Cleanup and Connection Management

The script properly closes all connections:
1. Database cursor is closed
2. PostgreSQL connection is closed
3. Neo4j driver is closed (if initialized)
