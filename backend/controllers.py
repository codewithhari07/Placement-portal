import os
from flask import Flask, render_template, request, url_for, redirect, session, flash, abort
from .models import *
from app import app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_





@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods = ['GET', 'POST'])
def signin():
    if request.method == 'POST':
        uname = request.form.get("Email")
        pwd = request.form.get("Password")
        usr = User.query.filter_by(email = uname).first()

        if usr and check_password_hash(usr.password, pwd):
            
            # company approval status
            if usr.role == "company":

                if usr.company_profile.approval_status == "pending":
                    flash("Wait! Admin not appproved yet.", "warning")
                    return redirect(url_for("index"))
                
                if usr.company_profile.approval_status == "Rejected":
                    flash(f"You company {usr.company_profile.company_name}  has been rejected by admin", "danger")
                    return redirect(url_for("index"))
                
                if usr.company_profile.is_blacklisted:
                    flash(f"You company {usr.company_profile.company_name}  has been blocked by admin", "warning")
                    return redirect(url_for("index"))
                
            if usr.role == "student":
                if usr.student_profile.is_blacklisted:
                    flash(f"{usr.student_profile.fullname}  has been blocked by admin", "danger")
                    return redirect(url_for("index"))

                
            # store session
            session["user_id"] = usr.id
            session["email"] = usr.email
            session["role"] = usr.role

            if usr.role == 'admin':
                return redirect(url_for("admin_home")) 
            elif usr.role == 'company':
                return redirect(url_for("company_home")) 
            else:
                return redirect(url_for("student_home")) 
            
        else:
            flash("Invalid Credentials", "danger")
            return redirect(url_for("index"))
        
    return redirect(url_for("index"))


# Student Register
@app.route("/register", methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get("Email")
        pwd = generate_password_hash(request.form.get("Password"))
        full_name = request.form.get("Fname")
        age = request.form.get("Age")
        gender = request.form.get("Gender")
        qualification = request.form.get("Edu")
        coll_name = request.form.get("College_name")
        experience = request.form.get("Work_status")
        contact = request.form.get("M_no")
        skill = request.form.get("Skill")

        # Resume Upload
        resume_file = request.files.get("Resume")
        resume_filename = None

        if resume_file and resume_file.filename != "":
            filename = secure_filename(resume_file.filename)

            # save inside static foler
            upload = os.path.join("static/resumes", filename)
            resume_file.save(upload)

            resume_filename = filename

        usr = User.query.filter_by(email = email).first() 

        if usr:
            flash("Sorry, this mail already registered!", "warning")
            return render_template("signup.html")
        
        new_usr = User(email = email, password = pwd, role = 'student')
        db.session.add(new_usr)
        db.session.flush()

        new_student = Student_Profile(user_id = new_usr.id, fullname = full_name, age = age, gender = gender,
                                      qualification = qualification, college_name = coll_name, experience = experience, contact_no = contact, skill = skill, resume = resume_filename)
        db.session.add(new_student)
        db.session.commit()

        flash("Registration successfull, Login now", "info")
        return redirect(url_for("index"))

    return render_template("signup.html")

# Company register
@app.route("/company_register", methods = ['GET', 'POST'])
def company_signup():
    if request.method == 'POST':
        email = request.form.get("Email")
        pwd = generate_password_hash(request.form.get("Password"))
        company_name = request.form.get("Company_name")
        company_desc= request.form.get("Desc")
        company_type = request.form.get("C_type")
        field = request.form.get("Field")
        hr_contact = request.form.get("Hr_contact")
        website = request.form.get("Website")

        usr = User.query.filter_by(email = email).first()
        if usr:
            flash("Sorry, this company mail already registered!", "warning")
            return render_template("company_register.html")
        
        new_usr = User(email = email, password = pwd, role = "company")
        db.session.add(new_usr)
        db.session.flush()
        
        new_company = Company_Profile(user_id = new_usr.id, company_name = company_name, Hr_contact = hr_contact, description = company_desc, company_type = company_type, company_field = field, website = website)
        db.session.add(new_company)
        db.session.commit()

        flash("Company Registration successfully, Wait Admin Approval", "info")
        return redirect(url_for("index"))

    
    return render_template("company_register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logout successfully", "info")
    return redirect(url_for("index"))




@app.route("/admin_home")
def admin_home():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("index"))
    
    current_user = User.query.get(session['user_id'])
    all_company = Company_Profile.query.all()
    all_student = Student_Profile.query.all()
    all_drive = Placement_Drive.query.join(Company_Profile).filter(Company_Profile.is_blacklisted == False, Company_Profile.approval_status == "Approved").all()
    all_applied = Application.query.join(Student_Profile).filter(Student_Profile.is_blacklisted == False).all()

    # Stats..
    total_company = len(all_company)
    total_drive = len(all_drive)
    total_student = len(all_student)
    total_application = len(all_applied)


    return render_template("Admin/admin_home.html", user = current_user, companies = all_company, students = all_student, drives = all_drive, applications = all_applied, search_word = "", total_application= total_application, total_company = total_company, total_drive = total_drive, total_student = total_student )



@app.route("/company_home")
def company_home():
    if "user_id" not in session or session.get("role") != "company":
        return redirect(url_for("index"))
    
    current_user = User.query.get(session['user_id'])
    company = Company_Profile.query.filter_by(user_id = session["user_id"]).first_or_404()
    approve_drive = Placement_Drive.query.filter_by(company_id = company.id, status = "Approved", drive_status = "not_complete").all()

    completed_drive = Placement_Drive.query.filter_by(company_id = company.id, drive_status = "Completed").all()

    return render_template("Company/company_home.html", user = current_user, approve_drives = approve_drive, company = company, completed_drives = completed_drive)



@app.route("/student_home")
def student_home():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("index"))
    
    current_user = User.query.get(session['user_id'])
    student = Student_Profile.query.filter_by(user_id = session["user_id"]).first()
    all_company = Company_Profile.query.filter_by(approval_status = "Approved").all()
    all_applied = student.applications

    return render_template("Student/student_home.html", user = current_user, companies = all_company, applications = all_applied, student= student)



@app.route("/admin/company_approve/<int:id>/")
def company_approve(id):
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    
    company = Company_Profile.query.get_or_404(id)
    if company.approval_status == "Approved":
        flash(f"Company {company.company_name} aleardy approved", "info")
        return redirect(url_for("admin_home"))
    
    company.approval_status = "Approved"
    db.session.commit()

    flash(f"Company {company.company_name} approved", "success")
    return redirect(url_for("admin_home"))


@app.route("/admin/company_rejecte/<int:id>/")
def company_reject(id):
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    
    company = Company_Profile.query.get_or_404(id)
    if company.approval_status == "Rejected":
        flash(f"Company {company.company_name} aleardy Rejected", "info")
        return redirect(url_for("admin_home"))
    
    company.approval_status = "Rejected"
    db.session.commit()

    flash(f"Company {company.company_name} rejected", "warning")
    return redirect(url_for("admin_home"))




@app.route("/admin/company_blacklist/<int:id>/")
def company_blacklist(id):
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    
    company = Company_Profile.query.get_or_404(id)
    if company.approval_status != "Approved":
        flash(f"company {company.company_name} not approve yet", "info")
        return redirect(url_for("admin_home"))
    
    company.is_blacklisted = not company.is_blacklisted 
    db.session.commit()
    if company.is_blacklisted:
        flash(f"Company {company.company_name} Blacklisted", "danger")

    else:
        flash(f"company {company.company_name} Unblock", "success")

    return redirect(url_for("admin_home"))


# Student block by admin

@app.route("/admin/student_blacklist/<int:id>/")
def student_blacklist(id):
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    
    student = Student_Profile.query.get_or_404(id)
    
    student.is_blacklisted = not student.is_blacklisted 
    db.session.commit()
    if student.is_blacklisted:
        flash(f"{student.fullname} Blacklisted", "danger")

    else:
        flash(f"{student.fullname} Unblock", "success")

    return redirect(url_for("admin_home"))


@app.route("/admin/company_drive/<int:id>")
def company_drive(id):
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    
    drives = Placement_Drive.query.get_or_404(id)
    company = drives.company_profile

    if drives.status == "Approved":
        flash(f"Company {company.company_name} {drives.drive_name} aleardy approved", "info")
        return redirect(url_for("admin_home"))
    
    drives.status = "Approved"
    db.session.commit()

    flash(f"Company {company.company_name} {drives.drive_name} approved", "success")
    return redirect(url_for("admin_home"))



@app.route("/admin/ongoing_drives")
def ongoing_drives():
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    
    ongoing_drive = Placement_Drive.query.join(Company_Profile).filter(Company_Profile.is_blacklisted == False, Placement_Drive.status == "Approved").all()
    
    return render_template("Admin/ongoing_drives.html", drives = ongoing_drive)


@app.route("/admin/student_applied")
def student_applied():
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    
    student_applied = Application.query.join(Student_Profile).filter(Student_Profile.is_blacklisted == False ).all()

    return render_template("Admin/student_applications.html", applications = student_applied)


@app.route("/admin/search")
def admin_search():
    search_word = request.args.get("search"," ").strip()

    student = []
    company = []
    if search_word:
        student = Student_Profile.query.filter(or_(Student_Profile.fullname.ilike(f"%{search_word}%"), Student_Profile.id ==  search_word, Student_Profile.qualification.ilike(f"%{search_word}%"))).all()

        company = Company_Profile.query.filter(Company_Profile.company_name.ilike(f"%{search_word}%")).all()

    return render_template("Admin/admin_home.html",students = student, companies = company, search_word = search_word)


@app.route("/admin/student_details/<int:id>")
def student_details(id):
    if session.get("role") != "admin":
        return redirect(url_for("index"))
    
    applications = Application.query.get_or_404(id)

    return render_template("Admin/student_details.html", applications = applications)



# Company dashboard details
@app.route("/company/add_drive", methods = ['GET', 'POST'])
def add_drive():
    if session.get("role") != "company":
        return redirect(url_for("index"))
    

    user = User.query.get_or_404(session["user_id"])
    company =  user.company_profile

    if company.approval_status != "Approved":
        flash("Your company is approve yet", "warning")
        return redirect(url_for("index"))

    if request.method == 'POST':
        drive_name = request.form.get("Drivename")
        job_title = request.form.get("Jtitle")
        job_desc = request.form.get("Jdesc")
        eligibility = request.form.get("Criteria")
        deadline = datetime.strptime(request.form.get("Deadline"), "%Y-%m-%d").date()
        salary = request.form.get("Salary")

        new_drive = Placement_Drive(drive_name = drive_name, job_title = job_title, job_desc = job_desc, eligibility_criteria = eligibility, salary = salary, application_deadline = deadline,company_id = company.id)
        db.session.add(new_drive)
        db.session.commit()

        flash("New Drive created successfully", "success")
        return redirect(url_for("company_home"))
    
    return render_template("Company/add_drive.html", company= company)


@app.route("/company/edit_drive/<int:id>", methods = ["GET", "POST"])
def edit_drive(id):
    if session.get("role") != "company":
        return redirect(url_for("index"))
     
    drive = Placement_Drive.query.get_or_404(id)
    company = drive.company_profile

    if request.method == "POST":
        drive.job_title = request.form.get("Jtitle")
        drive.job_desc = request.form.get("Jdesc")
        drive.eligibility_criteria = request.form.get("Criteria")
        drive.application_deadline = datetime.strptime(request.form.get("Deadline"), "%Y-%m-%d").date()
        drive.salary = request.form.get("Salary")

        db.session.commit()
        flash(f"{drive.drive_name} Updated successfully", "success")

        return redirect(url_for("company_home"))

    return render_template("Company/edit_drive.html", drives = drive, company =company )


@app.route("/company/delete_drive/<int:id>", methods = ["GET", "POST"])
def delete_drive(id):
    if session.get("role") != "company":
        return redirect(url_for("index"))
     
    drive = Placement_Drive.query.get_or_404(id)

    db.session.delete(drive)
    db.session.commit()
    flash(f"{drive.drive_name} deleted successfully", "warning")
    return redirect(url_for("company_home"))


@app.route("/company/view_drive/<int:id>/applications")
def view_application_by_company(id):
    if session.get("role") != "company":
        return redirect(url_for("index"))    

    drive = Placement_Drive.query.get_or_404(id)
    company = drive.company_profile

    application = drive.applications

    return render_template("Company/see_drive_student.html", company= company, applications = application, drives = drive)

@app.route("/company/reivew_application/<int:id>/update", methods = ["GET","POST"])
def review_applications(id):
    if session.get("role") != "company":
        return redirect(url_for("index"))
    
    company = Company_Profile.query.filter_by(user_id = session["user_id"]).first()
    

    application = Application.query.get_or_404(id)

    if application.placement_drive.company_id != company.id:
        abort(403)

    if request.method == "POST":
        new_status = request.form.get("status")
        allowed_status = ["Shortlisted", "Selected", "Rejected"]

        if new_status not in allowed_status:
            flash("Invalid status selected", "danger")
            return redirect(url_for("review_applications", id = id))
    
        application.status = new_status
        db.session.commit()
        flash(f" Student {application.student_profile.fullname} application updated successfully", "success")
        return redirect(url_for("view_application_by_company", id = application.placement_drive.id))

    return render_template("Company/update_student_application.html", id = id , applications = application, company = company)

@app.route("/company/complete_drive/<int:id>/completed", methods = ["POST"])
def completed_drive(id):
    if session.get("role") != "company":
        return redirect(url_for("index"))
    
    company = Company_Profile.query.filter_by(user_id = session["user_id"]).first_or_404()

    drive = Placement_Drive.query.get_or_404(id)
    if drive.company_id != company.id:
        abort(403)

    drive.drive_status = "Completed"
    db.session.commit()

    return redirect(url_for("company_home"))



# Student Dashboard 

@app.route("/student/view_company/<int:id>")
def view_company(id):
    if session.get("role") != "student":
        return redirect(url_for("index"))
    
    student = Student_Profile.query.filter_by(user_id=session["user_id"]).first_or_404()
    company = Company_Profile.query.get_or_404(id)

    drive_approve = Placement_Drive.query.filter_by(company_id = company.id, status = "Approved", drive_status = "not_complete").all()

    return render_template("Student/company_details.html", company = company, drives = drive_approve, student=student )


@app.route("/student/job_apply/<int:id>", methods = ["GET", "POST"])
def job_apply(id):
    if session.get("role") != "student":
        return redirect(url_for("index"))
    
    drive = Placement_Drive.query.get_or_404(id)

    student = Student_Profile.query.filter_by(
        user_id=session["user_id"]
    ).first()

    if not student:
        flash("Student profile not found", "danger")
        return redirect(url_for("student_home"))

    #check exiting application
    exit_application  = Application.query.filter_by(student_id = student.id, drive_id = drive.id).first()

    if exit_application:
        flash("You have already applied", "warning")
        return redirect(url_for("student_home"))
    
    new_application = Application(student_id = student.id, drive_id = drive.id)
    db.session.add(new_application)
    db.session.commit()
    flash("Your Application submitted successfully", "success")
    return redirect(url_for("view_drive", id = drive.id ))


# Common Drive for both Admin and student

@app.route("/drive/<int:id>")
def view_drive(id):

    drive = Placement_Drive.query.get_or_404(id)

    role = session.get("role")
    status = None

    if role == "student":
        student = Student_Profile.query.filter_by(
            user_id=session["user_id"]
        ).first()
        if student:

            application = Application.query.filter_by(student_id = student.id, drive_id = drive.id).first()
        if application:
            status = application.status

    return render_template("view_drive.html", drives = drive, role = role, status= status)


@app.route("/student/edit_profile/<int:id>", methods = ["GET", "POST"])
def edit_profile(id):
    if session.get("role") != "student":
        return redirect(url_for("index"))
     
    student = Student_Profile.query.filter_by(user_id = session["user_id"]).first_or_404()

    if request.method == "POST":

        student.fullname = request.form.get("Fname")
        student.age = request.form.get("Age")
        student.gender = request.form.get("Gender")
        student.qualification = request.form.get("Edu")
        student.college_name = request.form.get("College_name")
        student.experience = request.form.get("Work_status")
        student.contact_no = request.form.get("M_no")
        student.skill = request.form.get("Skill")

         # Resume Upload
        resume_file = request.files.get("Resume")

        if resume_file and resume_file.filename != "":
            # Delete old resume if exits
            if student.resume:
                old_path = os.path.join("static/resume", student.resume)
                if os.path.exists(old_path):
                    os.remove(old_path)

            # Save new resume
            filename = secure_filename(resume_file.filename)

            unique_resume_name = f"{student.id}_{filename}"



            # save inside static foler
            upload = os.path.join("static/resumes", unique_resume_name)
            resume_file.save(upload)

            student.resume = unique_resume_name


        db.session.commit()
        flash("Profile Updated successfully", "success")

        return redirect(url_for("student_home"))

    return render_template("Student/edit_profile.html", student = student)

@app.route("/student/history/")
def student_history():
    if session.get("role") != "student":
        return redirect(url_for("index"))
    
    student = Student_Profile.query.filter_by(user_id = session["user_id"]).first_or_404()
    application = Application.query.join(Placement_Drive).filter(Application.student_id == student.id, Placement_Drive.drive_status == "Completed").all()


    return render_template("Student/history.html", applications = application, student= student )

