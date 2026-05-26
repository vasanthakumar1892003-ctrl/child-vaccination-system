#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgitb
import sys
from datetime import date

# Enable error debugging
cgitb.enable()

# UTF-8 Support
sys.stdout.reconfigure(encoding="utf-8")

# Correct CGI Header
print("Content-Type: text/html\n")

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
    print("<html><body>")
    print("<h2>Database Connection Failed!</h2>")
    print("<p>Error:</p>", e)
    print("</body></html>")
    sys.exit()

# ── FETCH COUNTS FROM DATABASE ──────────────────────────────────────────────

def get_count(query, params=None):
    try:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        return cur.fetchone()[0]
    except:
        return 0

today = date.today().strftime("%Y-%m-%d")

hospital    = get_count("SELECT COUNT(*) FROM hospital")
hospital_approved   = get_count("SELECT COUNT(*) FROM hospital WHERE status = 'approved'")
hospital_rejected   = get_count("SELECT COUNT(*) FROM hospital WHERE status = 'rejected'")

parent_pending      = get_count("SELECT COUNT(*) FROM parent WHERE status = 'pending'")
parent_approved     = get_count("SELECT COUNT(*) FROM parent WHERE status = 'approved'")
parent_rejected     = get_count("SELECT COUNT(*) FROM parent WHERE status = 'rejected'")

children_total      = get_count("SELECT COUNT(*) FROM manage_child")

children_vaccinated = get_count("SELECT COUNT(*) FROM hospital_appointment WHERE status = 'completed'")
children_not_vac    = get_count("SELECT COUNT(*) FROM hospital_appointment WHERE status = 'cancelled'")

appointments_upcoming = get_count(
    "SELECT COUNT(*) FROM hospital_appointment WHERE appointment_date >= %s AND status = 'pending'",
    (today,)
)

# ── HTML ─────────────────────────────────────────────────────────────────────

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Admin Dashboard - CVS</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">

<!-- BOOTSTRAP CSS -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- FONT AWESOME -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

<style>
* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

body {{
  background: linear-gradient(135deg, #3b021f, #ec4899, #fdf2f8);
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow-x: hidden;
}}

/* NAVBAR STYLING */
.navbar {{
  background: linear-gradient(135deg, #3b021f, #ec4899, #fdf2f8) !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  padding: 15px 20px;
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
  color: #fda4af;
  font-size: 1.5rem;
  animation: pulse 2s infinite;
}}

@keyframes pulse {{
  0%, 100% {{ transform: scale(1); }}
  50% {{ transform: scale(1.1); }}
}}

/* Center brand text on mobile when hamburger is visible */
@media (max-width: 991.98px) {{
  .navbar-brand {{
    position: absolute;
    left: 45%;
    transform: translateX(-50%);
    margin: 0 !important;
  }}
}}

/* MOBILE MENU TOGGLE */
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

.btn-logout:hover {{
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(238, 9, 121, 0.6);
  color: white;
}}

/* SIDEBAR STYLING */
.sidebar {{
  min-height: 100vh;
  background: linear-gradient(135deg, #3b021f, #ec4899);
  box-shadow: 4px 0 15px rgba(0, 0, 0, 0.2);
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

.sidebar-link i {{
  margin-right: 10px;
  width: 20px;
  text-align: center;
}}

/* CONTENT AREA */
.content-area {{
  padding: 20px;
  min-height: 100vh;
}}

.section {{
  display: none;
  animation: fadeIn 0.5s ease-in;
}}

@keyframes fadeIn {{
  from {{ opacity: 0; transform: translateY(20px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

.page-header {{
  background: white;
  padding: 20px;
  border-radius: 15px;
  margin-bottom: 20px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  border-left: 5px solid #667eea;
}}

.page-header h4 {{
  margin: 0;
  color: #2c3e50;
  font-weight: 700;
  font-size: 1.5rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}}

.page-header h4 i {{
  margin-right: 10px;
  color: #667eea;
}}

/* DASHBOARD CARDS */
.card-box {{
  border-radius: 20px;
  padding: 35px;
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

.card-box:hover::before {{
  top: -100%;
  right: -100%;
}}

.card-box:hover {{
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
}}

.card-box h3 {{
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 1;
}}

.card-box p, .card-box a {{
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  color: white;
  text-decoration: none;
  text-transform: uppercase;
  letter-spacing: 1px;
  position: relative;
  z-index: 1;
}}

.card-box a:hover {{
  text-decoration: underline;
}}

.card-icon {{
  position: absolute;
  top: 15px;
  right: 15px;
  font-size: 2.5rem;
  opacity: 0.80;
  z-index: 0;
}}

/* CARD COLORS */
.bg-registered    {{ background: linear-gradient(135deg, #00c6ff, #0072ff, #8e2de2); }}
.bg-haccepted     {{ background: linear-gradient(135deg, #11998e, #38ef7d, #b7f8db); }}
.bg-hrejected     {{ background: linear-gradient(135deg, #833ab4, #fd1d1d, #fcb045); }}
.bg-parent        {{ background: linear-gradient(135deg, #f7971e, #ffd200, #fff6b7); }}
.bg-child         {{ background: linear-gradient(135deg, #b76e79, #f7cac9, #fde2e4); }}
.bg-paccepted     {{ background: linear-gradient(135deg, #5c7c2f 0%, #b2f2bb 100%); }}
.bg-prejected     {{ background: linear-gradient(135deg, #ff512f, #dd2476, #24c6dc); }}
.bg-vaccinated    {{ background: linear-gradient(135deg, #2b1055, #7597de, #b993d6); }}
.bg-notvac        {{ background: linear-gradient(135deg, #fbc2eb, #a6c1ee, #fdfbfb); }}
.bg-appointments  {{ background: linear-gradient(135deg, #ff512f, #f09819, #ffdd00); }}

/* TABLE STYLING */
.table-container {{
  background: white;
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}}

.table {{
  margin: 0;
  border-radius: 10px;
  overflow: hidden;
  width: 100%;
}}

.table thead {{
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}}

.table thead th {{
  border: none;
  padding: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.85rem;
  white-space: nowrap;
}}

.table tbody tr {{
  transition: all 0.3s ease;
}}

.table tbody tr:hover {{
  background: #f8f9ff;
  transform: scale(1.01);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}}

.table tbody td {{
  padding: 12px;
  vertical-align: middle;
  border-bottom: 1px solid #e9ecef;
  font-size: 0.9rem;
}}

/* BUTTONS */
.btn-action {{
  padding: 6px 15px;
  border-radius: 20px;
  border: none;
  font-weight: 600;
  transition: all 0.3s ease;
  margin: 3px;
  font-size: 0.85rem;
  white-space: nowrap;
}}

.btn-accept {{
  background: linear-gradient(135deg, #198754 0%, #51cf66 100%);
  color: white;
  box-shadow: 0 4px 10px rgba(25, 135, 84, 0.3);
}}

.btn-accept:hover {{
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(25, 135, 84, 0.5);
  color: white;
}}

.btn-reject-action {{
  background: linear-gradient(135deg, #dc3545 0%, #ff6b6b 100%);
  color: white;
  box-shadow: 0 4px 10px rgba(220, 53, 69, 0.3);
}}

.btn-reject-action:hover {{
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(220, 53, 69, 0.5);
  color: white;
}}

.btn-export {{
  padding: 10px 25px;
  border-radius: 25px;
  font-weight: 600;
  margin: 8px 5px;
  transition: all 0.3s ease;
  border: none;
  font-size: 0.95rem;
}}

.btn-primary {{
  background: linear-gradient(135deg, #0d6efd 0%, #4dabf7 100%);
  box-shadow: 0 4px 15px rgba(13, 110, 253, 0.4);
}}

.btn-primary:hover {{
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(13, 110, 253, 0.6);
}}

.btn-secondary {{
  background: linear-gradient(135deg, #6c757d 0%, #adb5bd 100%);
  box-shadow: 0 4px 15px rgba(108, 117, 125, 0.4);
}}

.btn-secondary:hover {{
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(108, 117, 125, 0.6);
}}

/* STATS BADGE */
.stats-badge {{
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(255, 255, 255, 0.3);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
  z-index: 1;
}}

/* SIDEBAR OVERLAY */
.sidebar-overlay {{
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 998;
}}

.sidebar-overlay.show {{
  display: block;
}}

/* ===== RESPONSIVE MEDIA QUERIES ===== */

/* Tablets and below (992px) */
@media (max-width: 991.98px) {{
  /* Show hamburger in navbar */
  .mobile-menu-toggle {{
    display: flex;
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

  .sidebar.show {{
    left: 0;
  }}

  .content-area {{
    padding: 15px;
    margin-left: 0 !important;
  }}

  .navbar-brand {{
    font-size: 1rem;
    letter-spacing: 1px;
  }}

  .navbar-brand i {{
    font-size: 1.3rem;
  }}
}}

/* Mobile devices (768px and below) */
@media (max-width: 767.98px) {{
  .card-box h3 {{
    font-size: 2.5rem;
  }}

  .card-box p, .card-box a {{
    font-size: 0.95rem;
  }}

  .page-header h4 {{
    font-size: 1.2rem;
  }}

  .page-header {{
    padding: 15px;
  }}

  .content-area {{
    padding: 10px;
  }}

  .card-box {{
    min-height: 140px;
    padding: 20px;
  }}

  .table-container {{
    padding: 15px;
  }}

  .btn-export {{
    padding: 8px 20px;
    font-size: 0.85rem;
    display: block;
    width: 100%;
    margin: 5px 0;
  }}

  .btn-logout {{
    padding: 6px 15px;
    font-size: 0.8rem;
  }}
}}

/* Small mobile devices (576px and below) */
@media (max-width: 575.98px) {{
  .navbar-brand {{
    font-size: 0.85rem;
    letter-spacing: 0.5px;
  }}

  .navbar-brand i {{
    font-size: 1.1rem;
    margin-right: 6px;
  }}

  .card-box h3 {{
    font-size: 2rem;
  }}

  .card-box p, .card-box a {{
    font-size: 0.85rem;
  }}

  .card-box {{
    min-height: 130px;
    padding: 15px;
  }}

  .btn-action {{
    padding: 5px 10px;
    font-size: 0.75rem;
    margin: 2px;
    display: inline-block;
  }}

  .table thead th {{
    font-size: 0.7rem;
    padding: 8px 5px;
  }}

  .table tbody td {{
    padding: 8px 5px;
    font-size: 0.8rem;
  }}

  .page-header h4 {{
    font-size: 1rem;
  }}

  .page-header h4 i {{
    display: block;
    margin-bottom: 5px;
  }}

  .card-icon {{
    font-size: 2rem;
    top: 10px;
    right: 10px;
  }}

  .stats-badge {{
    font-size: 0.65rem;
    padding: 3px 8px;
  }}
}}

/* Extra small devices (400px and below) */
@media (max-width: 400px) {{
  .navbar-brand {{
    font-size: 0.75rem;
  }}

  .card-box h3 {{
    font-size: 1.8rem;
  }}

  .card-box p, .card-box a {{
    font-size: 0.75rem;
  }}
}}
</style>

</head>

<body>

<!-- NAVBAR -->
<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container-fluid">

    <!-- Hamburger toggle (visible only on mobile/tablet) -->
    <button class="mobile-menu-toggle" onclick="toggleSidebar()">
      <i class="fas fa-bars"></i>
    </button>

    <span class="navbar-brand ms-2">
      <i class="fa-solid fa-hands-holding-child"></i> CVS - Admin
    </span>

    <button class="btn btn-logout ms-auto" onclick="logout()">
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
      <a href="admin_dashboard.py" class="sidebar-link active">
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

      <a href="admin_view_appointment.py" class="sidebar-link">
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

    <!-- CONTENT -->
    <div class="col-lg-10 col-md-9 col-12 content-area">

      <!-- HOME DASHBOARD -->
      <div id="home" class="section">
        <div class="page-header">
          <h4><i class="fas fa-chart-line"></i> Dashboard Overview</h4>
        </div>

        <div class="row">
          <div class="col-lg-4 col-md-6 col-sm-6 col-12">
            <div class="card-box bg-registered">
              <span class="stats-badge">PENDING</span>
              <i class="fas fa-hospital-alt card-icon"></i>
              <h3>{hospital}</h3>
              <p>Hospitals Registered</p>
            </div>
          </div>
          <div class="col-lg-4 col-md-6 col-sm-6 col-12">
            <div class="card-box bg-haccepted">
              <span class="stats-badge">ACTIVE</span>
              <i class="fas fa-check-circle card-icon"></i>
              <h3>{hospital_approved}</h3>
              <p>Hospitals Approved</p>
            </div>
          </div>
          <div class="col-lg-4 col-md-6 col-sm-6 col-12">
            <div class="card-box bg-hrejected">
              <span class="stats-badge">DECLINED</span>
              <i class="fas fa-times-circle card-icon"></i>
              <h3>{hospital_rejected}</h3>
              <p>Hospitals Rejected</p>
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-lg-6 col-md-6 col-12">
            <div class="card-box bg-parent">
              <span class="stats-badge">PENDING</span>
              <i class="fas fa-user-friends card-icon"></i>
              <h3>{parent_pending}</h3>
              <p>Parents Registered</p>
            </div>
          </div>
          <div class="col-lg-6 col-md-6 col-12">
            <div class="card-box bg-child">
              <span class="stats-badge">TOTAL</span>
              <i class="fas fa-baby card-icon"></i>
              <h3>{children_total}</h3>
              <p>Children Registered</p>
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-lg-6 col-md-6 col-12">
            <div class="card-box bg-paccepted">
              <span class="stats-badge">ACTIVE</span>
              <i class="fas fa-check-circle card-icon"></i>
              <h3>{parent_approved}</h3>
              <p>Parents Approved</p>
            </div>
          </div>
          <div class="col-lg-6 col-md-6 col-12">
            <div class="card-box bg-prejected">
              <span class="stats-badge">DECLINED</span>
              <i class="fas fa-times-circle card-icon"></i>
              <h3>{parent_rejected}</h3>
              <p>Parents Rejected</p>
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-lg-4 col-md-6 col-sm-6 col-12">
            <div class="card-box bg-vaccinated">
              <span class="stats-badge">COMPLETED</span>
              <i class="fas fa-syringe card-icon"></i>
              <h3>{children_vaccinated}</h3>
              <p>Children Vaccinated</p>
            </div>
          </div>
          <div class="col-lg-4 col-md-6 col-sm-6 col-12">
            <div class="card-box bg-notvac">
              <span class="stats-badge">PENDING</span>
              <i class="fas fa-exclamation-triangle card-icon"></i>
              <h3>{children_not_vac}</h3>
              <p>Not Vaccinated</p>
            </div>
          </div>
          <div class="col-lg-4 col-md-6 col-sm-6 col-12">
            <div class="card-box bg-appointments">
              <span class="stats-badge">SCHEDULED</span>
              <i class="fas fa-calendar-alt card-icon"></i>
              <h3>{appointments_upcoming}</h3>
              <p>Appointments Upcoming</p>
            </div>
          </div>
        </div>
      </div><!-- /home section -->

    </div><!-- /content-area -->
  </div><!-- /row -->
</div><!-- /container-fluid -->

<!-- BOOTSTRAP JS -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

<!-- JAVASCRIPT FUNCTIONS -->
<script>
function logout() {{
  if (confirm("Are you sure you want to logout?")) {{
    window.location.href = "main.py";
  }}
}}

function toggleSidebar() {{
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  sidebar.classList.toggle('show');
  overlay.classList.toggle('show');
}}

// Close sidebar when clicking outside on mobile
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

// Show home section on load
document.addEventListener('DOMContentLoaded', function() {{
  document.getElementById('home').style.display = 'block';
}});
</script>

</body>
</html>
""")

con.close()