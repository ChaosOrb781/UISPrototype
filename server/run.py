# serve.py

from flask import Flask, redirect, url_for, request
from flask import render_template
from flask_bcrypt import Bcrypt
import postgresql
import requests

current_user = ""
app = Flask(__name__)

@app.route("/")
def startPage():
  conn, stateConn = postgresql.createConnection("bank")
  header, data, _ = postgresql.getTableData(conn, "transfers", "*")
  print(header, "\n", data)
  return render_template('index.html', current_user=current_user, header=header, data=data)

@app.route("/login", methods=['GET', 'POST'])
def loginPage():
  global current_user
  usercolor = "#000000"
  pswdcolor = "#000000"
  error = ""
  try:
    if request.method == 'POST':
      username = request.form['username']
      password = request.form['password']
      if (username != ""):
        #DO DATABASE STUFFFFFFF
        #Check in database if CPR exists
        if (username == "admin"):
          #Check in database if password is correct for CPR
          if (password == "admin"):
            current_user = username
            return redirect(url_for('startPage'))
          else:
            pswdcolor = "#ff0000"
            error = "Password matcher ikke"
        else:
          usercolor = "#ff0000"
          error = "Ingen bruger med denne CPR"
    elif request.method == 'GET':
      print("Login: GET request")
      conn, stateConn = postgresql.createConnection("bank")
      header, data, _ = postgresql.getTableData(conn, "customers", "*")
  except Exception as e:
    print(e)
  return render_template('login.html', current_user=current_user, usercolor=usercolor, pswdcolor=pswdcolor, error=error)

@app.route("/logout")
def logout():
  global current_user
  current_user=""
  return redirect(url_for('startPage'))

# run the application
if __name__ == "__main__":
    app.run(debug=True)