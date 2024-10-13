from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///sampledb.sqlite3"
db=SQLAlchemy(app)
app.app_context().push()
class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(), unique=True, nullable=False)
    password=db.Column(db.String(), nullable=False)
    email=db.Column(db.String())
    priority=db.Column(db.Integer, nullable=False)
class Professional(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(), unique=True, nullable=False)
    password=db.Column(db.String(), nullable=False)
    email=db.Column(db.String())
    pin=db.Column(db.Integer, nullable=False)
    exp=db.Column(db.Integer, nullable=False)
    acc_reg=db.Column(db.Integer, nullable=False)
class Customer(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(), unique=True, nullable=False)
    password=db.Column(db.String(), nullable=False)
    full_name=db.Column(db.String(), nullable=False)
    pin=db.Column(db.Integer, nullable=False)
    email=db.Column(db.String())
db.drop_all()
db.create_all()
admin=User(username="admin_1@gmail.com",password="admin@8072",email="admin_1@gmail.com",priority=1)
db.session.add(admin)
db.session.commit()
visited=0
@app.route('/',methods=["GET","POST"])
def home():
    if request.method=="GET":
        return render_template('home_login.html')
    if request.method=='POST':
        email=request.form.get("email")
        password=request.form.get("password")
        users=User.query.all()
        p=True
        u=True
        for user in users:
            if(user.username==email):
                if(user.password==password):
                    return render_template("login.html",user=user)
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
        pin_code=request.form.get("PIN")
        customers=Customer.query.all()
        r=True
        for cust in customers:
            if(cust.username==email):
                r=False
                break
        if(r):
            cust_1=Customer(username=email,password=password,full_name=f_name,pin=pin_code,email=email)
            db.session.add(cust_1)
            db.session.commit()
            new_user=User(username=email,password=password,email=email,priority=3)
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
        pin_code=request.form.get("PIN")
        cust_1=Customer(username=email,password=password,full_name=f_name,pin=pin_code,email=email)
        db.session.add(cust_1)
        db.session.commit()
        return render_template("sign_up.html",email=email,password=password)
@app.route('/home_login.html')
def home_login():
    return redirect('/')
if (__name__=="__main__"):
    app.run(debug=True)