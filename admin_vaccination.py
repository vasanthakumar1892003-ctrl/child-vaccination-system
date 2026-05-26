#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgi
import cgitb
import sys
import os
import html
import csv
import io

# Enable CGI error display
cgitb.enable()

# UTF-8 output
sys.stdout.reconfigure(encoding="utf-8")

# CGI HEADER
print("Content-Type: text/html\r\n\r\n")

# Get form data
form = cgi.FieldStorage()

# ─── HELPER: safe HTML escape ─────────────────────────────────────────────────
def esc(val):
    return html.escape(str(val)) if val else ""

# ─── DB CONNECTION FACTORY ───────────────────────────────────────────────────
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="cvsdp"
    )

# ─── MESSAGES ─────────────────────────────────────────────────────────────────
success_msg = ""
error_msg   = ""

# ─── ADD ──────────────────────────────────────────────────────────────────────
if form.getvalue("submit_add"):
    vaccine_name = form.getvalue("vaccine_name", "").strip()
    age_group    = form.getvalue("age_group", "").strip()
    description  = form.getvalue("description", "").strip()

    if not vaccine_name or not age_group:
        error_msg = "Vaccine name and age group are required."
    elif len(vaccine_name) > 300:
        error_msg = "Vaccine name must be 300 characters or fewer."
    elif len(description) > 500:
        error_msg = "Description must be 500 characters or fewer."
    else:
        try:
            con = get_connection()
            cur = con.cursor()
            sql = """INSERT INTO vaccination_schedule
                     (vaccine_name, age_group, description)
                     VALUES (%s, %s, %s)"""
            cur.execute(sql, (vaccine_name, age_group, description))
            con.commit()
            con.close()
            success_msg = "Vaccination schedule added successfully!"
        except Exception as e:
            error_msg = f"Error: {esc(str(e))}"

# ─── EDIT ─────────────────────────────────────────────────────────────────────
if form.getvalue("submit_edit"):
    edit_id      = form.getvalue("edit_id", "")
    vaccine_name = form.getvalue("edit_vaccine_name", "").strip()
    age_group    = form.getvalue("edit_age_group", "").strip()
    description  = form.getvalue("edit_description", "").strip()

    if not edit_id.isdigit():
        error_msg = "Invalid record ID."
    elif len(vaccine_name) > 300:
        error_msg = "Vaccine name must be 300 characters or fewer."
    elif len(description) > 500:
        error_msg = "Description must be 500 characters or fewer."
    else:
        try:
            con = get_connection()
            cur = con.cursor()
            sql = """UPDATE vaccination_schedule
                     SET vaccine_name=%s, age_group=%s, description=%s
                     WHERE id=%s"""
            cur.execute(sql, (vaccine_name, age_group, description, int(edit_id)))
            con.commit()
            con.close()
            success_msg = "Vaccination schedule updated successfully!"
        except Exception as e:
            error_msg = f"Error: {esc(str(e))}"

# ─── INLINE DELETE ────────────────────────────────────────────────────────────
if form.getvalue("submit_delete"):
    del_id = form.getvalue("delete_id", "")
    if not del_id.isdigit():
        error_msg = "Invalid record ID."
    else:
        try:
            con = get_connection()
            cur = con.cursor()
            cur.execute("DELETE FROM vaccination_schedule WHERE id=%s", (int(del_id),))
            con.commit()
            con.close()
            success_msg = "Vaccination schedule deleted successfully!"
        except Exception as e:
            error_msg = f"Error: {esc(str(e))}"

# ─── CSV EXPORT ───────────────────────────────────────────────────────────────
if form.getvalue("export_csv"):
    try:
        con = get_connection()
        cur = con.cursor()
        cur.execute("SELECT id, vaccine_name, age_group, description FROM vaccination_schedule ORDER BY id")
        rows = cur.fetchall()
        con.close()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Vaccine Name", "Age Group", "Description"])
        writer.writerows(rows)
        csv_data = output.getvalue()

        import base64
        csv_b64 = base64.b64encode(csv_data.encode("utf-8")).decode()
        success_msg = f'__CSV_EXPORT__{csv_b64}'
    except Exception as e:
        error_msg = f"Export error: {esc(str(e))}"

# ─── FETCH RECORDS FOR DISPLAY ────────────────────────────────────────────────
schedules = []
try:
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT id, vaccine_name, age_group, description FROM vaccination_schedule ORDER BY id ASC")
    schedules = cur.fetchall()
    con.close()
except Exception as e:
    error_msg = f"Database connection failed: {esc(str(e))}"

# ─── CSV EXPORT TRIGGER ───────────────────────────────────────────────────────
csv_export_b64 = ""
if success_msg.startswith("__CSV_EXPORT__"):
    csv_export_b64 = success_msg.replace("__CSV_EXPORT__", "")
    success_msg = "CSV export ready — downloading now!"

print("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vaccination Schedule - Admin</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <style>
* { margin:0; padding:0; box-sizing:border-box; }
body {
  background: linear-gradient(135deg, #3b021f, #ec4899, #fdf2f8);
  min-height:100vh;
  font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;
  overflow-x:hidden;
}

/* ── NAVBAR ── */
.navbar {
  background: linear-gradient(135deg, #3b021f, #ec4899, #fdf2f8) !important;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  padding: 15px 20px;
}
.navbar .container-fluid {
  display: flex; flex-direction: row; align-items: center;
  flex-wrap: nowrap; position: relative;
}
.navbar-brand {
  font-weight: 600; color: white !important;
  letter-spacing: 2px; text-transform: uppercase;
}
.navbar-brand i {
  margin-right: 10px; color: #fda4af;
  font-size: 1.5rem; animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.1)} }

.btn-logout {
  background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
  border: none; padding: 8px 20px; border-radius: 25px; color: white;
  font-weight: 600; transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(238,9,121,0.4); font-size: 0.9rem;
  flex-shrink: 0; white-space: nowrap;
}
.btn-logout:hover { transform:translateY(-2px); box-shadow:0 6px 20px rgba(238,9,121,0.6); color:white; }

/* ── MOBILE MENU TOGGLE ── */
.mobile-menu-toggle {
  display: none; flex-shrink: 0; align-self: center;
  background: rgba(255,255,255,0.15); border: 1.5px solid rgba(255,255,255,0.35);
  color: white; padding: 6px 12px; border-radius: 8px; font-size: 1.2rem;
  cursor: pointer; transition: all 0.3s ease; backdrop-filter: blur(6px);
  line-height: 1; margin-right: 12px;
}
.mobile-menu-toggle:hover { background:rgba(255,255,255,0.28); border-color:rgba(255,255,255,0.6); color:white; }

/* ── SIDEBAR ── */
.sidebar {
  min-height: 100vh;
  background: linear-gradient(135deg, #3b021f, #ec4899);
  box-shadow: 4px 0 15px rgba(0,0,0,0.2); padding: 20px 0;
}
.sidebar-link {
  display: block; padding: 12px 15px; color: #ecf0f1; text-decoration: none;
  transition: all 0.3s ease; border-left: 4px solid transparent;
  font-weight: 500; margin: 5px 0; font-size: 0.95rem;
}
.sidebar-link:hover, .sidebar-link.active {
  background: linear-gradient(90deg, #ec4899, transparent);
  color: #fff; border-left: 4px solid #fdf2f8; padding-left: 20px;
}
.sidebar-link i { margin-right: 10px; width: 20px; text-align: center; }
.sidebar .dropdown-toggle {
  background: transparent; border: none; color: #ecf0f1; font-weight: 500;
  padding: 12px 15px; transition: all 0.3s ease;
  border-left: 4px solid transparent; font-size: 0.95rem;
  width: 100%; text-align: left;
}
.sidebar .dropdown-toggle:hover {
  background: linear-gradient(90deg, #ec4899, transparent 100%);
  color: #fff; border-left: 4px solid #fdf2f8;
}
.sidebar .dropdown-toggle i { margin-right: 10px; }
.sidebar .dropdown-menu {
  background: #3b021f; border: none;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3); margin-left: 10px; width: 90%;
}
.sidebar .dropdown-item {
  color: #ecf0f1; padding: 10px 15px; transition: all 0.3s ease;
  border-left: 3px solid transparent; font-size: 0.9rem;
}
.sidebar .dropdown-item:hover {
  background: linear-gradient(90deg, #ec4899, transparent 100%); color: white;
  border-left: 3px solid #ec4899; padding-left: 20px;
}

.sidebar-overlay {
  display: none; position: fixed; top: 0; left: 0;
  width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 998;
}
.sidebar-overlay.show { display: block; }

/* ── CONTENT ── */
.content-area { padding: 30px; }

/* ── CARDS ── */
.card {
  border: none; border-radius: 15px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.2); background: white; overflow: hidden;
}
.card-header {
  background: linear-gradient(135deg, #3b021f 0%, #ec4899 100%);
  color: white; padding: 20px; font-size: 1.3rem; font-weight: 600;
}

/* ── FORM ELEMENTS ── */
.form-label { font-weight: 600; color: #333; margin-bottom: 8px; }
.form-control, .form-select {
  border: 2px solid #e0e0e0; border-radius: 8px; padding: 10px 15px; transition: all 0.3s;
}
.form-control:focus, .form-select:focus {
  border-color: #ec4899; box-shadow: 0 0 0 0.2rem rgba(236,72,153,0.25);
}

/* ── BUTTONS ── */
.btn-primary {
  background: linear-gradient(135deg, #3b021f 0%, #ec4899 100%);
  border: none; padding: 12px 30px; border-radius: 25px; font-weight: 600;
  transition: all 0.3s; box-shadow: 0 4px 15px rgba(236,72,153,0.4);
}
.btn-primary:hover { transform:translateY(-2px); box-shadow:0 6px 20px rgba(236,72,153,0.6); }

.btn-danger {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border: none; padding: 8px 20px; border-radius: 20px; font-weight: 600; transition: all 0.3s;
}
.btn-danger:hover { transform:translateY(-2px); box-shadow:0 4px 15px rgba(245,87,108,0.5); }

.btn-warning {
  background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
  border: none; padding: 8px 20px; border-radius: 20px; font-weight: 600; transition: all 0.3s; color: #333;
}
.btn-warning:hover { transform:translateY(-2px); box-shadow:0 4px 15px rgba(253,160,133,0.5); color: #333; }

.btn-success {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  border: none; padding: 8px 20px; border-radius: 20px; font-weight: 600; transition: all 0.3s; color: #1a1a1a;
}
.btn-success:hover { transform:translateY(-2px); box-shadow:0 4px 15px rgba(67,233,123,0.5); color: #1a1a1a; }

/* ── SEARCH BOX ── */
.search-box { position: relative; margin-bottom: 20px; }
.search-box input {
  border: 2px solid #ec4899; border-radius: 25px; padding: 12px 20px 12px 45px;
}
.search-box input:focus {
  border-color: #3b021f; box-shadow: 0 0 0 0.2rem rgba(59,2,31,0.2); outline: none;
}
.search-box i { position: absolute; left: 18px; top: 50%; transform: translateY(-50%); color: #ec4899; font-size: 1.1rem; }

/* ── TABLE ── */
.table { margin-top: 20px; }
.table thead th {
  background: linear-gradient(135deg, #3b021f, #ec4899 40%);
  color: white; font-weight: 600; text-transform: uppercase;
  font-size: 0.85rem; letter-spacing: 0.5px;
  border: none; padding: 14px 10px; text-align:center;
}
.table thead th:first-child { border-radius: 8px 0 0 0; }
.table thead th:last-child  { border-radius: 0 8px 0 0; }
.table tbody tr { transition: all 0.3s; }
.table tbody tr:hover {
  background: linear-gradient(90deg, rgba(236,72,153,0.06), rgba(59,2,31,0.04));
}
.table tbody td { padding: 12px 10px; vertical-align: middle; border-bottom: 1px solid #f3e8ef; }

/* ── BADGES ── */
.badge-age  { background: linear-gradient(135deg, #ec4899, #be185d); color: white; padding: 5px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }

/* ── ALERTS ── */
.alert { border-radius: 10px; border: none; }

/* ── MODAL ── */
.modal-header { background: linear-gradient(135deg, #3b021f 0%, #ec4899 100%); color: white; }
.modal-header .btn-close { filter: brightness(0) invert(1); }

/* ── CHAR COUNT ── */
.char-count { font-size: 0.75rem; color: #888; text-align: right; }
.char-count.warn { color: #e67e22; }
.char-count.over { color: #e74c3c; font-weight: bold; }

/* ── RESPONSIVE ── */
@media (max-width: 991.98px) {
  .mobile-menu-toggle { display: flex; align-items: center; justify-content: center; }
  .sidebar {
    position: fixed; left: -100%; top: 0; width: 280px; height: 100vh;
    z-index: 999; transition: left 0.3s ease; overflow-y: auto;
  }
  .sidebar.show { left: 0; }
  .content-area { padding: 15px; margin-left: 0 !important; }
  .navbar-brand { position: absolute; left: 50%; transform: translateX(-50%); margin: 0 !important; font-size: 1rem; }
  .navbar-brand i { font-size: 1.3rem; }
}
@media (max-width: 767.98px) {
  .btn-logout { padding: 6px 15px; font-size: 0.8rem; }
  .filter-btn { padding: 6px 14px; font-size: 0.82rem; }
}
@media (max-width: 575.98px) {
  .navbar-brand { font-size: 0.85rem; }
  .navbar-brand i { font-size: 1.1rem; }
}
  </style>
</head>
<body>

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

    <!-- SIDEBAR -->
    <div class="col-lg-2 col-md-3 sidebar p-0" id="sidebar">
      <a href="admin_dashboard.py" class="sidebar-link"><i class="fas fa-home"></i> Home</a>
      <a href="admin_vaccination.py" class="sidebar-link active"><i class="fa-solid fa-circle-info"></i> Add Vaccination Info</a>
      <a href="admin_hospital_registration.py" class="sidebar-link">
        <i class="fas fa-hospital"></i> Hospital Registration
      </a>
      <a href="admin_parent_registration.py" class="sidebar-link">
        <i class="fas fa-user"></i> Parent Registration
      </a>
      <a href="admin_view_child.py" class="sidebar-link"><i class="fas fa-baby"></i> View Children</a>
      <a href="admin_view_appointment.py" class="sidebar-link"><i class="fas fa-calendar-check"></i> View Appointments</a>
      <a href="admin_vaccination_schedule.py" class="sidebar-link"><i class="fa-solid fa-syringe"></i> Vaccination Schedule</a>
      <a href="admin_appointment_reminder.py" class="sidebar-link">
        <i class="fas fa-bell"></i> Appointment Reminders
      </a>
      <a class="sidebar-link" href="admin_export_data.py"><i class="fas fa-file-export"></i> Export Data</a>
      <a href="admin_view_feedback.py" class="sidebar-link">
        <i class="fas fa-comment-dots"></i> Feedback
      </a>
    </div>

    <!-- MAIN CONTENT -->
    <div class="col-lg-10 col-md-9 content-area">
""")

# ─── ALERTS ──────────────────────────────────────────────────────────────────
if success_msg:
    print(f'<div class="alert alert-success alert-dismissible fade show" role="alert">'
          f'<i class="fas fa-check-circle"></i> {success_msg}'
          f'<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>')
if error_msg:
    print(f'<div class="alert alert-danger alert-dismissible fade show" role="alert">'
          f'<i class="fas fa-exclamation-circle"></i> {error_msg}'
          f'<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>')

print("""
<!-- ADD FORM -->
<div class="card mb-4">
  <div class="card-header"><i class="fa-solid fa-syringe"></i> Add Vaccination Schedule</div>
  <div class="card-body">
    <form method="POST" action="admin_vaccination.py">
      <div class="row">
        <div class="col-md-6 mb-3">
          <label for="vaccine_name" class="form-label">Vaccine Name * <small class="text-muted">(max 300 chars)</small></label>
          <input type="text" class="form-control" id="vaccine_name" name="vaccine_name" maxlength="300"
                 oninput="updateCharCount(this,'vc_count',300)" required>
          <div class="char-count" id="vc_count">0 / 300</div>
        </div>
        <div class="col-md-6 mb-3">
          <label for="age_group" class="form-label">Age Group *</label>
          <select class="form-select" id="age_group" name="age_group" required>
            <option value="">Select Age Group</option>
            <option>At Birth</option><option>6 Weeks</option><option>10 Weeks</option>
            <option>14 Weeks</option><option>6 Months</option><option>9 Months</option>
            <option>12 Months</option><option>15 Months</option><option>18 Months</option>
            <option>2 Years</option><option>4-6 Years</option><option>10 Years</option>
          </select>
        </div>
        <div class="col-md-12 mb-3">
          <label for="description" class="form-label">Description <small class="text-muted">(max 500 chars)</small></label>
          <textarea class="form-control" id="description" name="description" rows="3" maxlength="500"
                    oninput="updateCharCount(this,'desc_count',500)"
                    placeholder="Enter vaccine description or notes..."></textarea>
          <div class="char-count" id="desc_count">0 / 500</div>
        </div>
      </div>
      <div class="text-end">
        <button type="submit" name="submit_add" value="1" class="btn btn-primary">
          <i class="fas fa-plus-circle"></i> Add Vaccination Schedule
        </button>
      </div>
    </form>
  </div>
</div>

<!-- TABLE CARD -->
<div class="card">
  <div class="card-header d-flex justify-content-between align-items-center flex-wrap gap-2">
    <span><i class="fa-solid fa-list"></i> Existing Vaccination Schedules</span>
    <div class="d-flex align-items-center gap-2">
      <span class="badge bg-light text-dark" id="totalCount">Total: 0</span>
      <form method="POST" action="admin_vaccination.py" style="margin:0;">
        <button type="submit" name="export_csv" value="1" class="btn btn-success btn-sm">
          <i class="fas fa-file-csv"></i> Export CSV
        </button>
      </form>
    </div>
  </div>
  <div class="card-body">

    <!-- SEARCH -->
    <div class="search-box">
      <i class="fas fa-search"></i>
      <input type="text" class="form-control" id="searchInput"
             placeholder="Search by vaccine name, age group, or description..."
             onkeyup="searchTable()">
    </div>

    <div class="table-responsive">
      <table class="table table-hover" id="vaccineTable">
        <thead>
          <tr>
            <th style="width:8%">ID</th>
            <th style="width:25%">Vaccine Name</th>
            <th style="width:15%">Age Group</th>
            <th style="width:35%">Description</th>
            <th style="width:17%">Actions</th>
          </tr>
        </thead>
        <tbody>
""")

# ─── TABLE ROWS ───────────────────────────────────────────────────────────────
if schedules:
    for s in schedules:
        sid          = s[0]
        vname        = esc(s[1])
        age          = esc(s[2])
        desc         = esc(s[3]) if s[3] else ""
        desc_display = desc if desc else "N/A"

        print(f"""
          <tr data-age="{age}"
              data-id="{sid}"
              data-vname="{vname}"
              data-age-val="{age}"
              data-desc="{desc}">
            <td style="text-align:center;"><strong>{sid}</strong></td>
            <td><strong>{vname}</strong></td>
            <td style="text-align:center;"><span class="badge-age">{age}</span></td>
            <td>{desc_display}</td>
            <td style="text-align:center;">
              <button class="btn btn-warning btn-sm me-1`" onclick="openEditModal(this)" title="Edit">
                <i class="fas fa-edit"></i>
              </button>
              <button class="btn btn-danger btn-sm" onclick="confirmDelete({sid},'{vname}')" title="Delete">
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
        """)
else:
    print("""
          <tr id="noDataRow">
            <td colspan="5" class="text-center text-muted py-4">
              <i class="fas fa-info-circle fa-2x mb-2 d-block"></i>
              No vaccination schedules added yet
            </td>
          </tr>
    """)

print("""
        </tbody>
      </table>
    </div>
  </div>
</div>

    </div><!-- /content-area -->
  </div><!-- /row -->
</div><!-- /container -->

<!-- EDIT MODAL -->
<div class="modal fade" id="editModal" tabindex="-1" aria-labelledby="editModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="editModalLabel"><i class="fas fa-edit"></i> Edit Vaccination Schedule</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <form method="POST" action="admin_vaccination.py">
        <div class="modal-body">
          <input type="hidden" name="edit_id" id="edit_id">
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">Vaccine Name * <small class="text-muted">(max 300 chars)</small></label>
              <input type="text" class="form-control" id="edit_vaccine_name" name="edit_vaccine_name"
                     maxlength="300" oninput="updateCharCount(this,'edit_vc_count',300)" required>
              <div class="char-count" id="edit_vc_count">0 / 300</div>
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Age Group *</label>
              <select class="form-select" id="edit_age_group" name="edit_age_group" required>
                <option value="">Select Age Group</option>
                <option>At Birth</option><option>6 Weeks</option><option>10 Weeks</option>
                <option>14 Weeks</option><option>6 Months</option><option>9 Months</option>
                <option>12 Months</option><option>15 Months</option><option>18 Months</option>
                <option>2 Years</option><option>4-6 Years</option><option>10 Years</option>
              </select>
            </div>
            <div class="col-md-12 mb-3">
              <label class="form-label">Description <small class="text-muted">(max 500 chars)</small></label>
              <textarea class="form-control" id="edit_description" name="edit_description"
                        rows="3" maxlength="500"
                        oninput="updateCharCount(this,'edit_desc_count',500)"></textarea>
              <div class="char-count" id="edit_desc_count">0 / 500</div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            <i class="fas fa-times"></i> Cancel
          </button>
          <button type="submit" name="submit_edit" value="1" class="btn btn-primary">
            <i class="fas fa-save"></i> Update Schedule
          </button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- INLINE DELETE FORM (hidden, submitted via JS) -->
<form method="POST" action="admin_vaccination.py" id="deleteForm" style="display:none;">
  <input type="hidden" name="delete_id" id="delete_id_field">
  <input type="hidden" name="submit_delete" value="1">
</form>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
window.onload = function() { updateTotalCount(); };

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('show');
  document.getElementById('sidebarOverlay').classList.toggle('show');
}

function logout() {
  if (confirm('Are you sure you want to logout?')) window.location.href = 'main.py';
}

function openEditModal(btn) {
  const row = btn.closest('tr');
  document.getElementById('edit_id').value           = row.dataset.id;
  document.getElementById('edit_vaccine_name').value = row.dataset.vname;
  document.getElementById('edit_age_group').value    = row.dataset.ageVal;
  document.getElementById('edit_description').value  = row.dataset.desc;
  updateCharCount(document.getElementById('edit_vaccine_name'), 'edit_vc_count', 300);
  updateCharCount(document.getElementById('edit_description'),  'edit_desc_count', 500);
  new bootstrap.Modal(document.getElementById('editModal')).show();
}

function confirmDelete(id, name) {
  if (confirm('Delete vaccination schedule for "' + name + '"?\\nThis action cannot be undone.')) {
    document.getElementById('delete_id_field').value = id;
    document.getElementById('deleteForm').submit();
  }
}

function updateCharCount(el, counterId, max) {
  const len = el.value.length;
  const el2 = document.getElementById(counterId);
  el2.textContent = len + ' / ' + max;
  el2.className = 'char-count' + (len >= max ? ' over' : len >= max * 0.85 ? ' warn' : '');
}

function searchTable() {
  const filter = document.getElementById('searchInput').value.toLowerCase();
  const rows   = document.querySelectorAll('#vaccineTable tbody tr:not(#noDataRow)');
  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(filter) ? '' : 'none';
  });
  updateTotalCount();
}

function filterByAge(age, btn) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('searchInput').value = '';
  const rows = document.querySelectorAll('#vaccineTable tbody tr:not(#noDataRow)');
  rows.forEach(row => {
    row.style.display = (age === 'all' || row.dataset.age === age) ? '' : 'none';
  });
  updateTotalCount();
}

function updateTotalCount() {
  const visible = [...document.querySelectorAll('#vaccineTable tbody tr:not(#noDataRow)')]
                  .filter(r => r.style.display !== 'none').length;
  document.getElementById('totalCount').textContent = 'Total: ' + visible;
}

document.addEventListener('click', function(e) {
  const sb = document.getElementById('sidebar');
  const mt = document.querySelector('.mobile-menu-toggle');
  if (window.innerWidth < 992 && sb && mt &&
      !sb.contains(e.target) && !mt.contains(e.target) &&
      sb.classList.contains('show')) {
    sb.classList.remove('show');
    document.getElementById('sidebarOverlay').classList.remove('show');
  }
});
</script>
""")

# ─── CSV DOWNLOAD VIA DATA URI ────────────────────────────────────────────────
if csv_export_b64:
    print(f"""
<script>
(function() {{
  const b64 = "{csv_export_b64}";
  const csv = atob(b64);
  const blob = new Blob([csv], {{type:'text/csv;charset=utf-8;'}});
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href     = url;
  a.download = 'vaccination_schedule.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}})();
</script>
""")

print("</body>\n</html>")