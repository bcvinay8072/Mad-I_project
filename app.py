from flask import Flask, render_template, request, redirect, url_for,session
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sampledb.sqlite3"
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
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

# Initial data setup
db.drop_all()
db.create_all()
admin = Admin(username="admin_1@gmail.com", password="admin@8072")
db.session.add(admin)
db.session.commit()
admin_1 = AppUser(username="admin_1@gmail.com", password="admin@8072", priority=1, admin_id=admin.id)
db.session.add(admin_1)
services = [
    Service(name="Plumbing", base_price=100.00, time_required=2, description="General plumbing services"),
    Service(name="Electrical", base_price=120.00, time_required=1.5, description="Electrical repairs and installations"),
    Service(name="Cleaning", base_price=80.00, time_required=3, description="House cleaning services"),
]
db.session.bulk_save_objects(services)
db.session.commit()
@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template('home_login.html')
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        users = AppUser.query.all()
        for user in users:
            if user.username == email and user.password == password:
                if user.priority == 1:
                    return redirect(url_for("admin_dashboard"))
                elif user.priority == 2:
                    session['user_id'] = user.id 
                    session['username'] = user.username
                    return render_template("prof_dashboard.html")
                else:
                    session['user_id'] = user.id 
                    session['username'] = user.username
                    return render_template('customer_dashboard.html')
        return "<h2>Invalid username or password</h2>"
    
@app.route('/admin_dashboard')
def admin_dashboard():
    services = Service.query.all()
    professionals = ServiceProfessional.query.all()
    requests = ServiceRequest.query.all()
    return render_template('admin_dashboard.html', services=services, professionals=professionals, requests=requests)

@app.route('/cust_signup.html', methods=["GET", "POST"])
def cust_signup():
    if request.method == "GET":
        return render_template("cust_signup.html")
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        f_name = request.form.get("fname")
        customers = Customer.query.all()
        for cust in customers:
            if cust.username == email:
                return "<h1>Username Already Exists, please use another username</h1>"
        cust_1 = Customer(username=email, password=password, name=f_name)
        db.session.add(cust_1)
        db.session.commit()
        new_user = AppUser(username=email, password=password, priority=3, customer_id=cust_1.id)
        db.session.add(new_user)
        db.session.commit()
        return render_template("sign_up.html", email=email, password=password)

@app.route('/prof_signup.html', methods=["GET", "POST"])
def prof_signup():
    if request.method == "GET":
        services = Service.query.all()
        return render_template("prof_signup.html", services=services)
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        f_name = request.form.get("fname")
        service_name = request.form.get("service")
        exp = request.form.get("exp")
        profs = ServiceProfessional.query.all()
        r = True
        for prof in profs:
            if prof.username == email:
                r = False
                break
        if r:
            prof_1 = ServiceProfessional(username=email, password=password, name=f_name, service_type=service_name, experience=exp)
            db.session.add(prof_1)
            db.session.commit()
            new_user = AppUser(username=email, password=password, priority=2, professional_id=prof_1.id)
            db.session.add(new_user)
            db.session.commit()
            return render_template("sign_up.html", email=email, password=password)
        else:
            return "<h1>Username Already Exists, kindly use another username</h1>"
@app.route('/add_service', methods=['GET', 'POST'])
def add_service():
    if request.method == 'POST':
        name = request.form['name']
        base_price = request.form['base_price']
        time_required = request.form['time_required']
        description = request.form['description']
        new_service = Service(name=name, base_price=base_price, time_required=time_required, description=description)
        db.session.add(new_service)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_service.html')

@app.route('/edit_service/<int:service_id>', methods=['GET', 'POST'])
def edit_service(service_id):
    service = Service.query.get(service_id)
    if request.method == 'POST':
        service.name = request.form['name']
        service.base_price = request.form['base_price']
        service.time_required = request.form['time_required']
        service.description = request.form['description']
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_service.html', service=service)

@app.route('/update_service/<int:service_id>', methods=['POST'])
def update_service(service_id):
    service = Service.query.get(service_id)
    service.name = request.form['name']
    service.base_price = request.form['base_price']
    service.time_required = request.form['time_required']
    service.description = request.form['description']
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_service/<int:service_id>', methods=['GET', 'POST'])
def delete_service(service_id):
    service = Service.query.get(service_id)
    db.session.delete(service)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/accept_professional/<int:professional_id>', methods=['GET'])
def accept_professional(professional_id):
    professional = ServiceProfessional.query.get(professional_id)
    if professional:
        professional.profile_docs_verified = True
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/reject_professional/<int:professional_id>', methods=['GET'])
def reject_professional(professional_id):
    professional = ServiceProfessional.query.get(professional_id)
    if professional:
        professional.blocked = True
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_professional/<int:professional_id>', methods=['GET'])
def delete_professional(professional_id):
    professional = ServiceProfessional.query.get(professional_id)
    if professional:
        db.session.delete(professional)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/prof_dashboard')
def prof_dashboard():
    # Logic for rendering the professional dashboard
    return render_template('prof_dashboard.html')

@app.route('/customer_dashboard')
def customer_dashboard():
    services = Service.query.all()
    requests = ServiceRequest.query.filter_by(customer_id=session['user_id']).all()  # Assuming a current_user context
    return render_template('customer_dashboard.html', services=services, requests=requests)
@app.route('/search', methods=['GET', 'POST'])
def search():
    services = []
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        search_type = request.form.get('search_type')
        
        if search_type == 'name':
            services = Service.query.filter(Service.name.ilike(f'%{search_term}%')).all()
        elif search_type == 'location':
            # Assuming the Service table has a location field
            services = Service.query.filter(Service.location.ilike(f'%{search_term}%')).all()
        elif search_type == 'pin_code':
            # Assuming the Service table has a pin_code field
            services = Service.query.filter_by(pin_code=search_term).all()

    return render_template('cust_search.html', services=services)

@app.route('/summary')
def summary():
    # Logic for rendering the search page
    return render_template('cust_summary.html')

@app.route('/logout')
def logout():
    # Logic for rendering the search page
    return render_template('cust_logout.html')

@app.route('/create_request', methods=['GET', 'POST'])
def create_request():
    if request.method == 'POST':
        service_id = request.form.get('service_id')
        date_of_request = request.form.get('date_of_request')
        new_request = ServiceRequest(service_id=service_id, customer_id=session['user_id'], date_of_request=date_of_request, service_status='Pending')
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for('customer_dashboard'))
    services = Service.query.all()
    return render_template('create_request.html', services=services)

@app.route('/edit_request/<int:request_id>', methods=['GET', 'POST'])
def edit_request(request_id):
    service_request = ServiceRequest.query.get(request_id)
    if request.method == 'POST':
        service_request.date_of_request = request.form.get('date_of_request')
        service_request.date_of_completion = request.form.get('date_of_completion')
        service_request.service_status = request.form.get('service_status')
        service_request.remarks = request.form.get('remarks')
        db.session.commit()
        return redirect(url_for('customer_dashboard'))
    return render_template('edit_request.html', request=service_request)

@app.route('/close_request/<int:request_id>', methods=['GET', 'POST'])
def close_request(request_id):
    service_request = ServiceRequest.query.get(request_id)
    service_request.service_status = 'Closed'
    db.session.commit()
    return redirect(url_for('customer_dashboard'))

@app.route('/home_login.html')
def home_login():
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
