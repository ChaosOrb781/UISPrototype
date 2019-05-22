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
    print("Executing query:\n" + query_text)
    cursor = conn.cursor()
    cursor.execute(query_text)
    data = cursor.fetchall()
    data = np.array(data)
    conn.commit()
    return (data, cursor.rowcount, True)
  except (Exception, psycopg2.Error) as error:
    print("Failed to execute query due to: ", error)
    return (0, 0, False)

def execute(conn, query_text):
  try:
    print("Executing query:\n" + query_text)
    cursor = conn.cursor()
    cursor.execute(query_text)
    rownum = cursor.rowcount
    conn.commit()
    return (rownum, True)
  except (Exception, psycopg2.Error) as error:
    print("Failed to execute query due to: ", error)
    return (0, False)

def insertOrUpdate(conn, tableName, primaryColoumn, key, attributes):
  data, rowcount, stateExist = query(conn, "SELECT " + primaryColoumn + " FROM " + tableName + " WHERE " + primaryColoumn + "='" + key + "'")
  if rowcount == 1:
    #Should update row
    query_text = "UPDATE " + tableName + " SET"
    for i in range(len(attributes)):
      column, value = attributes[i]
      query_text += " " + column + "=" + str(value)
      if (i < len(attributes) - 1):
        query_text += ","
    query_text += " WHERE " + primaryColoumn + "='" + key + "'"
    return execute(conn, query_text)
  else:
    #Should insert row
    query_text = "INSERT INTO " + tableName + " ("
    query_values = " VALUES ("
    for i in range(len(attributes)):
      column, value = attributes[i]
      query_text += column
      query_values += str(value)
      if (i < len(attributes) - 1):
        query_text += ", "
        query_values += ", "
    query_text += ")" + query_values + ")"
    return execute(conn, query_text)

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
    return (0, 0, False)
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