#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgi
import cgitb
import sys
import os
from datetime import date, timedelta

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")
print("Content-Type: text/html\r\n\r\n")

try:
    con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
    cur = con.cursor()
except Exception as e:
    print(f'<h2 style="color:red;">Database Connection Failed!</h2><pre>{e}</pre>')
    sys.exit()

form = cgi.FieldStorage()
parent_id = form.getvalue("parent_id")

# ── FETCH PARENT EMAIL ────────────────────────────────────────────────────────
try:
    cur.execute("SELECT email_id FROM parent WHERE id = %s", (parent_id,))
    row = cur.fetchone()
    parent_email = row[0] if row else ""
except:
    parent_email = ""

today     = date.today()
today_str = today.strftime("%Y-%m-%d")
day1      = (today + timedelta(days=1)).strftime("%Y-%m-%d")
day2      = (today + timedelta(days=2)).strftime("%Y-%m-%d")
day3      = (today + timedelta(days=3)).strftime("%Y-%m-%d")

def get_count(query, params=None):
    try:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        return cur.fetchone()[0]
    except:
        return 0

my_children          = get_count("SELECT COUNT(*) FROM manage_child WHERE email_id = %s", (parent_email,))
total_appointments   = get_count("SELECT COUNT(*) FROM hospital_appointment WHERE email_id = %s", (parent_email,))
reminders            = get_count("SELECT COUNT(*) FROM hospital_appointment WHERE email_id = %s AND appointment_date >= %s AND status = 'pending'", (parent_email, today_str))
vaccinations_done    = get_count("SELECT COUNT(*) FROM hospital_appointment WHERE email_id = %s AND status = 'completed'", (parent_email,))
pending_vaccinations = get_count("SELECT COUNT(*) FROM hospital_appointment WHERE email_id = %s AND status = 'pending'", (parent_email,))
delay_vaccinations   = get_count("SELECT COUNT(*) FROM hospital_appointment WHERE email_id = %s AND appointment_date < %s AND status != 'completed'", (parent_email, today_str))
cancelled_vaccinations = get_count("SELECT COUNT(*) FROM hospital_appointment WHERE email_id = %s AND status = 'cancelled'", (parent_email,))
applied_hospitals    = get_count("SELECT COUNT(*) FROM parentform WHERE email = %s", (parent_email,))
appointed_hospitals  = get_count("SELECT COUNT(DISTINCT hospital_name) FROM hospital_appointment WHERE email_id = %s", (parent_email,))
total_hospitals      = get_count("SELECT COUNT(*) FROM hospital WHERE status = 'approved'")

# ── FETCH UPCOMING REMINDERS (today + next 3 days, pending only) ─────────────
try:
    notif_cur = con.cursor(pymysql.cursors.DictCursor)
    notif_cur.execute("""
        SELECT c_name, vaccination_name, appointment_date, hospital_name
        FROM hospital_appointment
        WHERE email_id = %s
          AND appointment_date IN (%s, %s, %s, %s)
          AND status = 'pending'
        ORDER BY appointment_date ASC
    """, (parent_email, today_str, day1, day2, day3))
    notification_rows = notif_cur.fetchall()
except:
    notification_rows = []

notif_count = len(notification_rows)

# ── BUILD NOTIFICATION ITEMS HTML ────────────────────────────────────────────
def get_notif_meta(apt_date_str):
    diff = (date.fromisoformat(str(apt_date_str)) - today).days
    if diff == 0: return "fas fa-exclamation-circle", "#ef4444", "TODAY",       "Vaccinate Today!"
    if diff == 1: return "fas fa-bell",               "#f97316", "TOMORROW",    "1 Day Left"
    if diff == 2: return "fas fa-clock",              "#f59e0b", "2 DAYS LEFT", "2 Days Left"
    return              "fas fa-calendar-check",     "#10b981", "3 DAYS LEFT", "3 Days Left"

notif_items_html = ""
for nr in notification_rows:
    icon, color, short_tag, label = get_notif_meta(nr['appointment_date'])
    notif_items_html += f"""
    <div class="nd-item">
      <div class="nd-dot" style="background:{color};">
        <i class="{icon}"></i>
      </div>
      <div class="nd-info">
        <div class="nd-child"><i class="fas fa-baby" style="margin-right:4px;opacity:0.6;"></i>{nr['c_name']}</div>
        <div class="nd-vaccine"><i class="fas fa-syringe" style="margin-right:4px;opacity:0.6;font-size:0.72rem;"></i>{nr['vaccination_name']}</div>
        <div class="nd-hospital"><i class="fas fa-hospital-alt"></i> <strong>{nr['hospital_name']}</strong></div>
      </div>
      <span class="nd-tag" style="background:{color}18;color:{color};border:1px solid {color}44;">{short_tag}</span>
    </div>"""

if not notification_rows:
    notif_items_html = """
    <div class="nd-empty">
      <i class="fas fa-bell-slash"></i>
      <p>No upcoming vaccinations<br>in the next 3 days</p>
    </div>"""

badge_html = f'<span class="notif-badge">{notif_count}</span>' if notif_count > 0 else ""
count_html  = f'<span class="nd-header-count">{notif_count} Alert{"s" if notif_count != 1 else ""}</span>' if notif_count > 0 else ""

# ── HTML ──────────────────────────────────────────────────────────────────────
print("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Parent Dashboard - CVS</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  background: linear-gradient(135deg, #052e16, #22c55e, #dcfce7);
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow-x: hidden;
}

/* ── NAVBAR ── */
.navbar {
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  padding: 12px 20px;
  background: linear-gradient(135deg, #052e16, #22c55e, #dcfce7) !important;
  position: sticky; top: 0; z-index: 1050;
}
.navbar .container-fluid {
  display: flex; align-items: center; flex-wrap: nowrap; gap: 10px;
}
.navbar-brand {
  font-weight: 600; color: white !important;
  letter-spacing: 3px; text-transform: uppercase;
  margin-right: auto;
}
.navbar-brand i {
  margin-right: 10px; color: #d1fae5;
  font-size: 1.5rem; animation: bounce 2s infinite;
}
@keyframes bounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }

.mobile-menu-toggle {
  display: none; flex-shrink: 0;
  background: rgba(255,255,255,0.15);
  border: 1.5px solid rgba(255,255,255,0.35);
  color: white; padding: 6px 12px; border-radius: 8px;
  font-size: 1.2rem; cursor: pointer;
  backdrop-filter: blur(6px); line-height: 1;
}

/* ── BELL BUTTON ── */
.notif-bell-wrap { position: relative; flex-shrink: 0; }
.notif-bell-btn {
  background: rgba(255,255,255,0.15);
  border: 1.5px solid rgba(255,255,255,0.3);
  color: white; width: 44px; height: 44px;
  border-radius: 50%; display: flex;
  align-items: center; justify-content: center;
  font-size: 1.2rem; cursor: pointer;
  transition: all 0.3s; backdrop-filter: blur(6px);
  position: relative;
}
.notif-bell-btn:hover {
  background: rgba(255,255,255,0.28);
  transform: scale(1.1);
}
.notif-bell-btn .bell-icon { animation: bellRing 3s infinite; }
@keyframes bellRing {
  0%,80%,100%{transform:rotate(0)}
  83%{transform:rotate(-18deg)} 87%{transform:rotate(18deg)}
  91%{transform:rotate(-12deg)} 95%{transform:rotate(8deg)}
}
.notif-badge {
  position: absolute; top: -5px; right: -5px;
  background: #ef4444; color: white;
  font-size: 0.62rem; font-weight: 800;
  min-width: 19px; height: 19px; border-radius: 20px;
  display: flex; align-items: center; justify-content: center;
  padding: 0 4px; border: 2px solid #052e16;
  animation: pulseBadge 2s infinite;
}
@keyframes pulseBadge { 0%,100%{transform:scale(1)} 50%{transform:scale(1.25)} }

/* ── NOTIFICATION DROPDOWN ── */
.notif-dropdown {
  position: absolute; top: calc(100% + 12px); right: 0;
  width: 340px; background: white; border-radius: 18px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.22);
  overflow: hidden; display: none;
  animation: dropDown 0.22s ease;
  z-index: 9999;
}
.notif-dropdown.open { display: block; }
@keyframes dropDown {
  from{opacity:0;transform:translateY(-10px)}
  to  {opacity:1;transform:translateY(0)}
}
.nd-header {
  background: linear-gradient(135deg, #052e16, #16a34a);
  padding: 16px 18px;
  display: flex; align-items: center; justify-content: space-between;
}
.nd-header-left { display: flex; align-items: center; gap: 10px; }
.nd-header-left i { color: #fbbf24; font-size: 1.2rem; }
.nd-header-title { color: white; font-weight: 700; font-size: 0.92rem; }
.nd-header-sub   { color: #bbf7d0; font-size: 0.7rem; margin-top: 1px; }
.nd-header-count {
  background: #ef4444; color: white;
  font-size: 0.68rem; font-weight: 800;
  padding: 3px 10px; border-radius: 20px; white-space: nowrap;
}
.nd-body { max-height: 330px; overflow-y: auto; padding: 10px; }
.nd-body::-webkit-scrollbar { width: 4px; }
.nd-body::-webkit-scrollbar-thumb { background: #22c55e; border-radius: 4px; }
.nd-item {
  display: flex; align-items: center; gap: 10px;
  background: #f8fafc; border-radius: 12px;
  padding: 11px 12px; margin-bottom: 8px;
  transition: all 0.2s;
}
.nd-item:last-child { margin-bottom: 0; }
.nd-item:hover { background: #f0fdf4; transform: translateX(3px); }
.nd-dot {
  width: 38px; height: 38px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 0.98rem; flex-shrink: 0;
}
.nd-info { flex: 1; min-width: 0; }
.nd-child   { font-weight: 700; color: #0f172a; font-size: 0.83rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.nd-vaccine { color: #374151; font-size: 0.76rem; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.nd-hospital{ color: #9ca3af; font-size: 0.69rem; margin-top: 2px; }
.nd-hospital i { margin-right: 3px; }
.nd-tag {
  font-size: 0.6rem; font-weight: 800;
  padding: 3px 8px; border-radius: 20px;
  white-space: nowrap; letter-spacing: 0.4px; flex-shrink: 0;
}
.nd-empty { text-align: center; padding: 28px 16px; color: #9ca3af; }
.nd-empty i { font-size: 2rem; margin-bottom: 10px; color: #d1d5db; display: block; }
.nd-empty p { font-size: 0.8rem; line-height: 1.6; }
.nd-footer {
  border-top: 1px solid #e5e7eb; padding: 12px 18px; text-align: center;
}
.nd-footer a {
  color: #16a34a; font-weight: 700;
  font-size: 0.82rem; text-decoration: none;
}
.nd-footer a:hover { color: #15803d; text-decoration: underline; }

/* ── LOGOUT ── */
.btn-logout {
  flex-shrink: 0;
  background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
  border: none; padding: 8px 20px; border-radius: 25px;
  color: white; font-weight: 600; font-size: 0.9rem;
  white-space: nowrap; cursor: pointer;
  box-shadow: 0 4px 15px rgba(238,9,121,0.4);
  transition: all 0.3s ease;
}
.btn-logout:hover { transform: translateY(-2px); color: white; }

/* ── SIDEBAR ── */
.sidebar {
  min-height: 100vh;
  background: linear-gradient(135deg, #052e16, #22c55e);
  box-shadow: 4px 0 20px rgba(0,0,0,0.3); padding: 20px 0;
}
.sidebar-link {
  display: block; padding: 14px 18px; color: #d1fae5;
  text-decoration: none; transition: all 0.3s ease;
  border-left: 4px solid transparent; font-weight: 500; margin: 6px 0;
}
.sidebar-link:hover, .sidebar-link.active {
  background: linear-gradient(90deg, #22c55e, transparent 100%);
  color: #fff; border-left: 4px solid #dcfce7; padding-left: 24px;
}
.sidebar-link i { margin-right: 12px; width: 22px; text-align: center; }
.sidebar-overlay {
  display: none; position: fixed; top: 0; left: 0;
  width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 998;
}
.sidebar-overlay.show { display: block; }

/* ── CONTENT ── */
.content-area { padding: 25px; min-height: 100vh; }
.section { display: none; animation: fadeInUp 0.5s ease-in; }
@keyframes fadeInUp { from{opacity:0;transform:translateY(30px)} to{opacity:1;transform:translateY(0)} }
.page-header {
  background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
  padding: 22px 25px; border-radius: 18px; margin-bottom: 25px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15); border-left: 6px solid #10b981;
}
.page-header h4 {
  margin: 0; color: #0f172a; font-weight: 700;
  font-size: 1.6rem; text-transform: uppercase; letter-spacing: 1px;
}
.page-header h4 i { margin-right: 12px; color: #10b981; }

/* ── STAT CARDS ── */
.card-box {
  border-radius: 20px; padding: 30px; color: white; text-align: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2); transition: all 0.4s ease;
  position: relative; overflow: hidden; cursor: pointer;
  min-height: 160px; display: flex; flex-direction: column;
  justify-content: center; align-items: center; margin-bottom: 15px;
}
.card-box::before {
  content: ''; position: absolute; top: -50%; right: -50%;
  width: 200%; height: 200%; background: rgba(255,255,255,0.1);
  transform: rotate(45deg); transition: all 0.6s ease;
}
.card-box:hover::before { top: -100%; right: -100%; }
.card-box:hover { transform: translateY(-5px) scale(1.02); box-shadow: 0 15px 40px rgba(0,0,0,0.3); }
.card-box h3 { font-size: 3rem; font-weight: 800; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); position: relative; z-index: 1; }
.card-box p  { font-size: 1.1rem; font-weight: 600; margin: 0; color: white; text-transform: uppercase; letter-spacing: 1px; position: relative; z-index: 1; }
.card-icon   { position: absolute; top: 15px; right: 15px; font-size: 2.5rem; opacity: 0.80; z-index: 0; }
.stats-badge {
  position: absolute; top: 14px; left: 14px;
  background: rgba(255,255,255,0.25); padding: 5px 14px; border-radius: 20px;
  font-size: 0.75rem; font-weight: 700; z-index: 1; letter-spacing: 0.5px;
}
.bg-children         { background: linear-gradient(135deg, #b76e79, #f7cac9, #fde2e4); }
.bg-appointment      { background: linear-gradient(135deg, #5c7c2f 0%, #b2f2bb 100%); }
.bg-reminder         { background: linear-gradient(135deg, #ff512f, #f09819, #ffdd00); }
.bg-vaccinated       { background: linear-gradient(135deg, #78350f 0%, #f59e0b 100%); }
.bg-pending-vac      { background: linear-gradient(135deg, #833ab4, #fd1d1d, #fcb045); }
.bg-delay-vac        { background: linear-gradient(135deg, #fbc2eb, #a6c1ee, #fdfbfb); }
.bg-cancel-vac       { background: linear-gradient(135deg, #ff512f, #dd2476, #24c6dc); }
.bg-appoint-hospital { background: linear-gradient(135deg, #f7971e, #ffd200, #fff6b7); }
.bg-apply-hospital   { background: linear-gradient(135deg, #2b1055, #7597de, #b993d6); }
.bg-hospital         { background: linear-gradient(135deg, #00c6ff, #0072ff, #8e2de2); }

/* ── RESPONSIVE ── */
@media (max-width: 991.98px) {
  .mobile-menu-toggle { display: flex; align-items: center; justify-content: center; }
  .sidebar {
    position: fixed; left: -100%; top: 0;
    width: 280px; height: 100vh; z-index: 999;
    transition: left 0.3s ease; overflow-y: auto;
  }
  .sidebar.show { left: 0; }
  .content-area { padding: 15px; margin-left: 0 !important; }
  .navbar-brand { font-size: 1rem; letter-spacing: 1px; }
  .navbar-brand i { font-size: 1.3rem; }
  .notif-dropdown { width: 450px; right: -115px; }
}
@media (max-width: 767.98px) {
  .card-box h3 { font-size: 2.6rem; }
  .page-header h4 { font-size: 1.3rem; }
  .content-area { padding: 12px; }
  .btn-logout { padding: 6px 16px; font-size: 0.85rem; }
  .notif-dropdown { width: 350px; right: -95px; }
}
@media (max-width: 575.98px) {
  .navbar-brand { font-size: 0.85rem; letter-spacing: 0.5px; }
  .navbar-brand i { font-size: 1.1rem; margin-right: 6px; }
  .btn-logout { padding: 6px 14px; font-size: 0.8rem; }
  .card-box h3 { font-size: 2.2rem; }
  .notif-dropdown { width: 300px; right: -75px; }
}
@media (max-width: 400px) { .navbar-brand { font-size: 0.75rem; } }
</style>
</head>
<body>
""")

print(f"""
<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container-fluid">

    <!-- Mobile sidebar toggle -->
    <button class="mobile-menu-toggle" onclick="toggleSidebar()">
      <i class="fas fa-bars"></i>
    </button>

    <!-- Brand -->
    <span class="navbar-brand ms-2">
      <i class="fa-solid fa-users"></i> CVS - Parent
    </span>

    <!-- ── NOTIFICATION BELL ── -->
    <div class="notif-bell-wrap" id="notifWrap">
      <button class="notif-bell-btn" onclick="toggleNotif(event)" title="Vaccination Reminders">
        <i class="fas fa-bell bell-icon"></i>
        {badge_html}
      </button>

      <div class="notif-dropdown" id="notifDropdown">
        <!-- Header -->
        <div class="nd-header">
          <div class="nd-header-left">
            <i class="fas fa-bell"></i>
            <div>
              <div class="nd-header-title">Vaccination Reminders</div>
              <div class="nd-header-sub">Next 3 days &nbsp;·&nbsp; Pending only</div>
            </div>
          </div>
          {count_html}
        </div>
        <!-- Items -->
        <div class="nd-body">
          {notif_items_html}
        </div>
        <!-- Footer -->
        <div class="nd-footer">
          <a href="parent_reminder.py?parent_id={parent_id}">
            <i class="fas fa-list-ul" style="margin-right:5px;"></i>View All Reminders
          </a>
        </div>
      </div>
    </div>

    <!-- Logout -->
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
      <a href="parent_dashboard.py?parent_id={parent_id}" class="sidebar-link active" onclick="closeSidebarMobile()"><i class="fas fa-home"></i> Home</a>
      <a href="parent_vaccination.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fa-solid fa-circle-info"></i> Vaccination Info</a>
      <a href="parent_manage_child.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-baby"></i> Manage Children</a>
      <a href="parent_view_hospital.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fa-solid fa-eye"></i> View Hospital</a>
      <a href="parent_booked_appointment.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fa-solid fa-calendar-day"></i> Booked Appointments
      </a>
      <a href="parent_my_appointment.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-calendar-check"></i> My Appointments</a>
      <a href="parent_reminder.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-bell"></i> My Reminders</a>
      <a href="parent_profile.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-user-circle"></i> My Profile</a>
      <a href="parent_feedback.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-comment-dots"></i> Feedback</a>
      <a href="parent_help.py?parent_id={parent_id}" class="sidebar-link">
        <i class="fas fa-circle-question"></i> Help & Support
      </a>
    </div>

    <!-- MAIN CONTENT -->
    <div class="col-lg-10 col-md-9 col-12 content-area">
      <div id="home" class="section">

        <div class="page-header">
          <h4><i class="fas fa-chart-line"></i> Parent Dashboard Overview</h4>
        </div>

        <!-- ROW 1 -->
        <div class="row">
          <div class="col-lg-4 col-md-6 col-12">
            <div class="card-box bg-children">
              <span class="stats-badge">REGISTERED</span>
              <i class="fas fa-baby card-icon"></i>
              <h3>{my_children}</h3>
              <p>My Children</p>
            </div>
          </div>
          <div class="col-lg-4 col-md-6 col-12">
            <div class="card-box bg-appointment">
              <span class="stats-badge">SCHEDULED</span>
              <i class="fas fa-calendar-alt card-icon"></i>
              <h3>{total_appointments}</h3>
              <p>Appointments</p>
            </div>
          </div>
          <div class="col-lg-4 col-md-6 col-12">
            <div class="card-box bg-reminder">
              <span class="stats-badge">ACTIVE</span>
              <i class="fas fa-bell card-icon"></i>
              <h3>{reminders}</h3>
              <p>Reminders</p>
            </div>
          </div>
        </div>

        <!-- ROW 2 -->
        <div class="row">
          <div class="col-lg-6 col-md-6 col-12">
            <div class="card-box bg-vaccinated">
              <span class="stats-badge">COMPLETED</span>
              <i class="fas fa-syringe card-icon"></i>
              <h3>{vaccinations_done}</h3>
              <p>Vaccinations Done</p>
            </div>
          </div>
          <div class="col-lg-6 col-md-6 col-12">
            <div class="card-box bg-pending-vac">
              <span class="stats-badge">PENDING</span>
              <i class="fas fa-exclamation-circle card-icon"></i>
              <h3>{pending_vaccinations}</h3>
              <p>Pending Vaccinations</p>
            </div>
          </div>
        </div>

        <!-- ROW 3 -->
        <div class="row">
          <div class="col-lg-4 col-md-6 col-12">
            <div class="card-box bg-delay-vac">
              <span class="stats-badge">OVERDUE</span>
              <i class="fas fa-calendar-minus card-icon"></i>
              <h3>{delay_vaccinations}</h3>
              <p>Delayed Vaccination</p>
            </div>
          </div>
          <div class="col-lg-4 col-md-6 col-12">
            <div class="card-box bg-cancel-vac">
              <span class="stats-badge">CANCEL</span>
              <i class="fas fa-circle-xmark card-icon"></i>
              <h3>{cancelled_vaccinations}</h3>
              <p>Cancelled Vaccination</p>
            </div>
          </div>
          <div class="col-lg-4 col-md-6 col-12">
            <div class="card-box bg-apply-hospital">
              <span class="stats-badge">APPLIED</span>
              <i class="fas fa-hospital-user card-icon"></i>
              <h3>{applied_hospitals}</h3>
              <p>Applied Hospitals</p>
            </div>
          </div>
        </div>

        <!-- ROW 4 -->
        <div class="row">
          <div class="col-lg-6 col-md-6 col-12">
            <div class="card-box bg-appoint-hospital">
              <span class="stats-badge">APPOINTED</span>
              <i class="fas fa-notes-medical card-icon"></i>
              <h3>{appointed_hospitals}</h3>
              <p>Appointed Hospitals</p>
            </div>
          </div>
          <div class="col-lg-6 col-md-6 col-12">
            <div class="card-box bg-hospital">
              <span class="stats-badge">TOTAL</span>
              <i class="fas fa-hospital card-icon"></i>
              <h3>{total_hospitals}</h3>
              <p>Vaccination Hospitals</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
/* ── Sidebar ── */
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

/* ── Notification Bell ── */
function toggleNotif(e) {{
  e.stopPropagation();
  document.getElementById('notifDropdown').classList.toggle('open');
}}

/* Close dropdown + sidebar when clicking outside */
document.addEventListener('click', function(e) {{
  const wrap = document.getElementById('notifWrap');
  const dd   = document.getElementById('notifDropdown');
  if (dd && wrap && !wrap.contains(e.target)) {{
    dd.classList.remove('open');
  }}
  const sidebar    = document.getElementById('sidebar');
  const menuToggle = document.querySelector('.mobile-menu-toggle');
  if (window.innerWidth < 992 &&
      sidebar && sidebar.classList.contains('show') &&
      menuToggle &&
      !sidebar.contains(e.target) &&
      !menuToggle.contains(e.target)) {{
    closeSidebarMobile();
  }}
}});

document.addEventListener('DOMContentLoaded', function() {{
  document.getElementById('home').style.display = 'block';
}});
</script>
</body>
</html>
""")

con.close()