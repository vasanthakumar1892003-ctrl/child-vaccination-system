#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgi
import cgitb
import sys

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")
print("Content-Type: text/html\r\n\r\n")

try:
    con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
    cur = con.cursor()
except Exception as e:
    print(f"<h2 style='color:red;'>Database Connection Failed!</h2><pre>{e}</pre>")
    sys.exit()

form        = cgi.FieldStorage()
parent_id   = form.getvalue("parent_id", "")
filter_date = form.getvalue("filter_date", "").strip()

# Fetch parent name
parent_name = ""
if parent_id and parent_id.isdigit():
    cur.execute("SELECT parent_name FROM parent WHERE id = %s", (int(parent_id),))
    pr = cur.fetchone()
    if pr:
        parent_name = pr[0]

# Fetch booked appointments from parentform
if parent_name and filter_date:
    cur.execute(
        "SELECT * FROM parentform WHERE p_name = %s AND appointment_date = %s ORDER BY id DESC",
        (parent_name, filter_date)
    )
elif parent_name:
    cur.execute(
        "SELECT * FROM parentform WHERE p_name = %s ORDER BY id DESC",
        (parent_name,)
    )
elif filter_date:
    cur.execute(
        "SELECT * FROM parentform WHERE appointment_date = %s ORDER BY id DESC",
        (filter_date,)
    )
else:
    cur.execute("SELECT * FROM parentform ORDER BY id DESC")

appointments = cur.fetchall()

# Pre-fetch all hospitals for modal lookup: hospital_name (lowercase) -> row
cur.execute("SELECT * FROM hospital")
all_hospitals = cur.fetchall()
hospital_dict = {}
for h in all_hospitals:
    if h[1]:
        hospital_dict[str(h[1]).strip().lower()] = h

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<title>Booked Appointments - CVS</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  background: linear-gradient(135deg, #052e16, #22c55e, #dcfce7);
  min-height:100vh; font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif; overflow-x:hidden;
}}
/* ===== NAVBAR ===== */
.navbar {{
  box-shadow:0 4px 20px rgba(0,0,0,0.4); padding:15px 20px;
  background: linear-gradient(135deg, #052e16, #22c55e, #dcfce7) !important;
}}
.navbar .container-fluid {{ display:flex; flex-direction:row; align-items:center; flex-wrap:nowrap; }}
.navbar-brand {{ font-weight:600; color:white !important; letter-spacing:2px; text-transform:uppercase; }}
.navbar-brand i {{ margin-right:10px; color:#d1fae5; font-size:1.5rem; animation:bounce 2s infinite; }}
@keyframes bounce {{
  0%,100% {{ transform:translateY(0); }}
  50%      {{ transform:translateY(-5px); }}
}}
.mobile-menu-toggle {{
  display:none; flex-shrink:0; align-self:center;
  background:rgba(255,255,255,0.15); border:1.5px solid rgba(255,255,255,0.35);
  color:white; padding:6px 12px; border-radius:8px; font-size:1.2rem;
  cursor:pointer; transition:all 0.3s ease; backdrop-filter:blur(6px);
  line-height:1; margin-right:12px;
}}
.mobile-menu-toggle:hover {{ background:rgba(255,255,255,0.28); border-color:rgba(255,255,255,0.6); color:white; }}
.btn-logout {{
  flex-shrink:0; background:linear-gradient(135deg,#ee0979 0%,#ff6a00 100%);
  border:none; padding:8px 20px; border-radius:25px; color:white; font-weight:600;
  transition:all 0.3s ease; box-shadow:0 4px 15px rgba(238,9,121,0.4);
  font-size:0.9rem; white-space:nowrap;
}}
.btn-logout:hover {{ transform:translateY(-2px); color:white; }}
/* ===== SIDEBAR ===== */
.sidebar {{
  min-height:100vh; background:linear-gradient(135deg,#052e16,#22c55e);
  box-shadow:4px 0 20px rgba(0,0,0,0.3); padding:20px 0;
}}
.sidebar-link {{
  display:block; padding:14px 18px; color:#d1fae5; text-decoration:none;
  transition:all 0.3s; border-left:4px solid transparent; font-weight:500; margin:6px 0;
}}
.sidebar-link:hover, .sidebar-link.active {{
  background:linear-gradient(90deg,#22c55e,transparent);
  color:#fff; border-left:4px solid #dcfce7;
}}
.sidebar-link i {{ margin-right:12px; width:22px; text-align:center; }}
.sidebar-overlay {{
  display:none; position:fixed; top:0; left:0;
  width:100%; height:100%; background:rgba(0,0,0,0.6); z-index:998; backdrop-filter:blur(2px);
}}
.sidebar-overlay.show {{ display:block; }}
/* ===== CONTENT ===== */
.content-wrap {{ padding:20px; }}
.page-title-card {{
  background:white; border-radius:18px; padding:22px 28px; margin-bottom:20px;
  box-shadow:0 8px 25px rgba(0,0,0,0.12); display:flex; align-items:center; gap:16px;
}}
.title-icon {{
  background:linear-gradient(135deg,#052e16,#22c55e); color:white;
  width:48px; height:48px; border-radius:12px;
  display:flex; align-items:center; justify-content:center;
  font-size:1.4rem; flex-shrink:0;
}}
.page-title-card h2 {{
  font-size:1.5rem; font-weight:800; color:#0f172a;
  letter-spacing:1.5px; text-transform:uppercase; margin:0;
}}
/* Filter Card */
.filter-card {{
  background:white; border-radius:16px; padding:22px 25px;
  box-shadow:0 6px 20px rgba(0,0,0,0.10); margin-bottom:20px;
}}
.filter-label {{ font-weight:600; color:#374151; font-size:0.9rem; margin-bottom:10px; display:block; }}
.filter-label i {{ margin-right:6px; color:#059669; }}
.filter-input {{
  border:2px solid #e5e7eb; border-radius:10px; padding:11px 14px;
  font-size:0.95rem; width:100%; transition:border-color 0.3s;
}}
.filter-input:focus {{ border-color:#059669; outline:none; box-shadow:0 0 0 3px rgba(5,150,105,0.15); }}
.btn-filter {{
  background:linear-gradient(135deg,#052e16,#22c55e); border:none; border-radius:10px;
  padding:11px 0; color:white; font-weight:700; font-size:0.95rem; width:100%;
  transition:all 0.3s; box-shadow:0 4px 15px rgba(5,150,105,0.4); cursor:pointer;
}}
.btn-filter:hover {{ transform:translateY(-2px); }}
.btn-clear {{
  background:linear-gradient(135deg,#6b7280,#4b5563); border:none; border-radius:10px;
  padding:11px 0; color:white; font-weight:700; font-size:0.95rem; width:100%;
  transition:all 0.3s; cursor:pointer;
}}
.btn-clear:hover {{ transform:translateY(-2px); }}
/* Table Card */
.table-card {{
  background:white; border-radius:18px; padding:28px;
  box-shadow:0 8px 25px rgba(0,0,0,0.12);
}}
table {{ width:100%; border-collapse:collapse; }}
table thead tr {{ border-bottom:2px solid #e5e7eb; }}
table thead th {{
  padding:14px 16px; font-weight:700; text-transform:uppercase;
  letter-spacing:0.8px; font-size:0.78rem; color:#374151;
  white-space:nowrap; background:transparent;
}}
table thead th i {{ margin-right:6px; color:#059669; }}
table tbody tr {{ border-bottom:1px solid #f1f5f9; transition:background 0.2s; }}
table tbody tr:last-child {{ border-bottom:none; }}
table tbody tr:hover {{ background:#f0fdf4; }}
table tbody td {{ padding:16px; vertical-align:middle; font-size:0.92rem; color:#1e293b; }}
.serial-num {{ font-weight:700; color:#374151; font-size:0.95rem; }}
.child-name-cell {{ display:flex; align-items:center; gap:8px; font-weight:600; color:#065f46; }}
.child-name-cell i {{ color:#10b981; font-size:1rem; }}
/* Status badges */
.badge-approved {{
  background:transparent; color:#059669; border:2px solid #10b981;
  padding:6px 18px; border-radius:50px; font-weight:700; font-size:0.78rem;
  letter-spacing:0.5px; white-space:nowrap;
}}
.badge-pending {{
  background:transparent; color:#d97706; border:2px solid #f59e0b;
  padding:6px 18px; border-radius:50px; font-weight:700; font-size:0.78rem;
  letter-spacing:0.5px; white-space:nowrap;
}}
.badge-rejected {{
  background:transparent; color:#dc2626; border:2px solid #ef4444;
  padding:6px 18px; border-radius:50px; font-weight:700; font-size:0.78rem;
  letter-spacing:0.5px; white-space:nowrap;
}}
.badge-completed {{
  background:transparent; color:#8e2de2; border:2px solid #8e2de2;
  padding:6px 18px; border-radius:50px; font-weight:700; font-size:0.78rem;
  letter-spacing:0.5px; white-space:nowrap;
}}
.badge-cancelled {{
  background:transparent; color:#dc2626; border:2px solid #dc2626;
  padding:6px 18px; border-radius:50px; font-weight:700; font-size:0.78rem;
  letter-spacing:0.5px; white-space:nowrap;
}}
.no-data {{ text-align:center; padding:60px 20px; color:#64748b; }}
.no-data i {{ font-size:3.5rem; color:#d1fae5; margin-bottom:15px; display:block; }}
/* View Button */
.btn-view {{
  background:linear-gradient(135deg,#0077b6,#00b4d8);
  border:none; border-radius:8px; padding:7px 16px;
  color:white; font-weight:600; font-size:0.78rem;
  cursor:pointer; transition:all 0.3s;
  box-shadow:0 3px 10px rgba(0,119,182,0.3); white-space:nowrap;
}}
.btn-view:hover {{ transform:translateY(-2px); box-shadow:0 5px 15px rgba(0,119,182,0.4); }}
.btn-view i {{ margin-right:5px; }}
/* ===== HOSPITAL MODAL ===== */
.modal-overlay {{
  display:none; position:fixed; top:0; left:0;
  width:100%; height:100%; background:rgba(0,0,0,0.65);
  z-index:2000; backdrop-filter:blur(4px);
  align-items:center; justify-content:center;
}}
.modal-overlay.show {{ display:flex; }}
.hosp-modal {{
  background:white; border-radius:20px; width:92%; max-width:720px;
  max-height:88vh; overflow-y:auto;
  box-shadow:0 20px 60px rgba(0,0,0,0.3);
  animation:slideUp 0.3s ease;
}}
@keyframes slideUp {{
  from {{ transform:translateY(40px); opacity:0; }}
  to   {{ transform:translateY(0);    opacity:1; }}
}}
.hosp-modal-header {{
  background:linear-gradient(135deg,#052e16,#22c55e);
  padding:22px 28px; border-radius:20px 20px 0 0;
  display:flex; align-items:center; justify-content:space-between;
  position:sticky; top:0; z-index:10;
}}
.hosp-modal-header h3 {{
  color:white; font-size:1.2rem; font-weight:800;
  letter-spacing:1px; text-transform:uppercase; margin:0;
  display:flex; align-items:center; gap:10px;
}}
.btn-modal-close {{
  background:rgba(255,255,255,0.2); border:none; color:white;
  width:34px; height:34px; border-radius:50%; font-size:1.1rem;
  cursor:pointer; display:flex; align-items:center; justify-content:center;
  transition:background 0.2s; flex-shrink:0;
}}
.btn-modal-close:hover {{ background:rgba(255,255,255,0.35); }}
.hosp-modal-body {{ padding:24px 28px; }}
.hosp-logo-wrap img {{
  width:90px; height:90px; object-fit:cover;
  border-radius:16px; border:3px solid #d1fae5;
  box-shadow:0 4px 16px rgba(0,0,0,0.12);
}}
.hosp-logo-placeholder {{
  width:90px; height:90px; border-radius:16px;
  background:linear-gradient(135deg,#052e16,#22c55e);
  display:inline-flex; align-items:center; justify-content:center;
  font-size:2.2rem; color:white;
  box-shadow:0 4px 16px rgba(0,0,0,0.12);
}}
.hosp-section-title {{
  font-size:0.72rem; font-weight:800; text-transform:uppercase;
  letter-spacing:1px; color:#059669; margin:18px 0 10px;
  display:flex; align-items:center; gap:7px;
  border-bottom:1.5px solid #d1fae5; padding-bottom:6px;
}}
.hosp-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:10px 20px; }}
.hosp-field {{
  background:#f8fffe; border-radius:10px; padding:10px 14px;
  border:1.5px solid #e6f7f0;
}}
.hosp-field-label {{
  font-size:0.68rem; font-weight:700; text-transform:uppercase;
  letter-spacing:0.5px; color:#94a3b8; margin-bottom:3px;
}}
.hosp-field-value {{ font-size:0.9rem; font-weight:600; color:#1e293b; word-break:break-word; }}
.hosp-field-value.green {{ color:#065f46; }}
.facility-wrap {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:4px; }}
.facility-badge {{
  padding:5px 13px; border-radius:50px; font-size:0.75rem; font-weight:700; letter-spacing:0.3px;
}}
.facility-yes {{ background:#d1fae5; color:#065f46; }}
.facility-no  {{ background:#f1f5f9; color:#94a3b8; }}
/* ===== MOBILE CARDS ===== */
.appt-cards {{ display:none; }}
.appt-card {{
  background:#fff; border-radius:14px; padding:16px 18px;
  box-shadow:0 4px 16px rgba(0,0,0,0.09); margin-bottom:14px;
  border-left:4px solid #22c55e;
}}
.appt-card-header {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; }}
.appt-card-num {{
  background:linear-gradient(135deg,#052e16,#22c55e);
  color:#fff; font-size:0.7rem; font-weight:700;
  border-radius:50px; padding:3px 10px; letter-spacing:0.5px;
}}
.appt-card-child {{
  font-size:0.98rem; font-weight:700; color:#065f46; margin-bottom:10px;
  display:flex; align-items:center; gap:7px;
}}
.appt-card-child i {{ color:#10b981; }}
.appt-card-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:8px 14px; }}
.appt-card-field {{ display:flex; flex-direction:column; gap:2px; }}
.appt-card-label {{
  font-size:0.68rem; font-weight:700; text-transform:uppercase;
  letter-spacing:0.5px; color:#94a3b8;
}}
.appt-card-value {{ font-size:0.86rem; font-weight:600; color:#1e293b; }}
.appt-card-footer {{ margin-top:12px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px; }}
/* ===== RESPONSIVE ===== */
@media (max-width:991.98px) {{
  .mobile-menu-toggle {{ display:flex; align-items:center; justify-content:center; }}
  .sidebar {{
    position:fixed; left:-100%; top:0;
    width:280px; height:100vh; z-index:999; transition:left 0.3s; overflow-y:auto;
  }}
  .sidebar.show {{ left:0; }}
  .content-wrap {{ padding:12px; }}
  .navbar-brand {{ font-size:1rem; letter-spacing:1px; }}
  .navbar-brand i {{ font-size:1.3rem; }}
}}
@media (max-width:767.98px) {{
  .desktop-table {{ display:none !important; }}
  .appt-cards    {{ display:block; }}
  .table-card    {{ padding:16px; }}
  .btn-logout    {{ padding:6px 16px; font-size:0.85rem; }}
  .page-title-card {{ padding:14px 16px; }}
  .page-title-card h2 {{ font-size:1.1rem; letter-spacing:0.8px; }}
  .filter-card   {{ padding:16px; }}
  .hosp-modal    {{ width:96%; }}
  .hosp-modal-body {{ padding:16px; }}
  .hosp-grid     {{ grid-template-columns:1fr; }}
}}
@media (max-width:575.98px) {{
  .navbar-brand  {{ font-size:0.85rem; letter-spacing:0.5px; }}
  .navbar-brand i {{ font-size:1.1rem; margin-right:6px; }}
  .btn-logout    {{ padding:6px 14px; font-size:0.8rem; }}
  .appt-card-grid {{ grid-template-columns:1fr; }}
}}
@media (max-width:400px) {{
  .navbar-brand  {{ font-size:0.75rem; }}
  .content-wrap  {{ padding:8px; }}
}}
</style>
</head>
<body>

<script>const PARENT_ID = "{parent_id}";</script>

<!-- NAVBAR -->
<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container-fluid">
    <button class="mobile-menu-toggle" onclick="toggleSidebar()">
      <i class="fas fa-bars"></i>
    </button>
    <span class="navbar-brand ms-2">
      <i class="fa-solid fa-users"></i> CVS - Parent
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
      <a href="parent_dashboard.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fas fa-home"></i> Home
      </a>
      <a href="parent_vaccination.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fa-solid fa-circle-info"></i> Vaccination Info
      </a>
      <a href="parent_manage_child.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fas fa-baby"></i> Manage Children
      </a>
      <a href="parent_view_hospital.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fa-solid fa-eye"></i> View Hospital
      </a>
      <a href="parent_booked_appointment.py?parent_id={parent_id}" class="sidebar-link active" onclick="closeSidebarMobile()">
        <i class="fa-solid fa-calendar-day"></i> Booked Appointments
      </a>
      <a href="parent_my_appointment.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fas fa-calendar-check"></i> My Appointments
      </a>
      <a href="parent_reminder.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fas fa-bell"></i> My Reminders
      </a>
      <a href="parent_profile.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fas fa-user-circle"></i> My Profile
      </a>
      <a href="parent_feedback.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fas fa-comment-dots"></i> Feedback
      </a>
      <a href="parent_help.py?parent_id={parent_id}" class="sidebar-link">
        <i class="fas fa-circle-question"></i> Help & Support
      </a>
    </div>

    <!-- MAIN CONTENT -->
    <div class="col-lg-10 col-md-9 col-12 content-wrap">

      <div class="page-title-card">
        <div class="title-icon"><i class="fa-solid fa-calendar-day"></i></div>
        <h2>Booked Appointments</h2>
      </div>

      <div class="filter-card">
        <span class="filter-label"><i class="fas fa-filter"></i> Filter by Date</span>
        <div class="row g-3 align-items-end">
          <div class="col-md-5">
            <input type="date" class="filter-input" id="filterDate" value="{filter_date}">
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

      <div class="table-card">
        <!-- Desktop/Tablet Table -->
        <div class="desktop-table" style="overflow-x:auto;">
          <table>
            <thead>
              <tr>
                <th><i class="fas fa-hashtag"></i> #</th>
                <th><i class="fas fa-user"></i> Parent Name</th>
                <th><i class="fas fa-baby"></i> Child Name</th>
                <th><i class="fas fa-hospital"></i> Hospital</th>
                <th><i class="fas fa-syringe"></i> Vaccine</th>
                <th><i class="fas fa-map-marker-alt"></i> District</th>
                <th><i class="fas fa-info-circle"></i> Status</th>
                <th><i class="fas fa-calendar-alt"></i> Appt. Date</th>
                <th><i class="fas fa-eye"></i> Action</th>
              </tr>
            </thead>
            <tbody>
""")

# ── Column index mapping for parentform ──
# 0:id  1:p_name  2:p_type  3:p_gender  4:mobile  5:email
# 6:aadhaar_number  7:c_name  8:c_gender  9:c_dob  10:c_order
# 11:vaccin  12:vaccin_age  13:vaccination  14:appointment_date
# 15:age_group  16:vaccine_name  17:address  18:district
# 19:pincode  20:hospital_name  21:status  22:created_at

# ── Hospital table column mapping ──
# 0:id  1:hospital_name  2:hospital_type  3:license_number  4:license_proof
# 5:year_of_establishment  6:hospital_logo  7:email_id  8:hospital_mobile
# 9:hospital_mobile_emergency  10:state  11:district  12:city  13:pincode
# 14:street  15:area  16:bed  17:icu  18:emergency  19:ambulance
# 20:blood_bank  21:pharmacy  22:service  23:working_time  24:opd_time
# 25:owner_name  26:owner_dob  27:owner_gender  28:owner_profile
# 29:id_type  30:id_number  31:id_proof  32:owner_type  33:ownership_proof
# 34:status  35:Created_at  36:user_id  37:password

def get_val(row, i, fallback="N/A"):
    return str(row[i]).strip() if len(row) > i and row[i] is not None and str(row[i]).strip() != "" else fallback

def get_badge(raw_status):
    s = str(raw_status).strip().lower()
    if s == "approved":
        return '<span class="badge-approved">APPROVED</span>'
    elif s == "completed":
        return '<span class="badge-completed">COMPLETED</span>'
    elif s == "rejected":
        return '<span class="badge-rejected">REJECTED</span>'
    elif s in ("cancelled", "canceled"):
        return '<span class="badge-cancelled">CANCELLED</span>'
    elif s == "pending":
        return '<span class="badge-pending">PENDING</span>'
    else:
        lbl = str(raw_status).upper() if raw_status else "PENDING"
        return f'<span class="badge-pending">{lbl}</span>'

def facility_badge(val, label):
    is_yes = str(val).strip().lower() in ("yes", "available", "1", "true")
    cls  = "facility-yes" if is_yes else "facility-no"
    icon = "fa-check"     if is_yes else "fa-times"
    return f'<span class="facility-badge {cls}"><i class="fas {icon} me-1"></i>{label}</span>'

if not appointments:
    print("""
              <tr>
                <td colspan="9" class="no-data">
                  <i class="fas fa-calendar-times"></i>
                  No booked appointments found.
                </td>
              </tr>
    """)
    print("""
            </tbody>
          </table>
        </div>
        <div class="appt-cards">
          <div class="no-data">
            <i class="fas fa-calendar-times"></i>
            No booked appointments found.
          </div>
        </div>
    """)
else:
    # ── Desktop table rows ──
    for idx, row in enumerate(appointments, start=1):
        p_name     = get_val(row, 1)
        c_name     = get_val(row, 7)
        hospital   = get_val(row, 20)
        vaccine    = get_val(row, 16) if get_val(row, 16) != "N/A" else get_val(row, 11)
        district   = get_val(row, 18)
        appt_date  = get_val(row, 14)
        raw_status = row[21] if len(row) > 21 and row[21] is not None else ""
        badge      = get_badge(raw_status)
        h_id       = f"hosp_{idx}"

        print(f"""
              <tr>
                <td class="serial-num">{idx}</td>
                <td>{p_name}</td>
                <td>
                  <div class="child-name-cell">
                    <i class="fas fa-baby"></i> {c_name}
                  </div>
                </td>
                <td><strong>{hospital}</strong></td>
                <td>{vaccine}</td>
                <td>{district}</td>
                <td>{badge}</td>
                <td><strong>{appt_date}</strong></td>
                <td>
                  <button class="btn-view" onclick="openModal('{h_id}')">
                    <i class="fas fa-eye"></i> View
                  </button>
                </td>
              </tr>
        """)

    print("""
            </tbody>
          </table>
        </div><!-- /desktop-table -->
    """)

    # ── Mobile cards ──
    print('<div class="appt-cards">')
    for idx, row in enumerate(appointments, start=1):
        p_name     = get_val(row, 1)
        c_name     = get_val(row, 7)
        hospital   = get_val(row, 20)
        vaccine    = get_val(row, 16) if get_val(row, 16) != "N/A" else get_val(row, 11)
        district   = get_val(row, 18)
        appt_date  = get_val(row, 14)
        raw_status = row[21] if len(row) > 21 and row[21] is not None else ""
        card_badge = get_badge(raw_status)
        h_id       = f"hosp_{idx}"

        print(f"""
        <div class="appt-card">
          <div class="appt-card-header">
            <span class="appt-card-num">#{idx}</span>
            {card_badge}
          </div>
          <div class="appt-card-child">
            <i class="fas fa-baby"></i> {c_name}
          </div>
          <div class="appt-card-grid">
            <div class="appt-card-field">
              <span class="appt-card-label"><i class="fas fa-user me-1"></i> Parent</span>
              <span class="appt-card-value">{p_name}</span>
            </div>
            <div class="appt-card-field">
              <span class="appt-card-label"><i class="fas fa-hospital me-1"></i> Hospital</span>
              <span class="appt-card-value">{hospital}</span>
            </div>
            <div class="appt-card-field">
              <span class="appt-card-label"><i class="fas fa-syringe me-1"></i> Vaccine</span>
              <span class="appt-card-value">{vaccine}</span>
            </div>
            <div class="appt-card-field">
              <span class="appt-card-label"><i class="fas fa-map-marker-alt me-1"></i> District</span>
              <span class="appt-card-value">{district}</span>
            </div>
            <div class="appt-card-field">
              <span class="appt-card-label"><i class="fas fa-calendar-alt me-1"></i> Date</span>
              <span class="appt-card-value">{appt_date}</span>
            </div>
          </div>
          <div class="appt-card-footer">
            {card_badge}
            <button class="btn-view" onclick="openModal('{h_id}')">
              <i class="fas fa-eye"></i> View Hospital
            </button>
          </div>
        </div>
        """)
    print('</div><!-- /appt-cards -->')

print("""
      </div><!-- /table-card -->
    </div><!-- /content-wrap -->
  </div><!-- /row -->
</div><!-- /container-fluid -->
""")

# ══════════════════════════════════════════
# HOSPITAL DETAIL MODALS (one per row)
# ══════════════════════════════════════════
if appointments:
    for idx, row in enumerate(appointments, start=1):
        hospital = get_val(row, 20)
        h_id     = f"hosp_{idx}"
        h        = hospital_dict.get(hospital.lower())

        if h:
            h_name  = get_val(h, 1)
            h_type  = get_val(h, 2)
            h_lic   = get_val(h, 3)
            h_year  = get_val(h, 5)
            h_logo  = get_val(h, 6)
            h_email = get_val(h, 7)
            h_mob   = get_val(h, 8)
            h_emerg = get_val(h, 9)
            h_state = get_val(h, 10)
            h_dist  = get_val(h, 11)
            h_city  = get_val(h, 12)
            h_pin   = get_val(h, 13)
            h_str   = get_val(h, 14)
            h_area  = get_val(h, 15)
            h_bed   = get_val(h, 16)
            h_icu   = get_val(h, 17)
            h_emg   = get_val(h, 18)
            h_amb   = get_val(h, 19)
            h_blood = get_val(h, 20)
            h_pharm = get_val(h, 21)
            h_svc   = get_val(h, 22)
            h_work  = get_val(h, 23)
            h_opd   = get_val(h, 24)
            h_own   = get_val(h, 25)
            h_odob  = get_val(h, 26)
            h_ogen  = get_val(h, 27)

            logo_html = (
                f'<img src="/hospital_logos/{h_logo}" alt="Logo">'
                if h_logo != "N/A" else
                '<div class="hosp-logo-placeholder"><i class="fas fa-hospital"></i></div>'
            )

            fac = (
                facility_badge(h_emg,   "Emergency")  +
                facility_badge(h_amb,   "Ambulance")  +
                facility_badge(h_blood, "Blood Bank") +
                facility_badge(h_pharm, "Pharmacy")
            )

            print(f"""
<div class="modal-overlay" id="{h_id}">
  <div class="hosp-modal">
    <div class="hosp-modal-header">
      <h3><i class="fas fa-hospital"></i> Hospital Details</h3>
      <button class="btn-modal-close" onclick="closeModal('{h_id}')">
        <i class="fas fa-times"></i>
      </button>
    </div>
    <div class="hosp-modal-body">

      <div class="hosp-section-title"><i class="fas fa-info-circle"></i> Basic Information</div>
      <div class="hosp-grid">
        <div class="hosp-field">
          <div class="hosp-field-label">Hospital Name</div>
          <div class="hosp-field-value green">{h_name}</div>
        </div>
        <div class="hosp-field">
          <div class="hosp-field-label">Hospital Type</div>
          <div class="hosp-field-value">{h_type}</div>
        </div>
        <div class="hosp-field">
          <div class="hosp-field-label">License Number</div>
          <div class="hosp-field-value">{h_lic}</div>
        </div>
        <div class="hosp-field">
          <div class="hosp-field-label">Year of Establishment</div>
          <div class="hosp-field-value">{h_year}</div>
        </div>
        <div class="hosp-field">
          <div class="hosp-field-label">Total Beds</div>
          <div class="hosp-field-value">{h_bed}</div>
        </div>
        <div class="hosp-field">
          <div class="hosp-field-label">ICU Beds</div>
          <div class="hosp-field-value">{h_icu}</div>
        </div>
      </div>

      <div class="hosp-section-title"><i class="fas fa-phone-alt"></i> Contact Details</div>
      <div class="hosp-grid">
        <div class="hosp-field">
          <div class="hosp-field-label">Email</div>
          <div class="hosp-field-value">{h_email}</div>
        </div>
        <div class="hosp-field">
          <div class="hosp-field-label">Mobile</div>
          <div class="hosp-field-value">{h_mob}</div>
        </div>
        <div class="hosp-field">
          <div class="hosp-field-label">Emergency Contact</div>
          <div class="hosp-field-value">{h_emerg}</div>
        </div>
        <div class="hosp-field">
          <div class="hosp-field-label">Working Hours</div>
          <div class="hosp-field-value">{h_work}</div>
        </div>
        <div class="hosp-field">
          <div class="hosp-field-label">OPD Timing</div>
          <div class="hosp-field-value">{h_opd}</div>
        </div>
      </div>

      <div class="hosp-section-title"><i class="fas fa-map-marker-alt"></i> Address</div>
      <div class="hosp-grid">
        <div class="hosp-field">
          <div class="hosp-field-label">Street</div>
          <div class="hosp-field-value">{h_str}</div>
        </div>
        <div class="hosp-field">
          <div class="hosp-field-label">Area</div>
          <div class="hosp-field-value">{h_area}</div>
        </div>
        <div class="hosp-field">
          <div class="hosp-field-label">City</div>
          <div class="hosp-field-value">{h_city}</div>
        </div>
        <div class="hosp-field">
          <div class="hosp-field-label">District</div>
          <div class="hosp-field-value">{h_dist}</div>
        </div>
        <div class="hosp-field">
          <div class="hosp-field-label">State</div>
          <div class="hosp-field-value">{h_state}</div>
        </div>
        <div class="hosp-field">
          <div class="hosp-field-label">Pincode</div>
          <div class="hosp-field-value">{h_pin}</div>
        </div>
      </div>

      <div class="hosp-section-title"><i class="fas fa-stethoscope"></i> Facilities & Services</div>
      <div class="facility-wrap">{fac}</div>
      <div style="margin-top:10px;">
        <div class="hosp-field">
          <div class="hosp-field-label">Services Offered</div>
          <div class="hosp-field-value">{h_svc}</div>
        </div>
      </div>

      <div class="hosp-section-title"><i class="fas fa-user-tie"></i> Owner Information</div>
      <div class="hosp-grid">
        <div class="hosp-field">
          <div class="hosp-field-label">Owner Name</div>
          <div class="hosp-field-value green">{h_own}</div>
        </div>
        <div class="hosp-field">
          <div class="hosp-field-label">Gender</div>
          <div class="hosp-field-value">{h_ogen}</div>
        </div>
        <div class="hosp-field">
          <div class="hosp-field-label">Date of Birth</div>
          <div class="hosp-field-value">{h_odob}</div>
        </div>
      </div>

    </div>
  </div>
</div>
            """)
        else:
            print(f"""
<div class="modal-overlay" id="{h_id}">
  <div class="hosp-modal">
    <div class="hosp-modal-header">
      <h3><i class="fas fa-hospital"></i> Hospital Details</h3>
      <button class="btn-modal-close" onclick="closeModal('{h_id}')">
        <i class="fas fa-times"></i>
      </button>
    </div>
    <div class="hosp-modal-body">
      <div class="no-data">
        <i class="fas fa-hospital-slash"></i>
        <p style="margin-top:10px;">No details found for <strong>{hospital}</strong>.</p>
      </div>
    </div>
  </div>
</div>
            """)

print(f"""
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
function openModal(id) {{
  document.getElementById(id).classList.add('show');
  document.body.style.overflow = 'hidden';
}}
function closeModal(id) {{
  document.getElementById(id).classList.remove('show');
  document.body.style.overflow = '';
}}
document.querySelectorAll('.modal-overlay').forEach(function(overlay) {{
  overlay.addEventListener('click', function(e) {{
    if (e.target === overlay) closeModal(overlay.id);
  }});
}});
document.addEventListener('keydown', function(e) {{
  if (e.key === 'Escape') {{
    document.querySelectorAll('.modal-overlay.show').forEach(function(m) {{
      closeModal(m.id);
    }});
  }}
}});
function applyFilter() {{
  const date = document.getElementById('filterDate').value;
  if (!date) {{ alert('Please select a date to filter.'); return; }}
  window.location.href = 'parent_booked_appointment.py?parent_id=' + PARENT_ID + '&filter_date=' + date;
}}
function clearFilter() {{
  window.location.href = 'parent_booked_appointment.py?parent_id=' + PARENT_ID;
}}
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
document.addEventListener('click', function(e) {{
  const sidebar    = document.getElementById('sidebar');
  const menuToggle = document.querySelector('.mobile-menu-toggle');
  if (window.innerWidth < 992 &&
      sidebar.classList.contains('show') &&
      !sidebar.contains(e.target) &&
      !menuToggle.contains(e.target)) {{
    closeSidebarMobile();
  }}
}});
</script>
</body>
</html>
""")

con.close()