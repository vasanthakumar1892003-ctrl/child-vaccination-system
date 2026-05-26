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
            CREATE TABLE IF NOT EXISTS hospital_support_ticket (
                ticket_id         INT(11)      AUTO_INCREMENT PRIMARY KEY,
                hospital_id       INT(11)      DEFAULT NULL,
                hospital_name     VARCHAR(100) NOT NULL,
                contact_email     VARCHAR(100) NOT NULL,
                issue_category    VARCHAR(100) NOT NULL,
                priority          VARCHAR(50)  NOT NULL,
                issue_description TEXT         NOT NULL,
                status            VARCHAR(30)  DEFAULT 'open',
                created_at        TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
                updated_at        TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        con.commit()
    except Exception:
        pass
    finally:
        con.close()

ensure_table()


# ── FORM PARAMS ──────────────────────────────────────────────────────────────
form        = cgi.FieldStorage()
hospital_id = form.getvalue('hospital_id', '').strip()
action      = form.getvalue('action',      '').strip()


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

    hosp_name         = form.getvalue('hospital_name',     '').strip()
    contact_email     = form.getvalue('contact_email',     '').strip()
    issue_cat         = form.getvalue('issue_category',    '').strip()
    priority          = form.getvalue('priority',          '').strip()
    issue_description = form.getvalue('issue_description', '').strip()   # ← fixed (was 'description')

    # Validation
    if not hosp_name:
        send_json(False, "Hospital name is required.")
    if not contact_email or "@" not in contact_email:
        send_json(False, "A valid contact email is required.")
    if not issue_cat or issue_cat == "-- Select Category --":
        send_json(False, "Please select an issue category.")
    if not priority:
        send_json(False, "Priority is required.")
    if not issue_description:
        send_json(False, "Please describe your issue.")

    con, cur = get_db()
    if con is None:
        send_json(False, f"Database connection failed: {cur}")

    try:
        cur.execute(
            """INSERT INTO hospital_support_ticket
               (hospital_id, hospital_name, contact_email,
                issue_category, priority, issue_description,
                status, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, 'open', NOW(), NOW())""",
            (
                int(hospital_id) if hospital_id.isdigit() else None,
                hosp_name,
                contact_email,
                issue_cat,
                priority,
                issue_description
            )
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

# Resolve hospital name — using correct PK column: hospital_id (not id)
hospital_name = ""
if db_ok and hospital_id and hospital_id.isdigit():
    try:
        cur.execute(
            "SELECT hospital_name FROM hospital WHERE hospital_id = %s",
            (int(hospital_id),)
        )
        hosp_row = cur.fetchone()
        if hosp_row:
            hospital_name = hosp_row[0]
    except Exception:
        pass

if db_ok:
    con.close()

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Help & Support - Hospital</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  background: linear-gradient(135deg, #083344, #22d3ee, #cffafe);
  min-height:100vh; font-family:'Segoe UI',sans-serif; overflow-x:hidden;
}}

/* ── NAVBAR ── */
.navbar {{
  background:linear-gradient(135deg,#083344,#22d3ee,#cffafe) !important;
  box-shadow:0 4px 20px rgba(0,0,0,0.4); padding:15px 20px;
}}
.navbar .container-fluid {{ display:flex; flex-direction:row; align-items:center; flex-wrap:nowrap; }}
.navbar-brand {{ font-weight:600; color:white !important; letter-spacing:2px; text-transform:uppercase; }}
.navbar-brand i {{ margin-right:10px; color:#e9d5ff; font-size:1.5rem; animation:bounce 2s infinite; }}
@keyframes bounce {{ 0%,100% {{ transform:translateY(0); }} 50% {{ transform:translateY(-5px); }} }}

.mobile-menu-toggle {{
  display:none; flex-shrink:0; align-self:center;
  background:rgba(255,255,255,0.15); border:1.5px solid rgba(255,255,255,0.35);
  color:white; padding:6px 12px; border-radius:8px; font-size:1.2rem;
  cursor:pointer; transition:all 0.3s ease; backdrop-filter:blur(6px);
  line-height:1; margin-right:12px;
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
  background:linear-gradient(135deg,#083344,#22d3ee);
  box-shadow:4px 0 20px rgba(0,0,0,0.3); padding:20px 0;
}}
.sidebar-link {{
  display:block; padding:14px 18px; color:#e9d5ff;
  text-decoration:none; font-weight:500; transition:all 0.3s;
  border-left:4px solid transparent; margin:6px 0;
}}
.sidebar-link:hover, .sidebar-link.active {{
  background:linear-gradient(90deg,#22d3ee,transparent 100%);
  color:#fff; border-left:4px solid #cffafe; padding-left:24px;
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
  background:linear-gradient(135deg,#ffffff,#f0f9ff);
  padding:22px 25px; border-radius:18px; margin-bottom:25px;
  box-shadow:0 8px 25px rgba(0,0,0,0.15); border-left:6px solid #0ea5e9;
  display:flex; align-items:center; gap:15px;
}}
.page-header i {{ font-size:1.8rem; color:#0ea5e9; }}
.page-header h4 {{ margin:0; font-weight:700; color:#0f172a; font-size:1.4rem; text-transform:uppercase; letter-spacing:1px; }}
.page-header p {{ margin:4px 0 0; font-size:0.9rem; color:#6b7280; }}

.contact-card {{
  background:#fff; border-radius:16px; padding:25px 20px;
  text-align:center; box-shadow:0 8px 25px rgba(0,0,0,0.1);
  border-top:4px solid; height:100%; transition:transform 0.3s;
}}
.contact-card:hover {{ transform:translateY(-4px); }}
.contact-card.blue  {{ border-color:#0ea5e9; }}
.contact-card.dark  {{ border-color:#083344; }}
.icon-circle {{
  width:65px; height:65px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  margin:0 auto 15px; font-size:1.6rem;
}}
.contact-card.blue .icon-circle {{ background:#e0f2fe; color:#0ea5e9; }}
.contact-card.dark .icon-circle {{ background:#ecfeff; color:#083344; }}
.contact-card h5 {{ font-weight:700; color:#083344; margin-bottom:8px; }}
.contact-card p {{ color:#666; font-size:0.88rem; margin-bottom:15px; }}
.contact-card a {{
  display:inline-block; padding:8px 22px; border-radius:20px;
  font-weight:600; font-size:0.85rem; text-decoration:none;
}}
.contact-card.blue a {{ background:linear-gradient(135deg,#0ea5e9,#22d3ee); color:#fff; }}
.contact-card.dark a {{ background:linear-gradient(135deg,#083344,#0e7490); color:#fff; }}
.contact-card a:hover {{ opacity:0.88; }}

.section-card {{
  background:#fff; border-radius:16px;
  padding:25px; box-shadow:0 8px 25px rgba(0,0,0,0.1); margin-bottom:25px;
}}
.section-card h5 {{
  font-weight:700; color:#083344; margin-bottom:20px;
  display:flex; align-items:center; gap:10px; font-size:1.1rem;
}}
.section-card h5 i {{ color:#0ea5e9; }}

.guide-card {{
  background:#ecfeff; border-radius:12px; padding:20px;
  height:100%; border-left:4px solid #22d3ee; transition:transform 0.3s;
}}
.guide-card:hover {{ transform:translateY(-3px); box-shadow:0 8px 20px rgba(34,211,238,0.15); }}
.step-num {{
  width:34px; height:34px; background:linear-gradient(135deg,#083344,#22d3ee); color:#fff;
  border-radius:50%; display:flex; align-items:center; justify-content:center;
  font-weight:700; font-size:0.9rem; margin-bottom:12px;
}}
.guide-card h6 {{ font-weight:700; color:#083344; margin-bottom:8px; }}
.guide-card p {{ color:#555; font-size:0.87rem; margin:0; }}

.accordion-button {{ font-weight:600; color:#083344; background:#ecfeff; }}
.accordion-button:not(.collapsed) {{ background:#cffafe; color:#0e7490; box-shadow:none; }}
.accordion-button:focus {{ box-shadow:none; }}
.accordion-body {{ color:#555; line-height:1.7; }}
.accordion-item {{ border:1px solid #a5f3fc; border-radius:8px !important; margin-bottom:8px; overflow:hidden; }}

.form-label {{ font-weight:600; color:#083344; font-size:0.9rem; }}
.form-control, .form-select {{
  border:2px solid #a5f3fc; border-radius:10px; padding:10px 14px; font-size:0.9rem;
}}
.form-control:focus, .form-select:focus {{
  border-color:#22d3ee; box-shadow:0 0 0 3px rgba(34,211,238,0.15);
}}
.btn-submit {{
  background:linear-gradient(135deg,#083344,#22d3ee); color:#fff;
  border:none; padding:12px 35px; border-radius:25px; font-weight:700;
  cursor:pointer; box-shadow:0 4px 15px rgba(34,211,238,0.4);
  transition:all 0.3s ease;
}}
.btn-submit:hover {{ opacity:0.9; color:#fff; transform:translateY(-2px); }}
.btn-submit:disabled {{ opacity:0.6; cursor:not-allowed; transform:none; }}

.info-box {{
  display:flex; align-items:center; gap:15px;
  padding:15px; border-radius:12px;
  background:linear-gradient(135deg,#ecfeff,#cffafe);
  border:1px solid #a5f3fc;
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
  .navbar-brand {{ font-size:0.85rem; letter-spacing:0.5px; }}
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
    <span class="navbar-brand ms-2">
      <i class="fa-solid fa-hospital"></i> CVS - Hospital
    </span>
    <button class="btn-logout" onclick="logout()">
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
      <a href="hospital_dashboard.py?hospital_id={hospital_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-home"></i> Home</a>
      <a href="hospital_vaccination.py?hospital_id={hospital_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fa-solid fa-circle-info"></i> Vaccination Info</a>
      <a href="hospital_view_application.py?hospital_id={hospital_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fa-solid fa-user-pen"></i> Parent Application</a>
      <a href="hospital_view_appointment.py?hospital_id={hospital_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-calendar-alt"></i> View Appointments</a>
      <a href="hospital_profile.py?hospital_id={hospital_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-user-circle"></i> My Profile</a>
      <a href="hospital_feedback.py?hospital_id={hospital_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-comment-dots"></i> Feedback</a>
      <a href="hospital_chat.py?hospital_id={hospital_id}" class="sidebar-link">
        <i class="fas fa-notes-medical"></i> Chats
      </a>
      <a href="hospital_help.py?hospital_id={hospital_id}" class="sidebar-link active" onclick="closeSidebarMobile()"><i class="fas fa-circle-question"></i> Help & Support</a>
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
          <span class="badge px-3 py-2 fs-6" style="background:linear-gradient(135deg,#083344,#22d3ee);color:#fff;">
            <i class="fas fa-circle me-1" style="font-size:0.5rem;"></i> Support Online
          </span>
        </div>
      </div>

      <!-- CONTACT CARDS -->
      <div class="row g-4 mb-4">
        <div class="col-lg-6 col-md-6">
          <div class="contact-card blue">
            <div class="icon-circle"><i class="fas fa-envelope"></i></div>
            <h5>Email Support</h5>
            <p>Send your issue and our team will respond within 24 hours on business days.</p>
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
        <h5><i class="fas fa-book-open"></i> Hospital Quick Start Guide</h5>
        <div class="row g-3">
          <div class="col-lg-3 col-md-6">
            <div class="guide-card">
              <div class="step-num">1</div>
              <h6>Complete Your Profile</h6>
              <p>Go to <strong>My Profile</strong> and fill in hospital details and upload required documents.</p>
            </div>
          </div>
          <div class="col-lg-3 col-md-6">
            <div class="guide-card">
              <div class="step-num">2</div>
              <h6>Review Applications</h6>
              <p>Check <strong>Parent Application</strong> to review parent requests for vaccination appointments.</p>
            </div>
          </div>
          <div class="col-lg-3 col-md-6">
            <div class="guide-card">
              <div class="step-num">3</div>
              <h6>Schedule Appointments</h6>
              <p>Use <strong>Add Appointment</strong> to create vaccination slots for registered children.</p>
            </div>
          </div>
          <div class="col-lg-3 col-md-6">
            <div class="guide-card">
              <div class="step-num">4</div>
              <h6>Record Vaccinations</h6>
              <p>After each visit, update records in <strong>Vaccination Info</strong> to keep everything accurate.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- FAQ -->
      <div class="section-card">
        <h5><i class="fas fa-question-circle"></i> Frequently Asked Questions</h5>
        <div class="accordion" id="hospitalFAQ">
          <div class="accordion-item">
            <h2 class="accordion-header">
              <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#faq1">
                <i class="fas fa-user-check me-2" style="color:#0ea5e9;"></i> How do I approve a parent's appointment request?
              </button>
            </h2>
            <div id="faq1" class="accordion-collapse collapse show" data-bs-parent="#hospitalFAQ">
              <div class="accordion-body">
                Go to <strong>Parent Application</strong> from the sidebar. You'll see pending parent requests. Click <strong>View</strong> to review the child's details, then click <strong>Approve</strong> or <strong>Reject</strong>. Approved applications automatically create an appointment entry.
              </div>
            </div>
          </div>
          <div class="accordion-item">
            <h2 class="accordion-header">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq2">
                <i class="fas fa-calendar-alt me-2 text-success"></i> How do I add a new appointment?
              </button>
            </h2>
            <div id="faq2" class="accordion-collapse collapse" data-bs-parent="#hospitalFAQ">
              <div class="accordion-body">
                Click <strong>Add Appointment</strong> in the sidebar. Fill in the appointment date, time, child details, and vaccination type. Click <strong>Save</strong>. The parent will be notified automatically.
              </div>
            </div>
          </div>
          <div class="accordion-item">
            <h2 class="accordion-header">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq3">
                <i class="fas fa-syringe me-2 text-warning"></i> How do I update vaccination records?
              </button>
            </h2>
            <div id="faq3" class="accordion-collapse collapse" data-bs-parent="#hospitalFAQ">
              <div class="accordion-body">
                Navigate to <strong>Vaccination Info</strong> in the sidebar. Find the child's appointment and click <strong>Update</strong>. Enter the vaccine name, batch number, and administration date, then save. Records update in the parent's dashboard immediately.
              </div>
            </div>
          </div>
          <div class="accordion-item">
            <h2 class="accordion-header">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq4">
                <i class="fas fa-edit me-2 text-info"></i> How do I update my hospital profile?
              </button>
            </h2>
            <div id="faq4" class="accordion-collapse collapse" data-bs-parent="#hospitalFAQ">
              <div class="accordion-body">
                Go to <strong>My Profile</strong> and click <strong>Edit</strong> to update your hospital name, address, contact number, or email. Save changes to apply them.
              </div>
            </div>
          </div>
          <div class="accordion-item">
            <h2 class="accordion-header">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq5">
                <i class="fas fa-exclamation-triangle me-2 text-danger"></i> What do I do for delayed appointments?
              </button>
            </h2>
            <div id="faq5" class="accordion-collapse collapse" data-bs-parent="#hospitalFAQ">
              <div class="accordion-body">
                Go to <strong>View Appointments</strong> and filter by "Delayed". Contact the parent to reschedule or do so directly from the appointment detail view.
              </div>
            </div>
          </div>
          <div class="accordion-item">
            <h2 class="accordion-header">
              <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq6">
                <i class="fas fa-lock me-2 text-secondary"></i> What if I can't log in to my account?
              </button>
            </h2>
            <div id="faq6" class="accordion-collapse collapse" data-bs-parent="#hospitalFAQ">
              <div class="accordion-body">
                Contact the support team at <strong>childvaccinationsystem2026@gmail.com</strong> or call <strong>+91 93457 90381</strong>. Provide your registered hospital ID and email for account recovery.
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- SUPPORT TICKET FORM -->
      <div class="section-card">
        <h5><i class="fas fa-headset"></i> Submit a Support Ticket</h5>
        <p class="text-muted mb-4" style="font-size:0.9rem;">Can't find what you need? Our team will respond within 24 hours.</p>
        <div class="row g-3" id="ticketForm">
          <div class="col-md-6">
            <label class="form-label">Hospital Name</label>
            <input type="text" class="form-control" id="hospitalName"
                   placeholder="Enter your hospital name"
                   value="{hospital_name}" required>
          </div>
          <div class="col-md-6">
            <label class="form-label">Contact Email</label>
            <input type="email" class="form-control" id="contactEmail" placeholder="your@email.com" required>
          </div>
          <div class="col-md-6">
            <label class="form-label">Issue Category</label>
            <select class="form-select" id="issueCategory">
              <option value="">-- Select Category --</option>
              <option>Appointment Management</option>
              <option>Vaccination Records</option>
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
              <option>Medium – Affecting Work</option>
              <option>High – Critical Issue</option>
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
              <i class="fas fa-clock fs-4" style="color:#0ea5e9;"></i>
              <div>
                <div class="fw-bold text-dark" style="font-size:0.9rem;">Support Hours</div>
                <div class="text-muted" style="font-size:0.83rem;">Mon–Sat: 9:00 AM – 6:00 PM IST</div>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="info-box">
              <i class="fas fa-reply fs-4" style="color:#0ea5e9;"></i>
              <div>
                <div class="fw-bold text-dark" style="font-size:0.9rem;">Response Time</div>
                <div class="text-muted" style="font-size:0.83rem;">Email: 24 hrs | Phone: Immediate</div>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="info-box">
              <i class="fas fa-shield-heart fs-4" style="color:#0ea5e9;"></i>
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
const HOSPITAL_ID = "{hospital_id}";

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
  const hospitalName  = document.getElementById('hospitalName').value.trim();
  const contactEmail  = document.getElementById('contactEmail').value.trim();
  const issueCategory = document.getElementById('issueCategory').value.trim();
  const priority      = document.getElementById('priority').value.trim();
  const issueDesc     = document.getElementById('issueDescription').value.trim();

  // Validation
  if (!hospitalName)  {{ showToast('Please enter your hospital name.', 'error'); return; }}
  if (!contactEmail)  {{ showToast('Please enter your contact email.', 'error'); return; }}
  if (!issueCategory) {{ showToast('Please select an issue category.', 'error'); return; }}
  if (!issueDesc)     {{ showToast('Please describe your issue.', 'error'); return; }}

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(contactEmail)) {{
    showToast('Please enter a valid email address.', 'error'); return;
  }}

  const btn = document.getElementById('submitBtn');
  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Submitting...';

  try {{
    const params = new URLSearchParams({{
      action:            'submit_ticket',
      hospital_id:       HOSPITAL_ID,
      hospital_name:     hospitalName,
      contact_email:     contactEmail,
      issue_category:    issueCategory,
      priority:          priority,
      issue_description: issueDesc        // ← key matches Python form.getvalue('issue_description')
    }});

    const response = await fetch('hospital_help.py', {{
      method:  'POST',
      headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
      body:    params.toString()
    }});

    const data = await response.json();

    if (data.success) {{
      showToast(data.message, 'success');
      // Clear form — keep hospital name pre-filled
      document.getElementById('hospitalName').value     = '{hospital_name}';
      document.getElementById('contactEmail').value     = '';
      document.getElementById('issueCategory').value   = '';
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
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  sidebar.classList.toggle('show');
  overlay.classList.toggle('show');
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