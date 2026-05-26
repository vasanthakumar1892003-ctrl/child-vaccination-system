#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import cgi
import cgitb
import sys
import json
import pymysql
from datetime import datetime

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")

# ── DB ───────────────────────────────────────────────────────────────────────
def get_db():
    try:
        con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
        return con, con.cursor()
    except Exception as e:
        return None, str(e)


# ── Ensure table exists ───────────────────────────────────────────────────────
def ensure_table():
    con, cur = get_db()
    if con is None:
        return
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS parent_support_ticket (
                id             INT(11)      AUTO_INCREMENT PRIMARY KEY,
                parent_id      VARCHAR(20)  DEFAULT '',
                parent_name    VARCHAR(100) NOT NULL,
                contact_email  VARCHAR(100) NOT NULL,
                issue_category VARCHAR(100) NOT NULL,
                priority       VARCHAR(50)  NOT NULL,
                description    TEXT         NOT NULL,
                status         VARCHAR(30)  DEFAULT 'open',
                created_at     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
            )
        """)
        con.commit()
    except Exception:
        pass
    finally:
        con.close()

ensure_table()


# ── FORM PARAMS ──────────────────────────────────────────────────────────────
form      = cgi.FieldStorage()
parent_id = form.getvalue('parent_id', '').strip()
action    = form.getvalue('action',    '').strip()


# ============================================================
# POST HANDLER — save ticket (AJAX)
# ============================================================
if action == 'submit_ticket':
    print("Content-Type: application/json\n")

    def send_json(ok, msg="", ticket_id=None):
        payload = {"success": ok, "message": msg}
        if ticket_id:
            payload["ticket_id"] = ticket_id
        print(json.dumps(payload))
        sys.exit()

    parent_name   = form.getvalue('parent_name',    '').strip()
    contact_email = form.getvalue('contact_email',  '').strip()
    issue_cat     = form.getvalue('issue_category', '').strip()
    priority      = form.getvalue('priority',       '').strip()
    description   = form.getvalue('description',    '').strip()

    # Validation
    if not parent_name:
        send_json(False, "Parent name is required.")
    if not contact_email or "@" not in contact_email:
        send_json(False, "A valid contact email is required.")
    if not issue_cat or issue_cat == "-- Select Category --":
        send_json(False, "Please select an issue category.")
    if not priority:
        send_json(False, "Priority is required.")
    if not description:
        send_json(False, "Please describe your issue.")

    con, cur = get_db()
    if con is None:
        send_json(False, f"Database connection failed: {cur}")

    try:
        cur.execute(
            """INSERT INTO parent_support_ticket
               (parent_id, parent_name, contact_email,
                issue_category, priority, description, status)
               VALUES (%s, %s, %s, %s, %s, %s, 'open')""",
            (parent_id, parent_name, contact_email, issue_cat, priority, description)
        )
        con.commit()
        ticket_id = cur.lastrowid
        con.close()
        send_json(
            True,
            f"Support ticket TKT-{ticket_id:05d} submitted successfully! "
            f"Our team will respond within 24 hours.",
            f"TKT-{ticket_id:05d}"
        )
    except Exception as e:
        try:
            con.rollback()
            con.close()
        except Exception:
            pass
        send_json(False, f"Database error: {str(e)}")


# ============================================================
# PAGE LOAD — GET
# ============================================================
print("Content-Type: text/html\n")

con, cur = get_db()
db_ok = con is not None

# ── Fetch parent_name AND email from DB ───────────────────
parent_name   = ""
parent_email  = ""
if db_ok and parent_id and parent_id.isdigit():
    try:
        cur.execute(
            "SELECT parent_name, email FROM parent WHERE parent_id = %s",
            (int(parent_id),)
        )
        row = cur.fetchone()
        if row:
            parent_name  = row[0] or ""
            parent_email = row[1] or ""
    except Exception:
        pass

if db_ok:
    con.close()

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Help & Support - Parent</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  background: linear-gradient(135deg, #052e16, #22c55e, #dcfce7);
  min-height:100vh; font-family:'Segoe UI',sans-serif; overflow-x:hidden;
}}

/* ── NAVBAR ── */
.navbar {{
  box-shadow: 0 4px 20px rgba(0,0,0,0.4); padding: 15px 20px;
  background: linear-gradient(135deg, #052e16, #22c55e, #dcfce7) !important;
}}
.navbar .container-fluid {{ display:flex; flex-direction:row; align-items:center; flex-wrap:nowrap; }}
.navbar-brand {{ font-weight:600; color:white !important; letter-spacing:3px; text-transform:uppercase; }}
.navbar-brand i {{ margin-right:10px; color:#d1fae5; font-size:1.5rem; animation:bounce 2s infinite; }}
@keyframes bounce {{ 0%,100% {{ transform:translateY(0); }} 50% {{ transform:translateY(-5px); }} }}

.mobile-menu-toggle {{
  display: none; flex-shrink: 0; align-self: center;
  background: rgba(255,255,255,0.15); border: 1.5px solid rgba(255,255,255,0.35);
  color: white; padding: 6px 12px; border-radius: 8px; font-size: 1.2rem;
  cursor: pointer; transition: all 0.3s ease; backdrop-filter: blur(6px); line-height: 1; margin-right: 12px;
}}
.mobile-menu-toggle:hover {{
  background:rgba(255,255,255,0.28); border-color:rgba(255,255,255,0.6);
}}

.btn-logout {{
  flex-shrink:0;
  background:linear-gradient(135deg,#ee0979,#ff6a00); border:none;
  color:#fff; padding:8px 20px; border-radius:25px; font-weight:600;
  cursor:pointer; box-shadow:0 4px 15px rgba(238,9,121,0.4);
  font-size:0.9rem; white-space:nowrap; transition:all 0.3s ease;
}}
.btn-logout:hover {{ transform:translateY(-2px); color:#fff; box-shadow:0 6px 20px rgba(238,9,121,0.6); }}

/* ── SIDEBAR ── */
.sidebar {{
  min-height:100vh;
  background:linear-gradient(135deg,#052e16,#22c55e);
  box-shadow:4px 0 20px rgba(0,0,0,0.3); padding:20px 0;
}}
.sidebar-link {{
  display:block; padding:14px 18px; color:#d1fae5;
  text-decoration:none; font-weight:500; transition:all 0.3s;
  border-left:4px solid transparent; margin:6px 0;
}}
.sidebar-link:hover, .sidebar-link.active {{
  background:linear-gradient(90deg,#22c55e,transparent 100%);
  color:#fff; border-left:4px solid #dcfce7; padding-left:24px;
}}
.sidebar-link i {{ margin-right:12px; width:22px; text-align:center; }}

.sidebar-overlay {{
  display:none; position:fixed; top:0; left:0;
  width:100%; height:100%; background:rgba(0,0,0,0.6); z-index:998;
}}
.sidebar-overlay.show {{ display:block; }}

/* ── CONTENT ── */
.content-area {{ padding:25px; min-height:100vh; }}

.page-header {{
  background:linear-gradient(135deg,#ffffff,#f0fdf4);
  padding:22px 25px; border-radius:18px; margin-bottom:25px;
  box-shadow:0 8px 25px rgba(0,0,0,0.15); border-left:6px solid #10b981;
  display:flex; align-items:center; gap:15px;
}}
.page-header i {{ font-size:1.8rem; color:#10b981; }}
.page-header h4 {{ margin:0; font-weight:700; color:#0f172a; font-size:1.4rem; text-transform:uppercase; letter-spacing:1px; }}
.page-header p {{ margin:4px 0 0; font-size:0.9rem; color:#6b7280; }}

.contact-card {{
  background:#fff; border-radius:16px; padding:25px 20px;
  text-align:center; box-shadow:0 8px 25px rgba(0,0,0,0.1);
  border-top:4px solid; height:100%; transition:transform 0.3s;
}}
.contact-card:hover {{ transform:translateY(-4px); }}
.contact-card.green {{ border-color:#22c55e; }}
.contact-card.dark  {{ border-color:#052e16; }}
.icon-circle {{
  width:65px; height:65px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  margin:0 auto 15px; font-size:1.6rem;
}}
.contact-card.green .icon-circle {{ background:#dcfce7; color:#16a34a; }}
.contact-card.dark  .icon-circle {{ background:#f0fdf4; color:#052e16; }}
.contact-card h5 {{ font-weight:700; color:#052e16; margin-bottom:8px; }}
.contact-card p {{ color:#666; font-size:0.88rem; margin-bottom:15px; }}
.contact-card a {{
  display:inline-block; padding:8px 22px; border-radius:20px;
  font-weight:600; font-size:0.85rem; text-decoration:none;
}}
.contact-card.green a {{ background:linear-gradient(135deg,#16a34a,#22c55e); color:#fff; }}
.contact-card.dark  a {{ background:linear-gradient(135deg,#052e16,#15803d); color:#fff; }}
.contact-card a:hover {{ opacity:0.88; }}

.section-card {{
  background:#fff; border-radius:16px;
  padding:25px; box-shadow:0 8px 25px rgba(0,0,0,0.1); margin-bottom:25px;
}}
.section-card h5 {{
  font-weight:700; color:#052e16; margin-bottom:20px;
  display:flex; align-items:center; gap:10px; font-size:1.1rem;
}}
.section-card h5 i {{ color:#22c55e; }}

.guide-card {{
  background:#f0fdf4; border-radius:12px; padding:20px;
  height:100%; border-left:4px solid #22c55e; transition:transform 0.3s;
}}
.guide-card:hover {{ transform:translateY(-3px); box-shadow:0 8px 20px rgba(34,197,94,0.15); }}
.step-num {{
  width:34px; height:34px; background:linear-gradient(135deg,#052e16,#22c55e); color:#fff;
  border-radius:50%; display:flex; align-items:center; justify-content:center;
  font-weight:700; font-size:0.9rem; margin-bottom:12px;
}}
.guide-card h6 {{ font-weight:700; color:#052e16; margin-bottom:8px; }}
.guide-card p {{ color:#555; font-size:0.87rem; margin:0; }}

.accordion-button {{ font-weight:600; color:#052e16; background:#f0fdf4; }}
.accordion-button:not(.collapsed) {{ background:#dcfce7; color:#15803d; box-shadow:none; }}
.accordion-button:focus {{ box-shadow:none; }}
.accordion-body {{ color:#555; line-height:1.7; }}
.accordion-item {{ border:1px solid #a7f3d0; border-radius:8px !important; margin-bottom:8px; overflow:hidden; }}

.form-label {{ font-weight:600; color:#052e16; font-size:0.9rem; }}
.form-control, .form-select {{
  border:2px solid #a7f3d0; border-radius:10px; padding:10px 14px; font-size:0.9rem;
}}
.form-control:focus, .form-select:focus {{
  border-color:#22c55e; box-shadow:0 0 0 3px rgba(34,197,94,0.15);
}}

/* Read-only prefilled fields */
.form-control[readonly] {{
  background:#f0fdf4; border-color:#86efac; color:#166534; font-weight:600; cursor:default;
}}

.btn-submit {{
  background:linear-gradient(135deg,#052e16,#22c55e); color:#fff;
  border:none; padding:12px 35px; border-radius:25px; font-weight:700;
  cursor:pointer; box-shadow:0 4px 15px rgba(34,197,94,0.4);
  transition:all 0.3s ease;
}}
.btn-submit:hover {{ opacity:0.9; color:#fff; transform:translateY(-2px); }}
.btn-submit:disabled {{ opacity:0.6; cursor:not-allowed; transform:none; }}

.info-box {{
  display:flex; align-items:center; gap:15px;
  padding:15px; border-radius:12px;
  background:linear-gradient(135deg,#f0fdf4,#dcfce7);
  border:1px solid #a7f3d0;
}}

/* Toast */
#toastContainer {{
  position:fixed; bottom:24px; right:24px; z-index:9999;
}}
.custom-toast {{
  min-width:280px; padding:16px 20px; border-radius:12px;
  color:#fff; font-weight:600; font-size:0.9rem;
  box-shadow:0 8px 25px rgba(0,0,0,0.2);
  display:flex; align-items:center; gap:12px;
  animation:slideIn 0.3s ease;
}}
@keyframes slideIn {{ from {{ opacity:0; transform:translateY(20px); }} to {{ opacity:1; transform:translateY(0); }} }}
.toast-success {{ background:linear-gradient(135deg,#059669,#34d399); }}
.toast-error   {{ background:linear-gradient(135deg,#dc2626,#f87171); }}

/* ── RESPONSIVE ── */
@media (max-width:991.98px) {{
  .mobile-menu-toggle {{ display:flex; align-items:center; justify-content:center; }}
  .sidebar {{
    position:fixed; left:-100%; top:0;
    width:280px; height:100vh; z-index:999;
    transition:left 0.3s ease; overflow-y:auto;
  }}
  .sidebar.show {{ left:0; }}
  .content-area {{ padding:15px; margin-left:0 !important; }}
  .navbar-brand {{ font-size:1rem; letter-spacing:1px; }}
  .navbar-brand i {{ font-size:1.3rem; }}
}}
@media (max-width:767.98px) {{
  .page-header h4 {{ font-size:1.3rem; }}
  .content-area {{ padding:12px; }}
  .btn-logout {{ padding:6px 16px; font-size:0.85rem; }}
}}
@media (max-width:575.98px) {{
  .navbar-brand {{ font-size:1rem; letter-spacing:1px; flex:1; text-align:center; }}
  .navbar-brand i {{ font-size:1.1rem; margin-right:6px; }}
  .btn-logout {{ padding:6px 14px; font-size:0.8rem; }}
}}
@media (max-width:400px) {{
  .navbar-brand {{ font-size:0.75rem; }}
}}
</style>
</head>
<body>

<!-- TOAST CONTAINER -->
<div id="toastContainer"></div>

<!-- NAVBAR -->
<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container-fluid">
    <button class="mobile-menu-toggle" onclick="toggleSidebar()">
      <i class="fas fa-bars"></i>
    </button>
    <span class="navbar-brand ms-2"><i class="fa-solid fa-users"></i> CVS - Parent</span>
    <button class="btn-logout ms-auto" onclick="logout()">
      <i class="fas fa-sign-out-alt"></i> Logout
    </button>
  </div>
</nav>

<!-- Sidebar Overlay -->
<div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

<div class="container-fluid">
  <div class="row">

    <!-- SIDEBAR -->
    <div class="col-lg-2 col-md-3 sidebar p-0" id="sidebar">
      <a href="parent_dashboard.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-home"></i> Home</a>
      <a href="parent_vaccination.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fa-solid fa-circle-info"></i> Vaccination Info</a>
      <a href="parent_manage_child.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-baby"></i> Manage Children</a>
      <a href="parent_view_hospital.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fa-solid fa-eye"></i> View Hospital</a>
      <a href="parent_booked_appointment.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fa-solid fa-calendar-day"></i> Booked Appointments
      </a>
      <a href="parent_my_appointment.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-calendar-check"></i> My Appointments</a>
      <a href="parent_reminder.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-bell"></i> My Reminders</a>
      <a href="parent_profile.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-user-circle"></i> My Profile</a>
      <a href="parent_feedback.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-comment-dots"></i> Feedback</a>
      <a href="parent_help.py?parent_id={parent_id}" class="sidebar-link active" onclick="closeSidebarMobile()"><i class="fas fa-circle-question"></i> Help & Support</a>
    </div>

    <!-- CONTENT -->
    <div class="col-lg-10 col-md-9 col-12 content-area">

      <div class="page-header">
        <i class="fas fa-headset"></i>
        <div>
          <h4>Help & Support</h4>
          <p>Find answers, guides, and contact our support team</p>
        </div>
        <div class="ms-auto">
          <span class="badge px-3 py-2 fs-6" style="background:linear-gradient(135deg,#052e16,#22c55e);color:#fff;">
            <i class="fas fa-circle me-1" style="font-size:0.5rem;"></i> Support Online
          </span>
        </div>
      </div>

      <!-- CONTACT CARDS -->
      <div class="row g-4 mb-4">
        <div class="col-lg-6 col-md-6">
          <div class="contact-card green">
            <div class="icon-circle"><i class="fas fa-envelope"></i></div>
            <h5>Email Support</h5>
            <p>Send your query and our team will respond within 24 hours on business days.</p>
            <a href="mailto:childvaccinationsystem2026@gmail.com">
              <i class="fas fa-paper-plane me-1"></i> childvaccinationsystem2026@gmail.com
            </a>
          </div>
        </div>
        <div class="col-lg-6 col-md-6">
          <div class="contact-card dark">
            <div class="icon-circle"><i class="fas fa-phone-alt"></i></div>
            <h5>Phone Support</h5>
            <p>Speak directly with an agent Monday–Saturday, 9:00 AM – 6:00 PM IST.</p>
            <a href="tel:+919345790381">
              <i class="fas fa-phone me-1"></i> +91 93457 90381
            </a>
          </div>
        </div>
      </div>

      <!-- QUICK START GUIDE -->
      <div class="section-card">
        <h5><i class="fas fa-book-open"></i> Parent Quick Start Guide</h5>
        <div class="row g-3">
          <div class="col-lg-3 col-md-6">
            <div class="guide-card">
              <div class="step-num">1</div>
              <h6>Register Your Child</h6>
              <p>Go to <strong>Manage Children</strong> and click <strong>Add New Child</strong> to register your child's details.</p>
            </div>
          </div>
          <div class="col-lg-3 col-md-6">
            <div class="guide-card">
              <div class="step-num">2</div>
              <h6>Find a Hospital</h6>
              <p>Browse <strong>View Hospital</strong> to find approved vaccination centers near you and apply.</p>
            </div>
          </div>
          <div class="col-lg-3 col-md-6">
            <div class="guide-card">
              <div class="step-num">3</div>
              <h6>Book Appointment</h6>
              <p>Apply for a vaccination appointment from the hospital listing page for your child.</p>
            </div>
          </div>
          <div class="col-lg-3 col-md-6">
            <div class="guide-card">
              <div class="step-num">4</div>
              <h6>Track Records</h6>
              <p>Monitor your child's vaccinations and upcoming schedules in <strong>Vaccination Info</strong>.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- FAQ -->
      <div class="section-card">
        <h5><i class="fas fa-question-circle"></i> Frequently Asked Questions</h5>
        <div class="accordion" id="parentFAQ">
          <div class="accordion-item">
            <h2 class="accordion-header">
              <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#pfaq1">
                <i class="fas fa-baby me-2 text-success"></i> How do I register my child?
              </button>
            </h2>
            <div id="pfaq1" class="accordion-collapse collapse show" data-bs-parent="#parentFAQ">
              <div class="accordion-body">
                Go to <strong>Manage Children</strong> in the sidebar and click <strong>Add New Child</strong>. Fill in your child's name, date of birth, and gender, then click Save. You can add multiple children to your account.
              </div>
            </div>
          </div>
          <div class="accordion-item">
            <h2 class="accordion-header">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#pfaq2">
                <i class="fas fa-hospital me-2 text-success"></i> How do I find and apply to a hospital?
              </button>
            </h2>
            <div id="pfaq2" class="accordion-collapse collapse" data-bs-parent="#parentFAQ">
              <div class="accordion-body">
                Go to <strong>View Hospital</strong> in the sidebar to see all approved vaccination hospitals. Click <strong>Apply</strong> next to your preferred hospital, select your child and desired vaccination, then submit the application.
              </div>
            </div>
          </div>
          <div class="accordion-item">
            <h2 class="accordion-header">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#pfaq3">
                <i class="fas fa-calendar me-2 text-success"></i> How do I view and manage my appointments?
              </button>
            </h2>
            <div id="pfaq3" class="accordion-collapse collapse" data-bs-parent="#parentFAQ">
              <div class="accordion-body">
                Click <strong>My Appointments</strong> in the sidebar to see all your scheduled, pending, completed, and cancelled appointments. You can view full details for each from this page.
              </div>
            </div>
          </div>
          <div class="accordion-item">
            <h2 class="accordion-header">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#pfaq4">
                <i class="fas fa-bell me-2 text-success"></i> How do reminders work?
              </button>
            </h2>
            <div id="pfaq4" class="accordion-collapse collapse" data-bs-parent="#parentFAQ">
              <div class="accordion-body">
                The system automatically generates reminders for upcoming vaccinations based on your child's schedule. View all reminders under <strong>My Reminders</strong>. Keep your contact details in <strong>My Profile</strong> updated to receive notifications.
              </div>
            </div>
          </div>
          <div class="accordion-item">
            <h2 class="accordion-header">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#pfaq5">
                <i class="fas fa-syringe me-2 text-success"></i> How do I view my child's vaccination history?
              </button>
            </h2>
            <div id="pfaq5" class="accordion-collapse collapse" data-bs-parent="#parentFAQ">
              <div class="accordion-body">
                Go to <strong>Vaccination Info</strong> in the sidebar to see a complete list of vaccines administered, pending vaccines, and upcoming schedules for all your registered children.
              </div>
            </div>
          </div>
          <div class="accordion-item">
            <h2 class="accordion-header">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#pfaq6">
                <i class="fas fa-lock me-2 text-success"></i> What if I can't log in?
              </button>
            </h2>
            <div id="pfaq6" class="accordion-collapse collapse" data-bs-parent="#parentFAQ">
              <div class="accordion-body">
                Contact the support team at <strong>childvaccinationsystem2026@gmail.com</strong> or call <strong>+91 98765 43210</strong>. Provide your registered User ID and email address for account recovery assistance.
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- SUPPORT TICKET -->
      <div class="section-card">
        <h5><i class="fas fa-headset"></i> Submit a Support Ticket</h5>
        <p class="text-muted mb-4" style="font-size:0.9rem;">Still need help? Fill the form below and we'll respond within 24 hours.</p>
        <div class="row g-3" id="ticketForm">

          <div class="col-md-6">
            <label class="form-label">
              <i class="fas fa-user me-1" style="color:#22c55e;"></i> Your Name
            </label>
            <!-- Pre-filled & readonly from DB -->
            <input type="text" class="form-control" id="parentName"
                   value="{parent_name}" required>
          </div>

          <div class="col-md-6">
            <label class="form-label">
              <i class="fas fa-envelope me-1" style="color:#22c55e;"></i> Contact Email
            </label>
            <!-- Pre-filled & readonly from DB -->
            <input type="email" class="form-control" id="contactEmail"
                   value="{parent_email}" required>
          </div>

          <div class="col-md-6">
            <label class="form-label">Issue Category</label>
            <select class="form-select" id="issueCategory">
              <option value="">-- Select Category --</option>
              <option>Child Registration</option>
              <option>Appointment Booking</option>
              <option>Vaccination Records</option>
              <option>Reminders &amp; Notifications</option>
              <option>Profile &amp; Account</option>
              <option>Login / Access Issues</option>
              <option>Technical Bug</option>
              <option>Other</option>
            </select>
          </div>

          <div class="col-md-6">
            <label class="form-label">Priority</label>
            <select class="form-select" id="priority">
              <option>Low – General Question</option>
              <option>Medium – Need Help Soon</option>
              <option>High – Urgent Issue</option>
            </select>
          </div>

          <div class="col-12">
            <label class="form-label">Describe Your Issue</label>
            <textarea class="form-control" id="issueDescription" rows="4"
                      placeholder="Please describe your issue in detail..."></textarea>
          </div>

          <div class="col-12">
            <button class="btn-submit" id="submitBtn" onclick="submitTicket()">
              <i class="fas fa-paper-plane me-2"></i> Submit Ticket
            </button>
          </div>
        </div>
      </div>

      <!-- SYSTEM INFO -->
      <div class="section-card">
        <h5><i class="fas fa-info-circle"></i> System Information</h5>
        <div class="row g-3">
          <div class="col-md-4">
            <div class="info-box">
              <i class="fas fa-clock text-success fs-4"></i>
              <div>
                <div class="fw-bold text-dark" style="font-size:0.9rem;">Support Hours</div>
                <div class="text-muted" style="font-size:0.83rem;">Mon–Sat: 9:00 AM – 6:00 PM IST</div>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="info-box">
              <i class="fas fa-reply text-success fs-4"></i>
              <div>
                <div class="fw-bold text-dark" style="font-size:0.9rem;">Response Time</div>
                <div class="text-muted" style="font-size:0.83rem;">Email: 24 hrs | Phone: Immediate</div>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="info-box">
              <i class="fas fa-shield-heart text-success fs-4"></i>
              <div>
                <div class="fw-bold text-dark" style="font-size:0.9rem;">Your Data is Safe</div>
                <div class="text-muted" style="font-size:0.83rem;">All records are encrypted &amp; secure</div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</div>

<script>
const PARENT_ID = "{parent_id}";

// ── TOAST ──────────────────────────────────────────────────
function showToast(message, type = 'success') {{
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `custom-toast toast-${{type}}`;
  toast.innerHTML = `
    <i class="fas fa-${{type === 'success' ? 'check-circle' : 'times-circle'}}"></i>
    <span>${{message}}</span>`;
  container.appendChild(toast);
  setTimeout(() => {{
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.4s ease';
    setTimeout(() => toast.remove(), 400);
  }}, 4000);
}}

// ── SUBMIT TICKET ──────────────────────────────────────────
async function submitTicket() {{
  const parentName    = document.getElementById('parentName').value.trim();
  const contactEmail  = document.getElementById('contactEmail').value.trim();
  const issueCategory = document.getElementById('issueCategory').value.trim();
  const priority      = document.getElementById('priority').value.trim();
  const issueDesc     = document.getElementById('issueDescription').value.trim();

  // Validation
  if (!parentName)    {{ showToast('Your name is missing. Please refresh the page.', 'error'); return; }}
  if (!contactEmail)  {{ showToast('Contact email is missing. Please refresh the page.', 'error'); return; }}
  if (!issueCategory) {{ showToast('Please select an issue category.', 'error'); return; }}
  if (!issueDesc)     {{ showToast('Please describe your issue.', 'error'); return; }}

  const btn = document.getElementById('submitBtn');
  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Submitting...';

  try {{
    const params = new URLSearchParams({{
      action:         'submit_ticket',
      parent_id:      PARENT_ID,
      parent_name:    parentName,
      contact_email:  contactEmail,
      issue_category: issueCategory,
      priority:       priority,
      description:    issueDesc        // ← matches schema column: description
    }});

    const response = await fetch('parent_help.py', {{
      method:  'POST',
      headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
      body:    params.toString()
    }});

    const data = await response.json();

    if (data.success) {{
      showToast(data.message, 'success');
      // Only clear editable fields; readonly name/email stay
      document.getElementById('issueCategory').value    = '';
      document.getElementById('priority').value         = 'Low – General Question';
      document.getElementById('issueDescription').value = '';
    }} else {{
      showToast(data.message || 'Submission failed. Please try again.', 'error');
    }}
  }} catch (err) {{
    showToast('Network error. Please try again.', 'error');
    console.error(err);
  }} finally {{
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-paper-plane me-2"></i> Submit Ticket';
  }}
}}

// ── SIDEBAR ────────────────────────────────────────────────
function toggleSidebar() {{
  document.getElementById('sidebar').classList.toggle('show');
  document.getElementById('sidebarOverlay').classList.toggle('show');
}}
function closeSidebarMobile() {{
  if (window.innerWidth < 992) {{
    document.getElementById('sidebar').classList.remove('show');
    document.getElementById('sidebarOverlay').classList.remove('show');
  }}
}}
function logout() {{
  if (confirm('Are you sure you want to logout?')) window.location.href = 'main.py';
}}
document.addEventListener('click', function(event) {{
  const sidebar    = document.getElementById('sidebar');
  const menuToggle = document.querySelector('.mobile-menu-toggle');
  if (window.innerWidth < 992 &&
      !sidebar.contains(event.target) &&
      !menuToggle.contains(event.target) &&
      sidebar.classList.contains('show')) {{
    closeSidebarMobile();
  }}
}});
</script>
</body>
</html>
""")