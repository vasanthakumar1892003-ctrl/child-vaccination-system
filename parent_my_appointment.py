#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgi
import cgitb
import sys
from datetime import date

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")

form = cgi.FieldStorage()

def get_field(name, default=""):
    """Safely extract a single string value from a CGI field (handles list returns)."""
    val = form.getvalue(name) or default
    if isinstance(val, list):
        val = val[0] if val else default
    return str(val).strip()

parent_id   = get_field("parent_id")
filter_date = get_field("filter_date")

# ── Action: update status ──────────────────────────────────────────────────
action     = get_field("action")
appt_id_f  = get_field("appt_id")
new_status = get_field("new_status")

try:
    con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
    cur = con.cursor()
except Exception as e:
    print("Content-Type: text/html\r\n\r\n")
    print(f"<h2 style='color:red;'>Database Connection Failed!</h2><pre>{e}</pre>")
    sys.exit()

# Ensure status column exists
try:
    cur.execute("SHOW COLUMNS FROM hospital_appointment LIKE 'status'")
    if not cur.fetchone():
        cur.execute("ALTER TABLE hospital_appointment ADD COLUMN status VARCHAR(20) DEFAULT 'pending'")
        con.commit()
except Exception:
    pass

# Handle status update POST
if action == "update_status" and appt_id_f and new_status:
    allowed = ["pending", "completed", "cancelled"]
    if new_status.lower() in allowed and appt_id_f.isdigit():
        try:
            cur.execute("UPDATE hospital_appointment SET status = %s WHERE id = %s",
                        (new_status.lower(), int(appt_id_f)))
            con.commit()
        except Exception:
            pass
    redirect_url = f"parent_my_appointment.py?parent_id={parent_id}"
    if filter_date:
        redirect_url += f"&filter_date={filter_date}"
    print(f"Content-Type: text/html\r\nLocation: {redirect_url}\r\n\r\n")
    con.close()
    sys.exit()

print("Content-Type: text/html\r\n\r\n")

# ── Today's date (YYYY-MM-DD) ──────────────────────────────────────────────
today_str = date.today().strftime("%Y-%m-%d")

# ── Fetch parent name ──────────────────────────────────────────────────────
parent_name = ""
if parent_id and parent_id.isdigit():
    cur.execute("SELECT parent_name FROM parent WHERE id = %s", (int(parent_id),))
    pr = cur.fetchone()
    if pr:
        parent_name = pr[0]

# ── Fetch appointments ─────────────────────────────────────────────────────
base_sql = """
    SELECT id, p_name, p_gender, email_id, mobile,
           c_name, c_gender, c_dob, age_group,
           vaccination_name, appointment_date, hospital_name,
           COALESCE(status,'pending') AS status, create_at
    FROM hospital_appointment
"""
if parent_name and filter_date:
    cur.execute(base_sql + " WHERE p_name=%s AND appointment_date=%s ORDER BY id DESC",
                (parent_name, filter_date))
elif parent_name:
    cur.execute(base_sql + " WHERE p_name=%s ORDER BY id DESC", (parent_name,))
elif filter_date:
    cur.execute(base_sql + " WHERE appointment_date=%s ORDER BY id DESC", (filter_date,))
else:
    cur.execute(base_sql + " ORDER BY id DESC")

appointments = cur.fetchall()

total_count     = len(appointments)
pending_count   = sum(1 for r in appointments if str(r[12]).strip().lower() == "pending")
completed_count = sum(1 for r in appointments if str(r[12]).strip().lower() == "completed")
cancelled_count = sum(1 for r in appointments if str(r[12]).strip().lower() == "cancelled")

form_action = f"parent_my_appointment.py?parent_id={parent_id}"
if filter_date:
    form_action += f"&filter_date={filter_date}"

def safe(row, idx):
    return str(row[idx]).strip() if len(row) > idx and row[idx] not in (None, "") else "N/A"

def normalize_date(val):
    """Normalize appointment_date to YYYY-MM-DD string for comparison."""
    if val in (None, "", "N/A"):
        return ""
    s = str(val).strip()
    if len(s) >= 10 and s[4] == "-":
        return s[:10]
    if hasattr(val, "strftime"):
        return val.strftime("%Y-%m-%d")
    return s

# ── Badge helpers ──────────────────────────────────────────────────────────
BADGE_ICONS = {
    "pending":   "fa-hourglass-half",
    "completed": "fa-check-circle",
    "cancelled": "fa-times-circle"
}

def status_badge_html(status, full_width=False):
    icon    = BADGE_ICONS.get(status, "fa-circle")
    style   = ' style="width:100%;display:inline-block;text-align:center;"' if full_width else ''
    return f'<span class="status-badge badge-{status}"{style}><i class="fas {icon} me-1"></i>{status.capitalize()}</span>'

# ══════════════════════════════════════════════════════════════════════════
# HTML OUTPUT
# ══════════════════════════════════════════════════════════════════════════
print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<title>My Appointments - CVS</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{
  background:linear-gradient(135deg,#052e16,#22c55e,#dcfce7);
  min-height:100vh;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;overflow-x:hidden;
}}
/* NAVBAR */
.navbar{{box-shadow:0 4px 20px rgba(0,0,0,0.4);padding:15px 20px;
  background:linear-gradient(135deg,#052e16,#22c55e,#dcfce7)!important;}}
.navbar .container-fluid{{display:flex;flex-direction:row;align-items:center;flex-wrap:nowrap;}}
.navbar-brand{{font-weight:600;color:white!important;letter-spacing:2px;text-transform:uppercase;}}
.navbar-brand i{{margin-right:10px;color:#d1fae5;font-size:1.5rem;animation:bounce 2s infinite;}}
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
.sidebar{{min-height:100vh;background:linear-gradient(135deg,#052e16,#22c55e);
  box-shadow:4px 0 20px rgba(0,0,0,0.3);padding:20px 0;}}
.sidebar-link{{display:block;padding:14px 18px;color:#d1fae5;text-decoration:none;
  transition:all 0.3s;border-left:4px solid transparent;font-weight:500;margin:6px 0;}}
.sidebar-link:hover,.sidebar-link.active{{
  background:linear-gradient(90deg,#22c55e,transparent);
  color:#fff;border-left:4px solid #dcfce7;
}}
.sidebar-link i{{margin-right:12px;width:22px;text-align:center;}}
.sidebar-overlay{{display:none;position:fixed;top:0;left:0;
  width:100%;height:100%;background:rgba(0,0,0,0.6);z-index:998;backdrop-filter:blur(2px);}}
.sidebar-overlay.show{{display:block;}}
/* CONTENT */
.content-wrap{{padding:20px;}}
.page-title-card{{
  background:white;border-radius:18px;padding:22px 28px;margin-bottom:20px;
  box-shadow:0 8px 25px rgba(0,0,0,0.12);display:flex;align-items:center;gap:16px;
}}
.title-icon{{
  background:linear-gradient(135deg,#052e16,#22c55e);color:white;
  width:48px;height:48px;border-radius:12px;
  display:flex;align-items:center;justify-content:center;font-size:1.4rem;flex-shrink:0;
}}
.page-title-card h2{{font-size:1.5rem;font-weight:800;color:#0f172a;
  letter-spacing:1.5px;text-transform:uppercase;margin:0;}}
/* COUNT CARDS */
.count-card{{border-radius:16px;padding:18px 22px;box-shadow:0 6px 20px rgba(0,0,0,0.10);
  display:flex;align-items:center;gap:14px;margin-bottom:20px;}}
.count-card .card-icon{{font-size:1.4rem;width:48px;height:48px;border-radius:12px;
  display:flex;align-items:center;justify-content:center;flex-shrink:0;}}
.count-card .card-num{{font-size:1.8rem;font-weight:800;line-height:1;}}
.count-card .card-label{{font-size:0.75rem;font-weight:700;text-transform:uppercase;
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
.tab-btn{{border:2px solid #059669;border-radius:25px;padding:8px 20px;font-size:0.85rem;
  font-weight:700;cursor:pointer;background:white;color:#059669;
  transition:all 0.25s ease;display:flex;align-items:center;gap:7px;}}
.tab-btn:hover{{background:#dcfce7;}}
.tab-btn.active{{background:linear-gradient(135deg,#052e16,#22c55e);color:white;
  border-color:#dcfce7;box-shadow:0 4px 14px rgba(5,150,105,0.45);}}
.showing-label{{margin-left:auto;font-size:0.82rem;font-weight:600;color:#059669;}}
/* FILTER CARD */
.filter-card{{background:white;border-radius:16px;padding:22px 25px;
  box-shadow:0 6px 20px rgba(0,0,0,0.10);margin-bottom:20px;}}
.filter-label{{font-weight:600;color:#374151;font-size:0.9rem;margin-bottom:10px;display:block;}}
.filter-label i{{margin-right:6px;color:#059669;}}
.filter-input{{border:2px solid #e5e7eb;border-radius:10px;padding:11px 14px;
  font-size:0.95rem;width:100%;transition:border-color 0.3s;}}
.filter-input:focus{{border-color:#059669;outline:none;box-shadow:0 0 0 3px rgba(5,150,105,0.15);}}
.btn-filter{{background:linear-gradient(135deg,#052e16,#22c55e);border:none;border-radius:10px;
  padding:11px 0;color:white;font-weight:700;font-size:0.95rem;width:100%;
  transition:all 0.3s;box-shadow:0 4px 15px rgba(5,150,105,0.4);cursor:pointer;}}
.btn-filter:hover{{transform:translateY(-2px);}}
.btn-clear{{background:linear-gradient(135deg,#6b7280,#4b5563);border:none;border-radius:10px;
  padding:11px 0;color:white;font-weight:700;font-size:0.95rem;
  width:100%;transition:all 0.3s;cursor:pointer;}}
.btn-clear:hover{{transform:translateY(-2px);}}
/* TABLE */
.table-card{{background:white;border-radius:18px;padding:25px;
  box-shadow:0 8px 25px rgba(0,0,0,0.12);overflow-x:auto;}}
.appt-table{{width:100%;border-collapse:collapse;}}
.appt-table thead th{{
  background:linear-gradient(135deg,#052e16,#22c55e 80%);
  color:white;padding:14px 13px;font-size:0.77rem;
  text-transform:uppercase;letter-spacing:0.8px;white-space:nowrap;border:none;
}}
.appt-table thead th:first-child{{border-radius:10px 0 0 10px;}}
.appt-table thead th:last-child{{border-radius:0 10px 10px 0;}}
.appt-table tbody tr{{transition:background 0.2s;}}
.appt-table tbody tr:hover{{background:#f0fdf4;}}
.appt-table tbody td{{padding:13px 13px;font-size:0.88rem;color:#374151;
  vertical-align:middle;white-space:nowrap;border-bottom:1px solid #f0f0f0;}}
.row-num{{font-weight:700;color:#6b7280;}}
.ic-orange{{color:#f97316;margin-right:5px;}}
/* STATUS SELECT (dropdown) */
.status-select{{border:2px solid #e5e7eb;border-radius:20px;padding:6px 14px;
  font-size:0.8rem;font-weight:700;cursor:pointer;min-width:130px;text-align:center;
  background:white;transition:all 0.2s ease;text-transform:uppercase;appearance:auto;}}
.status-select:focus{{outline:none;border-color:#059669;}}
.status-select.sel-pending{{background:#fef9c3;color:#b45309;border-color:#fde68a;}}
.status-select.sel-completed{{background:#d1fae5;color:#065f46;border-color:#6ee7b7;}}
.status-select.sel-cancelled{{background:#fee2e2;color:#991b1b;border-color:#fca5a5;}}
/* STATUS BADGE (read-only pill — shown when date != today OR status is locked) */
.status-badge{{
  display:inline-block;padding:6px 16px;border-radius:20px;
  font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;
}}
.badge-pending{{background:#fef9c3;color:#b45309;border:2px solid #fde68a;}}
.badge-completed{{background:#d1fae5;color:#065f46;border:2px solid #6ee7b7;}}
.badge-cancelled{{background:#fee2e2;color:#991b1b;border:2px solid #fca5a5;}}
/* VIEW BUTTON */
.btn-view-appt{{
  background:linear-gradient(135deg,#052e16,#22c55e);
  border:none;border-radius:8px;padding:6px 14px;
  color:white;font-weight:600;font-size:0.75rem;
  cursor:pointer;transition:all 0.3s;
  box-shadow:0 3px 10px rgba(5,150,105,0.3);white-space:nowrap;
}}
.btn-view-appt:hover{{transform:translateY(-2px);box-shadow:0 5px 15px rgba(5,150,105,0.45);}}
.btn-view-appt i{{margin-right:4px;}}
/* EMPTY */
#emptyMsg{{display:none;text-align:center;padding:60px 20px;}}
#emptyMsg .empty-icon{{font-size:4.5rem;color:#cbd5e1;display:block;margin-bottom:16px;}}
#emptyMsg p{{font-size:1.1rem;color:#94a3b8;font-weight:600;}}
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
  background:linear-gradient(135deg,#052e16,#22c55e);
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
  letter-spacing:1px;color:#059669;margin:16px 0 10px;
  display:flex;align-items:center;gap:7px;
  border-bottom:1.5px solid #dcfce7;padding-bottom:6px;
}}
.modal-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px 18px;}}
.modal-field{{background:#f0fdf4;border-radius:10px;padding:10px 14px;border:1.5px solid #dcfce7;}}
.modal-field-label{{font-size:0.67rem;font-weight:700;text-transform:uppercase;
  letter-spacing:0.5px;color:#94a3b8;margin-bottom:3px;}}
.modal-field-value{{font-size:0.88rem;font-weight:600;color:#1e293b;word-break:break-word;}}
.modal-field-value.accent{{color:#065f46;}}
.modal-status-pill{{
  display:inline-block;padding:6px 22px;border-radius:50px;
  font-size:0.8rem;font-weight:700;letter-spacing:0.5px;text-transform:uppercase;
}}
.pill-pending{{background:#fef9c3;color:#b45309;border:2px solid #fde68a;}}
.pill-completed{{background:#d1fae5;color:#065f46;border:2px solid #6ee7b7;}}
.pill-cancelled{{background:#fee2e2;color:#991b1b;border:2px solid #fca5a5;}}
/* MOBILE CARDS */
.appt-cards{{display:none;}}
.appt-card{{
  background:#fff;border-radius:14px;padding:16px 18px;
  box-shadow:0 4px 16px rgba(0,0,0,0.09);margin-bottom:14px;
  border-left:4px solid #22c55e;
}}
.appt-card-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;}}
.appt-card-num{{
  background:linear-gradient(135deg,#052e16,#22c55e);
  color:#fff;font-size:0.7rem;font-weight:700;
  border-radius:50px;padding:3px 10px;letter-spacing:0.5px;
}}
.appt-card-child{{font-size:0.98rem;font-weight:700;color:#065f46;margin-bottom:10px;
  display:flex;align-items:center;gap:7px;}}
.appt-card-child i{{color:#10b981;}}
.appt-card-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px 14px;}}
.appt-card-field{{display:flex;flex-direction:column;gap:2px;}}
.appt-card-label{{font-size:0.68rem;font-weight:700;text-transform:uppercase;
  letter-spacing:0.5px;color:#94a3b8;}}
.appt-card-value{{font-size:0.86rem;font-weight:600;color:#1e293b;}}
.appt-card-footer{{margin-top:12px;}}
.no-data{{text-align:center;padding:60px 20px;color:#94a3b8;}}
.no-data i{{font-size:4rem;display:block;margin-bottom:15px;color:#dcfce7;}}
.no-data p{{font-size:1.1rem;}}
/* RESPONSIVE */
@media(max-width:991.98px){{
  .mobile-menu-toggle{{display:flex;align-items:center;justify-content:center;}}
  .sidebar{{position:fixed;left:-100%;top:0;width:280px;height:100vh;
    z-index:999;transition:left 0.3s;overflow-y:auto;}}
  .sidebar.show{{left:0;}}
  .content-wrap{{padding:12px;margin-left:0!important;}}
  .navbar-brand{{font-size:1rem;letter-spacing:1px;}}
  .navbar-brand i{{font-size:1.3rem;}}
}}
@media(max-width:767.98px){{
  .desktop-table{{display:none!important;}}
  .appt-cards{{display:block;}}
  .table-card{{padding:16px;}}
  .appt-modal{{width:96%;}}
  .appt-modal-body{{padding:16px;}}
  .modal-grid{{grid-template-columns:1fr;}}
}}
@media(max-width:575.98px){{
  .navbar-brand{{font-size:0.85rem;letter-spacing:0.5px;}}
  .navbar-brand i{{font-size:1.1rem;margin-right:6px;}}
  .btn-logout{{padding:6px 14px;font-size:0.8rem;}}
  .appt-card-grid{{grid-template-columns:1fr;}}
}}
@media(max-width:400px){{
  .navbar-brand{{font-size:0.75rem;}}
  .content-wrap{{padding:8px;}}
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
      <a href="parent_booked_appointment.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fa-solid fa-calendar-day"></i> Booked Appointments
      </a>
      <a href="parent_my_appointment.py?parent_id={parent_id}" class="sidebar-link active" onclick="closeSidebarMobile()">
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
        <div class="title-icon"><i class="fas fa-calendar-check"></i></div>
        <h2>My Appointments</h2>
      </div>

      <!-- COUNT CARDS -->
      <div class="row g-3 mb-3">
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

      <!-- DESKTOP TABLE -->
      <div class="table-card desktop-table">
        <table class="appt-table" id="apptTable">
          <thead>
            <tr>
              <th><i class="fas fa-hashtag"></i> #</th>
              <th><i class="fas fa-baby"></i> Child Name</th>
              <th><i class="fas fa-birthday-cake"></i> DOB</th>
              <th><i class="fas fa-hospital"></i> Hospital</th>
              <th><i class="fas fa-layer-group"></i> Age Group</th>
              <th><i class="fas fa-calendar-alt"></i> Date</th>
              <th><i class="fas fa-info-circle"></i> Status</th>
              <th><i class="fas fa-eye"></i> View</th>
            </tr>
          </thead>
          <tbody id="apptBody">
""")

if not appointments:
    print("""
            <tr>
              <td colspan="8" class="no-data">
                <i class="fas fa-calendar-times"></i>
                <p>No appointments found.</p>
              </td>
            </tr>
    """)
else:
    for idx, i in enumerate(appointments, start=1):
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
        hospital_name    = safe(i, 11)
        raw_status       = safe(i, 12)
        status           = raw_status.lower() if raw_status != "N/A" else "pending"
        modal_id         = f"appt_{idx}"

        # ── Show dropdown ONLY when: date == today AND status == pending ──
        appt_date_norm = normalize_date(i[10])
        is_today       = (appt_date_norm == today_str)
        is_locked      = status in ("completed", "cancelled")
        show_dropdown  = is_today and not is_locked   # pending + today only

        options_html = ""
        for opt in ["pending", "completed", "cancelled"]:
            selected = "selected" if opt == status else ""
            options_html += f'<option value="{opt}" {selected}>{opt.capitalize()}</option>'

        if show_dropdown:
            status_cell = f"""
                <form method="POST" action="{form_action}" style="margin:0;">
                  <input type="hidden" name="action"      value="update_status">
                  <input type="hidden" name="parent_id"   value="{parent_id}">
                  <input type="hidden" name="appt_id"     value="{appt_id_val}">
                  <input type="hidden" name="filter_date" value="{filter_date}">
                  <select name="new_status"
                          class="status-select sel-{status}"
                          onchange="this.className='status-select sel-'+this.value; this.form.submit();">
                    {options_html}
                  </select>
                </form>"""
        else:
            status_cell = status_badge_html(status)

        print(f"""
            <tr class="appt-row" data-status="{status}">
              <td class="row-num">{idx}</td>
              <td><strong>{c_name}</strong></td>
              <td>{c_dob}</td>
              <td><strong>{hospital_name}</strong></td>
              <td>{age_group}</td>
              <td><i class="fas fa-calendar ic-orange"></i><strong>{appointment_date}</strong></td>
              <td>{status_cell}</td>
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
          <span class="empty-icon"><i class="fas fa-inbox"></i></span>
          <p id="emptyMsgText">No Appointments Found...!</p>
        </div>
      </div><!-- /desktop-table -->

      <!-- MOBILE CARDS -->
      <div class="appt-cards" id="mobileCards">
""")

if not appointments:
    print("""
        <div class="no-data">
          <i class="fas fa-calendar-times"></i>
          <p>No appointments found.</p>
        </div>
    """)
else:
    for idx, i in enumerate(appointments, start=1):
        appt_id_val      = safe(i, 0)
        c_name           = safe(i, 5)
        vaccination_name = safe(i, 9)
        appointment_date = safe(i, 10)
        hospital_name    = safe(i, 11)
        raw_status       = safe(i, 12)
        status           = raw_status.lower() if raw_status != "N/A" else "pending"
        modal_id         = f"appt_{idx}"

        # ── Show dropdown ONLY when: date == today AND status == pending ──
        appt_date_norm = normalize_date(i[10])
        is_today       = (appt_date_norm == today_str)
        is_locked      = status in ("completed", "cancelled")
        show_dropdown  = is_today and not is_locked

        options_html = ""
        for opt in ["pending", "completed", "cancelled"]:
            selected = "selected" if opt == status else ""
            options_html += f'<option value="{opt}" {selected}>{opt.capitalize()}</option>'

        if show_dropdown:
            status_footer = f"""
            <div class="appt-card-footer">
              <form method="POST" action="{form_action}" style="margin:0;">
                <input type="hidden" name="action"      value="update_status">
                <input type="hidden" name="parent_id"   value="{parent_id}">
                <input type="hidden" name="appt_id"     value="{appt_id_val}">
                <input type="hidden" name="filter_date" value="{filter_date}">
                <select name="new_status"
                        class="status-select sel-{status}"
                        style="width:100%;"
                        onchange="this.className='status-select sel-'+this.value; this.form.submit();">
                  {options_html}
                </select>
              </form>
            </div>"""
        else:
            status_footer = f"""
            <div class="appt-card-footer">
              {status_badge_html(status, full_width=True)}
            </div>"""

        print(f"""
        <div class="appt-card appt-row" data-status="{status}">
          <div class="appt-card-header">
            <span class="appt-card-num">#{idx}</span>
            <button class="btn-view-appt" onclick="openModal('{modal_id}')">
              <i class="fas fa-eye"></i> View
            </button>
          </div>
          <div class="appt-card-child">
            <i class="fas fa-baby"></i> {c_name}
          </div>
          <div class="appt-card-grid">
            <div class="appt-card-field">
              <span class="appt-card-label"><i class="fas fa-hospital me-1"></i> Hospital</span>
              <span class="appt-card-value">{hospital_name}</span>
            </div>
            <div class="appt-card-field">
              <span class="appt-card-label"><i class="fas fa-syringe me-1"></i> Vaccine</span>
              <span class="appt-card-value">{vaccination_name}</span>
            </div>
            <div class="appt-card-field">
              <span class="appt-card-label"><i class="fas fa-calendar-alt me-1"></i> Date</span>
              <span class="appt-card-value">{appointment_date}</span>
            </div>
          </div>
          {status_footer}
        </div>
        """)

print("""
      </div><!-- /mobile-cards -->

    </div><!-- /content-wrap -->
  </div><!-- /row -->
</div><!-- /container-fluid -->
""")

# ══════════════════════════════════════════
# APPOINTMENT DETAIL MODALS
# ══════════════════════════════════════════
if appointments:
    for idx, i in enumerate(appointments, start=1):
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
        hospital_name    = safe(i, 11)
        raw_status       = safe(i, 12)
        status           = raw_status.lower() if raw_status != "N/A" else "pending"
        pill_cls         = f"pill-{status}"

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
        <span class="modal-status-pill {pill_cls}">{status.upper()}</span>
        <div style="font-size:0.78rem;color:#94a3b8;margin-top:6px;">
          Appointment&nbsp;#<strong>{appt_id_val}</strong>
          &nbsp;|&nbsp;
          <i class="fas fa-calendar-alt" style="color:#059669;"></i>&nbsp;{appointment_date}
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
          <div class="modal-field-label">Hospital</div>
          <div class="modal-field-value">{hospital_name}</div>
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
const TOTAL_COUNT = {total_count};

/* Modal */
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

/* Tab filter */
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
  if (thead) {{
    if (visible === 0) {{
      thead.style.display = 'none';
      if (emptyDiv) {{ emptyDiv.style.display = 'block'; msgText.textContent = labels[status] || labels.all; }}
    }} else {{
      thead.style.display = '';
      if (emptyDiv) emptyDiv.style.display = 'none';
    }}
  }}
  document.getElementById('showingLabel').textContent = 'Showing: ' + visible + ' of ' + TOTAL_COUNT;
}}

/* Colour selects on load */
document.querySelectorAll('.status-select').forEach(function(sel) {{
  sel.className = 'status-select sel-' + sel.value;
}});

/* Sidebar */
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

function logout() {{
  if (confirm('Are you sure you want to logout?')) window.location.href = 'main.py';
}}
function applyFilter() {{
  const date = document.getElementById('filterDate').value;
  if (!date) {{ alert('Please select a date to filter.'); return; }}
  window.location.href = 'parent_my_appointment.py?parent_id=' + PARENT_ID + '&filter_date=' + date;
}}
function clearFilter() {{
  window.location.href = 'parent_my_appointment.py?parent_id=' + PARENT_ID;
}}
</script>
</body>
</html>
""")

con.close()