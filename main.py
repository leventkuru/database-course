import mysql.connector
from flask import Flask, url_for, render_template, redirect, request, session

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = '1234'

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


def updateData(type, id, name, surname, email, department):
    if type == 'students':
        typeIdName = "schoolId"
    elif type == 'instructors':
        typeIdName = "instructorId"
    elif type == 'assistants':
        typeIdName = "assistantId"
    sql = "UPDATE " + type + " SET name = %s, surname = %s, email = %s, department = %s WHERE " + typeIdName + " = %s"
    mycursor.execute(sql, (name, surname, email, department, id))
    mydb.commit()


def updateCourse(lessonName, location, startTime, endTime):
    sql = "UPDATE lessons SET lessonName = %s, location = %s, startTime = %s, endTime = %s WHERE CRN = %s"
    mycursor.execute(sql, (lessonName, location, startTime, endTime, updateId))
    mydb.commit()


@app.route('/', methods=['GET', 'POST'])
def home():
    sql = "SELECT *," \
          " instructors.name AS iName," \
          " students.name AS sName, " \
          "assistants.name AS aName" \
          " FROM lessons " \
          "INNER JOIN students ON students.schoolId = lessons.schoolId " \
          "INNER JOIN assistants ON assistants.assistantId = lessons.assistantId " \
          "INNER JOIN instructors ON instructors.instructorId = lessons.instructorId " \
          "ORDER BY CRN DESC"
    mycursor.execute(sql)
    lessons = mycursor.fetchall()
    if request.method == 'POST':
        if request.form['action'] == 'delete':
            sql = "DELETE FROM lessons WHERE CRN = %s"
            mycursor.execute(sql, (request.form['id'],))
            mydb.commit()
            return redirect(url_for('home'))
        elif request.form['action'] == 'update':
            global updateId
            updateId = request.form['id']
            session['updateId'] = updateId
            return redirect(url_for('addCourse'))
    return render_template('index.html', lessons=lessons)


@app.route('/addCourse', methods=['GET', 'POST'])
def addCourse():
    error = ''
    if request.method == 'POST':
        if request.form['lessonName'] == '':
            error = 'Lesson name cannot be empty'
        elif request.form['location'] == '':
            error = 'Location cannot be empty'
        elif request.form['startTime'] == '':
            error = 'Start time cannot be empty'
        elif request.form['endTime'] == '':
            error = 'End time cannot be empty'
        elif request.form['radio'] == 'add':
            if request.form['instructorId'] == '':
                error = 'Instructor id cannot be empty'
            elif request.form['schoolId'] == '':
                error = 'School id cannot be empty'
            elif request.form['assistantId'] == '':
                error = 'Assistant id cannot be empty'
            else:
                sql = "INSERT INTO lessons SET lessonName = %s, location = %s, instructorId = %s," \
                      " schoolId = %s, assistantId = %s, startTime = %s, endTime = %s"
                mycursor.execute(sql, (
                    request.form['lessonName'], request.form['location'], request.form['instructorId'],
                    request.form['schoolId'],
                    request.form['assistantId'], request.form['startTime'], request.form['endTime']))
                mydb.commit()
                return redirect(url_for('home'))
        elif request.form['radio'] == 'update':
            if request.form['instructorId'] != '':
                error = 'Please leave instructor id empty'
            elif request.form['schoolId'] != '':
                error = 'Please leave school id empty'
            elif request.form['assistantId'] != '':
                error = 'Please leave assistant id empty'
            else:
                updateCourse(request.form['lessonName'], request.form['location'], request.form['startTime'],
                             request.form['endTime'])
                return redirect(url_for('home'))
    return render_template('addCourse.html', error=error, update_id = session.get("updateId",None))


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
            if request.form['updateId'] != '':
                error = 'Update id should be empty for adding values'
            elif hasUser(request.form['email'], "students") or hasUser(request.form['email'], "instructors") or hasUser(
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
            updateData(request.form['entType'], request.form['updateId'], request.form['name'], request.form['surname'],
                       request.form['email'], request.form['department'])
            return redirect(url_for('home'))
    return render_template('data.html', error=error, update_id = session.get("updateId",None))


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
            session['updateId'] = updateId
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
