import psycopg2
import numpy as np

database = ""

def createConnection(db):
  global database
  try:
    db = "dbname='" + db + "' user='postgres' host='localhost' password ='postgres' port ='5432'"
    conn = psycopg2.connect(db)
    database = db
    return (conn, True)
  except (Exception, psycopg2.Error) as error:
    print("Failed to connect to postgresql: ", error)
    database = ""
    return (0, False)

def closeConnection(conn):
  if(conn):
    conn.cursor().close()
    conn.close()
    print("PostgreSQL connection is closed")
  global database
  database = ""

# Executes query and returns the data tupled with a boolean the state
def query(conn, query_text):
  try:
    cursor = conn.cursor()
    cursor.execute(query_text)
    data = cursor.fetchall()
    data = np.array(data)
    return (data, data.shape, True)
  except (Exception, psycopg2.Error) as error:
    print("Failed to execute query due to: ", error)
    return (0, 0, False)

def getUserByName(conn, username):
  user, shape, state = query(conn, 'SELECT * FROM users ')

def getDatabaseTableNames(conn):
  print("Querying all open tables of current database...")
  if database == "" or conn == None:
    print("Failed: No database currently open")
    return (0, False)
  else:
    getAllTablesNamesInDB = "SELECT table_name FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' AND table_catalog='" + database + "' AND table_schema='public'"
    print("Success.")
    return query(conn, getAllTableNamesInDB)


def getColumnsNames(conn, tableName):
  print("Querying coloumn names of " + tableName + "...")
  if database == "" or conn == None:
    print("Failed: No connected database in session")
    return (0, False)
  else:
    getColumnsNames = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '" + tableName + "'"
    return query(conn, getColumnsNames)

def getTableData(conn, tableName, columns):
  header, shape1, state1 = getColumnsNames(conn, tableName)
  getData = "SELECT " + columns + " FROM " + tableName
  data, shape2, state2 = query(conn, getData)
  return (header, data, shape2, state1 and state2)

def getSearchResult(conn, tableName, column, needle):
	query_text = "SELECT * FROM " + tableName + " WHERE " + column + " LIKE '%" + needle + "%'"
	return query(conn, query_text)