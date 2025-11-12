import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# More detailed debugging
print("Checking configuration...")
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME')

# Check for whitespace issues
if db_user and (db_user != db_user.strip()):
    print("   ⚠️  WARNING: DB_USER has leading/trailing whitespace!")
    db_user = db_user.strip()
if db_password and (db_password != db_password.strip()):
    print("   ⚠️  WARNING: DB_PASSWORD has leading/trailing whitespace!")
    db_password = db_password.strip()
if db_host and (db_host != db_host.strip()):
    print("   ⚠️  WARNING: DB_HOST has leading/trailing whitespace!")
    db_host = db_host.strip()
if db_name and (db_name != db_name.strip()):
    print("   ⚠️  WARNING: DB_NAME has leading/trailing whitespace!")
    db_name = db_name.strip()

CSV_DIR = os.getenv("CSV_DIR")

print("\n Attempting to connect to database...")

# === Connect to Neon PostgreSQL via psycopg2 ===
try:
    conn = psycopg2.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database=db_name,
        sslmode='require',
        connect_timeout=10
    )
    print("Successfully connected to database!")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    raise

cur = conn.cursor()

# === Helpers ===
def is_intermediate_table(filename):
    base = os.path.splitext(filename)[0]
    return base.isupper()

def truncate_table(cursor, table_name):
    try:
        cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
        conn.commit()
    except Exception as e:
        print(f"❌ Error truncating {table_name}: {e}")
        conn.rollback()

# === Main import loop ===
for file in sorted(os.listdir(CSV_DIR)):
    if not file.endswith(".csv"):
        continue

    table_name = os.path.splitext(file)[0]
    csv_path = os.path.join(CSV_DIR, file)

    # Truncate table first
    truncate_table(cur, table_name)

    # Read CSV
    df = pd.read_csv(csv_path, sep=";", quotechar='"', escapechar="'")

    # Drop _id for intermediate tables
    if is_intermediate_table(file) and "_id" in df.columns:
        df = df.drop(columns=["_id"])

    # Convert Ja/Nee to boolean, except for HAS_PROPERTY
    for col in df.columns:
        if col == "HAS_PROPERTY":
            continue
        if df[col].astype(str).str.lower().isin(["ja", "nee"]).any():
            df[col] = df[col].map(
                lambda x: True if str(x).lower() == "ja" else (False if str(x).lower() == "nee" else None)
            )

    # Prepare COPY command
    columns = ','.join(df.columns)
    copy_sql = f"""
        COPY {table_name} ({columns})
        FROM STDIN WITH (FORMAT CSV, DELIMITER ';', QUOTE '"', ESCAPE '''', HEADER TRUE);
    """

    # Write temporary CSV for proper encoding
    tmp_path = os.path.join(CSV_DIR, "_temp.csv")
    df.to_csv(tmp_path, index=False, sep=";", quotechar='"', escapechar="'")

    # Import into PostgreSQL
    with open(tmp_path, "r", encoding="utf-8") as f:
        try:
            cur.copy_expert(copy_sql, f)
            conn.commit()
        except Exception as e:
            print(f"❌ Error importing {table_name}: {e}")
            conn.rollback()

    os.remove(tmp_path)

# === Close connection ===
cur.close()
conn.close()
print("\n All CSVs processed successfully!")
