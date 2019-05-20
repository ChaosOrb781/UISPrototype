from flask import Flask, redirect, url_for, request
from flask import render_template
from flask_bcrypt import Bcrypt
import time
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

@app.route("/", methods=['GET'])
def startPage():
  global current_user
  global privilages
  if request.method == 'GET':
    return renderThreads(
      "SELECT threads.id, users.firstname, users.lastname, threads.header, threads.created_date " +
      "FROM threads INNER JOIN users ON users.CPR=threads.CPR " +
      "ORDER BY created_date LIMIT 10")

@app.route("/minetråde", methods=['GET'])
def myThreads():
  if request.method == 'GET':
    if current_user == []:
      return redirect(url_for('startPage'))
    return renderThreads(
      "SELECT threads.id, users.firstname, users.lastname, threads.header, threads.created_date " +
      "FROM threads INNER JOIN users ON users.CPR=threads.CPR AND threads.CPR='" + str(current_user[0]) + "' "
      "ORDER BY created_date")

def renderThreads(query : str):
  global current_user
  global privilages
  conn, stateConn = postgresql.createConnection("prototype")
  if stateConn:
    data, shape, stateQuery = postgresql.query(conn, query)
    if stateQuery:
      threads = []
      print("Overview threads:")
      for row in range(shape[0]):
        print("  Transfering thread #" + str(row))
        print("  User: " + data[row][1] + " " + data[row][2] + " Created: " + str(data[row][4]) + " Headline: " + str(data[row][3]))
        threads.append(forum.threadOverview(data[row][0], data[row][1] + " " + data[row][2], data[row][3], str(data[row][4])))
      postgresql.closeConnection(conn)
      return render_template('index.html', current_user=current_user, privilages=privilages, title="Nye diskussionstråde:", threads=threads)
    else:
      postgresql.closeConnection(conn)
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
    postText = request.form['postInput']
    if postText != "":
      conn, state = postgresql.createConnection("prototype")
      if state:
        threadid = request.args['threadid']
        success = postgresql.insert(conn,
          "INSERT INTO posts (tid, CPR, content, created_date, modified_date) " +
          "VALUES (" + threadid + ", '" + current_user[0] + "', '" + postText + "', '" +
            time.strftime('%Y-%m-%d') + "', '" + time.strftime('%Y-%m-%d') + "')")
        if success:
          return redirect(url_for('enterThread', threadid=threadid))
        else:
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
      threadDat, shape, stateThread = postgresql.query(conn,
        "SELECT threads.id, users.firstname, users.lastname, threads.header, threads.content, threads.created_date, " +
          "patients.process_id, patients.journal, " +
          "employees.specialization, employees.works_at, " +
          "users.CPR " +
          "FROM threads " +
            "INNER JOIN users ON threads.CPR=users.CPR " +
            "LEFT JOIN patients ON users.CPR=patients.CPR " +
            "LEFT JOIN employees ON users.CPR=employees.CPR " +
            "WHERE threads.id=" + str(threadid))
      if stateThread and shape != 0 and len(shape) > 0 and shape[0] > 0:
        thread = threadDat[0]
        #POST INFO
        #[0]: firstname, [1]: lastname, [2]: content, [3]: created_date, [4]: modified_date
        #[5]: processID, [6]: journalID, [7]: specialization, [8]: works_at
        postsDat, shape, statePosts = postgresql.query(conn,
          "SELECT users.firstname, users.lastname, posts.content, posts.created_date, posts.modified_date, " +
            "patients.process_id, patients.journal, " +
            "employees.specialization, employees.works_at " +
            "FROM posts " +
              "INNER JOIN users ON posts.CPR=users.CPR " +
              "LEFT JOIN patients ON users.CPR=patients.CPR " +
              "LEFT JOIN employees ON users.CPR=employees.CPR " +
              "WHERE posts.tid=" + str(thread[0]) + " ORDER BY posts.created_date")
        if statePosts:
          posts = []
          for post in postsDat:
            posts.append(forum.post(post[0] + " " + post[1], post[2], post[3], post[4], post[5], post[6], post[7], post[8]))
          thread = forum.thread(thread[10], thread[1] + " " + thread[2], thread[3], thread[4], thread[5], thread[6], thread[7], thread[8], thread[9], posts)
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

@app.route("/tråd", methods=['GET', 'POST'])
def enterThread():
  global current_user
  global privilages
  if request.method == 'POST':
    if current_user == []:
      return redirect(url_for('startPage'))

  elif request.method == 'GET':
    return redirect(url_for(''))

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
        if (request.form['changeType'] == "Ansat?" or request.form['changeType'] == "Patient?"):
          patient = not patient
          changebutton = True
      except:
        print("Not changing type")
      if (not changebutton):
        try:
          username = request.form['username']
          password = request.form['password']
          if (username != ""):
            conn, state = postgresql.createConnection("prototype")
            print("Attempt to log in on user: " + username)
            usertype = "patients" if patient else "employees"
            user, shape, state = postgresql.query(conn,
              "SELECT * FROM users INNER JOIN " + usertype + " ON users.CPR=" + usertype + ".CPR " +
              "AND users.CPR='" + str(username) + "'")
            #Check in database if CPR exists
            if (len(shape) > 0 and shape[0] == 1):
              print("Found user in DB: " + user[0][1] + " " + user[0][2] + " with password: " + user[0][3])
              #Check in database if password is correct for CPR
              if (password == user[0][3]):
                current_user=user[0]
                if (not patient):
                  privilages = int(user[0][7])
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
        except:
          print("Not submitting")
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