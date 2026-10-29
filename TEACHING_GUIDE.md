# Havenly — Step-by-Step Teaching Guide (Day 7)
## Feature: Customer Service Booking & Professional Acceptance

This guide is designed for you (the instructor) to teach your students how to complete the core marketplace workflow of the **Havenly** application: **Customers requesting a service** and **Professionals accepting that request**.

---

## 1. Context & Roadmap Recap (Day 1 to Day 6)

Before introducing today's topic, take 5 minutes to recap what students have already built:

| Day | Topic Built | Key Concepts Covered |
| :--- | :--- | :--- |
| **Day 1** | Initial Flask Setup & Templates | Flask app initialization, basic routing (`/`, `/login`), rendering Jinja2 templates. |
| **Day 2** | Database & Extensions Setup | SQLite configuration, Flask-SQLAlchemy, `User` model, Bootstrap base layout. |
| **Day 3** | Domain Models & Registration | Extended models (`Customer`, `Professional`, `Service`), registration forms for both roles. |
| **Day 4** | Authentication & Role Routing | Password hashing (`generate_password_hash`), Flask-Login session management, role-based dashboard redirects. |
| **Day 5** | Admin: Professional Management | Admin blueprint (`admin_bp`), approving/rejecting professionals, toggling active/blacklist status. |
| **Day 6** | Admin Services & Customer Catalog | Admin CRUD operations for services, customer blueprint (`customer_bp`), services catalog page (`/customer/services`). |
| **Day 7 (Today)** | **Customer Booking & Professional Acceptance** | Creating a transactional model (`ServiceRequest`), booking via modal form, role-filtered dashboard views, and accepting requests. |

---

## 2. Today's Learning Objectives

By the end of this session, students will understand:
1. **Transactional Data Modeling**: Designing a model (`ServiceRequest`) that connects three existing models (`Customer`, `Service`, `Professional`).
2. **State Management**: Managing an entity's lifecycle through status flags (`requested` $\rightarrow$ `accepted`).
3. **Form Submission from Modals**: Sending dynamic IDs and input data from Bootstrap modals to Flask POST routes.
4. **Relational Querying**: Filtering data based on user profile IDs and assigned service categories.
5. **Blueprint Modularity**: Creating a clean `professional_bp` blueprint following the established patterns in `admin_bp` and `customer_bp`.

---

## 3. Step-by-Step Implementation Guide

Follow these sequential steps during your lecture.

---

### Step 1: The Data Model (`ServiceRequest`)
**File**: `app/models.py`

#### 🗣️ Teacher Explanation to Students:
> *"Up until now, our models (`Customer`, `Professional`, `Service`) existed independently. When a customer wants a service, we need a record that captures this transaction. At the moment of booking, we know who the customer is, which service they want, and when they want it. However, no professional has accepted it yet! That is why `professional_id` must be nullable (`nullable=True`)."*

#### 💻 Code to Add:
```python
class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=True) # None until accepted!
    date = db.Column(db.String(20), nullable=False)
    time_slot = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='requested') # 'requested' -> 'accepted'
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))

    # Relationships for convenient access in templates (e.g. req.service.name)
    customer = db.relationship('Customer', backref='service_requests')
    service = db.relationship('Service', backref='service_requests')
    professional = db.relationship('Professional', backref='service_requests')
```

> [!NOTE]
> Point out to students how `backref='service_requests'` allows accessing `customer.service_requests` or `service_request.service.name` directly in Jinja templates without manual SQL joins.

---

### Step 2: The Customer Booking Route & Modal Form
**Files**: `app/templates/customer/services.html` & `app/routes/customer.py`

#### 🗣️ Teacher Explanation:
> *"In Day 6, we created the service cards and wrote the Bootstrap modal in `services.html`. Notice that `<form method="POST" action="">` had an empty action. Now, we define the route to handle this form and connect the form's action to it."*

#### 💻 2A. Update the Form Action in `app/templates/customer/services.html`:
Find the modal `<form>` tag and set its action:
```html
<form method="POST" action="{{ url_for('customer_bp.book_service') }}">
  <input type="hidden" name="service_id" value="{{ service.id }}" />
  <!-- date and time_slot inputs remain unchanged -->
```

#### 💻 2B. Add `book_service` Route in `app/routes/customer.py`:
```python
from datetime import datetime
from flask import Blueprint, flash, render_template, url_for, redirect, request
from flask_login import login_required, current_user
from app.models import Service, ServiceRequest
from app.extensions import db

@customer_bp.route('/services')
@login_required
def services():
    services = Service.query.all()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('/customer/services.html', services=services, today=today)

@customer_bp.route('/book-service', methods=['POST'])
@login_required
def book_service():
    if not current_user.customer_profile:
        flash("Only customers can book services.", "danger")
        return redirect(url_for('customer_bp.services'))

    service_id = request.form.get('service_id')
    date = request.form.get('date')
    time_slot = request.form.get('time_slot')

    if not service_id or not date or not time_slot:
        flash("Please fill in all booking details.", "danger")
        return redirect(url_for('customer_bp.services'))

    new_request = ServiceRequest(
        customer_id=current_user.customer_profile.id,
        service_id=int(service_id),
        date=date,
        time_slot=time_slot,
        status='requested'
    )
    db.session.add(new_request)
    db.session.commit()

    flash("Service requested successfully!", "success")
    return redirect(url_for('customer_bp.dashboard'))
```

---

### Step 3: Customer Dashboard — Viewing Booked Requests
**Files**: `app/routes/customer.py` & `app/templates/customer/dashboard.html`

#### 🗣️ Teacher Explanation:
> *"Once a customer books a service, they need to see their requests and know whether a professional has accepted yet."*

#### 💻 3A. Update `dashboard()` in `app/routes/customer.py`:
```python
@customer_bp.route('/dashboard')
@login_required
def dashboard():
    requests = []
    if current_user.customer_profile:
        requests = ServiceRequest.query.filter_by(
            customer_id=current_user.customer_profile.id
        ).all()
    return render_template('/customer/dashboard.html', requests=requests)
```

#### 💻 3B. Display Requests Table in `app/templates/customer/dashboard.html`:
```html
{% extends 'base.html' %}
{% block title %}Customer Dashboard{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
  <div>
    <h1>Customer Dashboard</h1>
    <p class="text-muted mb-0">Welcome, {{ current_user.username }}!</p>
  </div>
  <a href="{{ url_for('customer_bp.services') }}" class="btn btn-primary">Book a Service</a>
</div>

<h3 class="mt-4 mb-3">My Service Requests</h3>

{% if requests %}
<div class="table-responsive">
  <table class="table table-hover align-middle">
    <thead class="table-light">
      <tr>
        <th scope="col">#</th>
        <th scope="col">Service</th>
        <th scope="col">Price</th>
        <th scope="col">Date</th>
        <th scope="col">Time Slot</th>
        <th scope="col">Status</th>
        <th scope="col">Professional</th>
      </tr>
    </thead>
    <tbody>
      {% for req in requests %}
      <tr>
        <th scope="row">{{ loop.index }}</th>
        <td>{{ req.service.name }}</td>
        <td>${{ "%.2f"|format(req.service.price) }}</td>
        <td>{{ req.date }}</td>
        <td>{{ req.time_slot }}</td>
        <td>
          {% if req.status == 'requested' %}
            <span class="badge bg-warning text-dark">Requested</span>
          {% elif req.status == 'accepted' %}
            <span class="badge bg-success">Accepted</span>
          {% endif %}
        </td>
        <td>
          {% if req.professional %}
            <strong>{{ req.professional.user.username }}</strong>
          {% else %}
            <span class="text-muted fst-italic">Waiting for professional...</span>
          {% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% else %}
<div class="card p-5 text-center">
  <p class="text-muted mb-3">You haven't requested any services yet.</p>
  <div>
    <a href="{{ url_for('customer_bp.services') }}" class="btn btn-outline-primary">Browse Services</a>
  </div>
</div>
{% endif %}
{% endblock %}
```

---

### Step 4: Professional Blueprint & Acceptance Logic
**File**: `app/routes/professional.py` (New file!)

#### 🗣️ Teacher Explanation:
> *"Notice our architecture: admin features are in `admin.py`, customer features are in `customer.py`. To keep code clean and maintainable, professional features belong in `professional.py`.*
> *When a professional logs in, what should they see?*
> 1. *Requests that match their specific skill/service (`prof.service_id`) and have not been taken yet (`status == 'requested'`).*
> 2. *Requests they have already accepted (`professional_id == prof.id`)."*

#### 💻 Create `app/routes/professional.py`:
```python
from flask import Blueprint, flash, render_template, url_for, redirect
from flask_login import login_required, current_user
from app.models import ServiceRequest
from app.extensions import db

professional_bp = Blueprint('professional_bp', __name__, url_prefix='/professional')


@professional_bp.route('/dashboard')
@login_required
def dashboard():
    prof = current_user.professional_profile
    if not prof:
        flash("Professional profile not found.", "danger")
        return redirect(url_for('views.home'))

    available_requests = []
    accepted_requests = []

    if prof.service_id:
        # 1. Matching service requests waiting for a professional
        available_requests = ServiceRequest.query.filter_by(
            service_id=prof.service_id,
            status='requested'
        ).all()

        # 2. Requests already accepted by this professional
        accepted_requests = ServiceRequest.query.filter_by(
            professional_id=prof.id
        ).all()

    return render_template(
        '/professional/dashboard.html',
        available_requests=available_requests,
        accepted_requests=accepted_requests,
        professional=prof
    )


@professional_bp.route('/accept-request/<int:request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    prof = current_user.professional_profile
    if not prof:
        flash("Only professionals can accept service requests.", "danger")
        return redirect(url_for('views.home'))

    service_request = ServiceRequest.query.get(request_id)
    if not service_request:
        flash("Service request not found.", "danger")
        return redirect(url_for('professional_bp.dashboard'))

    # Guard: check if another professional already accepted it
    if service_request.status != 'requested':
        flash("This request is no longer available.", "warning")
        return redirect(url_for('professional_bp.dashboard'))

    # Assign professional and update status
    service_request.professional_id = prof.id
    service_request.status = 'accepted'
    db.session.commit()

    flash(f"You have accepted the booking for {service_request.service.name}!", "success")
    return redirect(url_for('professional_bp.dashboard'))
```

---

### Step 5: Professional Dashboard Template
**File**: `app/templates/professional/dashboard.html`

#### 🗣️ Teacher Explanation:
> *"We divide the dashboard into two clean cards: 'Available Requests' with an Accept button, and 'My Accepted Requests' showing the assigned client's contact and address."*

#### 💻 Code for `app/templates/professional/dashboard.html`:
```html
{% extends 'base.html' %}
{% block title %}Professional Dashboard{% endblock %}
{% block content %}
<div class="mb-4">
  <h1>Professional Dashboard</h1>
  <p class="text-muted">Welcome, <strong>{{ current_user.username }}</strong>!</p>
  <div>
    <span class="badge bg-primary">
      Service: {{ professional.service.name if professional.service else 'Not Assigned' }}
    </span>
    {% if professional.approved %}
      <span class="badge bg-success">Approved</span>
    {% else %}
      <span class="badge bg-warning text-dark">Pending Approval</span>
    {% endif %}
  </div>
</div>

<!-- 1. Available Requests -->
<div class="card mb-5 shadow-sm">
  <div class="card-header bg-white">
    <h4 class="mb-0">Available Requests ({{ professional.service.name if professional.service else 'General' }})</h4>
  </div>
  <div class="card-body">
    {% if available_requests %}
    <div class="table-responsive">
      <table class="table table-hover align-middle">
        <thead class="table-light">
          <tr>
            <th scope="col">#</th>
            <th scope="col">Customer</th>
            <th scope="col">Address</th>
            <th scope="col">Date</th>
            <th scope="col">Time Slot</th>
            <th scope="col">Action</th>
          </tr>
        </thead>
        <tbody>
          {% for req in available_requests %}
          <tr>
            <th scope="row">{{ loop.index }}</th>
            <td>{{ req.customer.user.username }}</td>
            <td>{{ req.customer.address or 'N/A' }}</td>
            <td>{{ req.date }}</td>
            <td>{{ req.time_slot }}</td>
            <td>
              <form action="{{ url_for('professional_bp.accept_request', request_id=req.id) }}" method="POST">
                <button type="submit" class="btn btn-sm btn-success">Accept</button>
              </form>
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% else %}
    <p class="text-muted mb-0">No new service requests available right now.</p>
    {% endif %}
  </div>
</div>

<!-- 2. Accepted Requests -->
<div class="card shadow-sm">
  <div class="card-header bg-white">
    <h4 class="mb-0">My Accepted Requests</h4>
  </div>
  <div class="card-body">
    {% if accepted_requests %}
    <div class="table-responsive">
      <table class="table table-hover align-middle">
        <thead class="table-light">
          <tr>
            <th scope="col">#</th>
            <th scope="col">Customer</th>
            <th scope="col">Address</th>
            <th scope="col">Date</th>
            <th scope="col">Time Slot</th>
            <th scope="col">Status</th>
          </tr>
        </thead>
        <tbody>
          {% for req in accepted_requests %}
          <tr>
            <th scope="row">{{ loop.index }}</th>
            <td>{{ req.customer.user.username }}</td>
            <td>{{ req.customer.address or 'N/A' }}</td>
            <td>{{ req.date }}</td>
            <td>{{ req.time_slot }}</td>
            <td><span class="badge bg-success">Accepted</span></td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    {% else %}
    <p class="text-muted mb-0">You have not accepted any service requests yet.</p>
    {% endif %}
  </div>
</div>
{% endblock %}
```

---

### Step 6: Wiring Navigation & Blueprint Registration
**Files**: `app/__init__.py`, `app/routes/auth.py`, `app/templates/base.html`

1. **Register the blueprint in `app/__init__.py`**:
   ```python
   from app.routes.professional import professional_bp
   app.register_blueprint(professional_bp)
   ```

2. **Fix login redirect in `app/routes/auth.py`**:
   ```python
   if role == 'customer':
       return redirect(url_for('customer_bp.dashboard')) # note: fixed typo 'dashbaord'
   elif role == 'professional':
       return redirect(url_for('professional_bp.dashboard'))
   ```

3. **Add Navbar link in `app/templates/base.html`**:
   ```html
   {% elif current_user.role == 'professional' %}
   <li class="nav-item">
     <a class="nav-link" href="{{ url_for('professional_bp.dashboard') }}">Dashboard</a>
   </li>
   {% endif %}
   ```

---

## 4. Live Classroom Demo Script (Teacher Walkthrough)

To demonstrate the full working flow to students, use the existing seeded test accounts:

### Demo Steps:
1. **Log in as Customer**:
   - Go to `/login`
   - Email: `cus1@email.com` | Password: `1234`
   - Notice you land on the **Customer Dashboard**.
2. **Book a Service**:
   - Click **Services** in the navbar (or **Book a Service** button).
   - Find **Electrical** (handled by professional `prof2`).
   - Click **Book**.
   - Select a date and time slot $\rightarrow$ click **Confirm Booking**.
   - Show students that the Customer Dashboard now lists this request with status **Requested** and professional showing **Waiting for professional...**.
3. **Log out** (Click **Logout** in navbar).
4. **Log in as Professional**:
   - Go to `/login`
   - Email: `prof2@email.com` | Password: `1234` (Approved for Electrical).
   - Notice the request booked by `cus1` appears under **Available Requests (Electrical)**!
5. **Accept the Request**:
   - Click the green **Accept** button.
   - Show students how the request immediately moves down into **My Accepted Requests**.
6. **Log out and log back in as Customer (`cus1@email.com`)**:
   - Show students that the status has automatically changed to **Accepted**, and the assigned professional now shows **Proff Two**!

---

## 5. Common Student Questions & Pitfalls

### Q1: "I added the `ServiceRequest` class, but SQLite throws `no such table: service_request`!"
- **Explanation**: In SQLite / SQLAlchemy, adding a model in Python code does not automatically create the table in an existing database file unless `db.create_all()` is executed inside an application context.
- **Fix**: Run `python run.py` (which has `db.create_all()` in `if __name__ == '__main__':`) or open a quick Python shell:
  ```python
  from app import create_app
  from app.extensions import db
  app = create_app()
  with app.app_context():
      db.create_all()
  ```

### Q2: "Why is the modal's booking button submitting to the same page or failing?"
- **Explanation**: Check `customer/services.html` line 36. An empty `action=""` submits back to `/customer/services` via POST. It must explicitly point to `{{ url_for('customer_bp.book_service') }}`.

### Q3: "Why did a redirect loop happen on `/professional/dashboard`?"
- **Explanation**: When creating `professional_bp = Blueprint('professional_bp', ..., url_prefix='/professional')` with `@professional_bp.route('/dashboard')`, the URL is `/professional/dashboard`. If `views.py` still has `@views.route('/professional/dashboard')`, Flask finds two conflicting route handlers for the exact same URL path. Always remove or retire old placeholder routes when moving them into a blueprint.

### Q4: "Why did we use POST for accepting instead of a normal GET link?"
- **Explanation**: Modifying server state (changing request status and assigning a professional) must always use `POST` (or `PUT`/`PATCH`), never `GET`. A `GET` request can be accidentally pre-fetched by browsers or search crawlers, triggering unwanted state changes.

---

## 6. Suggested Student Challenges / Next Steps

For fast-finishing students or as a homework assignment:
1. **Close / Complete Request**:
   Add a button for the professional to mark an accepted request as `completed`.
2. **Customer Cancellation**:
   Allow the customer to cancel a request if it is still in the `requested` status.
3. **Ratings / Reviews**:
   Allow the customer to leave a 1-5 star rating and comment once a service is completed.

