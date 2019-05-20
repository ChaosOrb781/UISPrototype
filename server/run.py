from flask import Flask, redirect, url_for, request
from flask import render_template
from flask_bcrypt import Bcrypt
import numpy as np
import forum as forum
import postgresql
import requests

current_user = []
patient = True
# 0 = write on threads
# 1 = register new users
# 2 = register new employees and medical dictonary entries
privilages = 0
app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def startPage():
  global current_user
  global privilages
  if request.method == 'POST':
    print("POST!")
    #try:
    fetch = request.form['enterThread']
    print("Entering thread: " + fetch)
    return enterThread(fetch)
    #except Exception as e:
      #print("Failed to find thread: " + str(e))
  elif request.method == 'GET':
    print("GET!")
    conn, stateConn = postgresql.createConnection("prototype")
    if stateConn:
      data, shape, stateQuery = postgresql.query(conn, "SELECT users.firstname, users.lastname, threads.header, threads.created_date FROM threads INNER JOIN users ON users.CPR=threads.CPR ORDER BY created_date LIMIT 5")
      if stateQuery:
        threads = []
        print("data shape: " + str(shape))
        print("Overview threads:")
        for row in range(shape[0]):
          print("  Transfering thread #" + str(row))
          print("  User: " + data[row][0] + " " + data[row][1] + " Created: " + str(data[row][3]) + " Headline: " + str(data[row][2]))
          threads.append(forum.threadOverview(data[row][0] + " " + data[row][1], data[row][2], str(data[row][3])))
        postgresql.closeConnection(conn)
        return render_template('index.html', current_user=current_user, privilages=privilages, title="Nye diskussionstråde:", threads=threads)
    postgresql.closeConnection(conn)
    return render_template('index.html', current_user=current_user, privilages=privilages, title="Nye diskussionstråde:")

@app.route("/minetråde", methods=['GET', 'POST'])
def myThreads():
  global current_user
  global privilages
  if request.method == 'POST':
    print("POST!")
    try:
      fetch = request.form['enterThread']
      print("Entering thread: " + fetch)
      return enterThread(fetch)
    except Exception as e:
      print("Failed to find thread: " + str(e))
  elif request.method == 'GET':
    print("GET!")
    conn, stateConn = postgresql.createConnection("prototype")
    if stateConn:
      data, shape, stateQuery = postgresql.query(conn, "SELECT users.firstname, users.lastname, threads.header, threads.created_date FROM threads INNER JOIN users ON users.CPR=threads.CPR AND threads.CPR=" + str(current_user[0]) + " ORDER BY created_date")
      if stateQuery:
        threads = []
        print("data shape: " + str(shape))
        print("Overview threads:")
        for row in range(shape[0]):
          print("  Transfering thread #" + str(row))
          print("  User: " + data[row][0] + " " + data[row][1] + " Created: " + str(data[row][3]) + " Headline: " + str(data[row][2]))
          threads.append(forum.threadOverview(data[row][0] + " " + data[row][1], data[row][2], str(data[row][3])))
        postgresql.closeConnection(conn)
        return render_template('index.html', current_user=current_user, privilages=privilages, title="Nye diskussionstråde:", threads=threads)
    postgresql.closeConnection(conn)
    return render_template('index.html', current_user=current_user, privilages=privilages, title="Nye diskussionstråde:")

def enterThread(threadHeader : str):
  conn, stateConn = postgresql.createConnection("prototype")
  if stateConn:
    # threads(0-4), users(5-10), patients(11-12), employees(13-16)
    threadDat, shape, stateThread = postgresql.query(conn, "SELECT * FROM threads INNER JOIN users ON threads.CPR=users.CPR LEFT JOIN patients ON threads.CPR=patients.CPR LEFT JOIN employees ON threads.CPR=employees.CPR AND threads.header='" + threadHeader + "'")
    if stateThread and shape != 0 and len(shape) > 0 and shape[0] > 0:
      chosenThread = threadDat[0]
      # posts(0-5), users(6-11), employees(12-15)
      postsDat, shape, statePosts = postgresql.query(conn, "SELECT * FROM posts INNER JOIN users ON posts.CPR=users.CPR LEFT JOIN employees ON posts.CPR=employees.CPR AND posts.tid=" + str(chosenThread[0]) + " ORDER BY posts.created_date")
      if statePosts:
        posts = []
        for post in postsDat:
          posts.append(forum.post(post[0], post[1], post[7] + " " + post[8], post[14], post[17], post[3], post[4], post[5]))
        thread = forum.thread(chosenThread[0], chosenThread[6] + " " + chosenThread[7], chosenThread[13], chosenThread[14], chosenThread[3], chosenThread[4], chosenThread[2], chosenThread[3], chosenThread[4], posts)
        postgresql.closeConnection(conn)
        return render_template('thread.html', current_user=current_user, privilages=privilages, thread=thread)
      else:
        postgresql.closeConnection(conn)
        print("Failed to fetch posts related to thread " + fetch)
    else:
      postgresql.closeConnection(conn)
      print("Failed to fetch thread related to header " + fetch)
  else:
    print("Failed to connect to database")
  return render_template('thread.html', current_user=current_user, privilages=privilages)

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
      try:
        if (request.form['changeType'] == "Ansat?" or request.form['changeType'] == "Patient?"):
          patient = not patient
      except:
        print("Not changing type")
      try:
        username = request.form['username']
        password = request.form['password']
        if (username != ""):
          conn, state = postgresql.createConnection("prototype")
          print("Attempt to log in on user: " + username)
          usertype = "patients" if patient else "employees"
          user, shape, state = postgresql.query(conn, "SELECT * FROM users INNER JOIN " + usertype + " ON users.CPR=" + usertype + ".CPR AND users.CPR=" + username)
          #Check in database if CPR exists
          if (len(shape) > 0 and shape[0] == 1):
            print("Found user in DB: " + user[0][1] + " " + user[0][2] + " with password: " + user[0][3])
            #Check in database if password is correct for CPR
            if (password == user[0][3]):
              current_user=user[0]
              if (not patient):
                privilages = int(user[0][7])
              else:
                privilages = 0
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
  privilages = 0
  return redirect(url_for('startPage'))

# run the application
if __name__ == "__main__":
    app.run(debug=True)