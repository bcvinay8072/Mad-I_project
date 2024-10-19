from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///sampledb.sqlite3"
db=SQLAlchemy(app)
app.app_context().push()
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class ServiceProfessional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    profile_docs_verified = db.Column(db.Boolean, default=False)
    blocked = db.Column(db.Boolean, default=False)
    service_type = db.Column(db.String(80), default="None")
    experience = db.Column(db.Integer, nullable=False)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    blocked = db.Column(db.Boolean, default=False)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.Integer)
    description = db.Column(db.String(200))

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id'))
    date_of_request = db.Column(db.Date)
    date_of_completion = db.Column(db.Date)
    service_status = db.Column(db.String(50))
    remarks = db.Column(db.String(200))

class AppUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id'), nullable=True)
# class User(db.Model):
#     id=db.Column(db.Integer, primary_key=True)
#     username=db.Column(db.String(), unique=True, nullable=False)
#     password=db.Column(db.String(), nullable=False)
#     email=db.Column(db.String())
#     priority=db.Column(db.Integer, nullable=False)
# class Professional(db.Model):
#     id=db.Column(db.Integer, primary_key=True)
#     username=db.Column(db.String(), unique=True, nullable=False)
#     password=db.Column(db.String(), nullable=False)
#     email=db.Column(db.String())
#     pin=db.Column(db.Integer, nullable=False)
#     exp=db.Column(db.Integer, nullable=False)
#     acc_reg=db.Column(db.Integer, nullable=False)
# class Customer(db.Model):
#     id=db.Column(db.Integer, primary_key=True)
#     username=db.Column(db.String(), unique=True, nullable=False)
#     password=db.Column(db.String(), nullable=False)
#     full_name=db.Column(db.String(), nullable=False)
#     pin=db.Column(db.Integer, nullable=False)
#     email=db.Column(db.String())
db.drop_all()
db.create_all()
admin=Admin(username="admin_1@gmail.com",password="admin@8072")
db.session.add(admin)
db.session.commit()
admin_1=AppUser(username="admin_1@gmail.com",password="admin@8072",priority=1,admin_id=admin.id)
db.session.add(admin_1)
db.session.commit()
visited=0
@app.route('/',methods=["GET","POST"])
def home():
    if request.method=="GET":
        return render_template('home_login.html')
    if request.method=='POST':
        email=request.form.get("email")
        password=request.form.get("password")
        users=AppUser.query.all()
        p=True
        u=True
        for user in users:
            if(user.username==email):
                if(user.password==password):
                    if(user.priority==1):
                        return render_template("admin_dashboard.html")
                    elif(user.priority==2):
                        return render_template("prof_dashboard.html")
                    else:   
                        return render_template("cust_dashboard.html")
                else:
                    p=False
            else:
                u=False
        if(p==False):
            return "<h2>Invalid password</h2>"
        elif(u==False):
            return "<h2>User doesn't exist please register!!</h2>"
@app.route('/cust_signup.html',methods=["GET","POST"])
def cust_signup():
    if request.method=="GET":
        return render_template("cust_signup.html")
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
        f_name=request.form.get("fname")
        customers=Customer.query.all()
        r=True
        for cust in customers:
            if(cust.username==email):
                r=False
                break
        if(r):
            cust_1=Customer(username=email,password=password,name=f_name)
            db.session.add(cust_1)
            db.session.commit()
            new_user=AppUser(username=email,password=password,priority=3,customer_id=cust_1.id)
            db.session.add(new_user)
            db.session.commit()
            return render_template("sign_up.html",email=email,password=password)
        else:
            return "<h1>Username Already Exist kindly use another username</h1>"
@app.route('/prof_signup.html',methods=["GET","POST"])
def prof_signup():
    if request.method=="GET":
        return render_template("prof_signup.html")
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
        f_name=request.form.get("fname")
        exp=request.form.get("exp")
        profs=ServiceProfessional.query.all()
        r=True
        for prof in profs:
            if(prof.username==email):
                r=False
                break
        if(r):
            prof_1=ServiceProfessional(username=email,password=password,name=f_name,experience=exp)
            db.session.add(prof_1)
            db.session.commit()
            new_user=AppUser(username=email,password=password,priority=2,professional_id=prof_1.id)
            db.session.add(new_user)
            db.session.commit()
            return render_template("sign_up.html",email=email,password=password)
        else:
            return "<h1>Username Already Exist kindly use another username</h1>"
@app.route('/home_login.html')
def home_login():
    return redirect('/')
if (__name__=="__main__"):
    app.run(debug=True)