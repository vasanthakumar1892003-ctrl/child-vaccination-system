#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgitb
import sys
import os
import string, random
import cgi
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")

FROM_EMAIL   = "childvaccinationsystem2026@gmail.com"
APP_PASSWORD = "wuxe lqii npcp nglf"


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


def send_email(to_email, subject, body):
    try:
        to_email = str(to_email).strip()
        if not to_email or to_email == "N/A" or "@" not in to_email:
            return False, f"Invalid email address: {to_email}"
        msg = MIMEMultipart('alternative')
        msg['From']    = f"Child Vaccination System <{FROM_EMAIL}>"
        msg['To']      = to_email
        msg['Subject'] = subject
        html_body = body.replace('\n', '<br>')
        html_content = f"""
        <html><head><style>
          body {{ font-family:Arial,sans-serif; line-height:1.6; color:#333; }}
          .container {{ max-width:600px; margin:0 auto; padding:20px; }}
          .header {{ background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
                     color:white; padding:20px; text-align:center; border-radius:10px 10px 0 0; }}
          .content {{ background:#f9f9f9; padding:30px; border-radius:0 0 10px 10px; }}
          .footer  {{ text-align:center; color:#666; font-size:12px; margin-top:20px;
                     padding-top:20px; border-top:1px solid #ddd; }}
        </style></head><body>
          <div class="container">
            <div class="header"><h2>Child Vaccination System</h2></div>
            <div class="content">{html_body}</div>
            <div class="footer">
              <p>This is an automated message from Child Vaccination System</p>
              <p>Support: {FROM_EMAIL}</p>
            </div>
          </div>
        </body></html>"""
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.ehlo(); server.starttls(); server.ehlo()
        server.login(FROM_EMAIL, APP_PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        server.quit()
        return True, "Email sent successfully"
    except smtplib.SMTPAuthenticationError as e:
        return False, f"Authentication failed: {str(e)}"
    except smtplib.SMTPRecipientsRefused as e:
        return False, f"Recipient email refused: {str(e)}"
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        return False, f"Email sending failed: {str(e)}"


def get_db():
    try:
        con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
        return con, con.cursor()
    except Exception as e:
        return None, str(e)


# ── Parse form ────────────────────────────────────────────────────────────────
# NOTE: NO enctype="multipart/form-data" on the modal form, so use default parse
form = cgi.FieldStorage()

active_tab = (form.getvalue('tab') or 'pending').strip().lower()
if active_tab not in ('pending', 'approved', 'rejected'):
    active_tab = 'pending'
filter_hospital = (form.getvalue('filter_hospital') or '').strip()

# ─────────────────────────────────────────────────────────────────────────────
# POST HANDLER — approve / reject
# ─────────────────────────────────────────────────────────────────────────────
if os.environ.get('REQUEST_METHOD', 'GET') == 'POST':
    print("Content-Type: text/html\n")
    try:
        con, cur = get_db()
        if con is None:
            print(f"<html><body><h2>DB Error</h2><p>{cur}</p></body></html>")
            sys.exit()

        id_hospital = form.getvalue("id")
        user_id     = form.getvalue("userid") or ""
        password    = form.getvalue("password") or ""
        action      = form.getvalue("action") or ""

        if not id_hospital:
            print("<html><body><script>alert('Error: Hospital ID not received.');history.back();</script></body></html>")
            con.close()
            sys.exit()

        cur.execute("SELECT hospital_name, email_id FROM hospital WHERE id=%s", (id_hospital,))
        data = cur.fetchone()

        if data:
            hospital_name, u_email = data
            u_email = str(u_email).strip() if u_email else "N/A"

            if action == "approve":
                cur.execute(
                    "UPDATE hospital SET user_id=%s, password=%s, status='approved' WHERE id=%s",
                    (user_id, password, id_hospital)
                )
                con.commit()
                email_body = f"""Hello {hospital_name} Team,

Congratulations! Your hospital registration has been APPROVED.

LOGIN CREDENTIALS
━━━━━━━━━━━━━━━━━━━━
User ID  : {user_id}
Password : {password}
━━━━━━━━━━━━━━━━━━━━

Please keep these credentials confidential and change your password after first login.

Best regards,
Administrator
Child Vaccination System
"""
                success, message = send_email(
                    u_email, "Hospital Account Approved - Login Credentials", email_body
                )
                msg_js   = "Hospital approved successfully! Login credentials sent to hospital email." if success \
                           else f"Hospital approved but email failed.\\nError: {message.replace(chr(34), chr(39))}"
                redirect = "admin_hospital_registration.py?tab=approved"

            elif action == "reject":
                cur.execute("UPDATE hospital SET status='rejected' WHERE id=%s", (id_hospital,))
                con.commit()
                email_body = f"""Hello {hospital_name},

After careful review, we regret to inform you that your hospital registration has been REJECTED.

Possible reasons:
- Incomplete or unclear documentation
- Verification issues with submitted credentials
- Non-compliance with system requirements

You are welcome to resubmit after addressing any outstanding issues.

Best regards,
Admin Team
Child Vaccination System
"""
                success, message = send_email(u_email, "Hospital Application Rejected", email_body)
                msg_js   = "Hospital rejected and notification email sent." if success \
                           else f"Hospital rejected but email failed.\\nError: {message.replace(chr(34), chr(39))}"
                redirect = "admin_hospital_registration.py?tab=rejected"

            else:
                msg_js   = f"Unknown action received: [{action}]"
                redirect = "admin_hospital_registration.py"

            print(f"""<html><body><script>
                alert("{msg_js}");
                window.location.href="{redirect}";
            </script></body></html>""")
        else:
            print(f"<html><body><script>alert('Hospital ID {id_hospital} not found in database.');history.back();</script></body></html>")

        con.close()
    except Exception as e:
        print(f"<html><body><h2>Server Error</h2><pre>{str(e)}</pre></body></html>")
    sys.exit()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE LOAD — GET
# ─────────────────────────────────────────────────────────────────────────────
print("Content-Type: text/html\n")

con, cur = get_db()
if con is None:
    print(f"<html><body><h2>Database Connection Failed!</h2><p>{cur}</p></body></html>")
    sys.exit()


def fetch_rows(status):
    q = "SELECT * FROM hospital WHERE status=%s"
    params = [status]
    if filter_hospital:
        q += " AND hospital_name LIKE %s"
        params.append(f"%{filter_hospital}%")
    cur.execute(q, params)
    return cur.fetchall()


pending_rows  = fetch_rows('pending')
approved_rows = fetch_rows('approved')
rejected_rows = fetch_rows('rejected')

tab_counts = {
    'pending':  len(pending_rows),
    'approved': len(approved_rows),
    'rejected': len(rejected_rows),
}

# ─────────────────────────────────────────────────────────────────────────────
# HTML OUTPUT
# ─────────────────────────────────────────────────────────────────────────────
print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<title>Hospital Registrations - Admin</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<style>

* {{ margin:0; padding:0; box-sizing:border-box; }}

body {{ background: linear-gradient(135deg, #3b021f, #ec4899, #fdf2f8); min-height:100vh;
       font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif; overflow-x:hidden; }}

.navbar {{ background: linear-gradient(135deg, #3b021f, #ec4899, #fdf2f8) !important;
          box-shadow:0 4px 15px rgba(0,0,0,0.3); padding:15px 20px; }}
.navbar .container-fluid {{ display:flex; flex-direction:row; align-items:center;
                            flex-wrap:nowrap; position:relative; }}
.navbar-brand {{ font-weight:600; color:white !important; letter-spacing:2px; text-transform:uppercase; }}
.navbar-brand i {{ margin-right:10px; color:#fda4af; font-size:1.5rem; animation:bounce 2s infinite; }}
@keyframes bounce {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-5px)}} }}

.mobile-menu-toggle {{ display:none; flex-shrink:0; align-self:center;
  background:rgba(255,255,255,0.15); border:1.5px solid rgba(255,255,255,0.35);
  color:white; padding:6px 12px; border-radius:8px; font-size:1.2rem; cursor:pointer;
  transition:all 0.3s ease; backdrop-filter:blur(6px); line-height:1; margin-right:12px; }}
.mobile-menu-toggle:hover {{ background:rgba(255,255,255,0.28);
  border-color:rgba(255,255,255,0.6); color:white; }}

.btn-logout {{ flex-shrink:0; background:linear-gradient(135deg,#ee0979 0%,#ff6a00 100%);
  border:none; padding:8px 20px; border-radius:25px; color:white; font-weight:600;
  transition:all 0.3s ease; box-shadow:0 4px 15px rgba(238,9,121,0.4);
  font-size:0.9rem; white-space:nowrap; }}
.btn-logout:hover {{ transform:translateY(-2px); box-shadow:0 6px 20px rgba(238,9,121,0.6); color:white; }}

.sidebar {{ min-height:100vh; background: linear-gradient(135deg, #3b021f, #ec4899);
           box-shadow:4px 0 15px rgba(0,0,0,0.2); padding:20px 0; }}
.sidebar-link {{ display:block; padding:12px 15px; color:#ecf0f1; text-decoration:none;
  cursor:pointer; transition:all 0.3s ease; border-left:4px solid transparent;
  font-weight:500; margin:5px 0; font-size:0.95rem; }}
.sidebar-link:hover, .sidebar-link.active {{
  background:linear-gradient(90deg,#ec4899,transparent);
  color:#fff; border-left:4px solid #fdf2f8; padding-left:20px; }}
.sidebar-link i {{ margin-right:10px; width:20px; text-align:center; }}

.sidebar-overlay {{ display:none; position:fixed; top:0; left:0; width:100%; height:100%;
  background:rgba(0,0,0,0.5); z-index:998; }}
.sidebar-overlay.show {{ display:block; }}

.content-wrap {{ padding:20px; }}
.page-title-card {{ background:white; border-radius:18px; padding:22px 25px;
  margin-bottom:20px; box-shadow:0 8px 25px rgba(0,0,0,0.12); border-left:8px solid #22d3ee; }}
.page-title {{ color:#0f172a; font-weight:500; font-size:1.9rem; text-transform:uppercase;
  letter-spacing:1px; margin:0; text-align:center; }}
.page-title i {{ margin-right:12px; color:#083344; }}

.tab-nav {{ display:flex; gap:10px; margin-bottom:20px; flex-wrap:wrap; }}
.tab-btn {{ flex:1; min-width:130px; padding:14px 10px; border:none; border-radius:14px;
  font-weight:700; font-size:0.9rem; cursor:pointer; transition:all 0.3s;
  display:flex; align-items:center; justify-content:center; gap:8px;
  background:rgba(255,255,255,0.25); color:white;
  box-shadow:0 4px 12px rgba(0,0,0,0.15); backdrop-filter:blur(6px); }}
.tab-btn:hover {{ transform:translateY(-2px); background:rgba(255,255,255,0.35); }}
.tab-btn.active-pending  {{ background:linear-gradient(135deg,#d97706,#f59e0b);
  box-shadow:0 6px 18px rgba(245,158,11,0.5); }}
.tab-btn.active-approved {{ background:linear-gradient(135deg,#059669,#10b981);
  box-shadow:0 6px 18px rgba(16,185,129,0.5); }}
.tab-btn.active-rejected {{ background:linear-gradient(135deg,#dc2626,#ef4444);
  box-shadow:0 6px 18px rgba(220,38,38,0.5); }}
.tab-count {{ background:rgba(255,255,255,0.3); border-radius:20px;
  padding:2px 9px; font-size:0.8rem; font-weight:800; }}

.filter-card {{ background:white; border-radius:16px; padding:22px 25px;
  box-shadow:0 6px 20px rgba(0,0,0,0.10); margin-bottom:20px; }}
.filter-label {{ font-weight:600; color:#374151; font-size:0.9rem; margin-bottom:10px; display:block; }}
.filter-label i {{ margin-right:6px; color:#764ba2; }}
.filter-input {{ border:2px solid #e5e7eb; border-radius:10px; padding:11px 14px;
  font-size:0.95rem; width:100%; transition:border-color 0.3s; }}
.filter-input:focus {{ border-color:#764ba2; outline:none; box-shadow:0 0 0 3px rgba(118,75,162,0.15); }}
.btn-filter {{ background:linear-gradient(135deg,#0ea5e9,#0284c7 50%); border:none; border-radius:10px;
  padding:11px 0; color:white; font-weight:700; font-size:0.95rem; width:100%;
  transition:all 0.3s; box-shadow:0 4px 15px rgba(14,165,233,0.4); }}
.btn-filter:hover {{ transform:translateY(-2px); }}
.btn-clear {{ background:linear-gradient(135deg,#6b7280,#4b5563); border:none; border-radius:10px;
  padding:11px 0; color:white; font-weight:700; font-size:0.95rem; width:100%; transition:all 0.3s; }}
.btn-clear:hover {{ transform:translateY(-2px); }}

.tab-panel {{ display:none; }}
.tab-panel.active {{ display:block; }}
.table-container {{ background:white; border-radius:15px;
  box-shadow:0 5px 20px rgba(0,0,0,0.2); padding:20px; overflow-x:auto; }}
table {{ width:100%; border-collapse:collapse; background:#fff; font-size:14px; }}
th, td {{ padding:15px 10px; text-align:center; vertical-align:middle; border-bottom:1px solid #e0e0e0; }}
th {{ background:linear-gradient(135deg, #083344, #22d3ee 90%); color:white;
  font-weight:600; text-transform:uppercase; font-size:13px;
  letter-spacing:0.5px; position:sticky; top:0; z-index:10; }}
tbody tr {{ transition:all 0.3s; }}
tbody tr:hover {{ background:#f8f9ff; transform:scale(1.01); box-shadow:0 2px 8px rgba(102,126,234,0.2); }}
.btn-view {{ background: linear-gradient(135deg, #0891b2, #06b6d4);
  border:none; padding:8px 20px; border-radius:25px; color:white;
  font-weight:500; transition:all 0.3s; box-shadow:0 4px 15px rgba(102,126,234,0.4); }}
.btn-view:hover {{ transform:translateY(-2px); }}
.icon-badge {{ display:inline-block; width:35px; height:35px;
  background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
  border-radius:50%; text-align:center; line-height:35px; color:white; margin-right:10px; }}
.no-data {{ text-align:center; padding:50px; color:#666; font-size:1.1rem; }}

.modal-content {{ border:none; border-radius:20px; overflow:hidden; box-shadow:0 10px 40px rgba(0,0,0,0.3); }}
.modal-header {{ background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
  color:white; padding:20px 30px; border:none; }}
.modal-title {{ font-weight:600; font-size:1.5rem; text-transform:uppercase; letter-spacing:1px; }}
.modal-body {{ padding:30px; background:#f8f9fa; }}
.detail-card {{ background:white; padding:20px; border-radius:15px;
  box-shadow:0 2px 10px rgba(0,0,0,0.1); margin-bottom:20px; }}
.detail-card h5 {{ color:#667eea; font-weight:600; margin-bottom:20px;
  padding-bottom:10px; border-bottom:2px solid #667eea; }}
.detail-row {{ display:flex; margin-bottom:12px; padding:8px 0; }}
.detail-label {{ font-weight:600; color:#555; width:160px; flex-shrink:0; }}
.detail-value {{ color:#333; flex-grow:1; }}
.proof-container {{ text-align:center; margin-top:20px; }}
.proof-img {{ max-width:100%; max-height:300px; border-radius:15px;
  box-shadow:0 5px 20px rgba(0,0,0,0.2); border:3px solid #667eea; }}
.credentials-section {{ background:linear-gradient(135deg,rgba(102,126,234,0.08) 0%,rgba(118,75,162,0.08) 100%);
  padding:20px; border-radius:15px; border:2px solid #667eea; }}
.credentials-section h5 {{ color:#764ba2; margin-bottom:20px; }}
.form-control[readonly] {{ background:white; border:2px solid #667eea; font-weight:600; color:#333; }}
.modal-footer {{ background:#f8f9fa; padding:20px 30px; border:none; }}
.btn-approve {{ background:linear-gradient(135deg,#0f5132 0%,#198754 100%);
  border:none; padding:10px 28px; border-radius:25px; color:white;
  font-weight:600; transition:all 0.3s; box-shadow:0 4px 15px rgba(15,81,50,0.4); }}
.btn-approve:hover {{ transform:translateY(-2px); }}
.btn-reject {{ background:linear-gradient(135deg,#ee0979 0%,#ff6a00 100%);
  border:none; padding:10px 28px; border-radius:25px; color:white;
  font-weight:600; transition:all 0.3s; box-shadow:0 4px 15px rgba(238,9,121,0.4); }}
.btn-reject:hover {{ transform:translateY(-2px); }}

@media (max-width:991.98px) {{
  .mobile-menu-toggle {{ display:flex; align-items:center; justify-content:center; }}
  .sidebar {{ position:fixed; left:-100%; top:0; width:280px; height:100vh;
    z-index:999; transition:left 0.3s ease; overflow-y:auto; }}
  .sidebar.show {{ left:0; }}
  .content-wrap {{ padding:15px; }}
  .navbar-brand {{ position:absolute; left:50%; transform:translateX(-50%);
    margin:0 !important; font-size:1rem; }}
  .navbar-brand i {{ font-size:1.3rem; }}
}}
@media (max-width:767.98px) {{
  .table-container {{ padding:12px; }}
  .btn-logout {{ padding:6px 15px; font-size:0.8rem; }}
  .page-title {{ font-size:1.4rem; }}
  .tab-btn {{ font-size:0.8rem; padding:11px 8px; min-width:100px; }}
}}
@media (max-width:575.98px) {{
  .navbar-brand {{ font-size:0.85rem; }}
  .navbar-brand i {{ font-size:1.1rem; }}
  th, td {{ font-size:0.75rem; padding:8px 5px; }}
  .page-title {{ font-size:1.1rem; }}
}}
@media (max-width:400px) {{
  .navbar-brand {{ font-size:0.75rem; }}
}}
</style>
</head>
<body>

<script>const ACTIVE_TAB = "{active_tab}";</script>

<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container-fluid">
    <button class="mobile-menu-toggle" onclick="toggleSidebar()">
      <i class="fas fa-bars"></i>
    </button>
    <span class="navbar-brand">
      <i class="fa-solid fa-hands-holding-child"></i> CVS - Admin
    </span>
    <button class="btn btn-logout ms-auto" onclick="logout()">
      <i class="fas fa-sign-out-alt"></i> Logout
    </button>
  </div>
</nav>

<div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

<div class="container-fluid">
  <div class="row">

    <div class="col-lg-2 col-md-3 sidebar p-0" id="sidebar">
      <a href="admin_dashboard.py" class="sidebar-link"><i class="fas fa-home"></i> Home</a>
      <a href="admin_vaccination.py" class="sidebar-link"><i class="fa-solid fa-circle-info"></i> Add Vaccination Info</a>
      <a href="admin_hospital_registration.py" class="sidebar-link active"><i class="fas fa-hospital"></i> Hospital Registration</a>
      <a href="admin_parent_registration.py" class="sidebar-link"><i class="fas fa-user"></i> Parent Registration</a>
      <a href="admin_view_child.py" class="sidebar-link"><i class="fas fa-baby"></i> View Children</a>
      <a href="admin_view_appointment.py" class="sidebar-link"><i class="fas fa-calendar-check"></i> View Appointments</a>
      <a href="admin_vaccination_schedule.py" class="sidebar-link"><i class="fa-solid fa-syringe"></i> Vaccination Schedule</a>
      <a href="admin_appointment_reminder.py" class="sidebar-link"><i class="fas fa-bell"></i> Appointment Reminders</a>
      <a href="admin_export_data.py" class="sidebar-link"><i class="fas fa-file-export"></i> Export Data</a>
      <a href="admin_view_feedback.py" class="sidebar-link"><i class="fas fa-comment-dots"></i> Feedback</a>
    </div>

    <div class="col-lg-10 col-md-9 col-12 content-wrap">

      <div class="page-title-card">
        <h4 class="page-title">
          <i class="fas fa-hospital-alt"></i> Hospital Registrations
        </h4>
      </div>

      <div class="tab-nav">
        <button class="tab-btn {'active-pending' if active_tab=='pending' else ''}" onclick="switchTab('pending')">
          <i class="fas fa-hospital-alt"></i> Pending
          <span class="tab-count">{tab_counts['pending']}</span>
        </button>
        <button class="tab-btn {'active-approved' if active_tab=='approved' else ''}" onclick="switchTab('approved')">
          <i class="fa-solid fa-house-medical-circle-check"></i> Approved
          <span class="tab-count">{tab_counts['approved']}</span>
        </button>
        <button class="tab-btn {'active-rejected' if active_tab=='rejected' else ''}" onclick="switchTab('rejected')">
          <i class="fa-solid fa-house-medical-circle-xmark"></i> Rejected
          <span class="tab-count">{tab_counts['rejected']}</span>
        </button>
      </div>

      <div class="filter-card">
        <span class="filter-label"><i class="fas fa-filter"></i> Filter by Hospital Name</span>
        <div class="row g-3 align-items-end">
          <div class="col-md-5">
            <input type="text" class="filter-input" id="filterHospital"
                   placeholder="Enter hospital name..." value="{filter_hospital}">
          </div>
          <div class="col-md-3">
            <button class="btn-filter" onclick="applyFilter()">
              <i class="fas fa-search"></i> Filter
            </button>
          </div>
          <div class="col-md-3">
            <button class="btn-clear" onclick="clearFilter()">
              <i class="fas fa-redo"></i> Clear
            </button>
          </div>
        </div>
      </div>
""")


def render_row_modal(i, tab_key):
    def val(idx):
        return str(i[idx]) if len(i) > idx and i[idx] else "N/A"

    id_h   = i[0]
    h_name = val(1);  h_type = val(2);   lic_no = val(3);  lic_prf = val(4)
    est_yr = val(5);  logo   = val(6);   email  = val(7);  mobile  = val(8)
    emerg  = val(9);  state  = val(10);  dist   = val(11); city    = val(12)
    pin    = val(13); street = val(14);  area   = val(15); t_beds  = val(16)
    icu    = val(17); e_svc  = val(18);  amb    = val(19); blood   = val(20)
    pharma = val(21); svcs   = val(22);  w_hrs  = val(23); opd     = val(24)
    o_name = val(25); o_dob  = val(26);  o_gen  = val(27); o_prof  = val(28)
    id_typ = val(29); id_num = val(30);  id_prf = val(31); o_type  = val(32)
    o_prf = val(33)

    if tab_key == 'approved' and len(i) > 37:
        uid = val(36)
        pwd = val(37)
    else:
        uid = f"hCvS{id_h}"
        pwd = h_name[:3].upper() + str(id_h) + generate_random_string(4)

    # ── KEY FIX: Use two separate mini-forms, one per action ──────────────────
    # This avoids all onclick/hidden-field timing issues entirely.
    # Each button is its own form with a hardcoded action value.
    if tab_key == 'pending':
        footer_btns = f"""
          <button form="form-approve-{id_h}" type="submit" class="btn btn-approve">
            <i class="fas fa-check-circle"></i> Approve
          </button>
          <button form="form-reject-{id_h}" type="submit" class="btn btn-reject">
            <i class="fas fa-times-circle"></i> Reject
          </button>"""
        hidden_forms = f"""
          <form id="form-approve-{id_h}" method="post" action="admin_hospital_registration.py" style="display:none">
            <input type="hidden" name="id"       value="{id_h}">
            <input type="hidden" name="userid"   value="{uid}">
            <input type="hidden" name="password" value="{pwd}">
            <input type="hidden" name="action"   value="approve">
          </form>
          <form id="form-reject-{id_h}" method="post" action="admin_hospital_registration.py" style="display:none">
            <input type="hidden" name="id"     value="{id_h}">
            <input type="hidden" name="action" value="reject">
          </form>"""
        cred_note = '<div class="alert alert-info mt-3 mb-0"><i class="fas fa-info-circle"></i> These credentials will be sent to the hospital\'s email upon approval.</div>'

    elif tab_key == 'approved':
        footer_btns = f"""
          <button form="form-reject-{id_h}" type="submit" class="btn btn-reject">
            <i class="fas fa-times-circle"></i> Reject Application
          </button>"""
        hidden_forms = f"""
          <form id="form-reject-{id_h}" method="post" action="admin_hospital_registration.py" style="display:none">
            <input type="hidden" name="id"     value="{id_h}">
            <input type="hidden" name="action" value="reject">
          </form>"""
        cred_note = '<div class="alert alert-success mt-3 mb-0"><i class="fas fa-check-circle"></i> These credentials have already been sent to the hospital\'s email.</div>'

    else:  # rejected
        footer_btns = f"""
          <button form="form-approve-{id_h}" type="submit" class="btn btn-approve">
            <i class="fas fa-check-circle"></i> Approve Application
          </button>"""
        hidden_forms = f"""
          <form id="form-approve-{id_h}" method="post" action="admin_hospital_registration.py" style="display:none">
            <input type="hidden" name="id"       value="{id_h}">
            <input type="hidden" name="userid"   value="{uid}">
            <input type="hidden" name="password" value="{pwd}">
            <input type="hidden" name="action"   value="approve">
          </form>"""
        cred_note = '<div class="alert alert-info mt-3 mb-0"><i class="fas fa-info-circle"></i> These credentials will be sent to the hospital\'s email upon approval.</div>'

    return f"""
        {hidden_forms}

        <tr>
          <td><span class="icon-badge">{id_h}</span></td>
          <td><strong>{h_name}</strong></td>
          <td>{h_type}</td>
          <td>{email}</td>
          <td>{mobile}</td>
          <td>
            <button type="button" class="btn btn-view"
                    data-bs-toggle="modal"
                    data-bs-target="#modal-{tab_key}-{id_h}">
              <i class="fas fa-eye"></i> View Details
            </button>
          </td>
        </tr>

        <div class="modal fade" id="modal-{tab_key}-{id_h}" tabindex="-1" aria-hidden="true">
          <div class="modal-dialog modal-xl">
            <div class="modal-content">
              <div class="modal-header">
                <h4 class="modal-title">
                  <i class="fas fa-hospital-alt"></i> Hospital Registration Details
                </h4>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
              </div>
              <div class="modal-body">
                <div class="row">

                  <div class="col-12">
                    <div class="detail-card">
                      <h5><i class="fa-regular fa-hospital"></i> Hospital Information</h5>
                      <div class="proof-container">
                        <img src="./image/{logo}" alt="Hospital Logo" class="proof-img">
                        <p class="mt-2"><span class="badge bg-primary">Hospital Logo</span></p>
                      </div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-hospital-alt"></i> Hospital Name :</span><span class="detail-value">{h_name}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-building"></i> Hospital Type :</span><span class="detail-value">{h_type}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-calendar"></i> Established Year :</span><span class="detail-value">{est_yr}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-envelope"></i> Email :</span><span class="detail-value">{email}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-phone"></i> Mobile :</span><span class="detail-value">{mobile}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-ambulance"></i> Emergency :</span><span class="detail-value">{emerg}</span></div>
                    </div>
                  </div>

                  <div class="col-md-6">
                    <div class="detail-card">
                      <h5><i class="fas fa-file-medical"></i> Hospital ID Proof Details</h5>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-certificate"></i> License Number :</span><span class="detail-value">{lic_no}</span></div>
                      <div class="proof-container">
                        <img src="./image/{lic_prf}" alt="License Proof" class="proof-img">
                        <p class="mt-2"><span class="badge bg-primary">License Proof</span></p>
                      </div>
                    </div>
                  </div>

                  <div class="col-md-6">
                    <div class="detail-card">
                      <h5><i class="fas fa-map-marker-alt"></i> Address Information</h5>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-map"></i> State :</span><span class="detail-value">{state}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-city"></i> District :</span><span class="detail-value">{dist}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-building"></i> City :</span><span class="detail-value">{city}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-road"></i> Street :</span><span class="detail-value">{street}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-location-arrow"></i> Area :</span><span class="detail-value">{area}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-mail-bulk"></i> Pincode :</span><span class="detail-value">{pin}</span></div>
                    </div>
                  </div>

                  <div class="col-md-6">
                    <div class="detail-card">
                      <h5><i class="fas fa-bed"></i> Facilities Information</h5>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-bed"></i> Total Beds :</span><span class="detail-value">{t_beds}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-procedures"></i> ICU Beds :</span><span class="detail-value">{icu}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-ambulance"></i> Emergency :</span><span class="detail-value">{e_svc}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-truck-medical"></i> Ambulance :</span><span class="detail-value">{amb}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-tint"></i> Blood Bank :</span><span class="detail-value">{blood}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-pills"></i> Pharmacy :</span><span class="detail-value">{pharma}</span></div>
                    </div>
                  </div>

                  <div class="col-md-6">
                    <div class="detail-card">
                      <h5><i class="fa-solid fa-user-clock"></i> Working Information</h5>
                      <div class="detail-row"><span class="detail-label"><i class="fa-solid fa-clock-rotate-left"></i> Working Hours :</span><span class="detail-value">{w_hrs}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-clock"></i> OPD Timings :</span><span class="detail-value">{opd}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-heartbeat"></i> Services 24x7 :</span><span class="detail-value">{svcs}</span></div>
                    </div>
                  </div>

                  <div class="col-md-6">
                    <div class="detail-card">
                      <h5><i class="fas fa-user-tie"></i> Owner Information</h5>
                      <div class="proof-container">
                        <img src="./image/{o_prof}" alt="Owner Profile" class="proof-img">
                        <p class="mt-2"><span class="badge bg-primary">Owner Profile</span></p>
                      </div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-user"></i> Owner Name :</span><span class="detail-value">{o_name}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-birthday-cake"></i> Owner DOB :</span><span class="detail-value">{o_dob}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-venus-mars"></i> Gender :</span><span class="detail-value">{o_gen}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-briefcase"></i> Owner Type :</span><span class="detail-value">{o_type}</span></div>
                    </div>
                  </div>

                  <div class="col-md-6">
                    <div class="detail-card">
                      <h5><i class="fas fa-address-card"></i> Owner ID Proof Details</h5>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-id-card"></i> ID Type :</span><span class="detail-value">{id_typ}</span></div>
                      <div class="detail-row"><span class="detail-label"><i class="fas fa-hashtag"></i> ID Number :</span><span class="detail-value">{id_num}</span></div>
                      <div class="proof-container">
                        <img src="./image/{id_prf}" alt="ID Proof" class="proof-img">
                        <p class="mt-2"><span class="badge bg-primary">ID Proof</span></p>
                      </div>
                    </div>
                  </div>
                  
                  <div class="col-md-6">
                    <div class="detail-card">
                      <h5><i class="fas fa-hospital-user"></i> Ownership Proof</h5>
                      <div class="proof-container">
                        <img src="./image/{o_prf}" alt="Ownership Proof" class="proof-img">
                        <p class="mt-2"><span class="badge bg-primary">Ownership Proof</span></p>
                      </div>
                    </div>
                  </div>

                </div>

                <hr class="my-4">

                <div class="credentials-section">
                  <h5><i class="fas fa-key"></i> Login Credentials</h5>
                  <div class="row">
                    <div class="col-md-6">
                      <label class="form-label fw-bold">User ID</label>
                      <input type="text" class="form-control" value="{uid}" readonly>
                    </div>
                    <div class="col-md-6">
                      <label class="form-label fw-bold">Password</label>
                      <input type="text" class="form-control" value="{pwd}" readonly>
                    </div>
                  </div>
                  {cred_note}
                </div>

              </div>
              <div class="modal-footer">
                {footer_btns}
              </div>
            </div>
          </div>
        </div>
    """


def render_panel(tab_key, rows):
    no_data_msg = {
        'pending':  'No Pending Registrations Found...!',
        'approved': 'No Approved Registrations Found...!',
        'rejected': 'No Rejected Registrations Found...!',
    }
    active_cls = 'active' if tab_key == active_tab else ''
    print(f'<div class="tab-panel {active_cls}" id="panel-{tab_key}">')
    print('<div class="table-container"><table><thead><tr>')
    print('''<th><i class="fas fa-hashtag"></i> ID</th>
              <th><i class="fas fa-hospital"></i> Hospital Name</th>
              <th><i class="fas fa-building"></i> Type</th>
              <th><i class="fas fa-envelope"></i> Email</th>
              <th><i class="fas fa-phone"></i> Mobile</th>
              <th><i class="fas fa-cogs"></i> Actions</th>''')
    print('</tr></thead><tbody>')
    if not rows:
        print(f'''<tr><td colspan="6" class="no-data">
          <i class="fas fa-inbox" style="font-size:3rem;color:#ccc;margin-bottom:15px;display:block;"></i>
          {no_data_msg[tab_key]}
        </td></tr>''')
    else:
        for row in rows:
            print(render_row_modal(row, tab_key))
    print('</tbody></table></div></div>')


render_panel('pending',  pending_rows)
render_panel('approved', approved_rows)
render_panel('rejected', rejected_rows)

print(f"""
    </div>
  </div>
</div>

<script>
const TAB_COLORS = {{
  pending:  'active-pending',
  approved: 'active-approved',
  rejected: 'active-rejected'
}};
const TAB_ORDER = ['pending', 'approved', 'rejected'];

function switchTab(tab) {{
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b =>
    b.classList.remove('active-pending', 'active-approved', 'active-rejected')
  );
  document.getElementById('panel-' + tab).classList.add('active');
  document.querySelectorAll('.tab-btn')[TAB_ORDER.indexOf(tab)].classList.add(TAB_COLORS[tab]);
  const url = new URL(window.location.href);
  url.searchParams.set('tab', tab);
  history.replaceState(null, '', url.toString());
}}

function applyFilter() {{
  const h = document.getElementById('filterHospital').value.trim();
  if (!h) {{ alert('Please enter a hospital name to filter.'); return; }}
  const url = new URL(window.location.href);
  url.searchParams.set('filter_hospital', h);
  window.location.href = url.toString();
}}

function clearFilter() {{
  const url = new URL(window.location.href);
  url.searchParams.delete('filter_hospital');
  window.location.href = url.toString();
}}

function toggleSidebar() {{
  document.getElementById('sidebar').classList.toggle('show');
  document.getElementById('sidebarOverlay').classList.toggle('show');
}}

document.addEventListener('click', function(e) {{
  const sb = document.getElementById('sidebar');
  const mt = document.querySelector('.mobile-menu-toggle');
  if (window.innerWidth < 992 && sb && mt &&
      !sb.contains(e.target) && !mt.contains(e.target) &&
      sb.classList.contains('show')) {{
    sb.classList.remove('show');
    document.getElementById('sidebarOverlay').classList.remove('show');
  }}
}});

function logout() {{
  if (confirm("Are you sure you want to logout?")) window.location.href = "main.py";
}}

document.addEventListener('DOMContentLoaded', () => switchTab(ACTIVE_TAB));
</script>
</body>
</html>
""")

con.close()