#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgitb
import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")
print("Content-Type: text/html\n")

# ── Milestone order ────────────────────────────────────────────────────────────
AGE_MILESTONES_ORDER = [
    "At Birth", "6 Weeks", "10 Weeks", "14 Weeks",
    "6 Months", "9 Months", "12 Months", "15 Months",
    "18 Months", "2 Years", "4-6 Years", "10 Years"
]

def age_index(age_str):
    s = (age_str or "").strip().lower()
    for i, a in enumerate(AGE_MILESTONES_ORDER):
        if a.lower() == s:
            return i
    return 999

def parse_age_str(age_str):
    if not age_str:
        return None
    s = age_str.strip().lower()
    if s in ("at birth", "0"):
        return relativedelta()
    if s == "4-6 years":
        return relativedelta(years=4)
    parts = s.split()
    if len(parts) == 2:
        try:
            num = int(parts[0])
        except ValueError:
            return None
        unit = parts[1]
        if "week"  in unit: return relativedelta(weeks=num)
        if "month" in unit: return relativedelta(months=num)
        if "year"  in unit: return relativedelta(years=num)
    return None

try:
    con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
    cur = con.cursor()
except Exception as e:
    print("<html><body><h2>Database Connection Failed!</h2><p>Error:</p>", e, "</body></html>")
    sys.exit()

try:
    cur.execute("""
        SELECT id, child_name, child_dob, child_gender, done_vaccin, vaccin_age, vaccin_name,
               last_vaccinedate, parent_name, parent_type, parent_gender, email_id
        FROM manage_child ORDER BY id DESC
    """)
    children = cur.fetchall()
    db_error = None
except Exception as e:
    children = []
    db_error = str(e)


# ── Build vaccination schedule (same logic as parent_manage_child.py) ──────────
def build_vaccination_schedule(child_dob, done_vaccin_int, vaccin_age, vaccin_name, last_vaccinedate):
    dob = None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            dob = datetime.strptime(str(child_dob).strip(), fmt).date()
            break
        except Exception:
            continue
    if dob is None:
        return [], []

    try:
        vc = con.cursor()
        vc.execute("SELECT vaccine_name, age_group, dose_number FROM vaccination_schedule ORDER BY id")
        raw = vc.fetchall()
        vc.close()
    except Exception:
        try:
            vc2 = con.cursor()
            vc2.execute("SELECT * FROM vaccination_schedule ORDER BY id")
            all_rows = vc2.fetchall()
            cols = [d[0].lower() for d in vc2.description]
            vc2.close()
            age_c  = next((i for i,c in enumerate(cols) if c == "age_group"), None)
            if age_c is None:
                age_c = next((i for i,c in enumerate(cols) if "age" in c), None)
            name_c = next((i for i,c in enumerate(cols) if c == "vaccine_name"), None)
            if name_c is None:
                name_c = next((i for i,c in enumerate(cols) if "name" in c), None)
            dose_c = next((i for i,c in enumerate(cols) if "dose" in c), None)
            if age_c is None or name_c is None:
                return [], []
            raw = [(r[name_c], r[age_c], r[dose_c] if dose_c is not None else "") for r in all_rows]
        except Exception:
            return [], []

    if not raw:
        return [], []

    raw = sorted(raw, key=lambda r: (age_index(r[1]), (r[0] or "").lower()))

    try:
        dv = int(done_vaccin_int)
    except (TypeError, ValueError):
        dv = 0

    all_rows_built = []
    for vax_name_raw, vax_age_raw, dose_raw in raw:
        vax_name_str = (vax_name_raw or "").strip()
        age_grp      = (vax_age_raw  or "").strip()
        dose_num     = (dose_raw     or "").strip() if dose_raw is not None else ""
        if not vax_name_str or not age_grp:
            continue
        rd = parse_age_str(age_grp)
        sched_date_str = (dob + rd).strftime("%d-%m-%Y") if rd is not None else "—"
        all_rows_built.append({
            "vaccine_age"   : age_grp,
            "vaccine_name"  : vax_name_str,
            "dose_number"   : dose_num,
            "scheduled_date": sched_date_str,
        })

    if dv > 0 and vaccin_age:
        milestone_idx = age_index(str(vaccin_age).strip())
        milestone_cap = sum(1 for r in all_rows_built if age_index(r["vaccine_age"]) <= milestone_idx)
        actual_done = min(dv, milestone_cap)
    else:
        actual_done = dv

    return all_rows_built[:actual_done], all_rows_built[actual_done:]


# ── Helper: render vax table rows ─────────────────────────────────────────────
def vax_table_html(rows, empty_msg):
    if not rows:
        return (f"<tr><td colspan='3' style='text-align:center;color:#888;"
                f"padding:14px;font-style:italic;'>{empty_msg}</td></tr>")
    out = ""
    prev_age = None
    for r in rows:
        if r["vaccine_age"] != prev_age:
            age_cell = f"<td style='font-weight:700;color:#065f46;white-space:nowrap;'>{r['vaccine_age']}</td>"
        else:
            age_cell = "<td style='color:#9ca3af;font-size:.8rem;'>↳</td>"
        prev_age = r["vaccine_age"]
        dose_badge = ""
        if r.get("dose_number"):
            dose_badge = (f"<span style='display:inline-block;padding:1px 7px;border-radius:8px;"
                          f"background:#e0f2fe;color:#0369a1;font-size:.75rem;font-weight:600;"
                          f"margin-left:6px;'>{r['dose_number']}</span>")
        out += (f"<tr>"
                f"{age_cell}"
                f"<td>{r['vaccine_name']}{dose_badge}</td>"
                f"<td style='white-space:nowrap;'>{r['scheduled_date']}</td>"
                f"</tr>")
    return out


print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>View Children - Admin Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}

body {{
  background: linear-gradient(135deg, #3b021f, #ec4899, #fdf2f8);
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow-x: hidden;
}}

/* ── NAVBAR ── */
.navbar {{
  background: linear-gradient(135deg, #3b021f, #ec4899, #fdf2f8) !important;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  padding: 15px 20px;
}}
.navbar-brand {{ font-weight:600; color:white !important; letter-spacing:2px; text-transform:uppercase; }}
.navbar-brand i {{ margin-right:10px; color:#fda4af; font-size:1.5rem; animation:pulse 2s infinite; }}
@keyframes pulse {{ 0%,100% {{ transform:scale(1); }} 50% {{ transform:scale(1.1); }} }}

.mobile-menu-toggle {{
  display:none;
  background:rgba(255,255,255,0.15); border:1.5px solid rgba(255,255,255,0.35);
  color:white; padding:6px 12px; border-radius:8px; font-size:1.2rem;
  cursor:pointer; line-height:1;
}}
.mobile-menu-toggle:hover {{ background:rgba(255,255,255,0.28); color:white; }}

.btn-logout {{
  background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
  border:none; padding:8px 20px; border-radius:25px;
  color:white; font-weight:600; font-size:0.9rem; transition:all 0.3s;
}}
.btn-logout:hover {{ transform:translateY(-2px); color:white; }}

/* ── SIDEBAR ── */
.sidebar {{
  min-height:100vh;
  background: linear-gradient(135deg, #3b021f, #ec4899);
  box-shadow:4px 0 15px rgba(0,0,0,0.2);
  padding:20px 0;
}}
.sidebar-link {{
  display:block; padding:12px 15px; color:#ecf0f1; text-decoration:none;
  transition:all 0.3s; border-left:4px solid transparent;
  font-weight:500; margin:5px 0; font-size:0.95rem;
}}
.sidebar-link:hover, .sidebar-link.active {{
  background: linear-gradient(90deg, #ec4899, transparent);
  color:#fff; border-left:4px solid #fdf2f8; padding-left:20px;
}}
.sidebar-link i {{ margin-right:10px; width:20px; text-align:center; }}

/* ── SIDEBAR OVERLAY ── */
.sidebar-overlay {{
  display:none; position:fixed; top:0; left:0;
  width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:998;
}}
.sidebar-overlay.show {{ display:block; }}

/* ── CONTENT ── */
.content-area {{ padding:20px; }}

.page-header {{
  background:white; padding:20px 25px; border-radius:18px; margin-bottom:20px;
  box-shadow:0 8px 25px rgba(0,0,0,0.12); border-left:8px solid #22c55e;
  display:flex; align-items:center; justify-content:center; flex-wrap:wrap; gap:10px;
}}
.page-header h4 {{
  margin:0; color:#0f172a; font-weight:500; font-size:1.9rem;
  text-transform:uppercase; letter-spacing:1px; text-align:center;
}}
.page-header h4 i {{ margin-right:12px; color:#052e16; }}

/* ── SEARCH BOX ── */
.search-box {{
  background:white; border-radius:16px; padding:18px 25px;
  margin-bottom:20px; box-shadow:0 6px 20px rgba(0,0,0,0.10);
  display:flex; align-items:center; gap:15px; flex-wrap:wrap;
}}
.search-box .form-control {{
  border:2px solid #e5e7eb; border-radius:0 25px 25px 0;
  padding:11px 20px; font-size:0.95rem; transition:border-color 0.3s;
}}
.search-box .form-control:focus {{
  border-color:#11998e; box-shadow:0 0 0 3px rgba(17,153,142,0.15); outline:none;
}}
.search-box .input-group-text {{
  background:white; border:2px solid #e5e7eb; border-right:none;
  border-radius:25px 0 0 25px; padding-left:15px; color:#11998e;
}}
.badge-count {{
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color:white; padding:10px 18px; border-radius:20px; font-size:0.9rem;
  font-weight:600; white-space:nowrap; flex-shrink:0;
}}

/* ── TABLE ── */
.table-container {{
  background:white; border-radius:15px; padding:20px;
  box-shadow:0 5px 20px rgba(0,0,0,0.1); overflow-x:auto;
}}
table {{ width:100%; border-collapse:collapse; background:#fff; font-size:14px; }}
th, td {{ padding:15px 10px; text-align:center; vertical-align:middle; border-bottom:1px solid #e0e0e0; }}
th {{
  background: linear-gradient(135deg, #052e16, #22c55e);
  color:white; font-weight:600; text-transform:uppercase; font-size:13px;
  letter-spacing:0.5px; position:sticky; top:0; z-index:10;
}}
tbody tr {{ transition:all 0.3s; }}
tbody tr:hover {{
  background:#f0fff4; transform:scale(1.01);
  box-shadow:0 2px 8px rgba(17,153,142,0.2);
}}

/* ── BADGES ── */
.badge-gender {{ padding:4px 12px; border-radius:20px; font-size:0.75rem; font-weight:600; }}
.badge-male   {{ background:#dbeafe; color:#1d4ed8; }}
.badge-female {{ background:#fce7f3; color:#be185d; }}
.badge-other  {{ background:#f3e8ff; color:#7c3aed; }}

/* ── VIEW MORE BUTTON ── */
.btn-view-more {{
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  border:none; padding:8px 20px; border-radius:25px;
  color:white; font-size:0.85rem; font-weight:500;
  transition:all 0.3s; white-space:nowrap;
  box-shadow:0 4px 15px rgba(17,153,142,0.4);
}}
.btn-view-more:hover {{
  transform:translateY(-2px); color:white;
  box-shadow:0 6px 20px rgba(17,153,142,0.6);
}}

/* ── ROW INDEX BADGE ── */
.row-index {{
  display:inline-flex; width:32px; height:32px;
  align-items:center; justify-content:center;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  border-radius:50%; color:white; font-weight:700; font-size:0.82rem;
}}

/* ── MODAL ── */
.modal-content {{ border-radius:20px; border:none; overflow:hidden; box-shadow:0 10px 40px rgba(0,0,0,0.3); }}
.view-modal-header {{
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color:white; padding:20px 30px; border:none;
}}
.view-modal-header .btn-close {{ filter:invert(1); }}
.view-modal-body {{ background:#f8f9fa; padding:24px 28px; }}
.view-modal-footer {{
  background:#f8f9fa; border-top:1px solid #e9ecef; padding:15px 25px;
}}

/* ── MODAL TABS ── */
.modal-tab-btns {{ display:flex; gap:8px; margin-bottom:18px; flex-wrap:wrap; }}
.tab-btn {{
  flex:1; min-width:90px; padding:9px; border:2px solid #a7f3d0;
  border-radius:10px; background:white; color:#059669;
  font-weight:600; font-size:.82rem; cursor:pointer; transition:all .25s; text-align:center;
}}
.tab-btn.active {{
  background: linear-gradient(135deg, #11998e, #38ef7d);
  color:white; border-color:transparent;
}}
.tab-panel {{ display:none; }}
.tab-panel.active {{ display:block; }}

/* ── VIEW SECTION ── */
.view-section-title {{
  font-size:.78rem; font-weight:700; color:#11998e; text-transform:uppercase;
  letter-spacing:.8px; margin:0 0 12px; padding-bottom:6px;
  border-bottom:2px solid #a7f3d0;
  display:flex; align-items:center; gap:6px;
}}
.view-section-title.orange {{ color:#ea580c; border-color:#fed7aa; }}

.info-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:18px; }}
.info-card {{
  background:white; border-radius:12px; padding:14px 16px;
  border-left:4px solid #11998e; box-shadow:0 2px 8px rgba(0,0,0,0.06);
}}
.info-card.green  {{ border-left-color:#38ef7d; }}
.info-card.pink   {{ border-left-color:#ec4899; }}
.info-card.orange {{ border-left-color:#f59e0b; }}
.info-card label {{
  font-size:.68rem; font-weight:700; color:#9ca3af; text-transform:uppercase;
  letter-spacing:.5px; margin-bottom:5px; display:block;
}}
.info-card .val {{ font-size:.92rem; font-weight:600; color:#1e293b; word-break:break-word; }}

/* ── VACCINATION SCHEDULE TABLES ── */
.vax-table {{ width:100%; border-collapse:collapse; font-size:.83rem; margin-top:6px; }}
.vax-table thead th {{
  padding:9px 10px; text-align:left; font-weight:700; font-size:.76rem;
  text-transform:uppercase; letter-spacing:.5px; color:#fff;
}}
.vax-table-done thead {{ background:#059669; }}
.vax-table-rem  thead {{ background:#ea580c; }}
.vax-table tbody td {{ padding:8px 10px; border-bottom:1px solid #e5e7eb; color:#374151; }}
.vax-table tbody tr:nth-child(even) {{ background:#f9fafb; }}

/* ── CLOSE BUTTON ── */
.btn-close-modal {{
  background: linear-gradient(135deg, #64748b, #94a3b8);
  border:none; padding:9px 22px; border-radius:25px; color:white; font-weight:600;
}}

/* ── NO DATA ── */
.no-data {{ text-align:center; padding:60px 20px; color:#888; }}
.no-data i {{ font-size:4rem; color:#ccc; margin-bottom:15px; display:block; }}

/* ── RESPONSIVE ── */
@media (max-width:991.98px) {{
  .mobile-menu-toggle {{ display:inline-flex; align-items:center; justify-content:center; }}
  .sidebar {{
    position:fixed; left:-100%; top:0;
    width:280px; height:100vh; z-index:999; transition:left 0.3s; overflow-y:auto;
  }}
  .sidebar.show {{ left:0; }}
  .content-area {{ padding:15px; margin-left:0 !important; }}
  .navbar-brand {{ font-size:1rem; }}
}}
@media (max-width:767.98px) {{
  .page-header h4 {{ font-size:1.4rem; }}
  .info-grid {{ grid-template-columns:1fr; }}
  .modal-tab-btns {{ flex-direction:column; }}
  table {{ font-size:.78rem; }}
  th {{ font-size:.72rem; padding:8px 6px; }}
  td {{ padding:8px 6px; font-size:.78rem; }}
  .search-box {{ flex-direction:column; align-items:stretch; }}
  .badge-count {{ text-align:center; }}
}}
@media (max-width:575.98px) {{
  .navbar-brand {{ font-size:.85rem; }}
  .navbar-brand i {{ font-size:1.1rem; }}
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
      <a href="admin_view_child.py" class="sidebar-link active"><i class="fas fa-baby"></i> View Children</a>
      <a href="admin_view_appointment.py" class="sidebar-link"><i class="fas fa-calendar-check"></i> View Appointments</a>
      <a href="admin_vaccination_schedule.py" class="sidebar-link"><i class="fa-solid fa-syringe"></i> Vaccination Schedule</a>
      <a href="admin_appointment_reminder.py" class="sidebar-link"><i class="fas fa-bell"></i> Appointment Reminders</a>
      <a href="admin_export_data.py" class="sidebar-link"><i class="fas fa-file-export"></i> Export Data</a>
      <a href="admin_view_feedback.py" class="sidebar-link"><i class="fas fa-comment-dots"></i> Feedback</a>
    </div>

    <!-- CONTENT -->
    <div class="col-lg-10 col-md-9 col-12 content-area">

      <div class="page-header">
        <h4><i class="fas fa-baby"></i> View Children</h4>
      </div>

      <!-- SEARCH + BADGE -->
      <div class="search-box">
        <div class="input-group">
          <span class="input-group-text border-0 bg-white ps-3">
            <i class="fas fa-search"></i>
          </span>
          <input type="text" class="form-control" id="searchInput" onkeyup="searchTable()"
                 placeholder="Search by child name, parent name, vaccine...">
        </div>
        <span class="badge-count">
          <i class="fas fa-list me-1"></i> Total Records: {len(children)}
        </span>
      </div>

      <div class="table-container">
""")

if db_error:
    print(f'<div class="alert alert-danger"><i class="fas fa-exclamation-triangle me-2"></i>Database Error: {db_error}</div>')
elif not children:
    print("""
        <div class="no-data">
          <i class="fas fa-baby"></i>
          <h5>No Children Records Found</h5>
          <p class="text-muted">There are no child records in the database yet.</p>
        </div>""")
else:
    print("""
        <table id="childTable">
          <thead>
            <tr>
              <th><i class="fas fa-hashtag"></i> No.</th>
              <th><i class="fas fa-baby me-1"></i> Child Name</th>
              <th><i class="fas fa-calendar me-1"></i> Date of Birth</th>
              <th><i class="fas fa-venus-mars me-1"></i> Gender</th>
              <th><i class="fas fa-user me-1"></i> Parent Name</th>
              <th><i class="fas fa-envelope me-1"></i> Email</th>
              <th><i class="fas fa-cogs me-1"></i> Actions</th>
            </tr>
          </thead>
          <tbody>""")

    modals_html = []

    for i, row in enumerate(children, 1):
        (child_id, child_name, child_dob, child_gender, done_vaccin, vaccin_age, vaccin_name,
         last_vaccinedate, parent_name, parent_type, parent_gender, email_id) = row

        # Gender badge
        g = (child_gender or "").lower()
        if "female" in g:
            gender_badge = '<span class="badge-gender badge-female"><i class="fas fa-venus me-1"></i>Female</span>'
        elif "male" in g:
            gender_badge = '<span class="badge-gender badge-male"><i class="fas fa-mars me-1"></i>Male</span>'
        else:
            gender_badge = f'<span class="badge-gender badge-other">{child_gender or "N/A"}</span>'

        # Safe display values
        safe_child_name    = child_name    or "N/A"
        safe_child_dob     = str(child_dob) if child_dob else "N/A"
        safe_child_gender  = child_gender  or "N/A"
        safe_done_vaccin   = str(done_vaccin) if done_vaccin is not None else "N/A"
        safe_vaccin_age    = str(vaccin_age) if vaccin_age else "N/A"
        safe_last_vac      = str(last_vaccinedate) if last_vaccinedate else "N/A"
        safe_vaccin_name   = vaccin_name   or "N/A"
        safe_parent_name   = parent_name   or "N/A"
        safe_parent_type   = parent_type   or "N/A"
        safe_parent_gender = parent_gender or "N/A"
        safe_email         = email_id      or "N/A"

        # Parse done_vaccin as int
        try:
            dv_int = int(done_vaccin) if done_vaccin is not None else 0
        except (ValueError, TypeError):
            dv_int = 0

        # Build vaccination schedule
        done_rows_m, remaining_rows_m = build_vaccination_schedule(
            safe_child_dob, dv_int, vaccin_age, vaccin_name, safe_last_vac
        )
        done_trs      = vax_table_html(done_rows_m,      "No vaccinations recorded as done yet.")
        remaining_trs = vax_table_html(remaining_rows_m, "All vaccinations completed — excellent work!")

        print(f"""
            <tr>
              <td><span class="row-index">{i}</span></td>
              <td><strong>{safe_child_name}</strong></td>
              <td>{safe_child_dob}</td>
              <td>{gender_badge}</td>
              <td>{safe_parent_name}</td>
              <td><small><a href="mailto:{safe_email}" class="text-decoration-none">{safe_email}</a></small></td>
              <td>
                <button class="btn-view-more" data-bs-toggle="modal" data-bs-target="#childModal_{child_id}">
                  <i class="fas fa-eye me-1"></i> View More
                </button>
              </td>
            </tr>""")

        modals_html.append(f"""
<div class="modal fade" id="childModal_{child_id}" tabindex="-1" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable" style="max-width:680px;">
    <div class="modal-content">
      <div class="modal-header view-modal-header">
        <div>
          <h5 class="modal-title mb-1"><i class="fas fa-baby me-2"></i>{safe_child_name}</h5>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>

      <div class="modal-body view-modal-body">

        <!-- TABS -->
        <div class="modal-tab-btns">
          <button class="tab-btn active" onclick="switchTab(this,'viewTab_{child_id}')">
            <i class="fas fa-eye me-1"></i> View Details
          </button>
          <button class="tab-btn" onclick="switchTab(this,'scheduleTab_{child_id}')">
            <i class="fas fa-syringe me-1"></i> Vaccination Schedule
          </button>
        </div>

        <!-- VIEW DETAILS TAB -->
        <div class="tab-panel active" id="viewTab_{child_id}">
          <div class="view-section-title"><i class="fas fa-baby"></i> Child Information</div>
          <div class="info-grid">
            <div class="info-card"><label>Child Name</label><div class="val">{safe_child_name}</div></div>
            <div class="info-card"><label>Date of Birth</label><div class="val">{safe_child_dob}</div></div>
            <div class="info-card"><label>Gender</label><div class="val">{safe_child_gender}</div></div>
            <div class="info-card pink"><label>Vaccinations Done</label><div class="val">{safe_done_vaccin}</div></div>
            <div class="info-card pink"><label>Vaccine Age Group</label><div class="val">{safe_vaccin_age}</div></div>
            <div class="info-card pink"><label>Last Vaccine Date</label><div class="val">{safe_last_vac}</div></div>
            <div class="info-card pink"><label>Vaccine Name</label><div class="val">{safe_vaccin_name}</div></div>
          </div>
          <div class="view-section-title"><i class="fas fa-user-circle"></i> Parent Information</div>
          <div class="info-grid">
            <div class="info-card green"><label>Parent Name</label><div class="val">{safe_parent_name}</div></div>
            <div class="info-card green"><label>Parent Type</label><div class="val">{safe_parent_type}</div></div>
            <div class="info-card green"><label>Parent Gender</label><div class="val">{safe_parent_gender}</div></div>
            <div class="info-card orange"><label>Email ID</label>
              <div class="val" style="word-break:break-all;">
                <a href="mailto:{safe_email}" style="color:#f59e0b;">{safe_email}</a>
              </div>
            </div>
          </div>
        </div>

        <!-- VACCINATION SCHEDULE TAB -->
        <div class="tab-panel" id="scheduleTab_{child_id}">
          <div class="view-section-title" style="color:#059669;border-color:#a7f3d0;">
            <i class="fas fa-check-circle"></i> Vaccinations Already Done
            <span style="margin-left:auto;background:#d1fae5;color:#065f46;padding:2px 10px;
              border-radius:10px;font-size:.78rem;">{len(done_rows_m)} done</span>
          </div>
          <div>
            <table class="vax-table vax-table-done">
              <thead>
                <tr>
                  <th>Age Group</th>
                  <th>Vaccine &amp; Dose</th>
                  <th>Scheduled Date</th>
                </tr>
              </thead>
              <tbody>{done_trs}</tbody>
            </table>
          </div>

          <div class="view-section-title orange" style="margin-top:20px;">
            <i class="fas fa-clock"></i> Upcoming Vaccinations
            <span style="margin-left:auto;background:#ffedd5;color:#7c2d12;padding:2px 10px;
              border-radius:10px;font-size:.78rem;">{len(remaining_rows_m)} upcoming</span>
          </div>
          <div>
            <table class="vax-table vax-table-rem">
              <thead>
                <tr>
                  <th>Age Group</th>
                  <th>Vaccine &amp; Dose</th>
                  <th>Scheduled Date</th>
                </tr>
              </thead>
              <tbody>{remaining_trs}</tbody>
            </table>
          </div>
          <p style="margin-top:10px;font-size:.75rem;color:#6b7280;">
            <i class="fas fa-info-circle"></i>
            Dates are calculated from the child's date of birth. Confirm with healthcare provider.
          </p>
        </div>

      </div>

      <div class="modal-footer view-modal-footer justify-content-end">
        <button type="button" class="btn btn-close-modal" data-bs-dismiss="modal">
          <i class="fas fa-times me-1"></i> Close
        </button>
      </div>
    </div>
  </div>
</div>""")

    print("</tbody></table>")
    for m in modals_html:
        print(m)

print("""
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
  function switchTab(btn, tabId) {
    const modal = btn.closest('.modal-content');
    modal.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    modal.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(tabId).classList.add('active');
  }
  function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('show');
    document.getElementById('sidebarOverlay').classList.toggle('show');
  }
  function logout() {
    if (confirm('Are you sure you want to logout?')) window.location.href = 'admin_login.py';
  }
  function searchTable() {
    const input = document.getElementById('searchInput').value.toLowerCase();
    let idx = 1;
    document.querySelectorAll('#childTable tbody tr').forEach(row => {
      const show = row.innerText.toLowerCase().includes(input);
      row.style.display = show ? '' : 'none';
      if (show) {
        const badge = row.querySelector('.row-index');
        if (badge) badge.textContent = idx++;
      }
    });
  }
  document.addEventListener('click', function(e) {
    const sb = document.getElementById('sidebar');
    const mt = document.querySelector('.mobile-menu-toggle');
    if (window.innerWidth < 992 && sb && mt &&
        !sb.contains(e.target) && !mt.contains(e.target) && sb.classList.contains('show')) {
      sb.classList.remove('show');
      document.getElementById('sidebarOverlay').classList.remove('show');
    }
  });
</script>
</body>
</html>""")

cur.close()
con.close()