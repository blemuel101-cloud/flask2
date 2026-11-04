from flask import Flask, render_template, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import random
import datetime 
from datetime import time
from datetime import datetime
import os
print(os.getcwd())
import csv
import firebase_admin
import uuid
from firebase_admin import credentials, db
from wtforms.validators import DataRequired, Length
import json

firebase_credentials = os.environ.get("FIREBASE_CREDENTIALS")

if firebase_credentials:
    cred = credentials.Certificate(json.loads(firebase_credentials))
else:
    cred = credentials.Certificate("api.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://student-a5554-default-rtdb.firebaseio.com/'
})
#Globals
app = Flask(__name__)
app.secret_key = "secret_key"

#correct_code = db.reference("checkin_code").get()

student_time = datetime.now().strftime("%I:%M %p")
print(student_time)



time_24  = "07:55:00"
time_obj = datetime.strptime(time_24, "%H:%M:%S").time()
cutoff_hour = time_obj.strftime("%I:%M %p")

format_str = "%I:%M %p"
object_a = datetime.strptime(student_time, format_str)
object_b = datetime.strptime(cutoff_hour, format_str)








#Globals



def login_ids():# This function organizes the csv file to organize the student and their corresponding name.
    students = {}

    with open('studentcheck.csv', 'r') as file: #Reads the csv file.
        reader = csv.reader(file)
        next(reader)  # skip header

        for row in reader:
            student_id = row[1]  # keep as STRING
            student_name = row[0]
            students[student_id] = student_name

    return students


valstudent = login_ids()

@app.route("/")
def home():
    return render_template("student.html")

@app.route("/teacher")
def teacher():
    teacher_code = db.reference("checkin_code").get()
    
    ref = db.reference("teacher/attendance/students")
    students = ref.get()
    print(f"Path: teacher/{teacher_code}/students")
    print(f"Students: {students}")
    names = []
    if students is None:
        pass
    else:
        for _, data in students.items():
            student_id = data["student_id"]
            status = data["status"]
            name = valstudent[student_id]
            names.append({
                "name": name,
                "status": status
            })   
    return render_template("Teacher.html", names=names, code= teacher_code)



@app.route('/submit', methods=['GET','POST'])
def submit():
    if request.method == "POST":
        student_id = request.form.get('ID') #Gets the info the student enters from the "ID" feild.
        teacher_code = request.form.get("code") # Gets the code the teacher generated
        #teacher_code = request.form["code"]
        #late_pass = request.form["late"]
      
        ref = db.reference("checkin_code")
        actual_code = ref.get()
         
      
        
   
        # Validation

        if student_id not in valstudent: #If the ID the student types in is not in the valstudent variable , I display an error.
            flash("Invalid Student ID, try again.", 'danger')
            return redirect(url_for('home'))#Makes everything dissapear if whether ID is correct or not.
        
        if teacher_code != actual_code: # Checks if the code the student enters matches the code the teacher generated. 
         
            flash("Invalid Teacher code, try again.", 'danger')
            return redirect(url_for('home'))

        

        if teacher_code == actual_code and student_id in valstudent:
            ref = db.reference("teacher/attendance/students")
            students = ref.get()
            if students:
                for _, data in students.items():
                    if data["student_id"] == student_id:
                        flash("You have already checked in!", 'danger')
                        return redirect(url_for('home'))

            
    # save to Firebase here, applies to both late and on time
    
            if object_a > object_b:
                status = "late"
                flash(f"You are late {valstudent[student_id]}", 'warning')
                
            else:
                status="Present"
                flash(f"Welcome {valstudent[student_id]}", 'success')#If everything is good, "Welcome Student"

           
            ref = db.reference("teacher/attendance/students")
            ref.push({
            "student_id": student_id,
            "status": status,
                })

          
        return redirect(url_for('home'))
                
    


@app.route('/button-code', methods=['POST'])
#This function generated the code for the student.
def click():
    if request.method == "POST":
         
         if "gencode" in request.form:

            code = str(random.randint(1000 , 2000))  # Uses the random function to generate random numbers 1000 - 2000, I converted it to a string because th code input box is a str
            ref = db.reference("checkin_code")#Stores the generated code in that node, If the node does not exist → Firebase creates it,If it exists → Firebase replaces the old code
        
            ref.set(code)
            #flash(code,'success')

         elif "genlate" in request.form:
           
           ref = db.reference("teacher/attendance/students")
           ref.delete()

#def show():
   #if request.method == "POST":
   

        
        


    return redirect(url_for('teacher'))












#@app.route('/submit', methods=['GET','POST'])





    




    


      

app.run(debug=True)