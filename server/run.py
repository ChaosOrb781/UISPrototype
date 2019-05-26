from flask import Flask, redirect, url_for, request
from flask import render_template
import time
import datetime
import numpy as np
import forum as forum
import postgresql
import requests

current_user = []
patient = True
#-1 = only viewing and personal threads
# 0 = write on threads
# 1 = register new users
# 2 = register new employees and medical dictonary entries
privilages = -1
app = Flask(__name__)

def tostring(s):
  return str(s).replace("'", "\'")

@app.route("/", methods=['GET', 'POST'])
def startPage():
  searchFilter = ""
  if request.method == 'POST':
    searchFilter = str(request.form.get('searchInput'))

  if searchFilter == "":
    return renderThreads(
      "SELECT threads.id, users.firstname, users.lastname, threads.header, threads.created_date, employees.privilege " +
        "FROM threads INNER JOIN users ON users.CPR=threads.CPR " +
        "LEFT JOIN employees ON employees.CPR=threads.CPR " +
          "ORDER BY CASE WHEN employees.privilege IS NOT NULL AND employees.privilege >= 1 THEN employees.privilege ELSE 0 END DESC, " +
          "created_date DESC",
      "Nye diskussionstråde")
  else:
    return renderThreads(
      "SELECT threads.id, users.firstname, users.lastname, threads.header, threads.created_date, employees.privilege " +
        "FROM threads INNER JOIN users ON users.CPR=threads.CPR " +
        "LEFT JOIN employees ON employees.CPR=threads.CPR " +
          "WHERE threads.header LIKE '%" + tostring(searchFilter) + "%' " +
            "ORDER BY CASE WHEN employees.privilege IS NOT NULL AND employees.privilege >= 1 THEN employees.privilege ELSE 0 END DESC, " +
            "created_date DESC " +
              "LIMIT 17",
      "Nye diskussionstråde")

@app.route("/minetråde", methods=['GET', 'POST'])
def myThreads():
  searchFilter = ""
  if request.method == 'POST':
    searchFilter = str(request.form.get('searchInput'))
  if request.method == 'GET':
    if current_user == []:
      return redirect(url_for('startPage'))
    if searchFilter == "":
      return renderThreads(
        "SELECT * FROM " +
        "(SELECT threads.id AS id, users.firstname AS fn, users.lastname AS ln, threads.header AS h, threads.created_date AS cd, employees.privilege AS ep " +
          "FROM threads INNER JOIN users ON users.CPR=threads.CPR AND threads.CPR='" + tostring(current_user[0]) + "' " +
          "LEFT JOIN employees ON employees.CPR=threads.CPR AND threads.CPR='" + tostring(current_user[0]) + "' " +
          "UNION " +
        "SELECT threads.id AS id, users.firstname AS fn, users.lastname AS ln, threads.header AS h, threads.created_date AS cd, employees.privilege AS ep " +
          "FROM threads INNER JOIN users ON users.CPR=threads.CPR " +
          "LEFT JOIN employees ON employees.CPR=threads.CPR " +
          "WHERE id IN (SELECT tid FROM posts WHERE posts.CPR='" + tostring(current_user[0]) + "')) AS foo " +
        "ORDER BY foo.cd DESC",
        "Mine diskussionstråde")
    else:
      return renderThreads(
        "SELECT * FROM " +
        "(SELECT threads.id AS id, users.firstname AS fn, users.lastname AS ln, threads.header AS h, threads.created_date AS cd, employees.privilege AS ep " +
          "FROM threads INNER JOIN users ON users.CPR=threads.CPR AND threads.CPR='" + tostring(current_user[0]) + "' " +
          "LEFT JOIN employees ON employees.CPR=threads.CPR AND threads.CPR='" + tostring(current_user[0]) + "' " +
          "UNION " +
        "SELECT threads.id AS id, users.firstname AS fn, users.lastname AS ln, threads.header AS h, threads.created_date AS cd, employees.privilege AS ep " +
          "FROM threads INNER JOIN users ON users.CPR=threads.CPR " +
          "LEFT JOIN employees ON employees.CPR=threads.CPR " +
          "WHERE id IN (SELECT tid FROM posts WHERE posts.CPR='" + tostring(current_user[0]) + "')) AS foo " +
        "WHERE foo.h LIKE '%" + searchFilter + "%' " +
        "ORDER BY foo.cd DESC",
        "Mine diskussionstråde")

def formatDate(date : str):
  dateformat = str.split(date, ' ');
  inputDate = str.split(dateformat[0], '-')
  input = datetime.datetime(int(inputDate[0]), int(inputDate[1]), int(inputDate[2])) + datetime.timedelta(hours=23)
  today = datetime.datetime.now()
  if today < input:
    return str.split(dateformat[1], '.')[0]
  else:
    return dateformat[0]

def renderThreads(query : str, title : str):
  global current_user
  global privilages
  conn, stateConn = postgresql.createConnection("prototype")
  if stateConn:
    data, rowcount, stateQuery = postgresql.query(conn, query)
    if stateQuery:
      threads = []
      print("Overview threads:")
      for row in range(rowcount):
        print("  Transfering thread #" + str(row))
        print("  User: " + data[row][1] + " " + data[row][2] + " Created: " + str(data[row][4]) + " Headline: " + str(data[row][3]))
        threads.append(forum.threadOverview(data[row][0], data[row][1] + " " + data[row][2], data[row][3], formatDate(str(data[row][4])), data[row][5]))
      postgresql.closeConnection(conn)
      if current_user != []:
        print("Opening startpage with user: " + current_user[0] + " with privilages: " + str(privilages))
      return render_template('index.html', current_user=current_user, privilages=privilages, title=title, threads=threads)
    else:
      postgresql.closeConnection(conn)
      print("Failed to get threads from database")
      return redirect(url_for('errorDisplay', error="Kunne ikke udtrække trådene fra databasen"))
  else:
    return redirect(url_for('errorDisplay', error="Kunne ikke forbinde til databasen"))

@app.route("/tråd", methods=['GET', 'POST'])
def enterThread():
  global current_user
  global privilages
  if request.method == 'POST':
    if current_user == []:
      return redirect(url_for('startPage'))
    postText = request.form.get('postInput')
    if postText != "":
      conn, state = postgresql.createConnection("prototype")
      if state:
        threadid = request.args['threadid']
        success = postgresql.execute(conn,
          "INSERT INTO posts (tid, CPR, content) " +
          "VALUES (" + threadid + ", '" + current_user[0] + "', '" + tostring(postText) + "')")
        if success:
          postgresql.closeConnection(conn)
          return redirect(url_for('enterThread', threadid=threadid))
        else:
          postgresql.closeConnection(conn)
          return redirect(url_for('errorDisplay', error="Kunne ikke indsætte ny besked i databasen"))
      else:
        return redirect(url_for('errorDisplay', error="Kunne ikke forbinde til databasen"))
    else:
      return redirect(url_for('enterThread', threadid=request.args['threadid'], error="Skriv dog noget mand!", border="border: 2px solid red"))

  elif request.method == 'GET':
    threadid = request.args['threadid']
    conn, stateConn = postgresql.createConnection("prototype")
    if stateConn:
      #THREAD INFO
      #[0]: tid, [1]: firstname, [2]: lastname, [3]: header, [4]: content, [5]: created_date
      #[6]: processID, [7]: journalID, [8]: specialization, [9]: works_at, [10]: CPR
      threadDat, rowcount, stateThread = postgresql.query(conn,
        "SELECT threads.id, users.firstname, users.lastname, threads.header, threads.content, threads.created_date, " +
          "patients.process_id, patients.journal, " +
          "employees.specialization, employees.works_at, " +
          "users.CPR, threads.is_open " +
          "FROM threads " +
            "INNER JOIN users ON threads.CPR=users.CPR " +
            "LEFT JOIN patients ON users.CPR=patients.CPR " +
            "LEFT JOIN employees ON users.CPR=employees.CPR " +
            "WHERE threads.id=" + tostring(threadid))
      if stateThread and rowcount > 0:
        thread = threadDat[0]
        #POST INFO
        #[0]: firstname, [1]: lastname, [2]: content, [3]: created_date, [4]: modified_date
        #[5]: processID, [6]: journalID, [7]: specialization, [8]: works_at
        postsDat, _, statePosts = postgresql.query(conn,
          "SELECT users.firstname, users.lastname, posts.content, posts.created_date, posts.modified_date, " +
            "patients.process_id, patients.journal, " +
            "employees.specialization, employees.works_at, posts.id " +
            "FROM posts " +
              "INNER JOIN users ON posts.CPR=users.CPR " +
              "LEFT JOIN patients ON users.CPR=patients.CPR " +
              "LEFT JOIN employees ON users.CPR=employees.CPR " +
              "WHERE posts.tid=" + tostring(thread[0]) + " ORDER BY posts.created_date DESC")
        if statePosts:
          posts = []
          for post in postsDat:
            posts.append(forum.post(str(post[9]), post[0] + " " + post[1], post[2], formatDate(str(post[3])), formatDate(str(post[4])), post[5], post[6], post[7], post[8]))
          thread = forum.thread(thread[10], thread[1] + " " + thread[2], thread[3], thread[4], formatDate(str(thread[5])), thread[6], thread[7], thread[8], thread[9], posts, thread[11])
          postgresql.closeConnection(conn)
          error=""
          border=""
          try:
            error = request.args['error']
          except:
            print("No error")
          try:
            border = request.args['border']
          except:
            print("No border")
          return render_template('thread.html', current_user=current_user, privilages=privilages, thread=thread, error=error, border=border)
        else:
          postgresql.closeConnection(conn)
          return redirect(url_for('errorDisplay', error="Kunne ikke udtrække svarene fra databasen"))
      else:
        postgresql.closeConnection(conn)
        return redirect(url_for('errorDisplay', error="Kunne ikke udtrække trådene fra databasen eller ingen tråd fundet med id: " + str(threadid)))
    else:
      return redirect(url_for('errorDisplay', error="Kunne ikke forbinde til databasen"))

@app.route("/lavtråd", methods=['GET', 'POST'])
def makeThread():
  global current_user
  global privilages
  information = ""
  if privilages < 2 :
    information = "Information: Husk at disse tråde skal hovedsagtligt blive anvendt til klargørelse af symptomer af vores professionelle eller spørge ind til processer"
  else:
    information = "Annonceringer vil altid så i toppen af forummet, for at angive retningslinjer eller nyheder"
  if request.method == 'POST':
    if current_user == []:
      return redirect(url_for('startPage'))
    header = tostring(request.form.get('header'))
    body = tostring(request.form.get('content'))
    open = tostring(request.form.get('open'))
    if header == "" or body == "":
      return render_template('createThread.html', current_user=current_user, privilages=privilages, information=information, postColor="red", error="Begge felter skal være udfyldte")
    conn, stateConn = postgresql.createConnection("prototype")
    if stateConn:
      rowcount, success = postgresql.execute(conn,
        "INSERT INTO threads (CPR, header, content, is_open) " +
        "VALUES ('" + current_user[0] + "', '" + tostring(header) + "', '" + tostring(body) + "', " + ("TRUE" if open == "on" else "FALSE") + ")")
      if success:
        postgresql.closeConnection(conn)
        return redirect(url_for('startPage'))
      else:
        postgresql.closeConnection(conn)
        return redirect(url_for('errorDisplay', error="Kunne ikke indsætte ny besked i databasen"))
    else:
      return redirect(url_for('errorDisplay', error="Kunne ikke forbinde til databasen"))
  elif request.method == 'GET':
    return render_template('createThread.html', current_user=current_user, privilages=privilages, information=information, postColor="lightgray", error="")

@app.route("/register", methods=['GET', 'POST'])
def registerUser():
  global current_user
  global privilages
  type = request.args['type']
  if request.method == 'POST':
    CPR = request.form.get('CPR')
    firstname = request.form.get('Fornavn')
    lastname = request.form.get('Efternavn')
    password = request.form.get('Password')
    if len(CPR) == 10 and firstname != "" and lastname != "" and password != "":
      #Tuple array with coloumn and value
      userAttributes = []
      userAttributes.append(("CPR", "'" + CPR + "'"))
      userAttributes.append(("firstname", "'" + firstname + "'"))
      userAttributes.append(("lastname", "'" + lastname + "'"))
      userAttributes.append(("password", "'" + password + "'"))
      #Optional attribute
      address = request.form.get('Adresse')
      if address != "":
        userAttributes.append(("address", "'" + address + "'"))

      if type == "borger":
        patientAttributes = []
        patientAttributes.append(("CPR", "'" + CPR + "'"))
        journalID = request.form.get('JournalID')
        if journalID != "":
          patientAttributes.append(("journal", journalID))
        processID = request.form.get('ProcesID')
        if processID != "":
          patientAttributes.append(("process_id", processID))
        conn, state = postgresql.createConnection("prototype")
        if state:
          _, successUser = postgresql.insertOrUpdate(conn, "users", "CPR", CPR, userAttributes)
          if successUser:
            _, successPatient = postgresql.insertOrUpdate(conn, "patients", "CPR", CPR, patientAttributes)
            if successPatient:
              postgresql.closeConnection(conn)
              return redirect(url_for('startPage'))
            else:
              postgresql.closeConnection(conn)
              return redirect(url_for('errorDisplay', error="Kunne ikke indsætte patienten"))
          else:
            postgresql.closeConnection(conn)
            return redirect(url_for('errorDisplay', error="Kunne ikke indsætte brugeren"))
        else:
          return redirect(url_for('errorDisplay', error="Kunne ikke forbinde til databasen"))
      elif type == "ansat":
        employeeAttributes = []
        employeeAttributes.append(("CPR", "'" + CPR + "'"))
        specialization = request.form.get('Jobstilling')
        works_at = request.form.get('Works_at')
        if specialization != "" and works_at != "":
          employeeAttributes.append(("specialization", "'" + specialization + "'"))
          employeeAttributes.append(("temp", request.form.get('temp') != None))
          employeeAttributes.append(("privilege", request.form.get('privilege')))
          employeeAttributes.append(("works_at", works_at))
          conn, state = postgresql.createConnection("prototype")
          if state:
            _, successUser = postgresql.insertOrUpdate(conn, "employees", "CPR", CPR, employeeAttributes)
            if successUser:
              _, successPatient = postgresql.insertOrUpdate(conn, "employees", "CPR", CPR, employeeAttributes)
              if successPatient:
                postgresql.closeConnection(conn)
                return redirect(url_for('startPage'))
              else:
                postgresql.closeConnection(conn)
                return redirect(url_for('errorDisplay', error="Kunne ikke indsætte ansatte"))
            else:
              postgresql.closeConnection(conn)
              return redirect(url_for('errorDisplay', error="Kunne ikke indsætte brugeren"))
          else:
            return render_template('register.html', current_user=current_user, privilages=privilages, type=type, error="Ikke alle påkrævet felter var udfyldt!")
        else:
          return redirect(url_for('errorDisplay', error="Kunne ikke forbinde til databasen"))
    else:
      return render_template('register.html', current_user=current_user, privilages=privilages, type=type, error="Ikke alle påkrævet felter var udfyldt!")
  if request.method == 'GET':
    return render_template('register.html', current_user=current_user, privilages=privilages, type=type, error="")

@app.route("/del", methods=['GET', 'POST'])
def deleteThread():
  global current_user
  global privilages
  if current_user != [] and privilages >= 0:
    tid = request.args['threadid']
    conn, state = postgresql.createConnection("prototype")
    if state:
      prownum, stateposts = postgresql.execute(conn, "DELETE FROM posts WHERE tid=" + tid)
      trownum, statethread = postgresql.execute(conn, "DELETE FROM threads WHERE id=" + tid)
      if not statethread or not stateposts:
        postgresql.closeConnection(conn)
        return redirect(url_for('errorDisplay', error="Kunne ikke slette tråd fra databasen"))
      if trownum < 1:
        print("No rows affected by delete")
      print("Deleted " + prownum + " posts from thread " + tid)
      postgresql.closeConnection(conn)
      return redirect(url_for('startPage'))
    else:
      return redirect(url_for('errorDisplay', error="Kunne ikke forbinde til databasen"))
  else:
    return redirect(url_for('startPage'))

@app.route("/delp", methods=['GET', 'POST'])
def deletePost():
  global current_user
  global privilages
  if current_user != [] and privilages >= 0:
    pid = request.args['postid']
    tid = request.args['threadid']
    query = "DELETE FROM posts WHERE id=" + pid
    conn, state = postgresql.createConnection("prototype")
    if state:
      rownum, statequery = postgresql.execute(conn, "DELETE FROM posts WHERE id=" + pid)
      if not statequery:
        postgresql.closeConnection(conn)
        return redirect(url_for('errorDisplay', error="Kunne ikke slette tråd fra databasen"))
      if rownum < 1:
        print("No rows affected by delete")
      postgresql.closeConnection(conn)
      return redirect(url_for('enterThread', threadid=tid))
    else:
      return redirect(url_for('errorDisplay', error="Kunne ikke forbinde til databasen"))
  else:
    return redirect(url_for('startPage'))

@app.route("/vistabel", methods=['GET', 'POST'])
def showTable():
  global current_user
  global privilages
  searchFilter = ""
  if request.method == 'POST':
    searchFilter = str(request.form.get('searchInput'))
  if current_user != [] and privilages >= 2:
    type = request.args['type']
    tableName = "patients" if type == "borger" else "employees"
    conn, state = postgresql.createConnection("prototype")
    if state:
      headers, _, _ = postgresql.query(conn, "SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='users' OR TABLE_NAME='" + tableName + "'")
      np.delete(headers, 7)
      query = "SELECT * FROM users INNER JOIN " + tableName + " ON users.CPR=" + tableName + ".CPR"
      if searchFilter != "":
        query += " WHERE users.firstname LIKE '%" + searchFilter + "%' OR users.lastname LIKE '%" + searchFilter + "%'"
      data, _, _ = postgresql.query(conn, query)
      return render_template("table.html", current_user=current_user, privilages=privilages, type=type, header=headers, data=data)
    else:
      return redirect(url_for('errorDisplay', error="Kunne ikke forbinde til databasen"))
  else:
    return redirect(url_for('startPage'))

@app.route("/login", methods=['GET', 'POST'])
def loginPage():
  global current_user
  global patient
  global privilages
  usercolor = "#000000"
  pswdcolor = "#000000"
  error = ""
  try:
    if request.method == 'POST':
      changebutton = False
      try:
        if (request.form.get('changeType') == "Ansat?" or request.form.get('changeType') == "Patient?"):
          patient = not patient
          changebutton = True
      except:
        print("Not changing type")
      if (not changebutton):
        try:
          username = request.form.get('username')
          password = request.form.get('password')
          if (username != ""):
            conn, state = postgresql.createConnection("prototype")
            print("Attempt to log in on user: " + username)
            usertype = "patients" if patient else "employees"
            user, rowcount, state = postgresql.query(conn,
              "SELECT * FROM users INNER JOIN " + usertype + " ON users.CPR=" + usertype + ".CPR " +
              "AND users.CPR='" + str(username) + "'")
            #Check in database if CPR exists
            if (rowcount == 1):
              print("Found user in DB: " + user[0][1] + " " + user[0][2] + " with password: " + user[0][3])
              #Check in database if password is correct for CPR
              if (password == user[0][3]):
                now = datetime.datetime.now()
                postgresql.execute(conn, "UPDATE users SET last_online_date='" + str(now) + "' WHERE CPR='" + user[0][0] + "'")
                user[0][6] = now
                current_user=user[0]
                if (not patient):
                  privilages = int(user[0][10])
                else:
                  privilages = -1
                print("Login success, privilages: " + str(privilages))
                return redirect(url_for('startPage'))
              else:
                print("Password missmatch, wrote " + password + " but expected " + user[0][3])
                pswdcolor = "#ff0000"
                error = "Password matcher ikke"
            else:
              usercolor = "#ff0000"
              error = "Ingen bruger med denne CPR"
        except Exception as e:
          print("Not submitting: " + str(e))
    elif request.method == 'GET':
      print("Login: GET request")
  except Exception as e:
    print(e)
  return render_template('login.html',
                         current_user=current_user,
                         privilages=privilages,
                         usertype="Patient" if patient else "Ansat",
                         notUsertype="Ansat?" if patient else "Patient?",
                         usercolor=usercolor,
                         pswdcolor=pswdcolor,
                         error=error)

@app.route("/logout")
def logout():
  global current_user
  current_user=[]
  privilages = -1
  return redirect(url_for('startPage'))

@app.route("/error")
def errorDisplay():
  global current_user
  global privilages
  try:
    return render_template('error.html', current_user=current_user, privilages=privilages, error=request.args['error'])
  except:
    return render_template('error.html', current_user=current_user, privilages=privilages, error="Kritikal fejl!")

# run the application
if __name__ == "__main__":
    app.run(debug=True)