#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgi
import cgitb
import sys
import os
from collections import OrderedDict

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")

form = cgi.FieldStorage()
parent_id = form.getvalue("parent_id") or ""

print("Content-Type: text/html\r\n\r\n")

try:
    con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
    cur = con.cursor()
except Exception as e:
    print(f'<h2 style="color:red;">Database Connection Failed!</h2><pre>{e}</pre>')
    sys.exit()

try:
    cur.execute("SELECT age_group, vaccine_name, description FROM vaccination_schedule ORDER BY id ASC")
    rows = cur.fetchall()
except Exception as e:
    print(f'<h2 style="color:red;">Query Failed!</h2><pre>{e}</pre>')
    con.close()
    sys.exit()

# Group by age_group
grouped = OrderedDict()
for row in rows:
    age_group, vaccine_name, description = row
    desc = description if description else ""
    if age_group not in grouped:
        grouped[age_group] = []
    grouped[age_group].append((vaccine_name, desc))

milestone_colors = [
    ("#e74c3c", "rgba(231,76,60,0.12)"),
    ("#e67e22", "rgba(230,126,34,0.12)"),
    ("#f1c40f", "rgba(241,196,15,0.12)"),
    ("#2ecc71", "rgba(46,204,113,0.12)"),
    ("#1abc9c", "rgba(26,188,156,0.12)"),
    ("#3498db", "rgba(52,152,219,0.12)"),
    ("#9b59b6", "rgba(155,89,182,0.12)"),
    ("#e91e63", "rgba(233,30,99,0.12)"),
]

tbody_rows = ""
if grouped:
    for i, (age_group, vaccines) in enumerate(grouped.items()):
        border_color, bg_color = milestone_colors[i % len(milestone_colors)]
        count = len(vaccines)
        for j, (vaccine, description) in enumerate(vaccines):
            if j == 0:
                tbody_rows += (
                    "<tr>"
                    "<td class='age-milestone' rowspan='" + str(count) + "' "
                    "style='border-left: 5px solid " + border_color + "; "
                    "background: " + bg_color + " !important; "
                    "color: " + border_color + " !important; "
                    "vertical-align: middle; text-align: center; font-weight: bold; font-size: 1.05em;'>"
                    + age_group +
                    "</td>"
                    "<td class='vaccine-list'>" + vaccine + "</td>"
                    "<td class='disease-list'>" + description + "</td>"
                    "</tr>"
                )
            else:
                tbody_rows += (
                    "<tr>"
                    "<td class='vaccine-list'>" + vaccine + "</td>"
                    "<td class='disease-list'>" + description + "</td>"
                    "</tr>"
                )
else:
    tbody_rows = "<tr><td colspan='3' style='text-align:center; color:#718096;'>No vaccination schedule records found.</td></tr>"

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<title>Childhood Vaccination Schedule - CVS</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  background: linear-gradient(135deg, #052e16, #22c55e, #dcfce7);
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow-x: hidden;
}}
.navbar {{
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  padding: 15px 20px;
  background: linear-gradient(135deg, #052e16, #22c55e, #dcfce7) !important;
}}
.navbar .container-fluid {{
  display: flex; flex-direction: row; align-items: center; flex-wrap: nowrap;
}}
.navbar-brand {{
  font-weight: 600; color: white !important; letter-spacing: 2px; text-transform: uppercase;
}}
.navbar-brand i {{ margin-right: 10px; color: #d1fae5; font-size: 1.5rem; animation: bounce 2s infinite; }}
@keyframes bounce {{
  0%, 100% {{ transform: translateY(0); }}
  50% {{ transform: translateY(-5px); }}
}}
.mobile-menu-toggle {{
  display: none; flex-shrink: 0; align-self: center;
  background: rgba(255,255,255,0.15); border: 1.5px solid rgba(255,255,255,0.35);
  color: white; padding: 6px 12px; border-radius: 8px; font-size: 1.2rem;
  cursor: pointer; transition: all 0.3s ease; backdrop-filter: blur(6px);
  line-height: 1; margin-right: 12px;
}}
.mobile-menu-toggle:hover {{
  background: rgba(255,255,255,0.28); border-color: rgba(255,255,255,0.6); color: white;
}}
.btn-logout {{
  flex-shrink: 0;
  background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
  border: none; padding: 8px 20px; border-radius: 25px; color: white;
  font-weight: 600; box-shadow: 0 4px 15px rgba(238,9,121,0.4);
  font-size: 0.9rem; white-space: nowrap; transition: all 0.3s ease;
}}
.btn-logout:hover {{ transform: translateY(-2px); color: white; }}
.sidebar {{
  min-height: 100vh;
  background: linear-gradient(135deg, #052e16, #22c55e);
  box-shadow: 4px 0 20px rgba(0,0,0,0.3); padding: 20px 0;
}}
.sidebar-link {{
  display: block; padding: 14px 18px; color: #d1fae5; text-decoration: none;
  transition: all 0.3s ease; border-left: 4px solid transparent;
  font-weight: 500; margin: 6px 0;
}}
.sidebar-link:hover, .sidebar-link.active {{
  background: linear-gradient(90deg, #22c55e, transparent 100%);
  color: #fff; border-left: 4px solid #dcfce7; padding-left: 24px;
}}
.sidebar-link i {{ margin-right: 12px; width: 22px; text-align: center; }}
.sidebar-overlay {{
  display: none; position: fixed; top: 0; left: 0;
  width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 998; backdrop-filter: blur(2px);
}}
.sidebar-overlay.show {{ display: block; }}
.content-area {{ padding: 25px; min-height: 100vh; }}
.vaccination-container {{
  background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
  padding: 40px; border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.15); margin: 0 auto;
}}
.vaccination-header {{
  text-align: center; margin-bottom: 40px;
  padding-bottom: 20px; border-bottom: 3px solid #10b981;
}}
.vaccination-header .icon {{ font-size: 3em; margin-bottom: 15px; }}
.vaccination-header h1 {{
  color: #2d3748; font-size: 2.5em; margin-bottom: 10px;
  text-transform: uppercase; letter-spacing: 2px;
}}
.vaccination-header .subtitle {{ color: #718096; font-size: 1.1em; font-weight: 300; }}
.vaccination-table {{
  width: 100%; border-collapse: collapse;
  margin-top: 30px; overflow: hidden; border-radius: 15px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}}
.vaccination-table thead {{
  background: linear-gradient(135deg, #052e16, #22c55e 60%);
}}
.vaccination-table th {{
  color: white; font-weight: 600; padding: 20px 15px; text-align: left;
  font-size: 1em; text-transform: uppercase; letter-spacing: 1px;
}}
.vaccination-table tbody tr {{ transition: all 0.3s ease; background: white; }}
.vaccination-table tbody tr:nth-child(odd) {{ background: #f7fafc; }}
.vaccination-table tbody tr:hover {{
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
}}
.vaccination-table td {{
  padding: 18px 15px; border-bottom: 1px solid #e2e8f0;
  vertical-align: middle; font-size: 0.95em; color: #4a5568;
}}
.age-milestone {{ border-bottom: 2px solid #6ee7b7 !important; }}
.vaccine-list {{ line-height: 1.6; color: #2c5282; font-weight: 500; }}
.disease-list {{ line-height: 1.6; color: #276749; }}
.vaccination-footer {{
  margin-top: 30px; padding: 20px;
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  border-radius: 10px; text-align: center; color: #065f46; font-weight: 500;
}}
@media (max-width: 991.98px) {{
  .mobile-menu-toggle {{ display: flex; align-items: center; justify-content: center; }}
  .sidebar {{
    position: fixed; left: -100%; top: 0;
    width: 280px; height: 100vh; z-index: 999; transition: left 0.3s ease; overflow-y: auto;
  }}
  .sidebar.show {{ left: 0; }}
  .content-area {{ padding: 15px; margin-left: 0 !important; }}
  .vaccination-container {{ padding: 25px; }}
  .vaccination-header h1 {{ font-size: 1.8em; }}
}}
@media (max-width: 767.98px) {{
  .vaccination-container {{ padding: 20px; }}
  .vaccination-table {{ font-size: 0.85em; }}
  .vaccination-table th, .vaccination-table td {{ padding: 10px 8px; }}
  .vaccination-header h1 {{ font-size: 1.5em; }}
  .vaccination-header .subtitle {{ font-size: 0.9em; }}
  .content-area {{ padding: 12px; }}
  .btn-logout {{ padding: 6px 16px; font-size: 0.85rem; }}
}}
@media (max-width: 575.98px) {{
  .navbar-brand {{ font-size: 0.85rem; letter-spacing: 0.5px; }}
  .navbar-brand i {{ font-size: 1.1rem; margin-right: 6px; }}
  .btn-logout {{ padding: 6px 14px; font-size: 0.8rem; }}
  .vaccination-container {{ padding: 15px; }}
  .vaccination-header .icon {{ font-size: 2em; }}
  .vaccination-header h1 {{ font-size: 1.2em; }}
  .vaccination-table th, .vaccination-table td {{ padding: 8px 5px; font-size: 0.75em; }}
}}
@media (max-width: 400px) {{ .navbar-brand {{ font-size: 0.75rem; }} }}
</style>
</head>
<body>

<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container-fluid">
    <button class="mobile-menu-toggle" onclick="toggleSidebar()">
      <i class="fas fa-bars"></i>
    </button>
    <span class="navbar-brand ms-2">
      <i class="fa-solid fa-users"></i> CVS - Parent
    </span>
    <button class="btn btn-logout" onclick="logout()">
      <i class="fas fa-sign-out-alt"></i> Logout
    </button>
  </div>
</nav>

<div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

<div class="container-fluid">
  <div class="row">
    <div class="col-lg-2 col-md-3 sidebar p-0" id="sidebar">
      <a href="parent_dashboard.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fas fa-home"></i> Home
      </a>
      <a href="parent_vaccination.py?parent_id={parent_id}" class="sidebar-link active" onclick="closeSidebarMobile()">
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
      <a href="parent_chat.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fas fa-comments"></i> Chats
      </a>
      <a href="parent_help.py?parent_id={parent_id}" class="sidebar-link">
        <i class="fas fa-circle-question"></i> Help &amp; Support
      </a>
    </div>

    <div class="col-lg-10 col-md-9 col-12 content-area">
      <div class="vaccination-container">
        <div class="vaccination-header">
          <div class="icon">💉🩺</div>
          <h1>Childhood Vaccination Schedule</h1>
          <p class="subtitle">Comprehensive Immunization Timeline from Birth to 10 Years</p>
        </div>

        <div class="table-responsive">
          <table class="vaccination-table">
            <thead>
              <tr>
                <th>Age Milestone</th>
                <th>Recommended Vaccines</th>
                <th>Protection Against (Diseases)</th>
              </tr>
            </thead>
            <tbody>
              {tbody_rows}
            </tbody>
          </table>
        </div>

        <div class="vaccination-footer">
          ⚕️ Always consult with your healthcare provider for personalized vaccination schedules ⚕️
        </div>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
function toggleSidebar() {{
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  sidebar.classList.toggle('show');
  overlay.classList.toggle('show');
}}
function closeSidebarMobile() {{
  if (window.innerWidth < 992) {{
    document.getElementById('sidebar').classList.remove('show');
    document.getElementById('sidebarOverlay').classList.remove('show');
  }}
}}
function logout() {{
  if (confirm('Are you sure you want to logout?')) {{
    window.location.href = 'main.py';
  }}
}}
document.addEventListener('click', function(event) {{
  const sidebar = document.getElementById('sidebar');
  const menuToggle = document.querySelector('.mobile-menu-toggle');
  if (window.innerWidth < 992 &&
      !sidebar.contains(event.target) &&
      !menuToggle.contains(event.target) &&
      sidebar.classList.contains('show')) {{
    closeSidebarMobile();
  }}
}});
</script>
</body>
</html>""")

con.close()