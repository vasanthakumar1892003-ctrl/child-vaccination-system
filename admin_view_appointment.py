#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import pymysql.cursors
import cgi
import cgitb
import sys
import json

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")

form = cgi.FieldStorage()

try:
    con = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="cvsdp",
        cursorclass=pymysql.cursors.DictCursor
    )
    cur = con.cursor()
    # FIX 4: separate cursor for sub-queries inside the row loop
    sub_cur = con.cursor()
except Exception as e:
    print("Content-Type: text/html\n")
    print(f"<html><body><h2>Database Connection Failed!</h2><p>{e}</p></body></html>")
    sys.exit()

# ============================================================
# AJAX HANDLER — POST with app_id + status  →  returns JSON
# ============================================================
app_id = form.getvalue('app_id', '').strip()
status = form.getvalue('status', '').strip().lower()

if app_id and status:
    print("Content-Type: application/json\n")

    def send_json(ok, msg=""):
        print(json.dumps({"success": ok, "message": msg}))
        con.close()
        sys.exit()

    if not app_id.isdigit():
        send_json(False, "Invalid application ID.")
    if status not in ('approved', 'rescheduled', 'pending'):
        send_json(False, "Invalid status value.")

    try:
        cur.execute("UPDATE parentform SET status = %s WHERE id = %s", (status, int(app_id)))
        con.commit()
        if cur.rowcount == 0:
            send_json(False, f"No application found with ID {app_id}.")
        else:
            send_json(True, f"Application {app_id} marked as {status}.")
    except Exception as e:
        con.rollback()
        send_json(False, f"Database error: {str(e)}")

# ============================================================
# PAGE LOAD — GET request  →  renders full HTML page
# ============================================================
print("Content-Type: text/html\n")

cur.execute("SELECT * FROM parentform ORDER BY id DESC")
rows = cur.fetchall()

total = len(rows)
pending = approved = rescheduled = 0

def get_status(r):
    s = r.get('status') or 'pending'
    return str(s).lower().strip()

for r in rows:
    s = get_status(r)
    if s == 'approved':
        approved += 1
    elif s == 'rescheduled':
        rescheduled += 1
    else:
        pending += 1

print("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Admin - View All Appointments</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  background: linear-gradient(135deg, #3b021f, #ec4899, #fdf2f8);
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow-x: hidden;
}

/* ── NAVBAR ── */
.navbar {
  background: linear-gradient(135deg, #3b021f, #ec4899, #fdf2f8) !important;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  padding: 15px 20px;
}

.navbar-brand {
  font-weight: 600;
  color: white !important;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.navbar-brand i {
  margin-right: 10px;
  color: #fda4af;
  font-size: 1.5rem;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-5px); }
}

/* ── MOBILE MENU TOGGLE ── */
.mobile-menu-toggle {
  display: none;
  background: rgba(255,255,255,0.15);
  border: 1.5px solid rgba(255,255,255,0.35);
  color: white;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(6px);
  line-height: 1;
}

.mobile-menu-toggle:hover {
  background: rgba(255,255,255,0.28);
  border-color: rgba(255,255,255,0.6);
  color: white;
}

/* ── LOGOUT ── */
.btn-logout {
  background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
  border: none;
  padding: 8px 20px;
  border-radius: 25px;
  color: white;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(238,9,121,0.4);
  font-size: 0.9rem;
}

.btn-logout:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(238,9,121,0.6);
  color: white;
}

/* ── SIDEBAR ── */
.sidebar {
  min-height: 100vh;
  background: linear-gradient(135deg, #3b021f, #ec4899);
  box-shadow: 4px 0 15px rgba(0,0,0,0.2);
  padding: 20px 0;
}

.sidebar-link {
  display: block;
  padding: 12px 15px;
  color: #ecf0f1;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
  font-weight: 500;
  margin: 5px 0;
  font-size: 0.95rem;
}

.sidebar-link:hover, .sidebar-link.active {
  background: linear-gradient(90deg, #ec4899, transparent);
  color: #fff;
  border-left: 4px solid #fdf2f8;
  padding-left: 20px;
}

.sidebar-link i { margin-right: 10px; width: 20px; text-align: center; }

/* ── SIDEBAR OVERLAY ── */
.sidebar-overlay {
  display: none;
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.5);
  z-index: 998;
}
.sidebar-overlay.show { display: block; }

/* ── CONTENT AREA ── */
.content-area { padding: 20px; }

/* ── TABLE CONTAINER ── */
.table-container {
  background: white;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.1);
  overflow-x: auto;
}

/* ── PAGE TITLE ── */
.page-title {
  color: #2c3e50;
  font-weight: 700;
  font-size: 1.5rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 3px solid #667eea;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
}

.page-title i { margin-right: 12px; color: #667eea; }

/* ── STAT CARDS ── */
.stats-row { display: flex; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; }

.stat-card {
  flex: 1; min-width: 140px; padding: 18px; border-radius: 15px;
  display: flex; align-items: center; gap: 12px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

.stat-card:hover { transform: translateY(-4px); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }
.stat-card.total    { background: linear-gradient(135deg, #ede9fe, #ddd6fe); color: #4c1d95; border: 2px solid #c4b5fd; }
.stat-card.pending  { background: linear-gradient(135deg, #fef9c3, #fef08a); color: #713f12; border: 2px solid #fde047; }
.stat-card.approved { background: linear-gradient(135deg, #d1fae5, #a7f3d0); color: #065f46; border: 2px solid #6ee7b7; }
.stat-card.rescheduled { background: linear-gradient(135deg, #fee2e2, #fecaca); color: #991b1b; border: 2px solid #fca5a5; }

.stat-icon {
  font-size: 2rem;
  width: 52px; height: 52px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 12px;
  flex-shrink: 0;
}
.stat-card.total    .stat-icon { background: rgba(139,92,246,0.2); color: #7c3aed; }
.stat-card.pending  .stat-icon { background: rgba(234,179,8,0.2);  color: #b45309; }
.stat-card.approved .stat-icon { background: rgba(16,185,129,0.2); color: #059669; }
.stat-card.rescheduled .stat-icon { background: rgba(239,68,68,0.2);  color: #dc2626; }

.stat-count { font-size: 1.8rem; font-weight: 800; line-height: 1; margin-bottom: 4px; }
.stat-label { font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; opacity: 0.9; }

/* ── CONTROLS ── */
.controls-row {
  display: flex; gap: 15px; margin-bottom: 20px;
  flex-wrap: wrap; align-items: center;
}

.search-box { flex: 1; min-width: 220px; position: relative; }

.search-box input {
  width: 100%;
  padding: 11px 15px 11px 42px;
  border: 2px solid #e5e7eb;
  border-radius: 25px;
  transition: all 0.3s;
  font-size: 0.9rem;
}

.search-box input:focus {
  border-color: #667eea;
  outline: none;
  box-shadow: 0 0 0 3px rgba(102,126,234,0.15);
}

.search-box i {
  position: absolute; left: 16px; top: 50%;
  transform: translateY(-50%); color: #667eea; font-size: 1rem;
}

.filter-tabs { display: flex; gap: 8px; flex-wrap: wrap; }

.filter-btn {
  padding: 9px 18px; border-radius: 25px;
  border: 2px solid #667eea; background: white; color: #667eea;
  font-weight: 600; cursor: pointer; transition: all 0.3s; font-size: 0.85rem;
}

.filter-btn:hover, .filter-btn.active {
  background: linear-gradient(135deg, #083344, #22d3ee);
  color: white; border-color: #cffafe;
  box-shadow:0 4px 14px rgba(124,58,237,0.45);
  transform: translateY(-2px);
}

/* ── TABLE ── */
table { width: 100%; border-collapse: collapse; margin-top: 15px; }

table thead th {
  background: linear-gradient(135deg, #083344, #22d3ee 90%);
  color: white;
  padding: 12px 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.85rem;
  white-space: nowrap;
  border: none;
}

table thead th:first-child { border-radius: 8px 0 0 0; }
table thead th:last-child  { border-radius: 0 8px 0 0; }

table tbody tr {
  transition: all 0.3s ease;
  border-bottom: 1px solid #e9ecef;
  background: white;
}

table tbody tr:hover {
  background: #f8f9ff;
  transform: scale(1.005);
  box-shadow: 0 2px 8px rgba(102,126,234,0.2);
}

table tbody td {
  padding: 12px 10px;
  vertical-align: middle;
  font-size: 0.9rem;
  color: #333;
}

/* ── ROW INDEX BADGE ── */
.row-index {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  width: 30px; height: 30px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.8rem;
}

/* ── STATUS BADGES ── */
.badge-pending {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  color: #92400e; border: 1px solid #f59e0b;
  padding: 5px 12px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; white-space: nowrap;
}
.badge-approved {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  color: #065f46; border: 1px solid #10b981;
  padding: 5px 12px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; white-space: nowrap;
}
.badge-rescheduled {
  background: linear-gradient(135deg, #fee2e2, #fecaca);
  color: #7f1d1d; border: 1px solid #ef4444;
  padding: 5px 12px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; white-space: nowrap;
}

/* ── ACTION BUTTONS ── */
.btn-view-det {
  background: linear-gradient(135deg, #0891b2, #06b6d4);
  color: white; border: none; padding: 6px 14px; border-radius: 20px;
  font-weight: 600; cursor: pointer; transition: all 0.3s;
  box-shadow: 0 3px 8px rgba(8,145,178,0.3); font-size: 0.85rem; margin: 2px;
}
.btn-view-det:hover { transform: translateY(-2px); box-shadow: 0 5px 12px rgba(6,182,212,0.5); color: white; }

/* ── MODAL ── */
.modal-content { border-radius: 18px; border: none; box-shadow: 0 10px 40px rgba(0,0,0,0.3); }
.modal-header {
  background: linear-gradient(135deg, #3a1c71 0%, #d76d77 100%);
  color: white; border-radius: 18px 18px 0 0;
  padding: 20px 30px; border: none;
}
.modal-header .modal-title { font-weight: 700; font-size: 1.2rem; }
.modal-header .btn-close { filter: brightness(0) invert(1); opacity: 0.8; }
.modal-body { padding: 25px; background: #f8f9fa; max-height: 70vh; overflow-y: auto; }
.modal-footer { border: none; padding: 20px 25px; background: #f8f9fa; border-radius: 0 0 18px 18px; }

.detail-section {
  background: white; border-radius: 12px; padding: 18px;
  margin-bottom: 18px; border-left: 4px solid #667eea;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.detail-section.hospital-info { border-left-color: #10b981; }
.detail-section.parent-info   { border-left-color: #f59e0b; }

.detail-section h6 { color: #667eea; font-weight: 700; margin-bottom: 12px; font-size: 1rem; }
.detail-section.hospital-info h6 { color: #10b981; }
.detail-section.parent-info h6   { color: #f59e0b; }

.detail-row { display: flex; padding: 8px 0; border-bottom: 1px solid #f3f4f6; font-size: 0.9rem; }
.detail-row:last-child { border-bottom: none; }
.detail-label { width: 40%; color: #6d28d9; font-weight: 600; }
.detail-label i { margin-right: 6px; width: 16px; }
.detail-value { width: 60%; color: #1e293b; font-weight: 500; }

/* ── NO DATA ── */
.no-data { text-align: center; padding: 60px 20px; color: #64748b; }
.no-data i { font-size: 4rem; color: #cbd5e1; display: block; margin-bottom: 15px; }
.no-data .message { font-size: 1.2rem; font-weight: 600; color: #475569; }

/* ── RESPONSIVE ── */
@media (max-width: 991.98px) {
  .mobile-menu-toggle { display: inline-flex; align-items: center; justify-content: center; }

  .sidebar {
    position: fixed; left: -100%; top: 0;
    width: 280px; height: 100vh;
    z-index: 999; transition: left 0.3s ease;
    overflow-y: auto;
  }
  .sidebar.show { left: 0; }

  .content-area { padding: 15px; margin-left: 0 !important; }
  .navbar-brand { font-size: 1rem; }
  .navbar-brand i { font-size: 1.3rem; }
}

@media (max-width: 767.98px) {
  .page-title { font-size: 1.2rem; }
  table thead th { font-size: 0.75rem; padding: 9px 6px; }
  table tbody td { font-size: 0.8rem; padding: 9px 6px; }
  .stats-row { gap: 10px; }
  .stat-card { padding: 13px; }
  .stat-count { font-size: 1.5rem; }
  .btn-logout { padding: 6px 15px; font-size: 0.8rem; }
}

@media (max-width: 575.98px) {
  .navbar-brand { font-size: 0.85rem; }
  .navbar-brand i { font-size: 1.1rem; }
}
</style>
</head>
<body>
""")

print(f"""
<!-- NAVBAR -->
<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container-fluid">
    <button class="mobile-menu-toggle me-3" onclick="toggleSidebar()">
      <i class="fas fa-bars"></i>
    </button>
    <span class="navbar-brand">
      <i class="fa-solid fa-hands-holding-child"></i> CVS - Admin
    </span>
    <button class="btn btn-logout btn-sm ms-auto" onclick="logout()">
      <i class="fas fa-sign-out-alt"></i> Logout
    </button>
  </div>
</nav>

<!-- Sidebar Overlay for Mobile -->
<div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

<div class="container-fluid">
  <div class="row">

    <!-- SIDEBAR -->
    <div class="col-lg-2 col-md-3 sidebar p-0" id="sidebar">
      <a href="admin_dashboard.py" class="sidebar-link">
        <i class="fas fa-home"></i> Home
      </a>
      <a href="admin_vaccination.py" class="sidebar-link">
        <i class="fa-solid fa-circle-info"></i> Add Vaccination Info
      </a>
      <a href="admin_hospital_registration.py" class="sidebar-link">
        <i class="fas fa-hospital"></i> Hospital Registration
      </a>
      <a href="admin_parent_registration.py" class="sidebar-link">
        <i class="fas fa-user"></i> Parent Registration
      </a>
      <a href="admin_view_child.py" class="sidebar-link">
        <i class="fas fa-baby"></i> View Children
      </a>
      <a href="admin_view_appointment.py" class="sidebar-link active">
        <i class="fas fa-calendar-check"></i> View Appointments
      </a>
      <a href="admin_vaccination_schedule.py" class="sidebar-link">
        <i class="fa-solid fa-syringe"></i> Vaccination Schedule
      </a>
      <a href="admin_appointment_reminder.py" class="sidebar-link">
        <i class="fas fa-bell"></i> Appointment Reminders
      </a>
      <a class="sidebar-link" href="admin_export_data.py">
        <i class="fas fa-file-export"></i> Export Data
      </a>
      <a href="admin_view_feedback.py" class="sidebar-link">
        <i class="fas fa-comment-dots"></i> Feedback
      </a>
    </div>

    <!-- MAIN CONTENT -->
    <div class="col-lg-10 col-md-9 col-12 content-area">
      <div class="table-container">

        <div class="page-title">
          <div>
            <i class="fa-solid fa-calendar-check"></i> All Vaccination Appointments
          </div>
          <div style="font-size:0.9rem;font-weight:500;color:#666;">
            <i class="fas fa-database"></i> Total Records:
            <span id="totalRecords">{total}</span>
          </div>
        </div>
""")

print(f"""
        <div class="stats-row">
          <div class="stat-card total">
            <div class="stat-icon"><i class="fas fa-clipboard-list"></i></div>
            <div class="stat-content">
              <div class="stat-count">{total}</div>
              <div class="stat-label">Total Applications</div>
            </div>
          </div>
          <div class="stat-card pending">
            <div class="stat-icon"><i class="fas fa-hourglass-half"></i></div>
            <div class="stat-content">
              <div class="stat-count">{pending}</div>
              <div class="stat-label">Pending Review</div>
            </div>
          </div>
          <div class="stat-card approved">
            <div class="stat-icon"><i class="fas fa-check-circle"></i></div>
            <div class="stat-content">
              <div class="stat-count">{approved}</div>
              <div class="stat-label">Approved</div>
            </div>
          </div>
          <div class="stat-card rescheduled">
            <div class="stat-icon"><i class="fa-solid fa-calendar-day"></i></div>
            <div class="stat-content">
              <div class="stat-count">{rescheduled}</div>
              <div class="stat-label">Rescheduled</div>
            </div>
          </div>
        </div>

        <div class="controls-row">
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input type="text" id="searchInput"
                   placeholder="Search by name, email, mobile, hospital..."
                   onkeyup="searchTable()">
          </div>
          <div class="filter-tabs">
            <button class="filter-btn active" onclick="filterTable('all',this)">
              <i class="fas fa-list"></i> All
            </button>
            <button class="filter-btn" onclick="filterTable('pending',this)">
              <i class="fas fa-clock"></i> Pending
            </button>
            <button class="filter-btn" onclick="filterTable('approved',this)">
              <i class="fas fa-check-circle"></i> Approved
            </button>
            <button class="filter-btn" onclick="filterTable('rescheduled',this)">
              <i class="fas fa-times-circle"></i> Rescheduled
            </button>
          </div>
        </div>

        <div style="overflow-x:auto;">
          <table id="appTable">
            <thead>
              <tr>
                <th><i class="fas fa-hashtag"></i> No.</th>
                <th><i class="fas fa-user"></i> Parent Name</th>
                <th><i class="fas fa-user-tag"></i> Type</th>
                <th><i class="fas fa-envelope"></i> Email</th>
                <th><i class="fas fa-baby"></i> Child Name</th>
                <th><i class="fas fa-venus-mars"></i> C.Gender</th>
                <th><i class="fas fa-hospital"></i> Hospital</th>
                <th><i class="fas fa-info-circle"></i> Status</th>
                <th><i class="fas fa-cogs"></i> Actions</th>
              </tr>
            </thead>
            <tbody>
""")

def safe(d, key):
    val = d.get(key)
    return str(val) if val is not None and val != '' else 'N/A'

# FIX 2: Helper functions defined ONCE outside the loop
def pget(row, keys):
    for k in keys:
        if k in row and row[k] is not None:
            return str(row[k])
    return 'N/A'

def hget(row, keys):
    for k in keys:
        if k in row and row[k] is not None:
            return str(row[k])
    return 'N/A'

if not rows:
    print("""
        <tr id="noDataRow">
          <td colspan="11">
            <div class="no-data">
              <i class="fas fa-inbox"></i>
              <div class="message">No Appointments Found...!</div>
              <p style="margin-top:10px;color:#94a3b8;">There are no vaccination appointments in the system yet.</p>
            </div>
          </td>
        </tr>
    """)
else:
    for row_num, r in enumerate(rows, start=1):
        # FIX 3: safely convert rid to int with fallback
        rid_raw     = r.get('id', '')
        rid         = int(rid_raw) if rid_raw != '' else 0
        rid_str     = f"{rid:05d}"

        p_name      = safe(r, 'p_name')
        p_type      = safe(r, 'p_type')
        p_gender    = safe(r, 'p_gender')
        mobile      = safe(r, 'mobile')
        email       = safe(r, 'email')
        aadhaar     = safe(r, 'aadhaar_number')
        c_name      = safe(r, 'c_name')
        c_gender    = safe(r, 'c_gender')
        c_dob       = safe(r, 'c_dob')
        c_order     = safe(r, 'c_order')
        vaccin      = safe(r, 'vaccin')
        vaccination = safe(r, 'vaccination')
        address     = safe(r, 'address')
        district    = safe(r, 'district')
        pincode     = safe(r, 'pincode')
        hospital    = safe(r, 'hospital_name')
        row_status  = get_status(r)

        parent_db_info = {}
        try:
            # FIX 4: use sub_cur so main cursor 'cur' is not disturbed
            sub_cur.execute("SELECT * FROM parent WHERE email_id = %s LIMIT 1", (email,))
            parent_row = sub_cur.fetchone()
            if parent_row:
                parent_db_info = {
                    'name':     pget(parent_row, ['parent_name']),
                    'mobile':   pget(parent_row, ['parent_mobile']),
                    'email':    pget(parent_row, ['email_id']),
                    'aadhaar':  pget(parent_row, ['id_number']),
                    'city':     pget(parent_row, ['city']),
                    'district': pget(parent_row, ['district']),
                    'state':    pget(parent_row, ['state']),
                    'pincode':  pget(parent_row, ['pincode']),
                    'status':   pget(parent_row, ['status']),
                }
        except Exception:
            parent_db_info = {}

        hospital_db_info = {}
        try:
            sub_cur.execute("SELECT * FROM hospital WHERE hospital_name = %s LIMIT 1", (hospital,))
            hospital_row = sub_cur.fetchone()
            if hospital_row:
                hospital_db_info = {
                    'name':    hget(hospital_row, ['hospital_name']),
                    'email':   hget(hospital_row, ['email_id']),
                    'phone':   hget(hospital_row, ['hospital_mobile']),
                    'city':    hget(hospital_row, ['city']),
                    'district':hget(hospital_row, ['district']),
                    'state':   hget(hospital_row, ['state']),
                    'pincode': hget(hospital_row, ['pincode']),
                    'license': hget(hospital_row, ['license_number']),
                    'type':    hget(hospital_row, ['hospital_type']),
                    'status':  hget(hospital_row, ['status']),
                }
        except Exception:
            hospital_db_info = {}

        if row_status == 'approved':
            badge = '<span class="badge-approved"><i class="fas fa-check-circle"></i> Approved</span>'
        elif row_status == 'rescheduled':
            # FIX 1: added missing closing </i> tag
            badge = '<span class="badge-rescheduled"><i class="fa-solid fa-calendar-day"></i> Rescheduled</span>'
        else:
            badge = '<span class="badge-pending"><i class="fas fa-clock"></i> Pending</span>'

        print(f"""
            <tr data-status="{row_status}" data-search="{p_name.lower()} {email.lower()} {mobile} {hospital.lower()} {c_name.lower()} {district.lower()}" data-rownum="{row_num}">
              <td><span class="row-index">{row_num}</span></td>
              <td><strong>{p_name}</strong></td>
              <td>{p_type}</td>
              <td style="font-size:0.85rem;">{email}</td>
              <td><strong>{c_name}</strong></td>
              <td>{c_gender}</td>
              <td>{hospital}</td>
              <td>{badge}</td>
              <td style="white-space:nowrap;">
                <button class="btn-view-det" data-bs-toggle="modal" data-bs-target="#modal{rid}">
                  <i class="fas fa-eye"></i> View
                </button>
              </td>
            </tr>

            <!-- DETAIL MODAL {rid} -->
            <div class="modal fade" id="modal{rid}" tabindex="-1" aria-hidden="true">
              <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
                <div class="modal-content">
                  <div class="modal-header">
                    <h5 class="modal-title">
                      <i class="fas fa-file-medical"></i> Complete Application Details
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                  </div> 
                  <div class="modal-body">
                    <div class="row">
                      <!-- LEFT: Application Form Data -->
                      <div class="col-md-6">
                        <h5 style="color:#667eea;font-weight:700;margin-bottom:15px;">
                          <i class="fas fa-file-alt"></i> Application Form Data
                        </h5>
                        <div class="detail-section">
                          <h6><i class="fas fa-user"></i> Parent Information</h6>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-user"></i> Parent Name</div>
                            <div class="detail-value">{p_name}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-user-tag"></i> Parent Type</div>
                            <div class="detail-value">{p_type}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-venus-mars"></i> Gender</div>
                            <div class="detail-value">{p_gender}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-phone"></i> Mobile</div>
                            <div class="detail-value">{mobile}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-envelope"></i> Email</div>
                            <div class="detail-value">{email}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-id-card"></i> Aadhaar</div>
                            <div class="detail-value">{aadhaar}</div>
                          </div>
                        </div>
                        <div class="detail-section">
                          <h6><i class="fas fa-baby"></i> Child Information</h6>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-baby"></i> Child Name</div>
                            <div class="detail-value">{c_name}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-venus-mars"></i> Gender</div>
                            <div class="detail-value">{c_gender}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-birthday-cake"></i> Date of Birth</div>
                            <div class="detail-value">{c_dob}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-sort-numeric-up"></i> Child Order</div>
                            <div class="detail-value">{c_order}</div>
                          </div>
                        </div>
                        <div class="detail-section">
                          <h6><i class="fas fa-syringe"></i> Vaccination Information</h6>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-question-circle"></i> Status</div>
                            <div class="detail-value">{vaccin}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-list-check"></i> Vaccines</div>
                            <div class="detail-value">{vaccination}</div>
                          </div>
                        </div>
                        <div class="detail-section">
                          <h6><i class="fas fa-map-marked-alt"></i> Address &amp; Appointment</h6>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-home"></i> Address</div>
                            <div class="detail-value">{address}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-map-marker-alt"></i> District</div>
                            <div class="detail-value">{district}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-mail-bulk"></i> Pincode</div>
                            <div class="detail-value">{pincode}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-hospital"></i> Hospital</div>
                            <div class="detail-value">{hospital}</div>
                          </div>
                        </div>
                      </div>

                      <!-- RIGHT: Database Records -->
                      <div class="col-md-6">
                        <h5 style="color:#10b981;font-weight:700;margin-bottom:15px;">
                          <i class="fas fa-database"></i> Database Records
                        </h5>
                        <div class="detail-section parent-info">
                          <h6><i class="fas fa-user-circle"></i> Parent Database Information</h6>
        """)

        if parent_db_info:
            print(f"""
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-user"></i> Registered Name</div>
                            <div class="detail-value">{parent_db_info['name']}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-phone"></i> Mobile</div>
                            <div class="detail-value">{parent_db_info['mobile']}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-envelope"></i> Email</div>
                            <div class="detail-value">{parent_db_info['email']}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-id-card"></i> Aadhaar</div>
                            <div class="detail-value">{parent_db_info['aadhaar']}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-city"></i> City</div>
                            <div class="detail-value">{parent_db_info['city']}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-map-marker-alt"></i> District</div>
                            <div class="detail-value">{parent_db_info['district']}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-flag"></i> State</div>
                            <div class="detail-value">{parent_db_info['state']}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-mail-bulk"></i> Pincode</div>
                            <div class="detail-value">{parent_db_info['pincode']}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-check-circle"></i> Account Status</div>
                            <div class="detail-value">{parent_db_info['status']}</div>
                          </div>
            """)
        else:
            print("""
                          <div class="detail-row">
                            <div class="detail-label" style="width:100%;text-align:center;color:#ef4444;">
                              <i class="fas fa-exclamation-triangle"></i> No parent found in database with this email
                            </div>
                          </div>
            """)

        print("""
                        </div>
                        <div class="detail-section hospital-info">
                          <h6><i class="fas fa-hospital"></i> Hospital Database Information</h6>
        """)

        if hospital_db_info:
            print(f"""
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-hospital"></i> Hospital Name</div>
                            <div class="detail-value">{hospital_db_info['name']}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-envelope"></i> Email</div>
                            <div class="detail-value">{hospital_db_info['email']}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-phone"></i> Phone</div>
                            <div class="detail-value">{hospital_db_info['phone']}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-city"></i> City</div>
                            <div class="detail-value">{hospital_db_info['city']}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-map-marker-alt"></i> District</div>
                            <div class="detail-value">{hospital_db_info['district']}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-flag"></i> State</div>
                            <div class="detail-value">{hospital_db_info['state']}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-mail-bulk"></i> Pincode</div>
                            <div class="detail-value">{hospital_db_info['pincode']}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-certificate"></i> License Number</div>
                            <div class="detail-value">{hospital_db_info['license']}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-building"></i> Hospital Type</div>
                            <div class="detail-value">{hospital_db_info['type']}</div>
                          </div>
                          <div class="detail-row">
                            <div class="detail-label"><i class="fas fa-check-circle"></i> Verification Status</div>
                            <div class="detail-value">{hospital_db_info['status']}</div>
                          </div>
            """)
        else:
            print("""
                          <div class="detail-row">
                            <div class="detail-label" style="width:100%;text-align:center;color:#ef4444;">
                              <i class="fas fa-exclamation-triangle"></i> No hospital found in database with this name
                            </div>
                          </div>
            """)

        print(f"""
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="modal-footer d-flex justify-content-between align-items-center">
                    <div style="font-size:0.95rem;font-weight:600;">
                      Application Status: {badge}
                    </div>
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                      <i class="fas fa-times"></i> Close
                    </button>
                  </div>
                </div>
              </div>
            </div>
        """)

print("""
            </tbody>
          </table>
        </div><!-- overflow-x -->
      </div><!-- table-container -->
    </div><!-- content-area -->
  </div><!-- row -->
</div><!-- container-fluid -->

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>

function reindexVisible() {
  let idx = 1;
  document.querySelectorAll('#appTable tbody tr[data-status]').forEach(row => {
    const badge = row.querySelector('.row-index');
    if (badge) {
      if (row.style.display !== 'none') {
        badge.textContent = idx++;
      }
    }
  });
}

function showNoDataIfEmpty(labelText) {
  const tbody = document.querySelector('#appTable tbody');
  const visibleRows = Array.from(
    document.querySelectorAll('#appTable tbody tr[data-status]')
  ).filter(r => r.style.display !== 'none');
  const existing = document.getElementById('noDataRow');
  if (visibleRows.length === 0) {
    if (!existing) {
      const tr = document.createElement('tr');
      tr.id = 'noDataRow';
      tr.innerHTML = `<td colspan="11">
        <div class="no-data">
          <i class="fas fa-inbox"></i>
          <div class="message">${labelText}</div>
        </div></td>`;
      tbody.appendChild(tr);
    } else {
      existing.querySelector('.message').textContent = labelText;
    }
  } else {
    if (existing) existing.remove();
  }
}

function searchTable() {
  const filter = document.getElementById('searchInput').value.toLowerCase();
  const rows = document.querySelectorAll('#appTable tbody tr[data-search]');
  let count = 0;
  rows.forEach(row => {
    const match = row.getAttribute('data-search').indexOf(filter) > -1;
    row.style.display = match ? '' : 'none';
    if (match) count++;
  });
  document.getElementById('totalRecords').textContent = count;
  reindexVisible();
  showNoDataIfEmpty('No Records Found...!');
}

function filterTable(status, btn) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const rows = document.querySelectorAll('#appTable tbody tr[data-status]');
  let count = 0;
  const labelMap = {
    all:      'No Appointments Found...!',
    pending:  'No Pending Appointments Found...!',
    approved: 'No Approved Appointments Found...!',
    rescheduled: 'No Rescheduled Appointments Found...!'
  };
  rows.forEach(row => {
    const show = status === 'all' || row.dataset.status === status;
    row.style.display = show ? '' : 'none';
    if (show) count++;
  });
  document.getElementById('totalRecords').textContent = count;
  document.getElementById('searchInput').value = '';
  reindexVisible();
  showNoDataIfEmpty(labelMap[status] || 'No Records Found...!');
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('show');
  document.getElementById('sidebarOverlay').classList.toggle('show');
}

document.addEventListener('click', function(e) {
  const sb = document.getElementById('sidebar');
  const mt = document.querySelector('.mobile-menu-toggle');
  if (window.innerWidth < 992 &&
      mt && !sb.contains(e.target) &&
      !mt.contains(e.target) &&
      sb.classList.contains('show')) {
    sb.classList.remove('show');
    document.getElementById('sidebarOverlay').classList.remove('show');
  }
});

function logout() {
  if (confirm('Are you sure you want to logout?'))
    window.location.href = 'main.py';
}
</script>
</body>
</html>
""")

sub_cur.close()
con.close()