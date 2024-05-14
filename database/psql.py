import psycopg2

class PSQL:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
        self.cursor = self.connection.cursor()

    def disconnect(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            self.cursor = None
            self.connection = None

    def execute_query(self, query: str, params: str = None):
        self.cursor.execute(query, params)
        self.connection.commit()

    def fetch_all(self, query: str, params: str = None):
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        return rows
    
    def check_record_existence(self, table_name: str, field_name: str, value: str) -> bool:
        query = f"SELECT 1 FROM {table_name} WHERE {field_name} = %s LIMIT 1"
        self.cursor.execute(query, (value,))
        return self.cursor.fetchone() is not None


