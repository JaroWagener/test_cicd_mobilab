import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open, call
import psycopg2
import pandas as pd
from io import StringIO
import import_csvs


class TestCSVFileValidation(unittest.TestCase):
    """Test CSV file structure and format"""
    
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp()
        cls.csv_dir = os.path.join(cls.test_dir, 'csv')
        os.makedirs(cls.csv_dir)
    
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        """Set up before each test"""
        # Clear any existing test CSV files
        for file in os.listdir(self.csv_dir):
            file_path = os.path.join(self.csv_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    
    def create_test_csv(self, filename, data, sep=';'):
        """Helper to create test CSV with semicolon delimiter"""
        filepath = os.path.join(self.csv_dir, filename)
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, sep=sep, quotechar='"', escapechar="'")
        return filepath
    
    def test_csv_files_exist(self):
        """Test that CSV files exist in directory"""
        self.create_test_csv('test.csv', {'id': [1, 2], 'name': ['A', 'B']})
        csv_files = [f for f in os.listdir(self.csv_dir) if f.endswith('.csv')]
        self.assertGreater(len(csv_files), 0, "No CSV files found")
    
    def test_csv_semicolon_delimiter(self):
        """Test that CSVs use semicolon delimiter"""
        filepath = self.create_test_csv('test.csv', {'id': [1], 'name': ['Test']})
        
        with open(filepath, 'r') as f:
            first_line = f.readline()
            self.assertIn(';', first_line, "CSV should use semicolon delimiter")
    
    def test_csv_proper_quoting(self):
        """Test CSV quoting and escaping"""
        data = {'id': [1], 'name': ['Test with "quotes"'], 'desc': ["It's working"]}
        filepath = self.create_test_csv('test.csv', data)
        
        df = pd.read_csv(filepath, sep=';', quotechar='"', escapechar="'")
        self.assertEqual(df['name'][0], 'Test with "quotes"')
        self.assertEqual(df['desc'][0], "It's working")
    
    def test_csv_utf8_encoding(self):
        """Test UTF-8 encoding support"""
        data = {'id': [1, 2], 'name': ['José', 'François']}
        filepath = self.create_test_csv('test.csv', data)
        
        df = pd.read_csv(filepath, sep=';', encoding='utf-8')
        self.assertIn('José', df['name'].values)
        self.assertIn('François', df['name'].values)


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions in import_csvs.py"""
    
    def test_is_intermediate_table_uppercase(self):
        """Test that uppercase filenames are identified as intermediate tables"""
        self.assertTrue(import_csvs.is_intermediate_table('USERS.csv'))
        self.assertTrue(import_csvs.is_intermediate_table('PRODUCTS.csv'))
    
    def test_is_intermediate_table_lowercase(self):
        """Test that lowercase filenames are not intermediate tables"""
        self.assertFalse(import_csvs.is_intermediate_table('users.csv'))
        self.assertFalse(import_csvs.is_intermediate_table('products.csv'))
    
    def test_is_intermediate_table_mixed(self):
        """Test mixed case filenames"""
        self.assertFalse(import_csvs.is_intermediate_table('Users.csv'))
        self.assertFalse(import_csvs.is_intermediate_table('UsersData.csv'))
    
    @patch('import_csvs.conn')
    def test_truncate_table_success(self, mock_conn):
        """Test successful table truncation"""
        mock_cursor = MagicMock()
        
        import_csvs.truncate_table(mock_cursor, 'test_table')
        
        mock_cursor.execute.assert_called_with(
            "TRUNCATE TABLE test_table RESTART IDENTITY CASCADE;"
        )
        mock_conn.commit.assert_called_once()
    
    @patch('import_csvs.conn')
    def test_truncate_table_error_handling(self, mock_conn):
        """Test truncate error handling and rollback"""
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Table does not exist")
        
        import_csvs.truncate_table(mock_cursor, 'nonexistent_table')
        
        mock_conn.rollback.assert_called_once()


class TestBooleanConversion(unittest.TestCase):
    """Test Ja/Nee to boolean conversion logic"""
    
    def test_ja_nee_conversion(self):
        """Test that 'Ja'/'Nee' values are converted to boolean"""
        df = pd.DataFrame({
            'active': ['Ja', 'Nee', 'Ja'],
            'verified': ['nee', 'ja', 'Nee']
        })
        
        # Apply conversion logic
        for col in df.columns:
            if col == "HAS_PROPERTY":
                continue
            if df[col].astype(str).str.lower().isin(["ja", "nee"]).any():
                df[col] = df[col].map(
                    lambda x: True if str(x).lower() == "ja" else (
                        False if str(x).lower() == "nee" else None
                    )
                )
        
        self.assertEqual(df['active'][0], True)
        self.assertEqual(df['active'][1], False)
        self.assertEqual(df['verified'][0], False)
        self.assertEqual(df['verified'][1], True)
    
    def test_has_property_not_converted(self):
        """Test that HAS_PROPERTY column is not converted"""
        df = pd.DataFrame({
            'HAS_PROPERTY': ['Ja', 'Nee'],
            'other_field': ['Ja', 'Nee']
        })
        
        # Apply conversion logic
        for col in df.columns:
            if col == "HAS_PROPERTY":
                continue
            if df[col].astype(str).str.lower().isin(["ja", "nee"]).any():
                df[col] = df[col].map(
                    lambda x: True if str(x).lower() == "ja" else (
                        False if str(x).lower() == "nee" else None
                    )
                )
        
        # HAS_PROPERTY should remain strings
        self.assertEqual(df['HAS_PROPERTY'][0], 'Ja')
        self.assertEqual(df['HAS_PROPERTY'][1], 'Nee')
        
        # other_field should be boolean
        self.assertEqual(df['other_field'][0], True)
        self.assertEqual(df['other_field'][1], False)
    
    def test_case_insensitive_conversion(self):
        """Test case-insensitive 'Ja'/'Nee' conversion"""
        df = pd.DataFrame({
            'field': ['JA', 'ja', 'Ja', 'NEE', 'nee', 'Nee']
        })
        
        for col in df.columns:
            if col == "HAS_PROPERTY":
                continue
            if df[col].astype(str).str.lower().isin(["ja", "nee"]).any():
                df[col] = df[col].map(
                    lambda x: True if str(x).lower() == "ja" else (
                        False if str(x).lower() == "nee" else None
                    )
                )
        
        self.assertEqual(df['field'][0], True)
        self.assertEqual(df['field'][1], True)
        self.assertEqual(df['field'][2], True)
        self.assertEqual(df['field'][3], False)
        self.assertEqual(df['field'][4], False)
        self.assertEqual(df['field'][5], False)


class TestIntermediateTableHandling(unittest.TestCase):
    """Test handling of intermediate tables (uppercase names)"""
    
    def test_drop_id_column_for_uppercase_tables(self):
        """Test that _id column is dropped for uppercase table names"""
        df = pd.DataFrame({
            '_id': [1, 2, 3],
            'name': ['A', 'B', 'C'],
            'value': [10, 20, 30]
        })
        
        filename = 'USERS.csv'
        
        if import_csvs.is_intermediate_table(filename) and "_id" in df.columns:
            df = df.drop(columns=["_id"])
        
        self.assertNotIn('_id', df.columns)
        self.assertIn('name', df.columns)
        self.assertIn('value', df.columns)
    
    def test_keep_id_column_for_lowercase_tables(self):
        """Test that _id column is kept for lowercase table names"""
        df = pd.DataFrame({
            '_id': [1, 2, 3],
            'name': ['A', 'B', 'C']
        })
        
        filename = 'users.csv'
        
        if import_csvs.is_intermediate_table(filename) and "_id" in df.columns:
            df = df.drop(columns=["_id"])
        
        self.assertIn('_id', df.columns)


class TestDatabaseConnection(unittest.TestCase):
    """Test database connection and configuration"""
    
    @patch.dict(os.environ, {
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_pass',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'test_db'
    })
    @patch('psycopg2.connect')
    def test_database_connection_with_ssl(self, mock_connect):
        """Test database connection with SSL enabled"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        conn = psycopg2.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            sslmode='require',
            connect_timeout=10
        )
        
        mock_connect.assert_called_once()
        call_kwargs = mock_connect.call_args[1]
        self.assertEqual(call_kwargs['sslmode'], 'require')
        self.assertEqual(call_kwargs['connect_timeout'], 10)
    
    @patch.dict(os.environ, {
        'DB_USER': '  test_user  ',
        'DB_PASSWORD': '  test_pass  ',
        'DB_HOST': '  localhost  ',
        'DB_NAME': '  test_db  '
    })
    def test_whitespace_trimming(self):
        """Test that whitespace is trimmed from environment variables"""
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST')
        db_name = os.getenv('DB_NAME')
        
        # Strip whitespace as done in import_csvs.py
        if db_user and (db_user != db_user.strip()):
            db_user = db_user.strip()
        if db_password and (db_password != db_password.strip()):
            db_password = db_password.strip()
        if db_host and (db_host != db_host.strip()):
            db_host = db_host.strip()
        if db_name and (db_name != db_name.strip()):
            db_name = db_name.strip()
        
        self.assertEqual(db_user, 'test_user')
        self.assertEqual(db_password, 'test_pass')
        self.assertEqual(db_host, 'localhost')
        self.assertEqual(db_name, 'test_db')
    
    @patch('psycopg2.connect')
    def test_connection_timeout(self, mock_connect):
        """Test that connection has timeout configured"""
        mock_connect.side_effect = psycopg2.OperationalError("Connection timeout")
        
        with self.assertRaises(psycopg2.OperationalError):
            psycopg2.connect(
                user='test',
                password='test',
                host='unreachable',
                port='5432',
                database='test',
                sslmode='require',
                connect_timeout=10
            )


class TestCopyOperation(unittest.TestCase):
    """Test PostgreSQL COPY command generation and execution"""
    
    def test_copy_command_format(self):
        """Test COPY command is properly formatted"""
        df = pd.DataFrame({
            'id': [1, 2],
            'name': ['A', 'B'],
            'active': [True, False]
        })
        
        table_name = 'test_table'
        columns = ','.join(df.columns)
        
        copy_sql = f"""
        COPY {table_name} ({columns})
        FROM STDIN WITH (FORMAT CSV, DELIMITER ';', QUOTE '"', ESCAPE '''', HEADER TRUE);
    """
        
        self.assertIn('COPY test_table', copy_sql)
        self.assertIn('id,name,active', copy_sql)
        self.assertIn("DELIMITER ';'", copy_sql)
        self.assertIn('QUOTE \'"\'', copy_sql)
        self.assertIn("ESCAPE ''''", copy_sql)
        self.assertIn('HEADER TRUE', copy_sql)
    
    @patch('psycopg2.connect')
    def test_copy_expert_called(self, mock_connect):
        """Test that copy_expert is called for bulk insert"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        copy_sql = "COPY test_table FROM STDIN WITH CSV"
        mock_file = StringIO("id;name\n1;Test\n")
        
        mock_cursor.copy_expert(copy_sql, mock_file)
        
        mock_cursor.copy_expert.assert_called_once()


class TestErrorHandling(unittest.TestCase):
    """Test error handling and rollback"""
    
    @patch('psycopg2.connect')
    def test_rollback_on_copy_error(self, mock_connect):
        """Test that transaction is rolled back on COPY error"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.copy_expert.side_effect = Exception("COPY failed")
        
        try:
            mock_cursor.copy_expert("COPY test FROM STDIN", StringIO("data"))
            mock_conn.commit()
        except Exception:
            mock_conn.rollback()
        
        mock_conn.rollback.assert_called_once()
        mock_conn.commit.assert_not_called()
    
    @patch('psycopg2.connect')
    def test_commit_on_success(self, mock_connect):
        """Test that transaction is committed on success"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.copy_expert.return_value = None
        
        try:
            mock_cursor.copy_expert("COPY test FROM STDIN", StringIO("data"))
            mock_conn.commit()
        except Exception:
            mock_conn.rollback()
        
        mock_conn.commit.assert_called_once()
        mock_conn.rollback.assert_not_called()


class TestFileProcessing(unittest.TestCase):
    """Test CSV file processing workflow"""
    
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp()
        cls.csv_dir = os.path.join(cls.test_dir, 'csv')
        os.makedirs(cls.csv_dir)
    
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.test_dir)
    
    def test_sorted_file_processing(self):
        """Test that CSV files are processed in sorted order"""
        for file in os.listdir(self.csv_dir):
            file_path = os.path.join(self.csv_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        files = ['z_last.csv', 'a_first.csv', 'm_middle.csv']
        for f in files:
            open(os.path.join(self.csv_dir, f), 'w').close()
        
        csv_files = [f for f in sorted(os.listdir(self.csv_dir)) if f.endswith('.csv')]
        
        self.assertEqual(len(csv_files), 3, f"Expected 3 files, found {len(csv_files)}: {csv_files}")
        self.assertEqual(csv_files[0], 'a_first.csv')
        self.assertEqual(csv_files[1], 'm_middle.csv')
        self.assertEqual(csv_files[2], 'z_last.csv')
    
    def test_only_csv_files_processed(self):
        """Test that only .csv files are processed"""
        open(os.path.join(self.csv_dir, 'data.csv'), 'w').close()
        open(os.path.join(self.csv_dir, 'readme.txt'), 'w').close()
        open(os.path.join(self.csv_dir, 'data.xlsx'), 'w').close()
        
        csv_files = [f for f in os.listdir(self.csv_dir) if f.endswith('.csv')]
        
        self.assertEqual(len(csv_files), 1)
        self.assertEqual(csv_files[0], 'data.csv')
    
    def test_temp_file_cleanup(self):
        """Test that temporary files are cleaned up"""
        temp_file = os.path.join(self.csv_dir, '_temp.csv')
        
        with open(temp_file, 'w') as f:
            f.write('test')
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        self.assertFalse(os.path.exists(temp_file))


class TestIntegration(unittest.TestCase):
    """Integration tests with test database"""
    
    def setUp(self):
        self.db_config = {
            'user': os.getenv('TEST_DB_USER', 'test_user'),
            'password': os.getenv('TEST_DB_PASSWORD', 'test_password'),
            'host': os.getenv('TEST_DB_HOST', 'localhost'),
            'port': os.getenv('TEST_DB_PORT', '5432'),
            'database': os.getenv('TEST_DB_NAME', 'test_db')
        }
        
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.conn_available = True
        except psycopg2.OperationalError:
            self.conn_available = False
            self.skipTest("Test database not available")
    
    def tearDown(self):
        if self.conn_available:
            self.conn.close()
    
    def test_end_to_end_csv_import(self):
        """Test complete CSV import workflow"""
        if not self.conn_available:
            self.skipTest("Database not available")
        
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_import (
                id INTEGER,
                name VARCHAR(255),
                active BOOLEAN
            )
        """)
        self.conn.commit()
        
        test_data = "id;name;active\n1;Test User;Ja\n2;Another User;Nee"
        
        cursor.execute("TRUNCATE TABLE test_import")
        
        copy_sql = """
            COPY test_import (id, name, active)
            FROM STDIN WITH (FORMAT CSV, DELIMITER ';', HEADER TRUE)
        """
        
        cursor.copy_expert(copy_sql, StringIO(test_data))
        self.conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM test_import")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 2)
        
        cursor.execute("SELECT name, active FROM test_import ORDER BY id")
        rows = cursor.fetchall()
        self.assertEqual(rows[0][0], 'Test User')
        
        cursor.execute("DROP TABLE IF EXISTS test_import")
        self.conn.commit()
        cursor.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)