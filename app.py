from flask import Flask, render_template, request, session, url_for, redirect,flash
# from logging import exception
from werkzeug.utils import secure_filename
import pymysql  
import os
from datetime import date, datetime
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import os
from flask_mail import Mail
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 
from logging import DEBUG

app = Flask(__name__)
app.logger.setLevel(DEBUG)

global final_labels

UPLOAD_FOLDER = 'static/upload/'
UPLOAD_FOLDER1 = 'static/company_img/'
UPLOAD_FOLDER2 = 'static/logo/'
UPLOAD_FOLDER3 = 'static/upload_resume/'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER1'] = UPLOAD_FOLDER1
app.config['UPLOAD_FOLDER2'] = UPLOAD_FOLDER2
app.config['UPLOAD_FOLDER3'] = UPLOAD_FOLDER3
app.secret_key = 'random string'

def dbConnection():
    try:
        connection = pymysql.connect(
            host="localhost", user="root", password="root", database="003placement")
        return connection
    except:
        print("Something went wrong in database Connection")


def dbClose():
    try:
        dbConnection().close()
    except:
        print("Something went wrong in Close DB Connection")

################################################################################################################################
#                                           Deadline Notification
################################################################################################################################
def DeadlineMail(studentMail,cmpName,JobTitle,JobType,RemainDays):   
    fromaddr = "madhavbansal9779@gmail.com"
    toaddr = studentMail
   
    #instance of MIMEMultipart 
    msg = MIMEMultipart() 
  
    # storing the senders email address   
    msg['From'] = fromaddr 
  
    # storing the receivers email address  
    msg['To'] = toaddr 
  
    # storing the subject  
    msg['Subject'] = "Last "+ str(RemainDays)+" days to apply for job"
  
    # string to store the body of the mail 
    body = "Hello! students, Posted job deadlie is near don't miss your dream jobs,Please login and check all the details \n\nNote: that after deadline you can't apply for this jobs \n\nCompany Name: "+str(cmpName)+" \nJob Profile: "+str(JobTitle)+" \nDeadline: "+str(JobType)
  
    # attach the body with the msg instance 
    msg.attach(MIMEText(body, 'plain')) 
  
    # open the file to be sent  
    # filename = filetosend
    # attachment = open(filetosend, "rb") 
  
    # # instance of MIMEBase and named as p 
    # p = MIMEBase('application', 'octet-stream') 
  
    # # To change the payload into encoded form 
    # p.set_payload((attachment).read()) 
  
    # # encode into base64 
    # encoders.encode_base64(p) 
   
    # p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
  
    # # attach the instance 'p' to instance 'msg' 
    # msg.attach(p) 
  
    # creates SMTP session 
    s = smtplib.SMTP('smtp.gmail.com', 587) 
  
    # start TLS for security 
    s.starttls() 
  
    # Authentication 
    s.login(fromaddr, "jpvsfigjbcnagvir") 
  
    # Converts the Multipart msg into a string 
    text = msg.as_string() 
  
    # sending the mail 
    s.sendmail(fromaddr, toaddr, text) 
  
    # terminating the session 
    s.quit() 
   


def deadlineNotif():
    con = dbConnection()
    cursor = con.cursor()
    cursor.execute("select companyName,jobTitle,jobType,datediff(ApplicationDeadline, curdate()) as days_remaining from jobinfo;")
    res = cursor.fetchall()

    cursor.execute("select email from userdetails;")
    res2 = cursor.fetchall()



    companyName = [i[0] for i in res]
    jobTitle = [i[1] for i in res]
    jobType = [i[2] for i in res]
    days_remaining = [i[3] for i in res]
    studentMail = [i[0] for i in res2]

    # print(companyName,jobTitle, jobType, days_remaining)
    allData = zip(studentMail,companyName,jobTitle, jobType, days_remaining)

    for studentMail,cmpName,JobTitle,JobType,RemainDays in allData:
        if RemainDays==3:
            DeadlineMail(studentMail,cmpName,JobTitle,JobType,RemainDays)

# deadlineNotif()
################################################################################################################################
#                                           After Deadline job gets deleted
################################################################################################################################
def deadline2(branch):
    con = dbConnection()
    cursor = con.cursor()
    cursor.execute("select companyName,Salary,jobTitle,jobType,datediff(ApplicationDeadline, curdate()) as days_remaining,logo,jobLoc,OtherBenifits,jobId from jobinfo where branches=%s;",(branch))
    res = cursor.fetchall()

    companyName = [i[0] for i in res]
    Salary = [i[1] for i in res]
    jobTitle = [i[2] for i in res]
    jobType = [i[3] for i in res]
    days_remaining = [i[4] for i in res]
    logo = [i[5] for i in res]
    jobLoc = [i[6] for i in res]
    OtherBenifits = [i[7] for i in res]
    jobid = [i[8] for i in res]

    # print(companyName,jobTitle, jobType, days_remaining)
    allData = zip(companyName,Salary,jobTitle, jobType,logo,jobLoc,OtherBenifits,jobid,days_remaining)

    for companyName,Salary,jobTitle, jobType,logo,jobLoc,OtherBenifits,jobId,RemainDays in allData:
        if int(RemainDays)<=0:
            print()
            print("jobid")
            print(type(jobId))
            sql1 = "INSERT INTO deadline_over SELECT * FROM jobinfo WHERE jobId = %s;"
            val1 = (int(jobId))
            cursor.execute(sql1,val1)

            sql2 = "DELETE from jobinfo where jobId=%s;"
            val2 = (int(jobId))
            cursor.execute(sql2,val2)
            con.commit()

    cursor.execute("select companyName,Salary,jobTitle,jobType,logo,jobLoc,OtherBenifits,jobId from deadline_over where branches=%s;",(branch))
    res2 = cursor.fetchall()

    companyName = [i[0] for i in res2]
    Salary = [i[1] for i in res2]
    jobTitle = [i[2] for i in res2]
    jobType = [i[3] for i in res2]
    logo = [i[4] for i in res2]
    jobLoc = [i[5] for i in res2]
    OtherBenifits = [i[6] for i in res2]
    jobid = [i[7] for i in res2]

    finalData = zip(companyName,Salary,jobTitle, jobType,logo,jobLoc,OtherBenifits)
    return finalData

# deadlineNotif()
################################################################################################################################
#                                           Student login page
################################################################################################################################
@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            # session.pop('user', None)
            studEmail = request.form.get("email")
            studpass = request.form.get("pass")
            studrole = request.form.get("role")

            print(studEmail, studpass, studrole)
            con = dbConnection()
            cursor = con.cursor()
            res_count = cursor.execute('SELECT * FROM userdetails WHERE email = %s AND pass = %s AND Department = %s', (studEmail, studpass, studrole))
            result = cursor.fetchone()
            print(res_count)
            if res_count>0:
                session['user'] = result[1]
                session['userlname'] = result[2]
                session['userid'] = result[0]
                session['email'] = studEmail
                session['branch'] = studrole
                print("hii in if")
                return redirect(url_for('index'))
            else:
                print("hii in else")
                msg = "Sorry, your Email/Password was incorrect. Please double-check your Email/Password."
                msg2 = "error"
                return render_template('login.html',msg=msg,msg2=msg2)
        except Exception as e:
            print(e)
            print("Exception occured at login")
            return render_template('login.html')
        finally:
            dbClose()
    return render_template('login.html')
################################################################################################################################
#                                           Student login page
################################################################################################################################
@app.route('/forget', methods=["GET", "POST"])
def forget():
    return render_template('forget.html')

################################################################################################################################
#                                           Placement Head login page
################################################################################################################################
@app.route('/head_login', methods=["GET", "POST"])
def head_login():
    msg = ''
    if request.method == "POST":
        try:
            session.pop('user', None)
            print(request.form)
            headEmail = request.form.get("email")
            password = request.form.get("pass")
            role = request.form.get("role")

            print(headEmail, password,role)
            con = dbConnection()
            cursor = con.cursor()
            cursor.execute('SELECT * FROM company WHERE email = %s AND pass = %s AND role=%s', (headEmail, password,role))
            result = cursor.fetchone()
            print(result)
            if result:
                session['user'] = result[1]
                session['userlname'] = result[2]
                session['userid'] = result[0]
                session['email'] = headEmail
                session['branch'] = role
                return redirect(url_for('cmpindex'))
            else:
                return render_template('head_login1.html')
        except Exception as e:
            print(e)
            print("Exception occured at login")
            return render_template('head_login1.html')
        finally:
            dbClose()
    # return redirect(url_for('index'))
    return render_template('head_login1.html')
################################################################################################################################
#                                           Logout
################################################################################################################################
@app.route('/logout')
def logout():
    session.pop('user')
    session.pop('userlname')
    session.pop('userid')
    session.pop('email')
    session.pop('branch')
    return redirect(url_for('login'))
################################################################################################################################
#                                           User home page
################################################################################################################################
@app.route('/index', methods=["GET", "POST"])
def index():
    print("hii before session")
    # if 'user' in session:
    print("hii after session")
    branch = session.get("branch")
    print("branch")
    print(branch)
    con = dbConnection()
    cursor = con.cursor()
    
    deadlineover = deadline2(branch)

    cursor.execute("select companyName,Salary,jobTitle,jobType,logo,jobLoc,OtherBenifits from jobinfo where branches=%s",(branch))
    res = cursor.fetchall()
    res = list(res)
    print(res)

    print()
    print("res")
    print(res)

    deadlinecompanyName = []
    deadlinesalary = []
    deadlinejobTitle = []
    deadlinejobType = []
    deadlinejoblogo = []
    deadlinejobloc = []
    deadlinejobperks = []

    for companyName,Salary,jobTitle, jobType,logo,jobLoc,OtherBenifits in deadlineover:
        # print()
        # print("companyName")
        # print(companyName)
        deadlinecompanyName.append(companyName)
        deadlinesalary.append(Salary)
        deadlinejobTitle.append(jobTitle)
        deadlinejobType.append(jobType)
        deadlinejoblogo.append(logo)
        deadlinejobloc.append(jobLoc)
        deadlinejobperks.append(OtherBenifits)
        for i in res:
            if companyName == i[1]:
                res.remove(i)


    companyName = [i[0] for i in res]
    salary = [i[1] for i in res]
    jobTitle = [i[2] for i in res]
    jobType = [i[3] for i in res]
    logo = [i[4] for i in res]
    jobLoc = [i[5] for i in res]
    jobperks = [i[6] for i in res]

    lst = zip(companyName,salary,jobTitle,jobType,logo,jobLoc,jobperks)
    # print(deadlinecompanyName,deadlinejobTitle,deadlinejobType,logo)
    deadlineovr = zip(deadlinecompanyName,deadlinesalary,deadlinejobTitle,deadlinejobType,deadlinejoblogo,deadlinejobloc,deadlinejobperks)
    return render_template('index.html', lst=lst,deadlineovr=deadlineovr)
    # return render_template('login.html')
################################################################################################################################
#                                           Company home page
################################################################################################################################
@app.route('/cmpindex')
def cmpindex():
    uname = session.get('user')
    headBranch = session.get('branch')
    con = dbConnection()
    cursor = con.cursor()

    deadlineover = deadline2(headBranch)

    cursor.execute("select companyName,Salary,jobTitle,jobType,logo,jobLoc,OtherBenifits from jobinfo where branches=%s",(headBranch))
    res = cursor.fetchall()
    res = list(res)
    print(res)

    deadlinecompanyName = []
    deadlinesalary = []
    deadlinejobTitle = []
    deadlinejobType = []
    deadlinejoblogo = []
    deadlinejobloc = []
    deadlinejobperks = []

    for companyname,Salary,jobtitle, jobtype,cmplogo,jobloc,OtherBenifits in deadlineover:
        # print()
        # print("companyName")
        # print(companyName)
        deadlinecompanyName.append(companyname)
        deadlinesalary.append(Salary)
        deadlinejobTitle.append(jobtitle)
        deadlinejobType.append(jobtype)
        deadlinejoblogo.append(cmplogo)
        deadlinejobloc.append(jobloc)
        deadlinejobperks.append(OtherBenifits)
        for i in res:
            if companyname == i[1]:
                res.remove(i)

    companyName = [i[0] for i in res]
    salary = [i[1] for i in res]
    jobTitle = [i[2] for i in res]
    jobType = [i[3] for i in res]
    logo = [i[4] for i in res]
    jobLoc = [i[5] for i in res]
    jobperks = [i[6] for i in res]

    lst = zip(companyName,salary,jobTitle,jobType,logo,jobLoc,jobperks)

    deadlineovr = zip(deadlinecompanyName,deadlinesalary,deadlinejobTitle,deadlinejobType,deadlinejoblogo,deadlinejobloc,deadlinejobperks)
    return render_template('cmpindex.html', lst=lst,deadlineovr=deadlineovr)
################################################################################################################################
#                                           admin view job description page
################################################################################################################################
@app.route('/singlejob')
def singlejob():
    cmpname = request.args.get('cmp_name')
    jbTitle = request.args.get('jbTitle')
    print(cmpname)

    if cmpname == None:
        cmpname=session.get('cmpname')

    con = dbConnection()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM jobinfo WHERE companyName=%s AND jobTitle=%s", (cmpname,jbTitle))
    res = cursor.fetchall()
    res = list(res)
    companyName = [i[1] for i in res]
    logo = [i[2] for i in res]
    jobTitle = [i[3] for i in res]
    jobLoc = [i[4] for i in res]
    jobType = [i[5] for i in res]
    publishedOn = [i[6] for i in res]
    salary = [i[7] for i in res]
    applicationDeadline = [i[8] for i in res]
    branch = [i[14] for i in res]
    studInfo1 = [i[15] for i in res]
    JobDescription = ""
    Responsibilities = ""
    Education_Experience = ""
    OtherBenifits = ""

    for i in res:
        JobDescription += i[9]

        Responsibilities += i[10]

        Education_Experience += i[11]

        OtherBenifits += i[12]

    print()
    print("studInfo")
    print(studInfo1)

    labledict = {"fname":"First Name"," fname":"First Name","lname":"Last Name"," lname":"Last Name","fathername":"Father Name","mothername":"Mother Name",
                "curntLoc":"Current Location","Hometwn":"HomeTown","achivmnt":"Achievement","skil":"Skills",
                "certif":"Certificates","cgpa":"Current CGPA","cgpa7":"Current CGPA","clgname":"Collage Name","rolno":"Roll No.","pEmail":"Personal Email",
                "phnno":"Phone No.","brnch":"Branch","degre":"Degree","percent10":"10th Percentage",
                "percent12":"12th Percentage","actbacklog":"Active Backlog"}

    
    studInfo = []
    for i in studInfo1:
        a = i.replace("'","")
        a = a.replace("[","")
        a = a.replace("]","")
        asdf = a.split(",")
        studInfo.append(asdf)
    
    inp_lables = []
    for i in studInfo[0]:
        a = i.replace(" ","")
        a = labledict[a]
        inp_lables.append(a)

    
    

    OtherBenifits = OtherBenifits.split("|")
    JobDescription = JobDescription.split("|")
    Responsibilities = Responsibilities.split("|")
    Education_Experience = Education_Experience.split("|")

    print(OtherBenifits)
    print()
    print(JobDescription)
    print()
    print(Responsibilities)
    print()
    print(Education_Experience)


    usrname = session.get('user')
    userlname = session.get('userlname')
    usrbranch = session.get('branch')
    usrmail = session.get('email')

    
    
    # cursor.execute("SELECT status FROM applycmp WHERE fname=%s and lname=%s", (usrname,userlname))
    # res2 = list(cursor.fetchone())
    # print()
    # print("len res2")
    # print(len(res2))
    # print(studInfo)

    # if len(res2)==0:
    #     res2 = ["not selected"]
    # else:
    #     res2 = list(res2[0])

    # final_studinfo = []
    # for i in studInfo[0]:
    #     # print()
    #     # print("printing i")
    #     # print(i)
    #     # print()
    #     cursor.execute("select "+i+" from studentinfo where fname=%s AND cEmail=%s AND brnch=%s;",(usrname,usrmail,usrbranch))
    #     res = list(cursor.fetchall())
    #     print(res)
    #     final_studinfo.append(res[0][0])

    print()
    print("studInfo")
    print(studInfo[0])
    print()

    lst = zip(companyName, logo, jobTitle, jobLoc, jobType, publishedOn,
              salary, applicationDeadline, JobDescription, Responsibilities, Education_Experience, OtherBenifits)

    lst2 = zip(logo,jobTitle,companyName,jobLoc,jobType)

    return render_template('cmp_view.html', lst=lst,studInfo=inp_lables)
################################################################################################################################
#                                           admin view job description page
################################################################################################################################
@app.route('/studsinglejob')
def studsinglejob():
    global final_labels

    cmpname = request.args.get('cmp_name')
    jbTitle = request.args.get('jbTitle')
    print("cmpname, jbTitle")
    print(cmpname, jbTitle)

    if cmpname == None:
        cmpname=session.get('cmpname')

    con = dbConnection()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM jobinfo WHERE companyName=%s AND jobTitle=%s", (cmpname,jbTitle))
    res = cursor.fetchall()
    res = list(res)
    print("printing res")
    print(res)
    print()
    companyName = [i[1] for i in res]
    logo = [i[2] for i in res]
    jobTitle = [i[3] for i in res]
    jobLoc = [i[4] for i in res]
    jobType = [i[5] for i in res]
    publishedOn = [i[6] for i in res]
    salary = [i[7] for i in res]
    applicationDeadline = [i[8] for i in res]
    branch = [i[14] for i in res]
    studInfo1 = [i[15] for i in res]
    JobDescription = ""
    Responsibilities = ""
    Education_Experience = ""
    OtherBenifits = ""

    print()
    print("studInfo")
    print(studInfo1)
    
    studInfo = []
    for i in studInfo1:
        a = i.replace("'","")
        a = a.replace("[","")
        a = a.replace("]","")
        asdf = a.split(",")
        studInfo.append(asdf)

    for i in res:
        JobDescription += i[9]

        Responsibilities += i[10]

        Education_Experience += i[11]

        OtherBenifits += i[12]
    

    OtherBenifits = OtherBenifits.split("|")
    JobDescription = JobDescription.split("|")
    Responsibilities = Responsibilities.split("|")
    Education_Experience = Education_Experience.split("|")

    print(OtherBenifits)
    print()
    print(JobDescription)
    print()
    print(Responsibilities)
    print()
    print(Education_Experience)


    usrname = session.get('user')
    userlname = session.get('userlname')
    usrbranch = session.get('branch')
    usrmail = session.get('email')

    
    
    res_count = cursor.execute("SELECT status FROM applycmp WHERE fname=%s and lname=%s", (usrname,userlname))

    if res_count==0:
        res2 = ["not selected"]
    else:
        res2 = list(cursor.fetchone())
        print()
        print("len res2")
        print(len(res2))
        print(res2)
        res2 = list(res2[0])

    labledict = {"fname":"First Name","lname":"Last Name","fathername":"Father Name","mothername":"Mother Name",
                "curntLoc":"Current Location","Hometwn":"HomeTown","achivmnt":"Achievement","skil":"Skills",
                "certif":"Certificates","cgpa":"Current CGPA","cgpa7":"Current CGPA","clgname":"Collage Name","rolno":"Roll No.","pEmail":"Personal Email",
                "phnno":"Phone No.","brnch":"Branch","degre":"Degree","percent10":"10th Percentage",
                "percent12":"12th Percentage","actbacklog":"Active Backlog"}

    print()
    print("usrname,usrmail,usrbranch")
    print(usrname,usrmail,usrbranch)
    print(studInfo)
    final_studinfo = []
    final_labels = []
    for i in studInfo[0]:
        print(i)
        cursor.execute("select "+i+" from studentinfo where fname=%s AND cEmail=%s AND brnch=%s;",(usrname,usrmail,usrbranch))
        res = list(cursor.fetchone())
        print()
        print("final_studinfo")
        print(res)
        print()
        # final_studinfo.append(res[0][0])
        final_studinfo.append(res[0])
        a = i.replace(" ","")
        final_labels.append(labledict[a])

    print()
    print("final_studinfo")
    print(final_studinfo)
    print(type(final_studinfo))
    print(studInfo)

    lst = zip(companyName, logo, jobTitle, jobLoc, jobType, publishedOn,
              salary, applicationDeadline, JobDescription, Responsibilities, Education_Experience, OtherBenifits)

    lst2 = zip(logo,jobTitle,companyName,jobLoc,jobType)

    formfields = zip(final_labels,final_studinfo)
    return render_template('stud_view.html', lst=lst,lst2=lst2,formfields=formfields,res2=res2)
################################################################################################################################
#                                           Apply to job
################################################################################################################################
@app.route('/applyjob',methods=["GET","POST"])
def applyjob():
    global final_labels
    if 'user' in session:
        if request.method=="POST":
            
            studinfo = []
            for i in final_labels:
                aplyinfo = request.form.get(i)
                studinfo.append(aplyinfo)
            
            aplycompanyName = request.form.get("companyName")
            aplyjobTitle = request.form.get("jobTitle")
            resumfile = request.files["stud_resume"]

            resume_filename = secure_filename(resumfile.filename)
            resumfile.save(os.path.join(app.config['UPLOAD_FOLDER2'], resume_filename))

            resumefile_path = "static/upload_resume/"+resume_filename

            print()
            print("student info")
            print(studinfo)
            print()
            print("resume file path")
            print(resumefile_path,aplycompanyName,aplyjobTitle)
            print()

            conn = dbConnection()
            cur = conn.cursor()

            fname = studinfo[0]
            lname = studinfo[1]
            studinfo.remove(fname)
            studinfo.remove(lname)
            status = "applied"
            cat1 = "Unavailable"
            cat2 = "Unavailable"
            cat3 = "Unavailable"
            cat4 = "Unavailable"
            cat5 = "Unavailable"
            cat6 = "Unavailable"
            cat7 = "Unavailable"
            cat8 = "Unavailable"
            cat9 = "Unavailable"


            sql1 = "insert into applycmp (cmpName,Jobtitle,resume,fname,lname,cat1,cat2,cat3,cat4,cat5,cat6,cat7,cat8,cat9,status) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            val1 = (aplycompanyName,aplyjobTitle,str(resumefile_path),fname,lname,cat1,cat2,cat3,cat4,cat5,cat6,cat7,cat8,cat9,status)
            cur.execute(sql1,val1)
            conn.commit()

            sql2 = "update applycmp SET cat1=%s ,cat2=%s,cat3=%s,cat4=%s,cat5=%s,cat6=%s,cat7=%s,cat8=%s,cat9=%s where cmpName=%s AND Jobtitle=%s AND resume=%s AND fname=%s AND lname=%s AND status=%s;"
            val2 = (cat1,cat2,cat3,cat4,cat5,cat6,cat7,cat8,cat9,aplycompanyName,aplyjobTitle,str(resumefile_path),fname,lname,status)
            cur.execute(sql2,val2)
            conn.commit()

            msg = "Congratulations! you have successfully applied to this profile."
            flash(msg)
            session['cmpname']=aplycompanyName
            return redirect(url_for("index"))
        return redirect(url_for("index"))
    return render_template('login.html')
################################################################################################################################
#                                           Display Selected Students
################################################################################################################################
@app.route('/placed')
def placed():
    if 'user' in session:
        con = dbConnection()
        cursor = con.cursor()
        cursor.execute("SELECT applyId,fname, lname, email, cmpname, jobprof FROM applycmp where status='Selected';")
        res = cursor.fetchall()
        res = list(res)
        print(res)

        Id = [i[0] for i in res]
        fname = [i[1] for i in res]
        lname = [i[2] for i in res]
        email = [i[3] for i in res]
        cmpname = [i[4] for i in res]
        jobprof = [i[5] for i in res]

        lst = zip(Id,fname, lname, email, cmpname, jobprof)
        return render_template('selectionResult.html', lst=lst)
    return render_template('login.html')
################################################################################################################################
#                                           Display Selected Students
################################################################################################################################
@app.route('/cmpplaced')
def cmpplaced():
    if 'user' in session:
        con = dbConnection()
        cursor = con.cursor()
        cursor.execute("SELECT applyId,fname, lname, email, cmpname, jobprof FROM applycmp where status='Selected';")
        res = cursor.fetchall()
        res = list(res)
        print(res)

        Id = [i[0] for i in res]
        fname = [i[1] for i in res]
        lname = [i[2] for i in res]
        email = [i[3] for i in res]
        cmpname = [i[4] for i in res]
        jobprof = [i[5] for i in res]

        lst = zip(Id,fname, lname, email, cmpname, jobprof)
        return render_template('cmp_result.html', lst=lst)
    return render_template('login.html')
################################################################################################################################
#                                           Update information
################################################################################################################################
@app.route('/updateinfo', methods=["GET", "POST"])
def updateinfo():
    if 'user' in session:
        if request.method=="POST":
            fileinput = request.files['infofile']
            filenaming = secure_filename(fileinput.filename)
            # fName = filenaming.split(".")
            
            fileinput.save(os.path.join(app.config['UPLOAD_FOLDER'], filenaming))
            
            if ".csv" in filenaming:
                df = pd.read_csv("static/upload/"+filenaming)
            else:
                df = pd.read_excel("static/upload/"+filenaming)
            
            Fname = df["First name"]
            Lname = df["Last name"]
            Fathername = df["Father Name"]
            Mothername = df["Mother Name"]
            curntLoc = df["Current Location"]
            Hometwn = df["Hometown Location"]
            achivmnt = df["Achievements"]
            skil = df["Skills"]
            certif = df["Certification Courses"]
            cgpa = df["CGPA"]
            clgname = df["College Name"]
            rolno = df["Roll Number"]
            pEmail = df["Personal Email"]
            cEmail = df["College Email"]
            Paswrd = df["Password"]
            phnno = df["Phone Number"]
            brnch = df["Branch"]
            degre = df["Degree"]
            percent10 = df["10th Percentage"]
            percent12 = df["12th Percentage"]
            actbacklog = df["Active Backlogs"]

            studinfo = zip(Fname,Lname,Fathername,Mothername,curntLoc,Hometwn,achivmnt,skil,certif,cgpa,clgname,
            rolno,cEmail,pEmail,phnno,brnch,degre,percent10,percent12,actbacklog)

            userdetailzip = zip(Fname,Lname,phnno,cEmail,Paswrd,brnch)

            conn = dbConnection()
            curs = conn.cursor()


            for Fname,Lname,phnno,cEmail,Paswrd,brnch in userdetailzip:
                res_count = curs.execute("SELECT * from userdetails where fname=%s and email=%s;",(Fname,cEmail))
                if res_count>0:
                    curs.execute("UPDATE userdetails set fname=%s , lname=%s , mob=%s , email=%s , pass=%s , Department=%s where fname=%s and email=%s;",(Fname,Lname,phnno,cEmail,Paswrd,brnch,Fname,cEmail,))
                    conn.commit()
                else:
                    sql1 = "INSERT into userdetails (fname,lname,mob,email,pass,Department) values (%s,%s,%s,%s,%s,%s);"
                    val1 = (Fname,Lname,phnno,cEmail,Paswrd,brnch)
                    curs.execute(sql1,val1)
                    conn.commit()

            for Fname,Lname,Fathername,Mothername,curntLoc,Hometwn,achivmnt,skil,certif,cgpa,clgname,rolno,cEmail,pEmail,phnno,brnch,degre,percent10,percent12,actbacklog in studinfo:
                res_count = curs.execute("SELECT * from studentinfo where fname=%s and Lname=%s and pEmail=%s and brnch=%s and cEmail=%s;",(Fname,Lname,pEmail,brnch,cEmail))
                if res_count>0:
                    curs.execute('''UPDATE studentinfo set fname=%s , lname=%s , fathername=%s , mothername=%s , curntLoc=%s , Hometown=%s , achivmnt=%s , skil=%s , certif=%s, cgpa=%s , clgname=%s , rolno=%s , cEmail=%s, pEmail=%s , phnno=%s , brnch=%s , degre=%s , percent10=%s , percent12=%s , actbacklog=%s where fname=%s and Lname=%s and pEmail=%s and brnch=%s AND cEmail=%s;''',(Fname,Lname,Fathername,Mothername,curntLoc,Hometwn,achivmnt,skil,certif,cgpa,clgname,rolno,cEmail,pEmail,phnno,brnch,degre,percent10,percent12,actbacklog,Fname,Lname,pEmail,brnch,cEmail))
                    conn.commit()
                else:
                    print()
                    print(df)
                    print()
                    print("printing sql2 data")
                    print(Fname,Lname,Fathername,Mothername,curntLoc,Hometwn,achivmnt,skil,certif,cgpa,clgname,rolno,pEmail,phnno,brnch,degre,percent10,percent12,actbacklog)
                    print()
                    sql2 = '''INSERT into studentinfo (fname,lname,fathername,mothername,curntLoc,Hometown,achivmnt,skil,certif,cgpa,clgname,rolno,cEmail,pEmail,phnno,brnch,degre,percent10,percent12,actbacklog) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'''       
                    val2 = (Fname,Lname,Fathername,Mothername,curntLoc,Hometwn,achivmnt,skil,certif,cgpa,clgname,rolno,cEmail,pEmail,phnno,brnch,degre,percent10,percent12,str(actbacklog))
                    curs.execute(sql2,val2)
                    conn.commit()
            
            msg = "Student Data Updated successfully!"
            return render_template('updateinfo.html',msg=msg)
        return render_template('updateinfo.html')
    return render_template('login.html')
################################################################################################################################
#                                           Company Post job page
################################################################################################################################
def sendemailtouser(usertoaddress,companyName,jobProfile,deadLine):   
    fromaddr = "madhavbansal9779@gmail.com"
    toaddr = usertoaddress
   
    #instance of MIMEMultipart 
    msg = MIMEMultipart() 
  
    # storing the senders email address   
    msg['From'] = fromaddr 
  
    # storing the receivers email address  
    msg['To'] = toaddr 
  
    # storing the subject  
    msg['Subject'] = "New job posted on portal"
  
    # string to store the body of the mail 
    body = "Hello! student, we posted a new job,Please login and check all the details \n Company Name: "+companyName+" \n Job Profile: "+jobProfile+" \n Deadline: "+deadLine
  
    # attach the body with the msg instance 
    msg.attach(MIMEText(body, 'plain')) 
  
    # creates SMTP session 
    s = smtplib.SMTP('smtp.gmail.com', 587) 
  
    # start TLS for security 
    s.starttls() 
  
    # Authentication 
    s.login(fromaddr, "jpvsfigjbcnagvir") 
  
    # Converts the Multipart msg into a string 
    text = msg.as_string() 
  
    # sending the mail 
    s.sendmail(fromaddr, toaddr, text) 
  
    # terminating the session 
    s.quit()    


@app.route('/postjob', methods=["GET", "POST"])
def postjob():
    msg1 = 12
    print("printing hi before post method")
    if request.method == "POST":
        print("printing hi after post method")
        logo = request.files['logo']
        filename_secure2 = secure_filename(logo.filename)
        logo.save(os.path.join(app.config['UPLOAD_FOLDER2'], filename_secure2))
        print("[info]: company logo saved")

        jtitle = request.form.get("jtitle")
        jloc = request.form.get("jloc")
        jobType = request.form.get("jobType")
        jd = request.form.get("jd")
        Salary = request.form.get("Salary")
        deadline = request.form.get("deadline")
        cmpname = request.form.get("cmpname")
        resp = request.form.get("resp")
        eduexp = request.form.get("eduexp")
        benif = request.form.get("benif")
        branch = request.form.get('branch')
        studinfo = request.form.getlist('studinfo')
        print()
        print("studinfo")
        print(studinfo)
        
        filename_secure2 = "../static/logo/"+filename_secure2
        publishedOn = str(date.today())

        uname = session.get("user")

        con = dbConnection()
        cursor = con.cursor()
        sql = "INSERT INTO jobinfo (companyName, logo, jobTitle, jobLoc, jobType, publishedOn, salary, applicationDeadline, JobDescription, Responsibilities, Education_Experience, OtherBenifits,uname,branches,studentInfo) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        val = (cmpname, str(filename_secure2), jtitle, jloc,jobType, str(publishedOn), Salary, str(deadline), jd, resp, eduexp, benif,uname,branch,str(studinfo))
        # print(cmpname, str(filename_secure2), str(filename_secure1), email, jtitle, jloc,jobType, str(publishedOn), Vacancy, exp, Salary, str(deadline), jd, resp, eduexp, benif,uname,branch,str(studinfo))
        # cursor.execute("INSERT INTO jobinfo (companyName, logo, email, jobTitle, jobLoc, jobType, publishedOn, vacancy, Experience, salary, applicationDeadline, JobDescription, Responsibilities, Education_Experience, OtherBenifits,uname,branches,studentInfo) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"(cmpname, str(filename_secure2), str(filename_secure1), email, jtitle, jloc,jobType, str(publishedOn), Vacancy, exp, Salary, str(deadline), jd, resp, eduexp, benif,uname,branch,str(studinfo)))
        cursor.execute(sql,val)
        con.commit()
        
        cursor.execute("SELECT pEmail from studentinfo")
        res = cursor.fetchall()
        result = list(res)

        # for i in result:
        #     sendemailtouser(i[0],cmpname,jtitle,deadline) 
        
        msg = "job added successfully!"

        return render_template('post-job.html', msg=msg)
    msg = "Post a job for any profile"
    return render_template('post-job.html', msg=msg)

################################################################################################################################
#                                           Students get hired
################################################################################################################################
def SelectedMailToUser(usertoaddress,companyName,jobProfile):   
    fromaddr = "madhavbansal9779@gmail.com"
    toaddr = usertoaddress
   
    #instance of MIMEMultipart 
    msg = MIMEMultipart() 
  
    # storing the senders email address   
    msg['From'] = fromaddr 
  
    # storing the receivers email address  
    msg['To'] = toaddr 
  
    # storing the subject  
    msg['Subject'] = "Congatulations! You have been selected by "+companyName
  
    # string to store the body of the mail 
    body = "Congratulations! student you have been seleted by "+companyName+" For "+jobProfile+" Please contact to placement cell for further process.", 
  
    # attach the body with the msg instance 
    msg.attach(MIMEText(body, 'plain')) 
  
    # creates SMTP session 
    s = smtplib.SMTP('smtp.gmail.com', 587) 
  
    # start TLS for security 
    s.starttls() 
  
    # Authentication 
    s.login(fromaddr, "jpvsfigjbcnagvir") 
  
    # Converts the Multipart msg into a string 
    text = msg.as_string() 
  
    # sending the mail 
    s.sendmail(fromaddr, toaddr, text) 
  
    # terminating the session 
    s.quit()    

@app.route('/hiring', methods=["GET", "POST"])
def hiring():
    uname = session.get("user")
    print(uname)
    studFname = request.args.get('Fname')
    studLname = request.args.get('Lname')
    studmail = request.args.get('emaill')
    CmpName = request.args.get('CmpName')
    jobProfile = request.args.get('jobProfile')
    Status = "Selected"
    print(studFname,studLname,studmail,CmpName,jobProfile)

    # SelectedMailToUser(studmail,CmpName,jobProfile)

    uname = session.get("user")
    print(uname)
    con = dbConnection()
    cursor = con.cursor()
    cursor.execute("UPDATE applycmp set status=%s where fname=%s and lname=%s and email=%s and cmpname=%s and jobprof=%s",(Status,studFname,studLname,studmail,CmpName,jobProfile))
    con.commit()
    cursor.execute("SELECT * from applycmp")
    result = cursor.fetchall()
    result = list(result)
    print(result)

    ufname = [i[1] for i in result]
    ulname = [i[2] for i in result]
    email = [i[3] for i in result]
    mobno = [i[4] for i in result]
    prev_post = [i[5] for i in result]
    skills = [i[6] for i in result]
    exp = [i[7] for i in result]
    cmpName = [i[9] for i in result]
    jobpos = [i[10] for i in result]
    status = [i[11] for i in result]

    print(ufname,ulname,email,mobno,prev_post,skills,exp,cmpName,jobpos)

    lst2 = zip(ufname,ulname,email,mobno,prev_post,skills,exp,cmpName,jobpos,status)

    return render_template('hireemp.html',lst2=lst2)
################################################################################################################################
#                                           Company Post job page
################################################################################################################################
@app.route('/emp', methods=["GET", "POST"])
def emp():

    uname = session.get("user")
    print(uname)
    con = dbConnection()
    cursor = con.cursor()
    cursor.execute("SELECT * from applycmp")
    result = cursor.fetchall()
    result = list(result)
    print(result)

    cmpName = [i[1] for i in result]
    Jobtitle = [i[2] for i in result]
    resume = [i[3] for i in result]
    fname = [i[4] for i in result]
    lname = [i[5] for i in result]
    cat1 = [i[6] for i in result]
    cat2 = [i[7] for i in result]
    cat3 = [i[8] for i in result]
    cat4 = [i[9] for i in result]
    cat5 = [i[10] for i in result]
    cat6 = [i[11] for i in result]
    cat7 = [i[12] for i in result]
    cat8 = [i[13] for i in result]
    cat9 = [i[14] for i in result]
    status = [i[15] for i in result]

    lst2 = zip(cmpName,Jobtitle,fname,lname,cat1,cat2,cat3,cat4,cat5,cat6,cat7,cat8,cat9,status)

    return render_template('hireemp.html',lst2=lst2)



if __name__ == '__main__':
    app.run(debug=True)
    # app.run('0.0.0.0')
