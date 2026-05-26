#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgi
import cgitb
import sys

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")

form = cgi.FieldStorage()

_hid = form.getvalue("hospital_id") or ""
hospital_id = (_hid[0] if isinstance(_hid, list) else _hid).strip()

filter_date = (form.getvalue("filter_date") or "").strip()

try:
    con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
    cur = con.cursor()
except Exception as e:
    print("Content-Type: text/html\r\n\r\n")
    print(f"<h2 style='color:red;'>Database Connection Failed!</h2><pre>{e}</pre>")
    sys.exit()

try:
    cur.execute("SHOW COLUMNS FROM hospital_appointment LIKE 'status'")
    if not cur.fetchone():
        cur.execute("ALTER TABLE hospital_appointment ADD COLUMN status VARCHAR(20) DEFAULT 'pending'")
        con.commit()
except Exception:
    pass

print("Content-Type: text/html\r\n\r\n")

# FETCH HOSPITAL NAME
hospital_name_filter = ""
try:
    cur.execute("DESCRIBE hospital")
    cols     = [row[0] for row in cur.fetchall()]
    name_col = next((c for c in cols if c in ("hospital_name","h_name","name")), None)
    id_col   = next((c for c in cols if c in ("hospital_id","id")), None)
    if name_col and id_col and hospital_id:
        cur.execute(f"SELECT {name_col} FROM hospital WHERE {id_col} = %s", (hospital_id,))
        row = cur.fetchone()
        if row and row[0]:
            hospital_name_filter = row[0]
except Exception:
    pass

# FETCH APPOINTMENTS
rows = []
try:
    base_sql = """
        SELECT id, p_name, p_gender, email_id, mobile,
               c_name, c_gender, c_dob, age_group,
               vaccination_name, appointment_date,
               COALESCE(status,'pending') AS status
        FROM hospital_appointment
    """
    if hospital_name_filter and filter_date:
        cur.execute(base_sql + " WHERE hospital_name=%s AND appointment_date=%s ORDER BY id DESC",
                    (hospital_name_filter, filter_date))
    elif hospital_name_filter:
        cur.execute(base_sql + " WHERE hospital_name=%s ORDER BY id DESC", (hospital_name_filter,))
    else:
        cur.execute(base_sql + " ORDER BY id DESC")
    rows = cur.fetchall()
except Exception:
    rows = []

total_count     = len(rows)
pending_count   = sum(1 for r in rows if str(r[11]).strip().lower() == "pending")
completed_count = sum(1 for r in rows if str(r[11]).strip().lower() == "completed")
cancelled_count = sum(1 for r in rows if str(r[11]).strip().lower() == "cancelled")

def safe(row, idx):
    return str(row[idx]).strip() if len(row) > idx and row[idx] not in (None,"") else "N/A"

# ── Status badge helper matching screenshot exactly ────────────────────────
# Completed : mint-green border, white bg, green filled check icon
# Pending   : yellow border, pale yellow bg, orange hourglass icon
# Cancelled : red border, pale red bg, red times icon
def status_badge(status):
    cfg = {
        "completed": {
            "border": "#4ade80",
            "bg":     "#f0fdf4",
            "color":  "#16a34a",
            "icon":   "fa-check-circle",
            "label":  "COMPLETED"
        },
        "pending": {
            "border": "#fbbf24",
            "bg":     "#fffbeb",
            "color":  "#d97706",
            "icon":   "fa-hourglass-half",
            "label":  "PENDING"
        },
        "cancelled": {
            "border": "#f87171",
            "bg":     "#fff1f2",
            "color":  "#dc2626",
            "icon":   "fa-times-circle",
            "label":  "CANCELLED"
        },
    }.get(status, {
        "border": "#cbd5e1", "bg": "#f8fafc",
        "color": "#64748b", "icon": "fa-circle", "label": status.upper()
    })
    return (
        f'<span style="'
        f'display:inline-flex;align-items:center;gap:6px;'
        f'padding:5px 14px 5px 10px;'
        f'border-radius:50px;'
        f'border:2px solid {cfg["border"]};'
        f'background:{cfg["bg"]};'
        f'color:{cfg["color"]};'
        f'font-size:0.75rem;font-weight:800;letter-spacing:0.8px;'
        f'white-space:nowrap;">'
        f'<i class="fas {cfg["icon"]}" style="font-size:0.9rem;"></i>'
        f'{cfg["label"]}'
        f'</span>'
    )

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>View Appointments - CVS</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{
  background:linear-gradient(135deg,#083344,#22d3ee,#cffafe);
  min-height:100vh;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;overflow-x:hidden;
}}
/* NAVBAR */
.navbar{{box-shadow:0 4px 20px rgba(0,0,0,0.4);padding:15px 20px;
  background:linear-gradient(135deg,#083344,#22d3ee,#cffafe)!important;}}
.navbar .container-fluid{{display:flex;flex-direction:row;align-items:center;flex-wrap:nowrap;}}
.navbar-brand{{font-weight:600;color:white!important;letter-spacing:2px;text-transform:uppercase;}}
.navbar-brand i{{margin-right:10px;color:#e9d5ff;font-size:1.5rem;animation:bounce 2s infinite;}}
@keyframes bounce{{0%,100%{{transform:translateY(0);}}50%{{transform:translateY(-5px);}}}}
.mobile-menu-toggle{{
  display:none;flex-shrink:0;align-self:center;
  background:rgba(255,255,255,0.15);border:1.5px solid rgba(255,255,255,0.35);
  color:white;padding:6px 12px;border-radius:8px;font-size:1.2rem;
  cursor:pointer;transition:all 0.3s ease;backdrop-filter:blur(6px);
  line-height:1;margin-right:12px;
}}
.mobile-menu-toggle:hover{{background:rgba(255,255,255,0.28);border-color:rgba(255,255,255,0.6);color:white;}}
.btn-logout{{
  flex-shrink:0;background:linear-gradient(135deg,#ee0979 0%,#ff6a00 100%);
  border:none;padding:8px 20px;border-radius:25px;color:white;font-weight:600;
  transition:all 0.3s ease;box-shadow:0 4px 15px rgba(238,9,121,0.4);
  font-size:0.9rem;white-space:nowrap;
}}
.btn-logout:hover{{transform:translateY(-2px);color:white;}}
/* SIDEBAR */
.sidebar{{min-height:100vh;background:linear-gradient(135deg,#083344,#22d3ee);
  box-shadow:4px 0 20px rgba(0,0,0,0.3);padding:20px 0;}}
.sidebar-link{{display:block;padding:14px 18px;color:#e9d5ff;text-decoration:none;
  transition:all 0.3s ease;border-left:4px solid transparent;font-weight:500;margin:6px 0;}}
.sidebar-link:hover,.sidebar-link.active{{
  background:linear-gradient(90deg,#22d3ee,transparent 100%);
  color:#fff;border-left:4px solid #cffafe;padding-left:24px;
}}
.sidebar-link i{{margin-right:12px;width:22px;text-align:center;}}
.sidebar-overlay{{display:none;position:fixed;top:0;left:0;
  width:100%;height:100%;background:rgba(0,0,0,0.6);z-index:998;}}
.sidebar-overlay.show{{display:block;}}
/* CONTENT */
.content-area{{padding:25px;min-height:100vh;}}
.page-header{{background:white;padding:22px 25px;border-radius:18px;margin-bottom:20px;
  box-shadow:0 8px 25px rgba(0,0,0,0.12);border-left:6px solid #22d3ee;}}
.page-header h4{{margin:0;color:#0f172a;font-weight:700;
  font-size:1.5rem;text-transform:uppercase;letter-spacing:1px;}}
.page-header h4 i{{margin-right:12px;color:#083344;}}
/* COUNT CARDS */
.count-card{{border-radius:16px;padding:20px 24px;box-shadow:0 6px 20px rgba(0,0,0,0.10);
  display:flex;align-items:center;gap:16px;margin-bottom:20px;}}
.count-card .card-icon{{font-size:1.6rem;width:52px;height:52px;border-radius:12px;
  display:flex;align-items:center;justify-content:center;flex-shrink:0;}}
.count-card .card-num{{font-size:2rem;font-weight:800;line-height:1;}}
.count-card .card-label{{font-size:0.78rem;font-weight:700;text-transform:uppercase;
  letter-spacing:1px;opacity:0.8;margin-top:2px;}}
.card-total{{background:#ede9fe;color:#4c1d95;}}
.card-total .card-icon{{background:#c4b5fd;color:#4c1d95;}}
.card-pending{{background:#fef9c3;color:#92400e;}}
.card-pending .card-icon{{background:#fde68a;color:#b45309;}}
.card-completed{{background:#d1fae5;color:#065f46;}}
.card-completed .card-icon{{background:#6ee7b7;color:#065f46;}}
.card-cancelled{{background:#fee2e2;color:#991b1b;}}
.card-cancelled .card-icon{{background:#fca5a5;color:#991b1b;}}
/* FILTER TABS */
.filter-tabs{{display:flex;flex-wrap:wrap;gap:10px;background:white;border-radius:16px;
  padding:18px 22px;box-shadow:0 6px 20px rgba(0,0,0,0.10);margin-bottom:20px;align-items:center;}}
.tab-btn{{border:2px solid #7c3aed;border-radius:25px;padding:8px 20px;font-size:0.85rem;
  font-weight:700;cursor:pointer;background:white;color:#7c3aed;
  transition:all 0.25s ease;display:flex;align-items:center;gap:7px;}}
.tab-btn:hover{{background:#cffafe;}}
.tab-btn.active{{background:linear-gradient(135deg,#083344,#22d3ee);color:white;
  border-color:#cffafe;box-shadow:0 4px 14px rgba(124,58,237,0.45);}}
.tab-btn i{{font-size:0.85rem;}}
.showing-label{{margin-left:auto;font-size:0.82rem;font-weight:600;color:#7c3aed;}}
#emptyMsg{{display:none;text-align:center;padding:60px 20px;}}
#emptyMsg .empty-icon{{font-size:4.5rem;color:#cbd5e1;display:block;margin-bottom:16px;}}
#emptyMsg p{{font-size:1.1rem;color:#94a3b8;font-weight:600;}}
/* FILTER CARD */
.filter-card{{background:white;border-radius:16px;padding:22px 25px;
  box-shadow:0 6px 20px rgba(0,0,0,0.10);margin-bottom:20px;}}
.filter-label{{font-weight:600;color:#374151;font-size:0.9rem;margin-bottom:10px;display:block;}}
.filter-label i{{margin-right:6px;color:#7c3aed;}}
.filter-input{{border:2px solid #e5e7eb;border-radius:10px;padding:11px 14px;
  font-size:0.95rem;width:100%;transition:border-color 0.3s ease;}}
.filter-input:focus{{border-color:#7c3aed;outline:none;box-shadow:0 0 0 3px rgba(124,58,237,0.15);}}
.btn-filter{{background:linear-gradient(135deg,#083344,#22d3ee 90%);border:none;
  border-radius:10px;padding:11px 0;color:white;font-weight:700;font-size:0.95rem;width:100%;
  transition:all 0.3s ease;box-shadow:0 4px 15px rgba(124,58,237,0.4);cursor:pointer;}}
.btn-filter:hover{{transform:translateY(-2px);}}
.btn-clear{{background:linear-gradient(135deg,#6b7280 0%,#4b5563 100%);border:none;
  border-radius:10px;padding:11px 0;color:white;font-weight:700;font-size:0.95rem;
  width:100%;transition:all 0.3s ease;cursor:pointer;}}
.btn-clear:hover{{transform:translateY(-2px);}}
/* TABLE */
.table-card{{background:white;border-radius:18px;padding:25px;
  box-shadow:0 10px 40px rgba(0,0,0,0.12);overflow-x:auto;}}
.appt-table{{width:100%;border-collapse:collapse;}}
.appt-table thead th{{
  background:linear-gradient(135deg,#083344,#22d3ee 80%);
  color:white;padding:15px 14px;font-size:0.78rem;
  text-transform:uppercase;letter-spacing:0.8px;white-space:nowrap;border:none;
}}
.appt-table thead th:first-child{{border-radius:10px 0 0 10px;}}
.appt-table thead th:last-child{{border-radius:0 10px 10px 0;}}
.appt-table tbody tr{{transition:background 0.2s;}}
.appt-table tbody tr:hover{{background:#f8f5ff;}}
.appt-table tbody td{{padding:14px 14px;font-size:0.88rem;color:#374151;
  vertical-align:middle;white-space:nowrap;border-bottom:1px solid #f0f0f0;}}
.row-num{{font-weight:700;color:#6b7280;}}
.ic-orange{{color:#f97316;margin-right:5px;}}
.no-data{{text-align:center;padding:50px 20px;color:#94a3b8;}}
.no-data i{{font-size:4rem;display:block;margin-bottom:15px;color:#cbd5e1;}}
.no-data p{{font-size:1.1rem;}}
/* VIEW BUTTON */
.btn-view-appt{{
  background:linear-gradient(135deg,#0077b6,#00b4d8);
  border:none;border-radius:8px;padding:6px 14px;
  color:white;font-weight:600;font-size:0.75rem;
  cursor:pointer;transition:all 0.3s;
  box-shadow:0 3px 10px rgba(0,119,182,0.3);white-space:nowrap;
}}
.btn-view-appt:hover{{transform:translateY(-2px);box-shadow:0 5px 15px rgba(0,119,182,0.45);}}
.btn-view-appt i{{margin-right:4px;}}
/* MODAL */
.modal-overlay{{
  display:none;position:fixed;top:0;left:0;
  width:100%;height:100%;background:rgba(0,0,0,0.65);
  z-index:2000;backdrop-filter:blur(4px);
  align-items:center;justify-content:center;
}}
.modal-overlay.show{{display:flex;}}
.appt-modal{{
  background:white;border-radius:20px;
  width:92%;max-width:680px;max-height:90vh;overflow-y:auto;
  box-shadow:0 20px 60px rgba(0,0,0,0.3);
  animation:slideUp 0.3s ease;
}}
@keyframes slideUp{{
  from{{transform:translateY(40px);opacity:0;}}
  to{{transform:translateY(0);opacity:1;}}
}}
.appt-modal-header{{
  background:linear-gradient(135deg,#083344,#22d3ee);
  padding:20px 26px;border-radius:20px 20px 0 0;
  display:flex;align-items:center;justify-content:space-between;
  position:sticky;top:0;z-index:10;
}}
.appt-modal-header h3{{
  color:white;font-size:1.1rem;font-weight:800;
  text-transform:uppercase;letter-spacing:1px;margin:0;
  display:flex;align-items:center;gap:10px;
}}
.btn-modal-close{{
  background:rgba(255,255,255,0.2);border:none;color:white;
  width:34px;height:34px;border-radius:50%;font-size:1.1rem;
  cursor:pointer;display:flex;align-items:center;justify-content:center;
  transition:background 0.2s;flex-shrink:0;
}}
.btn-modal-close:hover{{background:rgba(255,255,255,0.35);}}
.appt-modal-body{{padding:24px 26px;}}
.modal-section-title{{
  font-size:0.7rem;font-weight:800;text-transform:uppercase;
  letter-spacing:1px;color:#0891b2;margin:16px 0 10px;
  display:flex;align-items:center;gap:7px;
  border-bottom:1.5px solid #cffafe;padding-bottom:6px;
}}
.modal-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px 18px;}}
.modal-field{{background:#f0fdff;border-radius:10px;padding:10px 14px;border:1.5px solid #cffafe;}}
.modal-field-label{{font-size:0.67rem;font-weight:700;text-transform:uppercase;
  letter-spacing:0.5px;color:#94a3b8;margin-bottom:3px;}}
.modal-field-value{{font-size:0.88rem;font-weight:600;color:#1e293b;word-break:break-word;}}
.modal-field-value.accent{{color:#0e7490;}}
/* RESPONSIVE */
@media(max-width:991.98px){{
  .mobile-menu-toggle{{display:flex;align-items:center;justify-content:center;}}
  .sidebar{{position:fixed;left:-100%;top:0;width:280px;height:100vh;
    z-index:999;transition:left 0.3s ease;overflow-y:auto;}}
  .sidebar.show{{left:0;}}
  .content-area{{padding:15px;margin-left:0!important;}}
  .navbar-brand{{font-size:1rem;letter-spacing:1px;}}
  .navbar-brand i{{font-size:1.3rem;}}
}}
@media(max-width:767.98px){{
  .appt-modal{{width:96%;}}
  .appt-modal-body{{padding:16px;}}
  .modal-grid{{grid-template-columns:1fr;}}
}}
@media(max-width:575.98px){{
  .navbar-brand{{font-size:0.85rem;letter-spacing:0.5px;}}
  .navbar-brand i{{font-size:1.1rem;margin-right:6px;}}
  .btn-logout{{padding:6px 14px;font-size:0.8rem;}}
}}
@media(max-width:400px){{.navbar-brand{{font-size:0.75rem;}}}}
</style>
</head>
<body>

<!-- NAVBAR -->
<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container-fluid">
    <button class="mobile-menu-toggle" onclick="toggleSidebar()">
      <i class="fas fa-bars"></i>
    </button>
    <span class="navbar-brand ms-2">
      <i class="fa-solid fa-hospital"></i> CVS - Hospital
    </span>
    <button class="btn btn-logout" onclick="logout()">
      <i class="fas fa-sign-out-alt"></i> Logout
    </button>
  </div>
</nav>

<div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

<div class="container-fluid">
  <div class="row">

    <!-- SIDEBAR -->
    <div class="col-lg-2 col-md-3 sidebar p-0" id="sidebar">
      <a href="hospital_dashboard.py?hospital_id={hospital_id}" class="sidebar-link">
        <i class="fas fa-home"></i> Home
      </a>
      <a href="hospital_vaccination.py?hospital_id={hospital_id}" class="sidebar-link">
        <i class="fa-solid fa-circle-info"></i> Vaccination Info
      </a>
      <a href="hospital_view_application.py?hospital_id={hospital_id}" class="sidebar-link">
        <i class="fa-solid fa-user-pen"></i> Parent Application
      </a>
      <a href="hospital_view_appointment.py?hospital_id={hospital_id}" class="sidebar-link active">
        <i class="fas fa-calendar-alt"></i> View Appointments
      </a>
      <a href="hospital_profile.py?hospital_id={hospital_id}" class="sidebar-link">
        <i class="fas fa-user-circle"></i> My Profile
      </a>
      <a href="hospital_feedback.py?hospital_id={hospital_id}" class="sidebar-link">
        <i class="fas fa-comment-dots"></i> Feedback
      </a>
      <a href="hospital_chat.py?hospital_id={hospital_id}" class="sidebar-link">
        <i class="fas fa-notes-medical"></i> Chats
      </a>
      <a href="hospital_help.py?hospital_id={hospital_id}" class="sidebar-link">
        <i class="fas fa-circle-question"></i> Help & Support
      </a>
    </div>

    <!-- CONTENT -->
    <div class="col-lg-10 col-md-9 col-12 content-area">

      <div class="page-header">
        <h4><i class="fas fa-list-alt"></i> View All Appointments</h4>
      </div>

      <!-- COUNT CARDS -->
      <div class="row g-3 mb-2">
        <div class="col-6 col-lg-3">
          <div class="count-card card-total">
            <div class="card-icon"><i class="fas fa-clipboard-list"></i></div>
            <div><div class="card-num">{total_count}</div><div class="card-label">Total</div></div>
          </div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="count-card card-pending">
            <div class="card-icon"><i class="fas fa-hourglass-half"></i></div>
            <div><div class="card-num">{pending_count}</div><div class="card-label">Pending</div></div>
          </div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="count-card card-completed">
            <div class="card-icon"><i class="fas fa-check-circle"></i></div>
            <div><div class="card-num">{completed_count}</div><div class="card-label">Completed</div></div>
          </div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="count-card card-cancelled">
            <div class="card-icon"><i class="fas fa-times-circle"></i></div>
            <div><div class="card-num">{cancelled_count}</div><div class="card-label">Cancelled</div></div>
          </div>
        </div>
      </div>

      <!-- STATUS FILTER TABS -->
      <div class="filter-tabs">
        <button class="tab-btn active" id="tab-all" onclick="filterTab('all')">
          <i class="fas fa-list"></i> All
        </button>
        <button class="tab-btn" id="tab-pending" onclick="filterTab('pending')">
          <i class="fas fa-hourglass-half"></i> Pending
        </button>
        <button class="tab-btn" id="tab-completed" onclick="filterTab('completed')">
          <i class="fas fa-check-circle"></i> Completed
        </button>
        <button class="tab-btn" id="tab-cancelled" onclick="filterTab('cancelled')">
          <i class="fas fa-times-circle"></i> Cancelled
        </button>
        <span class="showing-label" id="showingLabel">Showing: {total_count} of {total_count}</span>
      </div>

      <!-- DATE FILTER -->
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

      <!-- TABLE -->
      <div class="table-card">
        <table class="appt-table" id="apptTable">
          <thead>
            <tr>
              <th><i class="fas fa-hashtag"></i></th>
              <th><i class="fas fa-user"></i> Parent Name</th>
              <th><i class="fas fa-venus-mars"></i> P. Gender</th>
              <th><i class="fas fa-envelope"></i> Email</th>
              <th><i class="fas fa-phone"></i> Mobile</th>
              <th><i class="fas fa-child"></i> Child Name</th>
              <th><i class="fas fa-calendar-alt"></i> Date</th>
              <th><i class="fas fa-info-circle"></i> Status</th>
              <th><i class="fas fa-eye"></i> Action</th>
            </tr>
          </thead>
          <tbody id="apptBody">
""")

if not rows:
    print("""
        <tr>
          <td colspan="9" class="no-data">
            <i class="fas fa-inbox"></i>
            <p>No appointments found for this hospital.</p>
          </td>
        </tr>
    """)
else:
    for idx, i in enumerate(rows, start=1):
        appt_id_val      = safe(i, 0)
        p_name           = safe(i, 1)
        p_gender         = safe(i, 2)
        email_id         = safe(i, 3)
        mobile           = safe(i, 4)
        c_name           = safe(i, 5)
        c_gender         = safe(i, 6)
        c_dob            = safe(i, 7)
        age_group        = safe(i, 8)
        vaccination_name = safe(i, 9)
        appointment_date = safe(i, 10)
        raw_status       = safe(i, 11)
        status           = raw_status.lower() if raw_status != "N/A" else "pending"
        modal_id         = f"appt_{idx}"

        print(f"""
            <tr class="appt-row" data-status="{status}">
              <td class="row-num">{idx}</td>
              <td><strong>{p_name}</strong></td>
              <td>{p_gender}</td>
              <td>{email_id}</td>
              <td>{mobile}</td>
              <td><strong>{c_name}</strong></td>
              <td><i class="fas fa-calendar ic-orange"></i><strong>{appointment_date}</strong></td>
              <td>{status_badge(status)}</td>
              <td>
                <button class="btn-view-appt" onclick="openModal('{modal_id}')">
                  <i class="fas fa-eye"></i> View
                </button>
              </td>
            </tr>
        """)

print(f"""
          </tbody>
        </table>
        <div id="emptyMsg">
          <i class="fas fa-inbox empty-icon"></i>
          <p id="emptyMsgText">No Appointments Found...!</p>
        </div>
      </div><!-- /table-card -->
    </div><!-- /content-area -->
  </div><!-- /row -->
</div><!-- /container-fluid -->
""")

# ── MODALS ─────────────────────────────────────────────────────────────────
MODAL_STATUS_CFG = {
    "completed": {"border":"#4ade80","bg":"#f0fdf4","color":"#16a34a","icon":"fa-check-circle"},
    "pending":   {"border":"#fbbf24","bg":"#fffbeb","color":"#d97706","icon":"fa-hourglass-half"},
    "cancelled": {"border":"#f87171","bg":"#fff1f2","color":"#dc2626","icon":"fa-times-circle"},
}

if rows:
    for idx, i in enumerate(rows, start=1):
        modal_id         = f"appt_{idx}"
        appt_id_val      = safe(i, 0)
        p_name           = safe(i, 1)
        p_gender         = safe(i, 2)
        email_id         = safe(i, 3)
        mobile           = safe(i, 4)
        c_name           = safe(i, 5)
        c_gender         = safe(i, 6)
        c_dob            = safe(i, 7)
        age_group        = safe(i, 8)
        vaccination_name = safe(i, 9)
        appointment_date = safe(i, 10)
        raw_status       = safe(i, 11)
        status           = raw_status.lower() if raw_status != "N/A" else "pending"
        sc               = MODAL_STATUS_CFG.get(status, {"border":"#cbd5e1","bg":"#f8fafc","color":"#64748b","icon":"fa-circle"})

        print(f"""
<div class="modal-overlay" id="{modal_id}">
  <div class="appt-modal">
    <div class="appt-modal-header">
      <h3><i class="fas fa-calendar-check"></i> Appointment Details</h3>
      <button class="btn-modal-close" onclick="closeModal('{modal_id}')">
        <i class="fas fa-times"></i>
      </button>
    </div>
    <div class="appt-modal-body">

      <div style="text-align:center;margin-bottom:18px;">
        <span style="display:inline-flex;align-items:center;gap:7px;
          padding:7px 22px 7px 16px;border-radius:50px;
          border:2px solid {sc['border']};background:{sc['bg']};color:{sc['color']};
          font-size:0.82rem;font-weight:800;letter-spacing:0.8px;text-transform:uppercase;">
          <i class="fas {sc['icon']}" style="font-size:1rem;"></i>
          {status.upper()}
        </span>
        <div style="font-size:0.78rem;color:#94a3b8;margin-top:8px;">
          Appointment&nbsp;#<strong>{appt_id_val}</strong>
          &nbsp;|&nbsp;
          <i class="fas fa-calendar-alt" style="color:#0891b2;"></i>&nbsp;{appointment_date}
        </div>
      </div>

      <div class="modal-section-title"><i class="fas fa-user"></i> Parent Information</div>
      <div class="modal-grid">
        <div class="modal-field">
          <div class="modal-field-label">Parent Name</div>
          <div class="modal-field-value accent">{p_name}</div>
        </div>
        <div class="modal-field">
          <div class="modal-field-label">Gender</div>
          <div class="modal-field-value">{p_gender}</div>
        </div>
        <div class="modal-field">
          <div class="modal-field-label">Email</div>
          <div class="modal-field-value">{email_id}</div>
        </div>
        <div class="modal-field">
          <div class="modal-field-label">Mobile</div>
          <div class="modal-field-value">{mobile}</div>
        </div>
      </div>

      <div class="modal-section-title"><i class="fas fa-baby"></i> Child Information</div>
      <div class="modal-grid">
        <div class="modal-field">
          <div class="modal-field-label">Child Name</div>
          <div class="modal-field-value accent">{c_name}</div>
        </div>
        <div class="modal-field">
          <div class="modal-field-label">Gender</div>
          <div class="modal-field-value">{c_gender}</div>
        </div>
        <div class="modal-field">
          <div class="modal-field-label">Date of Birth</div>
          <div class="modal-field-value">{c_dob}</div>
        </div>
      </div>

      <div class="modal-section-title"><i class="fas fa-syringe"></i> Vaccination Details</div>
      <div class="modal-grid">
        <div class="modal-field">
          <div class="modal-field-label">Age Group</div>
          <div class="modal-field-value">{age_group}</div>
        </div>
        <div class="modal-field">
          <div class="modal-field-label">Vaccine Name</div>
          <div class="modal-field-value accent">{vaccination_name}</div>
        </div>
        <div class="modal-field">
          <div class="modal-field-label">Appointment Date</div>
          <div class="modal-field-value">{appointment_date}</div>
        </div>
      </div>

    </div>
  </div>
</div>
        """)

print(f"""
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
const HOSPITAL_ID = "{hospital_id}";
const TOTAL_COUNT = {total_count};

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

function filterTab(status) {{
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + status).classList.add('active');
  const rows = document.querySelectorAll('.appt-row');
  let visible = 0;
  rows.forEach(function(row) {{
    if (status === 'all' || row.dataset.status === status) {{
      row.style.display = ''; visible++;
    }} else {{
      row.style.display = 'none';
    }}
  }});
  const thead    = document.querySelector('#apptTable thead');
  const emptyDiv = document.getElementById('emptyMsg');
  const msgText  = document.getElementById('emptyMsgText');
  const labels   = {{
    all:'No Appointments Found...!',
    pending:'No Pending Appointments Found...!',
    completed:'No Completed Appointments Found...!',
    cancelled:'No Cancelled Appointments Found...!'
  }};
  if (visible === 0) {{
    thead.style.display = 'none'; emptyDiv.style.display = 'block';
    msgText.textContent = labels[status] || 'No Appointments Found...!';
  }} else {{
    thead.style.display = ''; emptyDiv.style.display = 'none';
  }}
  document.getElementById('showingLabel').textContent = 'Showing: ' + visible + ' of ' + TOTAL_COUNT;
}}

function toggleSidebar() {{
  document.getElementById('sidebar').classList.toggle('show');
  document.getElementById('sidebarOverlay').classList.toggle('show');
}}
document.addEventListener('click', function(event) {{
  const sidebar    = document.getElementById('sidebar');
  const menuToggle = document.querySelector('.mobile-menu-toggle');
  if (window.innerWidth < 992 &&
      !sidebar.contains(event.target) &&
      !menuToggle.contains(event.target) &&
      sidebar.classList.contains('show')) {{
    sidebar.classList.remove('show');
    document.getElementById('sidebarOverlay').classList.remove('show');
  }}
}});

function logout() {{
  if (confirm("Are you sure you want to logout?")) window.location.href = "main.py";
}}
function applyFilter() {{
  const date = document.getElementById('filterDate').value;
  if (!date) {{ alert("Please select a date to filter."); return; }}
  window.location.href = "hospital_view_appointment.py?hospital_id=" + HOSPITAL_ID + "&filter_date=" + date;
}}
function clearFilter() {{
  window.location.href = "hospital_view_appointment.py?hospital_id=" + HOSPITAL_ID;
}}
</script>
</body>
</html>
""")

con.close()