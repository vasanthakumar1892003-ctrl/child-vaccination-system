#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgi
import cgitb
import sys

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")

# Read form data BEFORE headers
form = cgi.FieldStorage()
filter_date     = (form.getvalue("filter_date")     or "").strip()
filter_hospital = (form.getvalue("filter_hospital") or "").strip()
filter_status   = (form.getvalue("filter_status")   or "").strip()

print("Content-Type: text/html\r\n\r\n")

# Database Connection
try:
    con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
    cur = con.cursor()
except Exception as e:
    print(f"<h2 style='color:red;'>Database Connection Failed!</h2><pre>{e}</pre>")
    sys.exit()

# Fetch all appointments with filters
try:
    sql = """
        SELECT id, p_name, p_gender, email_id, mobile,
               c_name, c_gender, c_dob,
               vaccination_name, appointment_date,
               hospital_name, COALESCE(status, 'pending') AS status
        FROM hospital_appointment
        WHERE 1=1
    """
    params = []
    if filter_date:
        sql += " AND appointment_date = %s"
        params.append(filter_date)
    if filter_hospital:
        sql += " AND hospital_name LIKE %s"
        params.append(f"%{filter_hospital}%")
    if filter_status:
        sql += " AND status = %s"
        params.append(filter_status)
    sql += " ORDER BY id DESC"
    cur.execute(sql, params)
    rows = cur.fetchall()
except Exception as e:
    rows = []

# Counts
total_count     = len(rows)
pending_count   = sum(1 for r in rows if str(r[11]).strip().lower() == "pending")
completed_count = sum(1 for r in rows if str(r[11]).strip().lower() == "completed")
cancelled_count = sum(1 for r in rows if str(r[11]).strip().lower() == "cancelled")

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Admin - Vaccination Schedule</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}

body {{
  background: linear-gradient(135deg, #3b021f, #ec4899, #fdf2f8);
  min-height:100vh;
  font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;
  overflow-x:hidden;
}}

/* ── NAVBAR ── */
.navbar {{
  background: linear-gradient(135deg, #3b021f, #ec4899, #fdf2f8) !important;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  padding: 15px 20px;
}}
.navbar-brand {{
  font-weight: 600;
  color: white !important;
  letter-spacing: 2px;
  text-transform: uppercase;
}}
.navbar-brand i {{
  margin-right: 10px;
  color: #fda4af;
  font-size: 1.5rem;
  animation: pulse 2s infinite;
}}
@keyframes pulse {{
  0%, 100% {{ transform: scale(1); }}
  50%       {{ transform: scale(1.1); }}
}}

/* ── MOBILE MENU TOGGLE ── */
.mobile-menu-toggle {{
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
}}
.mobile-menu-toggle:hover {{
  background: rgba(255,255,255,0.28);
  border-color: rgba(255,255,255,0.6);
  color: white;
}}

/* ── LOGOUT ── */
.btn-logout {{
  background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
  border: none;
  padding: 8px 20px;
  border-radius: 25px;
  color: white;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(238,9,121,0.4);
  font-size: 0.9rem;
}}
.btn-logout:hover {{
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(238,9,121,0.6);
  color: white;
}}

/* ── SIDEBAR ── */
.sidebar {{
  min-height: 100vh;
  background: linear-gradient(135deg, #3b021f, #ec4899);
  box-shadow: 4px 0 15px rgba(0,0,0,0.2);
  padding: 20px 0;
}}
.sidebar-link {{
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
}}
.sidebar-link:hover, .sidebar-link.active {{
  background: linear-gradient(90deg, #ec4899, transparent);
  color: #fff;
  border-left: 4px solid #fdf2f8;
  padding-left: 20px;
}}
.sidebar-link i {{ margin-right: 10px; width: 20px; text-align: center; }}

/* ── SIDEBAR OVERLAY ── */
.sidebar-overlay {{
  display: none;
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.5);
  z-index: 998;
}}
.sidebar-overlay.show {{ display: block; }}

/* ── CONTENT ── */
.content-area {{ padding: 25px; min-height: 100vh; }}

/* ── PAGE HEADER ── */
.page-header {{
  background: white;
  padding: 22px 25px;
  border-radius: 18px;
  margin-bottom: 20px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.12);
  border-left: 6px solid #ec4899;
}}
.page-header h4 {{
  margin: 0;
  color: #0f172a;
  font-weight: 700;
  font-size: 1.5rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}}
.page-header h4 i {{ margin-right: 12px; color: #3b021f; }}

/* ── COUNT CARDS ── */
.count-card {{
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.10);
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}}
.count-card .card-icon {{
  font-size: 1.6rem;
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}}
.count-card .card-num   {{ font-size: 2rem; font-weight: 800; line-height: 1; }}
.count-card .card-label {{ font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8; margin-top: 2px; }}
.card-total     {{ background: #ede9fe; color: #4c1d95; }}
.card-total     .card-icon {{ background: #c4b5fd; color: #4c1d95; }}
.card-pending   {{ background: #fef9c3; color: #92400e; }}
.card-pending   .card-icon {{ background: #fde68a; color: #b45309; }}
.card-completed {{ background: #d1fae5; color: #065f46; }}
.card-completed .card-icon {{ background: #6ee7b7; color: #065f46; }}
.card-cancelled {{ background: #fee2e2; color: #991b1b; }}
.card-cancelled .card-icon {{ background: #fca5a5; color: #991b1b; }}

/* ── FILTER CARD ── */
.filter-card {{
  background: white;
  border-radius: 16px;
  padding: 22px 25px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.10);
  margin-bottom: 20px;
}}
.filter-label {{ font-weight: 600; color: #374151; font-size: 0.9rem; margin-bottom: 8px; display: block; }}
.filter-label i {{ margin-right: 6px; color: #8e2de2; }}
.filter-input {{
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 0.9rem;
  width: 100%;
  transition: border-color 0.3s;
  background: white;
}}
.filter-input:focus {{ border-color: #8e2de2; outline: none; box-shadow: 0 0 0 3px rgba(142,45,226,0.15); }}
.btn-filter {{
  background: linear-gradient(135deg, #3b021f, #ec4899);
  border: none; border-radius: 10px; padding: 10px 0;
  color: white; font-weight: 700; width: 100%; transition: all 0.3s;
}}
.btn-filter:hover {{ transform: translateY(-2px); }}
.btn-clear {{
  background: linear-gradient(135deg, #6b7280, #4b5563);
  border: none; border-radius: 10px; padding: 10px 0;
  color: white; font-weight: 700; width: 100%; transition: all 0.3s;
}}
.btn-clear:hover {{ transform: translateY(-2px); }}

/* ── FILTER TABS ── */
.filter-tabs {{
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  background: white;
  border-radius: 16px;
  padding: 16px 20px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.10);
  margin-bottom: 20px;
  align-items: center;
}}
.tab-btn {{
  border: 2px solid #8e2de2;
  border-radius: 25px;
  padding: 7px 18px;
  font-size: 0.83rem;
  font-weight: 700;
  cursor: pointer;
  background: white;
  color: #8e2de2;
  transition: all 0.25s ease;
}}
.tab-btn:hover {{ background: #fdf2f8; }}
.tab-btn.active {{
  background: linear-gradient(135deg, #3b021f, #ec4899);
  color: white;
  border-color: #fdf2f8;
  box-shadow: 0 4px 14px rgba(142,45,226,0.45);
}}
.showing-label {{ margin-left: auto; font-size: 0.82rem; font-weight: 600; color: #8e2de2; }}

/* ── TABLE ── */
.table-card {{
  background: white;
  border-radius: 18px;
  padding: 25px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.12);
  overflow-x: auto;
}}
.appt-table {{ width: 100%; border-collapse: collapse; }}

.appt-table thead th {{
  background: linear-gradient(135deg, #3b021f, #ec4899 50%);
  color: white;
  padding: 14px 12px;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  white-space: nowrap;
  border: none;
}}
.appt-table thead th:first-child {{ border-radius: 10px 0 0 10px; }}
.appt-table thead th:last-child  {{ border-radius: 0 10px 10px 0; }}
.appt-table tbody tr:hover {{ background: #fdf4ff; }}
.appt-table tbody td {{
  padding: 13px 12px;
  font-size: 0.87rem;
  color: #374151;
  vertical-align: middle;
  white-space: nowrap;
  border-bottom: 1px solid #f0f0f0;
}}
.badge-pending   {{ background: #fef9c3; color: #b45309; border: 1px solid #fde68a; border-radius: 20px; padding: 4px 12px; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; }}
.badge-completed {{ background: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; border-radius: 20px; padding: 4px 12px; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; }}
.badge-cancelled {{ background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; border-radius: 20px; padding: 4px 12px; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; }}

/* ── VIEW MORE BUTTON ── */
.btn-view-more {{
  background: linear-gradient(135deg, #3b021f, #ec4899);
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.3s;
}}
.btn-view-more:hover {{
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(236,72,153,0.5);
  color: white;
}}

/* ── EMPTY STATE ── */
.empty-state {{
  display: none;
  text-align: center;
  padding: 70px 20px;
}}
.empty-state .empty-icon {{ font-size: 5rem; color: #d1d5db; display: block; margin-bottom: 18px; }}
.empty-state p {{ font-size: 1.15rem; color: #94a3b8; font-weight: 600; margin: 0; }}

/* ── MODAL ── */
.view-modal-section-title {{
  font-size: .72rem;
  font-weight: 700;
  color: #be185d;
  text-transform: uppercase;
  letter-spacing: .8px;
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 2px solid #fbcfe8;
}}
.view-info-grid {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 18px;
}}
.view-info-card {{
  background: white;
  border-radius: 10px;
  padding: 12px 14px;
  border-left: 4px solid #ec4899;
}}
.view-info-card.purple {{ border-left-color: #7c3aed; }}
.view-info-card.dark   {{ border-left-color: #3b021f; }}
.view-info-card label {{
  font-size: .7rem;
  font-weight: 700;
  color: #9ca3af;
  text-transform: uppercase;
  margin-bottom: 3px;
  display: block;
}}
.view-info-card .val {{
  font-weight: 600;
  color: #1e293b;
  word-break: break-all;
}}

/* ── RESPONSIVE ── */
@media (max-width: 991.98px) {{
  .mobile-menu-toggle {{
    display: inline-flex !important;
    align-items: center;
    justify-content: center;
  }}
  .sidebar {{
    position: fixed;
    left: -100%;
    top: 0;
    width: 280px;
    height: 100vh;
    z-index: 999;
    transition: left 0.3s ease;
    overflow-y: auto;
  }}
  .sidebar.show {{ left: 0; }}
  .content-area {{ padding: 15px; margin-left: 0 !important; }}
  .navbar-brand {{ font-size: 1rem; }}
  .navbar-brand i {{ font-size: 1.3rem; }}
}}
@media (max-width: 767.98px) {{
  .page-header h4 {{ font-size: 1.2rem; }}
  .content-area {{ padding: 10px; }}
  .btn-logout {{ padding: 6px 15px; font-size: 0.8rem; }}
  .view-info-grid {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 575.98px) {{
  .navbar-brand {{ font-size: 0.85rem; }}
  .navbar-brand i {{ font-size: 1.1rem; }}
  .page-header h4 {{ font-size: 1rem; }}
}}
</style>
</head>
<body>

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

<!-- Sidebar Overlay -->
<div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

<div class="container-fluid">
  <div class="row">

    <!-- SIDEBAR -->
    <div class="col-lg-2 col-md-3 sidebar p-0" id="sidebar">
      <a href="admin_dashboard.py" class="sidebar-link"><i class="fas fa-home"></i> Home</a>
      <a href="admin_vaccination.py" class="sidebar-link"><i class="fa-solid fa-circle-info"></i> Add Vaccination Info</a>
      <a href="admin_hospital_registration.py" class="sidebar-link"><i class="fas fa-hospital"></i> Hospital Registration</a>
      <a href="admin_parent_registration.py" class="sidebar-link"><i class="fas fa-user"></i> Parent Registration</a>
      <a href="admin_view_child.py" class="sidebar-link"><i class="fas fa-baby"></i> View Children</a>
      <a href="admin_view_appointment.py" class="sidebar-link"><i class="fas fa-calendar-check"></i> View Appointments</a>
      <a href="admin_vaccination_schedule.py" class="sidebar-link active"><i class="fa-solid fa-syringe"></i> Vaccination Schedule</a>
      <a href="admin_appointment_reminder.py" class="sidebar-link"><i class="fas fa-bell"></i> Appointment Reminders</a>
      <a href="admin_export_data.py" class="sidebar-link"><i class="fas fa-file-export"></i> Export Data</a>
      <a href="admin_view_feedback.py" class="sidebar-link"><i class="fas fa-comment-dots"></i> Feedback</a>
    </div>

    <!-- CONTENT -->
    <div class="col-lg-10 col-md-9 col-12 content-area">

      <div class="page-header">
        <h4><i class="fa-solid fa-syringe"></i> Vaccination Schedule</h4>
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
        <button class="tab-btn active" id="tab-all"       onclick="filterTab('all')">      <i class="fas fa-list"></i> All</button>
        <button class="tab-btn"        id="tab-pending"   onclick="filterTab('pending')">  <i class="fas fa-hourglass-half"></i> Pending</button>
        <button class="tab-btn"        id="tab-completed" onclick="filterTab('completed')"><i class="fas fa-check-circle"></i> Completed</button>
        <button class="tab-btn"        id="tab-cancelled" onclick="filterTab('cancelled')"><i class="fas fa-times-circle"></i> Cancelled</button>
        <span class="showing-label" id="showingLabel">Showing: {total_count} of {total_count}</span>
      </div>

      <!-- FILTERS -->
      <div class="filter-card">
        <span class="filter-label"><i class="fas fa-filter"></i> Filter Records</span>
        <div class="row g-3 align-items-end">
          <div class="col-md-3">
            <label class="filter-label"><i class="fas fa-calendar"></i> By Date</label>
            <input type="date" class="filter-input" id="filterDate" value="{filter_date}">
          </div>
          <div class="col-md-3">
            <label class="filter-label"><i class="fas fa-hospital"></i> By Hospital</label>
            <input type="text" class="filter-input" id="filterHospital"
                   placeholder="Type hospital name..." value="{filter_hospital}">
          </div>
          <div class="col-md-2">
            <label class="filter-label"><i class="fas fa-info-circle"></i> By Status</label>
            <select class="filter-input" id="filterStatus">
              <option value="">-- All --</option>
              <option value="pending"   {"selected" if filter_status == "pending"   else ""}>Pending</option>
              <option value="completed" {"selected" if filter_status == "completed" else ""}>Completed</option>
              <option value="cancelled" {"selected" if filter_status == "cancelled" else ""}>Cancelled</option>
            </select>
          </div>
          <div class="col-md-2">
            <button class="btn-filter" onclick="applyFilter()"><i class="fas fa-search"></i> Filter</button>
          </div>
          <div class="col-md-2">
            <button class="btn-clear" onclick="clearFilter()"><i class="fas fa-redo"></i> Clear</button>
          </div>
        </div>
      </div>

      <!-- TABLE -->
      <div class="table-card">
        <table class="appt-table" id="apptTable">
          <thead id="tableHead">
            <tr>
              <th>#</th>
              <th><i class="fas fa-user"></i> Parent Name</th>
              <th><i class="fas fa-venus-mars"></i> P. Gender</th>
              <th><i class="fas fa-child"></i> Child Name</th>
              <th><i class="fas fa-venus-mars"></i> C. Gender</th>
              <th><i class="fas fa-birthday-cake"></i> Child DOB</th>
              <th><i class="fas fa-syringe"></i> Vaccine</th>
              <th><i class="fas fa-calendar-alt"></i> Appt. Date</th>
              <th><i class="fas fa-hospital"></i> Hospital</th>
              <th><i class="fas fa-cog"></i> Action</th>
            </tr>
          </thead>
          <tbody id="apptBody">
""")

def safe(row, idx):
    return str(row[idx]).strip() if len(row) > idx and row[idx] not in (None, "") else "N/A"

if not rows:
    print("""
        <tr id="noDataRow">
          <td colspan="13">
            <div class="empty-state" style="display:block;">
              <i class="fas fa-inbox empty-icon"></i>
              <p>No Vaccination Schedule Found...!</p>
            </div>
          </td>
        </tr>
    """)
else:
    for idx, r in enumerate(rows, start=1):
        status    = safe(r, 11).lower() if safe(r, 11) != "N/A" else "pending"
        badge_cls = f"badge-{status}"
        print(f"""
            <tr class="appt-row" data-status="{status}">
              <td><strong>{idx}</strong></td>
              <td><strong>{safe(r,1)}</strong></td>
              <td>{safe(r,2)}</td>
              <td><strong>{safe(r,5)}</strong></td>
              <td>{safe(r,6)}</td>
              <td>{safe(r,7)}</td>
              <td><strong>{safe(r,8)}</strong></td>
              <td><strong>{safe(r,9)}</strong></td>
              <td>{safe(r,10)}</td>
              <td>
                <button class="btn-view-more"
                  onclick="openViewModal(this)"
                  data-id="{safe(r,0)}"
                  data-pname="{safe(r,1)}"
                  data-pgender="{safe(r,2)}"
                  data-email="{safe(r,3)}"
                  data-mobile="{safe(r,4)}"
                  data-cname="{safe(r,5)}"
                  data-cgender="{safe(r,6)}"
                  data-cdob="{safe(r,7)}"
                  data-vaccine="{safe(r,8)}"
                  data-date="{safe(r,9)}"
                  data-hospital="{safe(r,10)}"
                  data-status="{status}">
                  <i class="fas fa-eye"></i> View More
                </button>
              </td>
            </tr>
        """)

print(f"""
          </tbody>
        </table>

        <div class="empty-state" id="emptyState">
          <i class="fas fa-inbox empty-icon"></i>
          <p id="emptyMsg">No Records Found...!</p>
        </div>

      </div>
    </div>
  </div>
</div>

<!-- VIEW MORE MODAL -->
<div class="modal fade" id="viewModal" tabindex="-1" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-lg">
    <div class="modal-content" style="border-radius:16px;overflow:hidden;border:none;">
      <div class="modal-header" style="background:linear-gradient(135deg,#3b021f,#ec4899);color:white;">
        <h5 class="modal-title"><i class="fas fa-calendar-check me-2"></i> Appointment Details</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" style="filter:invert(1);"></button>
      </div>
      <div class="modal-body" style="background:#fdf2f8;padding:28px;">

        <!-- Parent Info -->
        <div class="view-modal-section-title"><i class="fas fa-user me-1"></i> Parent Information</div>
        <div class="view-info-grid">
          <div class="view-info-card">
            <label>Parent Name</label>
            <div class="val" id="v_pname"></div>
          </div>
          <div class="view-info-card">
            <label>Gender</label>
            <div class="val" id="v_pgender"></div>
          </div>
          <div class="view-info-card">
            <label>Email</label>
            <div class="val" id="v_email"></div>
          </div>
          <div class="view-info-card">
            <label>Mobile</label>
            <div class="val" id="v_mobile"></div>
          </div>
        </div>

        <!-- Child Info -->
        <div class="view-modal-section-title"><i class="fas fa-baby me-1"></i> Child Information</div>
        <div class="view-info-grid">
          <div class="view-info-card dark">
            <label>Child Name</label>
            <div class="val" id="v_cname"></div>
          </div>
          <div class="view-info-card dark">
            <label>Gender</label>
            <div class="val" id="v_cgender"></div>
          </div>
          <div class="view-info-card dark">
            <label>Date of Birth</label>
            <div class="val" id="v_cdob"></div>
          </div>
        </div>

        <!-- Appointment Info -->
        <div class="view-modal-section-title"><i class="fas fa-syringe me-1"></i> Appointment Information</div>
        <div class="view-info-grid">
          <div class="view-info-card purple">
            <label>Vaccine</label>
            <div class="val" id="v_vaccine"></div>
          </div>
          <div class="view-info-card purple">
            <label>Appointment Date</label>
            <div class="val" id="v_date"></div>
          </div>
          <div class="view-info-card purple">
            <label>Hospital</label>
            <div class="val" id="v_hospital"></div>
          </div>
          <div class="view-info-card purple">
            <label>Status</label>
            <div id="v_status"></div>
          </div>
        </div>

      </div>
      <div class="modal-footer" style="background:#fdf2f8;border-top:1px solid #fbcfe8;">
        <button type="button" class="btn" data-bs-dismiss="modal"
          style="background:linear-gradient(135deg,#6b7280,#4b5563);color:white;border:none;
                 padding:9px 24px;border-radius:20px;font-weight:600;">
          <i class="fas fa-times me-1"></i> Close
        </button>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
const TOTAL = {total_count};

const emptyMessages = {{
  all:       'No Vaccination Schedule Found...!',
  pending:   'No Pending Records Found...!',
  completed: 'No Completed Records Found...!',
  cancelled: 'No Cancelled Records Found...!'
}};

function openViewModal(btn) {{
  const status = btn.dataset.status;
  const badgeMap = {{
    pending:   'background:#fef9c3;color:#b45309;border:1px solid #fde68a;',
    completed: 'background:#d1fae5;color:#065f46;border:1px solid #6ee7b7;',
    cancelled: 'background:#fee2e2;color:#991b1b;border:1px solid #fca5a5;'
  }};
  const style = badgeMap[status] || badgeMap['pending'];
  document.getElementById('v_pname').textContent    = btn.dataset.pname;
  document.getElementById('v_pgender').textContent  = btn.dataset.pgender;
  document.getElementById('v_email').textContent    = btn.dataset.email;
  document.getElementById('v_mobile').textContent   = btn.dataset.mobile;
  document.getElementById('v_cname').textContent    = btn.dataset.cname;
  document.getElementById('v_cgender').textContent  = btn.dataset.cgender;
  document.getElementById('v_cdob').textContent     = btn.dataset.cdob;
  document.getElementById('v_vaccine').textContent  = btn.dataset.vaccine;
  document.getElementById('v_date').textContent     = btn.dataset.date;
  document.getElementById('v_hospital').textContent = btn.dataset.hospital;
  document.getElementById('v_status').innerHTML =
    `<span style="padding:4px 14px;border-radius:20px;font-size:.82rem;font-weight:700;
     text-transform:uppercase;${{style}}">${{status.charAt(0).toUpperCase()+status.slice(1)}}</span>`;
  new bootstrap.Modal(document.getElementById('viewModal')).show();
}}

function filterTab(status) {{
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + status).classList.add('active');

  const rows  = document.querySelectorAll('.appt-row');
  const thead = document.getElementById('tableHead');
  const empty = document.getElementById('emptyState');
  const msg   = document.getElementById('emptyMsg');
  let visible = 0;

  rows.forEach(row => {{
    const match = status === 'all' || row.dataset.status === status;
    row.style.display = match ? '' : 'none';
    if (match) visible++;
  }});

  if (visible === 0) {{
    thead.style.display = 'none';
    empty.style.display = 'block';
    msg.textContent     = emptyMessages[status] || 'No Records Found...!';
  }} else {{
    thead.style.display = '';
    empty.style.display = 'none';
  }}

  document.getElementById('showingLabel').textContent = 'Showing: ' + visible + ' of ' + TOTAL;
}}

function applyFilter() {{
  const date     = document.getElementById('filterDate').value;
  const hospital = document.getElementById('filterHospital').value.trim();
  const status   = document.getElementById('filterStatus').value;
  let url = 'admin_vaccination_schedule.py?';
  if (date)     url += 'filter_date='     + date                         + '&';
  if (hospital) url += 'filter_hospital=' + encodeURIComponent(hospital) + '&';
  if (status)   url += 'filter_status='   + status                       + '&';
  window.location.href = url;
}}

function clearFilter() {{
  window.location.href = 'admin_vaccination_schedule.py';
}}

function toggleSidebar() {{
  document.getElementById('sidebar').classList.toggle('show');
  document.getElementById('sidebarOverlay').classList.toggle('show');
}}

document.addEventListener('click', function(e) {{
  const sb = document.getElementById('sidebar');
  const mt = document.querySelector('.mobile-menu-toggle');
  if (window.innerWidth < 992 &&
      mt && !sb.contains(e.target) &&
      !mt.contains(e.target) &&
      sb.classList.contains('show')) {{
    sb.classList.remove('show');
    document.getElementById('sidebarOverlay').classList.remove('show');
  }}
}});

function logout() {{
  if (confirm('Are you sure you want to logout?'))
    window.location.href = 'logout.py';
}}
</script>
</body>
</html>""")

con.close()