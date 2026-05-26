#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgi
import cgitb
import sys
from datetime import date

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")

# ✅ Read form data BEFORE printing headers
form = cgi.FieldStorage()
_hid = form.getvalue("hospital_id") or ""
hospital_id = (_hid[0] if isinstance(_hid, list) else _hid).strip()

print("Content-Type: text/html\r\n\r\n")

# Database Connection
try:
    con = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="cvsdp"
    )
    cur = con.cursor()
except Exception as e:
    print(f"<h2 style='color:red;'>Database Connection Failed!</h2><pre>{e}</pre>")
    sys.exit()

# ── FETCH HOSPITAL NAME ──────────────────────────────────────────────────────
try:
    cur.execute("SELECT hospital_name FROM hospital WHERE id = %s", (hospital_id,))
    row = cur.fetchone()
    hospital_name = row[0] if row else ""
except:
    hospital_name = ""

# ── FETCH DASHBOARD COUNTS ───────────────────────────────────────────────────
today = date.today().strftime("%Y-%m-%d")

def get_count(query, params=None):
    try:
        cur.execute(query, params) if params else cur.execute(query)
        return cur.fetchone()[0]
    except:
        return 0

# ── APPOINTMENT COUNTS (from hospital_appointment table) ────────────────────
# Card 1: Total Appointments (all time)
total_appointments = get_count(
    "SELECT COUNT(*) FROM hospital_appointment WHERE hospital_name = %s",
    (hospital_name,)
)

# Card 2: Today's Appointments
today_appointments = get_count(
    "SELECT COUNT(*) FROM hospital_appointment WHERE hospital_name = %s AND appointment_date = %s",
    (hospital_name, today)
)

# Card 3: Future Appointments — upcoming appointments (date > today, status = 'pending')
future_appointments = get_count(
    "SELECT COUNT(*) FROM hospital_appointment WHERE hospital_name = %s AND appointment_date > %s AND status = 'pending'",
    (hospital_name, today)
)

# Card 4: Delay / Overdue Appointments — past due and still pending (date < today, status = 'pending')
delay_appointments = get_count(
    "SELECT COUNT(*) FROM hospital_appointment WHERE hospital_name = %s AND appointment_date < %s AND status = 'pending'",
    (hospital_name, today)
)

# Card 5: Completed Vaccination (status = 'completed')
completed_vaccination = get_count(
    "SELECT COUNT(*) FROM hospital_appointment WHERE hospital_name = %s AND status = 'completed'",
    (hospital_name,)
)

# Card 6: Pending Vaccination (status = 'pending')
pending_vaccination = get_count(
    "SELECT COUNT(*) FROM hospital_appointment WHERE hospital_name = %s AND status = 'pending'",
    (hospital_name,)
)

# Card 7: Cancelled Vaccination (status = 'cancelled')
cancelled_vaccination = get_count(
    "SELECT COUNT(*) FROM hospital_appointment WHERE hospital_name = %s AND status = 'cancelled'",
    (hospital_name,)
)

# ── PARENT APPLICATION COUNTS (from parentform table) ───────────────────────
# Card 8: Pending Applications (parent applied, not yet approved/rejected)
pending_applications = get_count(
    "SELECT COUNT(*) FROM parentform WHERE hospital_name = %s AND status = 'pending'",
    (hospital_name,)
)

# Card 9: Approved Applications
approved_applications = get_count(
    "SELECT COUNT(*) FROM parentform WHERE hospital_name = %s AND status = 'approved'",
    (hospital_name,)
)

# Card 10: Rejected Applications
rejected_applications = get_count(
    "SELECT COUNT(*) FROM parentform WHERE hospital_name = %s AND status = 'rejected'",
    (hospital_name,)
)

# ── HTML ─────────────────────────────────────────────────────────────────────

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Hospital Dashboard - CVS</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  background: linear-gradient(135deg, #083344, #22d3ee, #cffafe);
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow-x: hidden;
}}

/* ===== NAVBAR ===== */
.navbar {{
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  padding: 15px 20px;
  background: linear-gradient(135deg, #083344, #22d3ee, #cffafe) !important;
}}
.navbar .container-fluid {{
  display: flex;
  flex-direction: row;
  align-items: center;
  flex-wrap: nowrap;
}}
.navbar-brand {{
  font-weight: 600;
  color: white !important;
  letter-spacing: 2px;
  text-transform: uppercase;
}}
.navbar-brand i {{
  margin-right: 10px;
  color: #e9d5ff;
  font-size: 1.5rem;
  animation: bounce 2s infinite;
}}

@keyframes bounce {{
  0%, 100% {{ transform: translateY(0); }}
  50% {{ transform: translateY(-5px); }}
}}

.mobile-menu-toggle {{
  display: none;
  flex-shrink: 0;
  align-self: center;
  background: rgba(255, 255, 255, 0.15);
  border: 1.5px solid rgba(255, 255, 255, 0.35);
  color: white;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(6px);
  line-height: 1;
  margin-right: 12px;
}}
.mobile-menu-toggle:hover {{
  background: rgba(255, 255, 255, 0.28);
  border-color: rgba(255, 255, 255, 0.6);
  color: white;
}}

.btn-logout {{
  flex-shrink: 0;
  background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
  border: none;
  padding: 8px 20px;
  border-radius: 25px;
  color: white;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(238, 9, 121, 0.4);
  font-size: 0.9rem;
  white-space: nowrap;
  transition: all 0.3s ease;
}}
.btn-logout:hover {{ transform: translateY(-2px); color: white; box-shadow: 0 6px 20px rgba(238, 9, 121, 0.6); }}

/* ===== SIDEBAR ===== */
.sidebar {{
  min-height: 100vh;
  background: linear-gradient(135deg, #083344, #22d3ee);
  box-shadow: 4px 0 20px rgba(0,0,0,0.3);
  padding: 20px 0;
}}
.sidebar-link {{
  display: block; padding: 14px 18px; color: #e9d5ff;
  text-decoration: none; transition: all 0.3s ease;
  border-left: 4px solid transparent; font-weight: 500; margin: 6px 0;
}}
.sidebar-link:hover, .sidebar-link.active {{
  background: linear-gradient(90deg, #22d3ee, transparent 100%);
  color: #fff; border-left: 4px solid #cffafe; padding-left: 24px;
}}
.sidebar-link i {{ margin-right: 12px; width: 22px; text-align: center; }}

.sidebar-overlay {{
  display: none; position: fixed; top: 0; left: 0;
  width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 998;
}}
.sidebar-overlay.show {{ display: block; }}

/* ===== CONTENT ===== */
.content-area {{ padding: 25px; min-height: 100vh; }}
.section {{ display: none; animation: fadeInUp 0.5s ease-in; }}
@keyframes fadeInUp {{
  from {{ opacity: 0; transform: translateY(30px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.page-header {{
  background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
  padding: 22px 25px; border-radius: 18px; margin-bottom: 25px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15); border-left: 6px solid #0ea5e9;
}}
.page-header h4 {{
  margin: 0; color: #0f172a; font-weight: 700;
  font-size: 1.6rem; text-transform: uppercase; letter-spacing: 1px;
}}
.page-header h4 i {{ margin-right: 12px; color: #0ea5e9; }}
.card-box {{
  border-radius: 20px;
  padding: 25px;
  color: white;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  min-height: 160px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin-bottom: 15px;
}}
.card-box::before {{
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: rgba(255, 255, 255, 0.1);
  transform: rotate(45deg);
  transition: all 0.6s ease;
}}
.card-box:hover::before {{ top: -100%; right: -100%; }}
.card-box:hover {{
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
}}
.card-box h3 {{ font-size: 3rem; font-weight: 800; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); position: relative; z-index: 1; }}
.card-box p {{ font-size: 1.1rem; font-weight: 600; margin: 0; color: white; text-transform: uppercase; letter-spacing: 1px; position: relative; z-index: 1; }}
.card-icon {{ position: absolute; top: 15px; right: 15px; font-size: 2.5rem; opacity: 0.80; z-index: 0; }}
.stats-badge {{
  position: absolute; top: 14px; left: 14px;
  background: rgba(255,255,255,0.25); padding: 5px 14px; border-radius: 20px;
  font-size: 0.75rem; font-weight: 700; z-index: 1;
}}

.bg-total      {{ background: linear-gradient(135deg, #00c6ff, #0072ff, #8e2de2); }}
.bg-today      {{ background: linear-gradient(135deg, #b76e79, #f7cac9, #fde2e4); }}
.bg-future     {{ background: linear-gradient(135deg, #2b1055, #7597de, #b993d6); }}
.bg-delay      {{ background: linear-gradient(135deg, #fbc2eb, #a6c1ee, #fdfbfb); }}
.bg-complete   {{ background: linear-gradient(135deg, #11998e, #38ef7d, #b7f8db); }}
.bg-pending    {{ background: linear-gradient(135deg, #f7971e, #ffd200, #fff6b7); }}
.bg-cancel     {{ background: linear-gradient(135deg, #78350f 0%, #f59e0b 100%); }}
.bg-appending  {{ background: linear-gradient(135deg, #ff512f, #f09819, #ffdd00); }}
.bg-apapprove  {{ background: linear-gradient(135deg, #5c7c2f 0%, #b2f2bb 100%); }}
.bg-apreject   {{ background: linear-gradient(135deg, #ff512f, #dd2476, #24c6dc); }}

@media (max-width: 991.98px) {{
  .mobile-menu-toggle {{ display: flex; align-items: center; justify-content: center; }}
  .sidebar {{
    position: fixed; left: -100%; top: 0;
    width: 280px; height: 100vh; z-index: 999;
    transition: left 0.3s ease; overflow-y: auto;
  }}
  .sidebar.show {{ left: 0; }}
  .navbar-brand {{ font-size: 1rem; letter-spacing: 1px; }}
  .navbar-brand i {{ font-size: 1.3rem; }}
  .content-area {{ padding: 15px; margin-left: 0 !important; }}
}}
@media (max-width: 767.98px) {{
  .card-box h3 {{ font-size: 2.6rem; }}
  .page-header h4 {{ font-size: 1.3rem; }}
  .btn-logout {{ padding: 6px 16px; font-size: 0.85rem; }}
}}
@media (max-width: 575.98px) {{
  .navbar-brand {{ font-size: 0.85rem; letter-spacing: 0.5px; }}
  .navbar-brand i {{ font-size: 1.1rem; margin-right: 6px; }}
  .btn-logout {{ padding: 6px 14px; font-size: 0.8rem; }}
}}
@media (max-width: 400px) {{
  .navbar-brand {{ font-size: 0.75rem; }}
}}
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
      <a href="hospital_dashboard.py?hospital_id={hospital_id}" class="sidebar-link active">
        <i class="fas fa-home"></i> Home
      </a>
      <a href="hospital_vaccination.py?hospital_id={hospital_id}" class="sidebar-link">
        <i class="fa-solid fa-circle-info"></i> Vaccination Info
      </a>
      <a href="hospital_view_application.py?hospital_id={hospital_id}" class="sidebar-link">
        <i class="fa-solid fa-user-pen"></i> Parent Application
      </a>
      <a href="hospital_view_appointment.py?hospital_id={hospital_id}" class="sidebar-link">
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

      <!-- HOME DASHBOARD -->
      <div id="home" class="section">
        <div class="page-header">
          <h4><i class="fas fa-chart-bar"></i> Hospital Dashboard Overview</h4>
        </div>

        <!-- ROW 1: Appointment Overview -->
        <div class="row">
          <div class="col-lg-4 col-md-6 col-12">
            <div class="card-box bg-total">
              <span class="stats-badge">ALL TIME</span>
              <i class="fas fa-calendar-check card-icon"></i>
              <h3>{total_appointments}</h3>
              <p>Total Appointments</p>
            </div>
          </div>
          <div class="col-lg-4 col-md-6 col-12">
            <div class="card-box bg-today">
              <span class="stats-badge">TODAY</span>
              <i class="fas fa-calendar-day card-icon"></i>
              <h3>{today_appointments}</h3>
              <p>Today's Appointments</p>
            </div>
          </div>
          <div class="col-lg-4 col-md-6 col-12">
            <div class="card-box bg-future">
              <span class="stats-badge">FUTURE</span>
              <i class="fas fa-calendar-plus card-icon"></i>
              <h3>{future_appointments}</h3>
              <p>Future Appointments</p>
            </div>
          </div>
        </div>

        <!-- ROW 2: Delay + Completed -->
        <div class="row">
          <div class="col-lg-6 col-md-6 col-12">
            <div class="card-box bg-delay">
              <span class="stats-badge">OVERDUE</span>
              <i class="fas fa-calendar-minus card-icon"></i>
              <h3>{delay_appointments}</h3>
              <p>Delay Appointments</p>
            </div>
          </div>
          <div class="col-lg-6 col-md-6 col-12">
            <div class="card-box bg-complete">
              <span class="stats-badge">COMPLETE</span>
              <i class="fas fa-check-circle card-icon"></i>
              <h3>{completed_vaccination}</h3>
              <p>Completed Vaccination</p>
            </div>
          </div>
        </div>

        <!-- ROW 3: Pending + Cancelled + Pending Appointments -->
        <div class="row">
          <div class="col-lg-4 col-md-6 col-12">
            <div class="card-box bg-pending">
              <span class="stats-badge">PENDING</span>
              <i class="fas fa-clock card-icon"></i>
              <h3>{pending_vaccination}</h3>
              <p>Pending Vaccination</p>
            </div>
          </div>
          <div class="col-lg-4 col-md-6 col-12">
            <div class="card-box bg-cancel">
              <span class="stats-badge">CANCEL</span>
              <i class="fas fa-times-circle card-icon"></i>
              <h3>{cancelled_vaccination}</h3>
              <p>Cancelled Vaccination</p>
            </div>
          </div>
          <div class="col-lg-4 col-md-6 col-12">
            <div class="card-box bg-appending">
              <span class="stats-badge">PENDING</span>
              <i class="fas fa-clock card-icon"></i>
              <h3>{pending_applications}</h3>
              <p>Pending Applications</p>
            </div>
          </div>
        </div>

        <!-- ROW 4: Approved + Rejected Applications -->
        <div class="row">
          <div class="col-lg-6 col-md-6 col-12">
            <div class="card-box bg-apapprove">
              <span class="stats-badge">APPROVE</span>
              <i class="fas fa-check-circle card-icon"></i>
              <h3>{approved_applications}</h3>
              <p>Approved Applications</p>
            </div>
          </div>
          <div class="col-lg-6 col-md-6 col-12">
            <div class="card-box bg-apreject">
              <span class="stats-badge">REJECT</span>
              <i class="fas fa-times-circle card-icon"></i>
              <h3>{rejected_applications}</h3>
              <p>Rejected Applications</p>
            </div>
          </div>
        </div>

      </div><!-- end #home -->
    </div><!-- end content-area -->
  </div><!-- end row -->
</div><!-- end container-fluid -->

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
function toggleSidebar() {{
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  sidebar.classList.toggle('show');
  overlay.classList.toggle('show');
}}

function logout() {{
  if (confirm("Are you sure you want to logout?")) window.location.href = "main.py";
}}

document.addEventListener('click', function(event) {{
  const sidebar = document.getElementById('sidebar');
  const menuToggle = document.querySelector('.mobile-menu-toggle');
  if (window.innerWidth < 992 &&
      !sidebar.contains(event.target) &&
      !menuToggle.contains(event.target) &&
      sidebar.classList.contains('show')) {{
    sidebar.classList.remove('show');
    document.getElementById('sidebarOverlay').classList.remove('show');
  }}
}});

document.addEventListener('DOMContentLoaded', function() {{
  document.getElementById('home').style.display = 'block';
}});
</script>

</body>
</html>""")

con.close()