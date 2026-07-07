from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


class BaseModel(db.Model):
    __abstract__ = True # Does not create table in db
    id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime(timezone = True), default = lambda:datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone = True), default = lambda:datetime.now(timezone.utc), onupdate = lambda:datetime.now(timezone.utc))

class User(BaseModel):
    __tablename__ = "user"
    email = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)

    role = db.Column(db.String, nullable = False)

# Relationship

    student_profile = db.relationship("Student_Profile", backref = "user", cascade = "all,delete", uselist = False)
    company_profile = db.relationship("Company_Profile", backref = "user", cascade = "all,delete", uselist = False)

class Student_Profile(BaseModel):
    __tablename__ = "student_profile" 
    fullname = db.Column(db.String, nullable = False)
    age= db.Column(db.Integer, nullable = False)
    gender = db.Column(db.String, nullable = False)
    qualification = db.Column(db.String, nullable = False)
    college_name = db.Column(db.String, nullable = False)
    experience = db.Column(db.Integer)
    contact_no = db.Column(db.Integer, nullable = False)
    skill = db.Column(db.String, nullable = False)
    resume = db.Column(db.String)

    is_blacklisted = db.Column(db.Boolean, default = False)
    is_active = db.Column(db.Boolean, default = True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete = "CASCADE"), nullable = False, unique = True)

# Relationship
    applications = db.relationship("Application", backref = "student_profile", cascade = "all, delete", lazy = True)

class Company_Profile(BaseModel):
    __tablename__ = "company_profile"
    
    company_name = db.Column(db.String, nullable = False)
    Hr_contact = db.Column(db.Integer, nullable = False)
    description = db.Column(db.String, nullable = False)
    company_type = db.Column(db.String, nullable = False)
    company_field = db.Column(db.String, nullable = False)
    website = db.Column(db.String, nullable = False)
    approval_status = db.Column(db.String, default = 'pending')

    
    is_blacklisted = db.Column(db.Boolean, default = False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete = "CASCADE"), nullable = False, unique =True)

# Relationship
    placement_drives = db.relationship("Placement_Drive", backref = "company_profile", lazy = True, cascade = "all, delete")
    
class Placement_Drive(BaseModel):
    __tablename__ = "placement_drive"
    
    drive_name = db.Column(db.String, nullable = False)
    job_title = db.Column(db.String, nullable = False)
    job_desc = db.Column(db.String, nullable = False)
    eligibility_criteria = db.Column(db.String, nullable = False)
    salary = db.Column(db.Integer)
    application_deadline = db.Column(db.Date, nullable = False)
    status = db.Column(db.String, default = 'pending')
    drive_status = db.Column(db.String, default = 'not_complete')

    company_id = db.Column(db.Integer, db.ForeignKey("company_profile.id", ondelete = "CASCADE"), nullable = False)

# Relationship

    applications = db.relationship("Application", backref = "placement_drive", cascade = "all, delete", lazy = True) 

class Application(BaseModel):
    __tablename__ = "application"
    status = db.Column(db.Enum("Applied", "Shortlisted", "Selected", "Rejected", name = "status"), default = 'Applied', nullable = False)

    student_id = db.Column(db.Integer, db.ForeignKey("student_profile.id", ondelete = "CASCADE"), nullable = False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drive.id", ondelete = "CASCADE"), nullable = False)


    __table_args__ = (db.UniqueConstraint("student_id", "drive_id", name = "unique_student_drive"),)

