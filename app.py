from flask import Flask, render_template, request, redirect, url_for,session
from flask_sqlalchemy import SQLAlchemy 
from models import db, Admin, ServiceProfessional, Customer, Service, ServiceRequest,AppUser

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sampledb.sqlite3"
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)
app.app_context().push()

# Initial data setup
db.drop_all()
db.create_all()

# Add an admin
admin = Admin(username="admin_1@gmail.com", password="admin@8072")
db.session.add(admin)
db.session.commit()

admin_1 = AppUser(username="admin_1@gmail.com", password="admin@8072", priority=1, admin_id=admin.id)
db.session.add(admin_1)

# Add services
services = [
    Service(name="Plumbing", base_price=100.00, time_required=2, description="General plumbing services"),
    Service(name="Electrical", base_price=120.00, time_required=1.5, description="Electrical repairs and installations"),
    Service(name="Cleaning", base_price=80.00, time_required=3, description="House cleaning services"),
]
db.session.bulk_save_objects(services)
db.session.commit()

# Add professionals
professional_1 = ServiceProfessional(username="prof_1@gmail.com", password="prof1", name="Professional One", service_type="Plumbing", experience=5, about="Expert Plumber", location="Mumbai", pincode=587134)
professional_2 = ServiceProfessional(username="prof_2@gmail.com", password="prof2", name="Professional Two", service_type="Electrical", experience=7, about="Highly professional", location="New Delhi", pincode=512839)
db.session.add(professional_1)
db.session.add(professional_2)
db.session.commit()

app_user_prof_1 = AppUser(username="prof_1@gmail.com", password="prof1", priority=2, professional_id=professional_1.id)
app_user_prof_2 = AppUser(username="prof_2@gmail.com", password="prof2", priority=2, professional_id=professional_2.id)
db.session.add(app_user_prof_1)
db.session.add(app_user_prof_2)
db.session.commit()

# Add customers
customer_1 = Customer(username="cust_1@gmail.com", password="cust1", name="Customer One")
customer_2 = Customer(username="cust_2@gmail.com", password="cust2", name="Customer Two")
db.session.add(customer_1)
db.session.add(customer_2)
db.session.commit()

app_user_cust_1 = AppUser(username="cust_1@gmail.com", password="cust1", priority=3, customer_id=customer_1.id)
app_user_cust_2 = AppUser(username="cust_2@gmail.com", password="cust2", priority=3, customer_id=customer_2.id)
db.session.add(app_user_cust_1)
db.session.add(app_user_cust_2)
db.session.commit()


@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template('home_login.html')
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = AppUser.query.filter_by(username=email, password=password).first()
        if user:
            session['user_id'] = user.customer_id or user.professional_id  # Ensure this is set correctly
            session['username'] = user.username
            session['priority'] = user.priority
            if user.priority == 1:
                return redirect(url_for("admin_dashboard"))
            elif user.priority == 2:
                prof_user=ServiceProfessional.query.get(user.professional_id)
                if(prof_user.blocked==0):
                    return redirect(url_for("prof_dashboard"))
                else:
                    return "<h2>Sorry professional you are blocked by admin..</h2>"
            else:
                c_user=Customer.query.get(user.customer_id)
                if(c_user.blocked==0):
                    return redirect(url_for("customer_dashboard"))
                else:
                    return "<h2>Sorry customer you are blocked by admin..</h2>"
        return "<h2>Invalid username or password</h2>"




@app.route('/prof_dashboard')
def prof_dashboard():
    professional_id = session['user_id']  # Assume professional is logged in
    professional = ServiceProfessional.query.get(professional_id)
    
    pending_requests = ServiceRequest.query.join(Service, ServiceRequest.service_id == Service.id).filter(
        Service.name == professional.service_type,
        ServiceRequest.service_status == 'Pending'
    ).all()
    
    accepted_requests = ServiceRequest.query.filter_by(professional_id=professional_id, service_status='Accepted').all()
    completed_requests = ServiceRequest.query.filter_by(professional_id=professional_id, service_status='Completed').all()
    
    return render_template(
        'prof_dashboard.html',
        professional=professional,
        pending_requests=pending_requests,
        accepted_requests=accepted_requests,
        completed_requests=completed_requests
    )


@app.route('/customer_dashboard')
def customer_dashboard():
    customer_id = session['user_id']  # Assume customer is logged in
    customer = Customer.query.get(customer_id)
    
    pending_requests = ServiceRequest.query.filter_by(customer_id=customer_id, service_status='Pending').all()
    accepted_requests = ServiceRequest.query.filter_by(customer_id=customer_id, service_status='Accepted').all()
    completed_requests = ServiceRequest.query.filter_by(customer_id=customer_id, service_status='Completed').all()
    
    services = Service.query.all()  # Fetch all services for creating new requests
    
    return render_template(
        'customer_dashboard.html',
        customer=customer,
        pending_requests=pending_requests,
        accepted_requests=accepted_requests,
        completed_requests=completed_requests,
        services=services
    )


@app.route('/admin_dashboard', methods=['GET'])
def admin_dashboard():
    search_query = request.args.get('search_query', '')
    
    if search_query:
        professionals = ServiceProfessional.query.filter(
            ServiceProfessional.name.ilike(f'%{search_query}%') |
            ServiceProfessional.username.ilike(f'%{search_query}%')
        ).all()
    else:
        professionals = ServiceProfessional.query.all()
    
    services = Service.query.all()
    customers = Customer.query.all()
    requests = ServiceRequest.query.all()
    
    return render_template('admin_dashboard.html', services=services, professionals=professionals, customers=customers, requests=requests)

@app.route('/cust_signup.html', methods=["GET", "POST"])
def cust_signup():
    services = Service.query.all()
    if request.method == "GET":
        return render_template("cust_signup.html",services=services)
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

@app.route('/prof_signup.html', methods=['GET', 'POST'])
def prof_signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        loc = request.form.get('address')
        pin = request.form.get('pincode')
        service_type = request.form.get('service_type')
        experience = request.form.get('experience')
        phone_no = request.form.get('phone_no')
        about = request.form.get('about')
        profile_docs_verified = False
        blocked = False
        
        new_professional = ServiceProfessional(
            username=username,
            password=password,
            name=name,
            service_type=service_type,
            experience=experience,
            phone_no=phone_no,
            about=about,
            location=loc,
            pincode=pin,
            verified=profile_docs_verified,
            blocked=blocked
        )
        db.session.add(new_professional)
        db.session.commit()
        return redirect(url_for('login'))

    # Query services and pass them to the template
    services = Service.query.all()
    return render_template('prof_signup.html', services=services)


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
        professional.verified = True
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

@app.route('/accept_request/<int:request_id>', methods=['POST'])
def accept_request(request_id):
    request = ServiceRequest.query.get(request_id)
    request.service_status = 'Accepted'
    request.professional_id = session['user_id']  # Set the professional ID
    db.session.commit()
    return redirect(url_for('prof_dashboard'))

@app.route('/reject_request/<int:request_id>', methods=['POST'])
def reject_request(request_id):
    request = ServiceRequest.query.get(request_id)
    request.service_status = 'Rejected'
    db.session.commit()
    return redirect(url_for('prof_dashboard'))

@app.route('/update_request_status/<int:request_id>', methods=['POST'])
def update_request_status(request_id):
    service_request = ServiceRequest.query.get(request_id)
    
    if service_request:
        new_status = request.form.get('status')  
        service_request.service_status = new_status
        if new_status == 'Completed':
            service_request.date_of_completion = datetime.now().date()
        db.session.commit()
    
    return redirect(url_for('prof_dashboard'))

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

from datetime import datetime

# Existing route to handle creation without a pre-selected service ID
@app.route('/create_request', methods=['GET', 'POST'])
@app.route('/create_request/<int:service_id>', methods=['GET', 'POST'])
def create_request(service_id=None):
    if request.method == 'POST':
        if service_id is None:
            service_id = request.form.get('service_id')
        date_of_request_str = request.form.get('date_of_request')
        date_of_request = datetime.strptime(date_of_request_str, '%Y-%m-%d').date()

        new_request = ServiceRequest(
            service_id=service_id,
            customer_id=session['user_id'],  # Ensure this is correctly set
            date_of_request=date_of_request,
            service_status='Pending'
        )
        db.session.add(new_request)
        db.session.commit()

        # Fetch the service and notify professionals
        service = Service.query.get(service_id)
        professionals = ServiceProfessional.query.filter_by(service_type=service.name, verified=True, blocked=False).all()
        for professional in professionals:
            print(f'New service request for {professional.name} - ID: {professional.id}')

        return redirect(url_for('customer_dashboard'))

    services = Service.query.all()
    return render_template('create_request.html', services=services, selected_service_id=service_id)

from datetime import datetime

@app.route('/edit_request/<int:request_id>', methods=['GET', 'POST'])
def edit_request(request_id):
    service_request = ServiceRequest.query.get(request_id)
    if request.method == 'POST':
        date_of_request_str = request.form.get('date_of_request')
        date_of_completion_str = request.form.get('date_of_completion')
        service_request.date_of_request = datetime.strptime(date_of_request_str, '%Y-%m-%d').date()
        service_request.date_of_completion = datetime.strptime(date_of_completion_str, '%Y-%m-%d').date() if date_of_completion_str else None
        service_request.service_status = request.form.get('service_status')
        service_request.remarks = request.form.get('remarks')
        db.session.commit()
        return redirect(url_for('customer_dashboard'))
    return render_template('edit_request.html', request=service_request)

@app.route('/close_request/<int:request_id>', methods=['GET', 'POST'])
def close_request(request_id):
    service_request = ServiceRequest.query.get(request_id)
    
    if service_request:
        if request.method == 'POST':  # Correctly using Flask's request object
            review = request.form.get('review')
            rating = int(request.form.get('rating'))
            
            # Update the service request
            service_request.service_status = 'Completed'
            service_request.date_of_completion = datetime.now().date()
            service_request.remarks = review
            service_request.rating = rating

            # Update the professional's rating
            professional = service_request.professional
            if professional:
                total_rating = professional.rating * professional.rating_count
                new_total_rating = total_rating + rating
                professional.rating_count += 1
                professional.rating = new_total_rating / professional.rating_count
            
            db.session.commit()
            
            return redirect(url_for('customer_dashboard'))
        
        return render_template('close_request.html', request=service_request)
    return redirect(url_for('customer_dashboard'))


@app.route('/delete_request/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        return "<h2>Service request not found</h2>", 404
    
    db.session.delete(service_request)
    db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/search_professionals', methods=['GET'])
def search_professionals():
    search_query = request.args.get('search_query', '')
    
    if search_query:
        professionals = ServiceProfessional.query.filter(
            ServiceProfessional.name.ilike(f'%{search_query}%') |
            ServiceProfessional.username.ilike(f'%{search_query}%')
        ).all()
    else:
        professionals = []

    return render_template('search_professionals.html', professionals=professionals, search_query=search_query)

@app.route('/search_services', methods=['GET'])
def search_services():
    search_type = request.args.get('search_type')
    search_term = request.args.get('search_term')
    
    search_results = []

    if search_type and search_term:
        if search_type == 'name':
            search_results = Service.query.filter(Service.name.ilike(f'%{search_term}%')).all()
        elif search_type == 'location':
            search_results = Service.query.join(ServiceProfessional, Service.name == ServiceProfessional.service_type).filter(ServiceProfessional.location.ilike(f'%{search_term}%')).all()
        elif search_type == 'pin_code':
            search_results = Service.query.join(ServiceProfessional, Service.name == ServiceProfessional.service_type).filter(ServiceProfessional.pincode.ilike(f'%{search_term}%')).all()

    return render_template('search.html', search_results=search_results)


@app.route('/toggle_block_customer/<int:customer_id>', methods=['POST'])
def toggle_block_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return "<h2>Customer not found</h2>", 404
    
    customer.blocked = not customer.blocked
    db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/toggle_block_professional/<int:professional_id>', methods=['POST'])
def toggle_block_professional(professional_id):
    professional = ServiceProfessional.query.get(professional_id)
    if not professional:
        return "<h2>Professional not found</h2>", 404
    
    professional.blocked = not professional.blocked
    db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

import matplotlib.pyplot as plt
import io
import base64

@app.route('/cust_summary')
def cust_summary():
    customer_id = session['user_id']
    
    # Calculate the number of requested, closed, and accepted requests
    num_requested = ServiceRequest.query.filter_by(customer_id=customer_id, service_status='Pending').count()
    num_closed = ServiceRequest.query.filter_by(customer_id=customer_id, service_status='Completed').count()
    num_accepted = ServiceRequest.query.filter_by(customer_id=customer_id, service_status='Accepted').count()

    request_data = [num_requested, num_closed, num_accepted]
    labels = ['Requested', 'Closed', 'Accepted']

    # Create the bar chart using Matplotlib
    fig, ax = plt.subplots()
    ax.bar(labels, request_data, color=['blue', 'green', 'orange'])
    ax.set_xlabel('Request Status')
    ax.set_ylabel('Number of Requests')
    ax.set_title('Service Request Summary')

    # Save the chart to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.getvalue()).decode()

    return render_template('cust_summary.html', chart_base64=chart_base64)

@app.route('/prof_summary')
def prof_summary():
    professional_id = session['user_id']
    
    # Calculate the number of received, closed, and rejected requests
    num_received = ServiceRequest.query.filter_by(service_status='Pending').count()+ServiceRequest.query.filter_by(professional_id=professional_id, service_status='Accepted').count()
    num_closed = ServiceRequest.query.filter_by(professional_id=professional_id, service_status='Completed').count()
    num_rejected = ServiceRequest.query.filter_by(service_status='Rejected').count()

    request_data = [num_received, num_closed, num_rejected]
    labels = ['Received', 'Closed', 'Rejected']

    # Create the bar chart using Matplotlib
    fig, ax = plt.subplots()
    ax.bar(labels, request_data, color=['blue', 'green', 'red'])
    ax.set_xlabel('Request Status')
    ax.set_ylabel('Number of Requests')
    ax.set_title('Service Request Summary')

    # Save the chart to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.getvalue()).decode()

    return render_template('prof_summary.html', chart_base64=chart_base64)
@app.route('/admin_summary')
def admin_summary():
    
    # Calculate the number of received, closed, and rejected requests
    num_received = len(ServiceRequest.query.all())
    num_closed = ServiceRequest.query.filter_by(service_status='Completed').count()
    num_rejected = ServiceRequest.query.filter_by(service_status='Rejected').count()

    request_data = [num_received, num_closed, num_rejected]
    labels = ['Received', 'Closed', 'Rejected']

    # Create the bar chart using Matplotlib
    fig, ax = plt.subplots()
    ax.bar(labels, request_data, color=['blue', 'green', 'red'])
    ax.set_xlabel('Request Status')
    ax.set_ylabel('Number of Requests')
    ax.set_title('Service Request Summary')

    # Save the chart to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.getvalue()).decode()

    return render_template('admin_summary.html', chart_base64=chart_base64)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/home_login.html')
def home_login():
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
