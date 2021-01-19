from datetime import datetime
import mysql.connector
import timeago
import hashlib
from slugify import slugify
from flask import Flask, url_for, render_template, redirect, request, session

app = Flask(__name__)
app.debug = True

mydb = mysql.connector.connect(
    host="localhost",
    user="levent",
    password="levent1234",
    database="course"
)

mycursor = mydb.cursor(buffered=True, dictionary=True)



def hasUser(email, table_name):
    sql = "SELECT * FROM " + table_name + " WHERE email = %s"
    mycursor.execute(sql, (email,))
    emailused = mycursor.fetchone()
    if emailused:
        print(emailused)
        return True
    else:
        print(emailused)
        return False


def update(type, id, name, surname, email, department):
    if type == 'students':
        typeIdName = "schoolId"
    elif type == 'instructors':
        typeIdName = "instructorId"
    elif type == 'assistants':
        typeIdName = "assistantId"
    sql = "UPDATE " + type + " SET name = %s, surname = %s, email = %s, department = %s WHERE " + typeIdName + " = %s"
    mycursor.execute(sql, (name, surname, email, department, updateId))
    mydb.commit()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/data', methods=['GET', 'POST'])
def data():
    error = ''
    if request.method == 'POST':
        if request.form['name'] == '':
            error = 'Name cannot be empty'
        elif request.form['surname'] == '':
            error = 'Surname cannot be empty'
        elif request.form['email'] == '':
            error = 'Email cannot be empty'
        elif request.form['department'] == '':
            error = 'Department cannot be empty'
        elif request.form['radio'] == 'add':
            if hasUser(request.form['email'], "students") or hasUser(request.form['email'], "instructors") or hasUser(
                    request.form['email'], "assistants"):
                error = 'This email has already been registered'
            else:
                sql = "INSERT INTO " + request.form['entType'] + " SET name = %s, surname = %s, email = %s, department " \
                                                                 "= %s "
                mycursor.execute(sql, (
                    request.form['name'], request.form['surname'], request.form['email'], request.form['department']))
                mydb.commit()
                return redirect(url_for('home'))
        elif request.form['radio'] == 'update':
            update(request.form['entType'], updateId, request.form['name'], request.form['surname'],
                   request.form['email'], request.form['department'])
            return redirect(url_for('home'))
    return render_template('data.html', error=error)


@app.route('/student', methods=['GET', 'POST'])
def student():
    sql = "SELECT * FROM students " \
          "ORDER BY schoolId DESC"
    mycursor.execute(sql)
    students = mycursor.fetchall()
    if request.method == 'POST':
        if request.form['action'] == 'delete':
            sql = "DELETE FROM students WHERE schoolId = %s"
            mycursor.execute(sql, (request.form['id'],))
            mydb.commit()
            return redirect(url_for('student'))
        elif request.form['action'] == 'update':
            global updateId
            updateId = request.form['id']
            return redirect(url_for('data'))
    return render_template('student.html', students=students)


@app.route('/instructor', methods=['GET', 'POST'])
def instructor():
    sql = "SELECT * FROM instructors " \
          "ORDER BY instructorId DESC"
    mycursor.execute(sql)
    instructors = mycursor.fetchall()
    if request.method == 'POST':
        if request.form['action'] == 'delete':
            sql = "DELETE FROM instructors WHERE instructorId = %s"
            mycursor.execute(sql, (request.form['id'],))
            mydb.commit()
            return redirect(url_for('instructor'))
        elif request.form['action'] == 'update':
            global updateId
            updateId = request.form['id']
            return redirect(url_for('data'))
    return render_template('instructor.html', instructors=instructors)


@app.route('/assistant', methods=['GET', 'POST'])
def assistant():
    sql = "SELECT * FROM assistants " \
          "ORDER BY assistantId DESC"
    mycursor.execute(sql)
    assistants = mycursor.fetchall()
    if request.method == 'POST':
        if request.form['action'] == 'delete':
            sql = "DELETE FROM assistants WHERE assistantId = %s"
            mycursor.execute(sql, (request.form['id'],))
            mydb.commit()
            return redirect(url_for('assistant'))
        elif request.form['action'] == 'update':
            global updateId
            updateId = request.form['id']
            return redirect(url_for('data'))
    return render_template('assistant.html', assistants=assistants)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('not_found.html'), 404
