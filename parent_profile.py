#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgi
import cgitb
import sys
import os

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")
print("Content-Type: text/html\r\n\r\n")

# ============ DATABASE CONNECTION ============
try:
    con = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="cvsdp",
        cursorclass=pymysql.cursors.DictCursor
    )
    cur = con.cursor()
except Exception as e:
    print(f'<h2 style="color:red;">Database Connection Failed!</h2><pre>{e}</pre>')
    sys.exit()

# ============ GET & VALIDATE parent_id ============
form = cgi.FieldStorage()
parent_id = form.getvalue("parent_id")

if not parent_id or not str(parent_id).isdigit():
    print("<h3>Invalid user</h3>")
    sys.exit()

# ============ UPDATE HANDLERS ============

# --- Profile Photo ---
profilesubmit = form.getvalue("profileupdate")
if profilesubmit is not None:
    if 'new_profile' in form:
        profile = form['new_profile']
        new_profile_name = os.path.basename(profile.filename)
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        file_ext = os.path.splitext(new_profile_name)[1].lower()
        if file_ext not in allowed_extensions:
            print(f"""<script>alert("Invalid file type. Only JPG, PNG, GIF, and WEBP are allowed.");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
            sys.exit()
        else:
            if not os.path.exists("image"):
                os.makedirs("image")
            open("image/" + new_profile_name, "wb").write(profile.file.read())
            cur.execute("UPDATE parent SET parent_profile = %s WHERE id = %s", (new_profile_name, parent_id))
            con.commit()
            print(f"""<script>alert("Profile photo updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
            sys.exit()

# --- Parent Type ---
parenttypesubmit = form.getvalue("parenttypeupdate")
new_parent_type = form.getvalue("up_parent_type")
if parenttypesubmit is not None and new_parent_type:
    cur.execute("UPDATE parent SET parent_type = %s WHERE id = %s", (new_parent_type, parent_id))
    con.commit()
    print(f"""<script>alert("Parent type updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
    sys.exit()

# --- Parent Name ---
parentnamesubmit = form.getvalue("parentnameupdate")
new_parent_name = form.getvalue("up_parent_name")
if parentnamesubmit is not None and new_parent_name:
    cur.execute("UPDATE parent SET parent_name = %s WHERE id = %s", (new_parent_name, parent_id))
    con.commit()
    print(f"""<script>alert("Parent name updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
    sys.exit()

# --- Gender ---
gendersubmit = form.getvalue("genderupdate")
new_parent_gender = form.getvalue("up_parent_gender")
if gendersubmit is not None and new_parent_gender:
    cur.execute("UPDATE parent SET parent_gender = %s WHERE id = %s", (new_parent_gender, parent_id))
    con.commit()
    print(f"""<script>alert("Gender updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
    sys.exit()

# --- Date of Birth ---
dobsubmit = form.getvalue("dobupdate")
new_parent_dob = form.getvalue("up_parent_dob")
if dobsubmit is not None and new_parent_dob:
    cur.execute("UPDATE parent SET parent_dob = %s WHERE id = %s", (new_parent_dob, parent_id))
    con.commit()
    print(f"""<script>alert("Date of birth updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
    sys.exit()

# --- Mobile ---
mobilesubmit = form.getvalue("mobileupdate")
new_parent_mobile = form.getvalue("up_parent_mobile")
if mobilesubmit is not None and new_parent_mobile:
    cur.execute("UPDATE parent SET parent_mobile = %s WHERE id = %s", (new_parent_mobile, parent_id))
    con.commit()
    print(f"""<script>alert("Mobile number updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
    sys.exit()

# --- Alternate Mobile ---
altmobilesubmit = form.getvalue("altmobileupdate")
new_alternate_mobile = form.getvalue("up_alternate_mobile")
if altmobilesubmit is not None:
    cur.execute("UPDATE parent SET alternate_mobile = %s WHERE id = %s", (new_alternate_mobile, parent_id))
    con.commit()
    print(f"""<script>alert("Alternate mobile updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
    sys.exit()

# --- Email ---
emailsubmit = form.getvalue("emailupdate")
new_email_id = form.getvalue("up_email_id")
if emailsubmit is not None and new_email_id:
    cur.execute("UPDATE parent SET email_id = %s WHERE id = %s", (new_email_id, parent_id))
    con.commit()
    print(f"""<script>alert("Email updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
    sys.exit()

# --- Password ---
passwordsubmit = form.getvalue("passwordupdate")
new_password = form.getvalue("up_password")
if passwordsubmit is not None and new_password:
    cur.execute("UPDATE parent SET password = %s WHERE id = %s", (new_password, parent_id))
    con.commit()
    print(f"""<script>alert("Password updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
    sys.exit()

# --- Street ---
streetsubmit = form.getvalue("streetupdate")
new_street = form.getvalue("up_street")
if streetsubmit is not None and new_street:
    cur.execute("UPDATE parent SET street = %s WHERE id = %s", (new_street, parent_id))
    con.commit()
    print(f"""<script>alert("Street updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
    sys.exit()

# --- Area ---
areasubmit = form.getvalue("areaupdate")
new_area = form.getvalue("up_area")
if areasubmit is not None and new_area:
    cur.execute("UPDATE parent SET area = %s WHERE id = %s", (new_area, parent_id))
    con.commit()
    print(f"""<script>alert("Area updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
    sys.exit()

# --- City ---
citysubmit = form.getvalue("cityupdate")
new_city = form.getvalue("up_city")
if citysubmit is not None and new_city:
    cur.execute("UPDATE parent SET city = %s WHERE id = %s", (new_city, parent_id))
    con.commit()
    print(f"""<script>alert("City updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
    sys.exit()

# --- District ---
districtsubmit = form.getvalue("districtupdate")
new_district = form.getvalue("up_district")
if districtsubmit is not None and new_district:
    cur.execute("UPDATE parent SET district = %s WHERE id = %s", (new_district, parent_id))
    con.commit()
    print(f"""<script>alert("District updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
    sys.exit()

# --- State ---
statesubmit = form.getvalue("stateupdate")
new_state = form.getvalue("up_state")
if statesubmit is not None and new_state:
    cur.execute("UPDATE parent SET state = %s WHERE id = %s", (new_state, parent_id))
    con.commit()
    print(f"""<script>alert("State updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
    sys.exit()

# --- Pincode ---
pincodesubmit = form.getvalue("pincodeupdate")
new_pincode = form.getvalue("up_pincode")
if pincodesubmit is not None and new_pincode:
    cur.execute("UPDATE parent SET pincode = %s WHERE id = %s", (new_pincode, parent_id))
    con.commit()
    print(f"""<script>alert("Pincode updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
    sys.exit()

# --- ID Type ---
idtypesubmit = form.getvalue("idtypeupdate")
new_id_type = form.getvalue("up_id_type")
if idtypesubmit is not None and new_id_type:
    cur.execute("UPDATE parent SET id_type = %s WHERE id = %s", (new_id_type, parent_id))
    con.commit()
    print(f"""<script>alert("ID type updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
    sys.exit()

# --- ID Number ---
idnumbersubmit = form.getvalue("idnumberupdate")
new_id_number = form.getvalue("up_id_number")
if idnumbersubmit is not None and new_id_number:
    cur.execute("UPDATE parent SET id_number = %s WHERE id = %s", (new_id_number, parent_id))
    con.commit()
    print(f"""<script>alert("ID number updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
    sys.exit()

# --- ID Proof Upload ---
idproofsubmit = form.getvalue("idproofupdate")
if idproofsubmit is not None:
    if 'new_id_proof' in form:
        proof = form['new_id_proof']
        new_proof_name = os.path.basename(proof.filename)
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        file_ext = os.path.splitext(new_proof_name)[1].lower()
        if file_ext not in allowed_extensions:
            print(f"""<script>alert("Invalid file type. Only PDF and images are allowed.");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
            sys.exit()
        else:
            if not os.path.exists("documents"):
                os.makedirs("documents")
            open("documents/" + new_proof_name, "wb").write(proof.file.read())
            cur.execute("UPDATE parent SET id_proof = %s WHERE id = %s", (new_proof_name, parent_id))
            con.commit()
            print(f"""<script>alert("ID proof updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
            sys.exit()

# --- Child Order ---
childordersubmit = form.getvalue("childorderupdate")
new_child_order = form.getvalue("up_child_order")
if childordersubmit is not None and new_child_order:
    cur.execute("UPDATE parent SET child_order = %s WHERE id = %s", (new_child_order, parent_id))
    con.commit()
    print(f"""<script>alert("Child order updated successfully");location.href="parent_profile.py?parent_id={parent_id}";</script>""")
    sys.exit()

# ============ FETCH PARENT DATA ============
cur.execute("SELECT * FROM parent WHERE id = %s", (parent_id,))
parent = cur.fetchone()

if not parent:
    print("<h3>Parent not found</h3>")
    sys.exit()

id                 = parent["id"]
parent_type        = parent["parent_type"]
parent_name        = parent["parent_name"]
parent_gender      = parent["parent_gender"]
parent_dob         = parent["parent_dob"]
parent_mobile      = parent["parent_mobile"]
email_id           = parent["email_id"]
parent_profile_img = parent["parent_profile"]
alternate_mobile   = parent["alternate_mobile"]
state              = parent["state"]
district           = parent["district"]
city               = parent["city"]
pincode            = parent["pincode"]
street             = parent["street"]
area               = parent["area"]
id_type            = parent["id_type"]
id_number          = parent["id_number"]
id_proof           = parent["id_proof"]
child_order        = parent["child_order"]
status             = parent["status"]
created_at         = parent["Created_at"]
user_id            = parent["user_id"]
# NOTE: password intentionally NOT sent to the frontend for security

con.close()

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<title>Parent Profile - CVS</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
:root {{
  --pastel-gradient: linear-gradient(135deg, #fbc2eb, #a6c1ee, #fdfbfb);
  --pastel-start:   #fbc2eb;
  --pastel-mid:     #a6c1ee;
  --pastel-end:     #fdfbfb;
  --pastel-dark:    #7a5a8a;
  --pastel-text:    #3d2b5e;
  --success-color:  #10b981;
  --danger-color:   #ef4444;
  --text-dark:      #1f2937;
  --border-color:   #e5e7eb;
  --table-stripe:   #edfaef;
  --table-hover:    #d4f5d8;
  --table-border:   #a8ddb0;
  --table-header-bg: linear-gradient(135deg, #5c7c2f, #7aab3e);
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  background: linear-gradient(135deg, #052e16, #22c55e, #dcfce7);
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow-x: hidden;
}}

/* ===== NAVBAR ===== */
.navbar {{
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  padding: 12px 20px;
  background: linear-gradient(135deg, #052e16, #22c55e, #dcfce7) !important;
}}
.navbar .container-fluid {{
  display: flex; flex-direction: row; align-items: center; flex-wrap: nowrap; gap: 10px;
}}
.navbar-brand {{
  font-weight: 600; color: white !important;
  letter-spacing: 2px; text-transform: uppercase;
}}
.navbar-brand i {{
  margin-right: 10px; color: #d1fae5; font-size: 1.5rem; animation: bounce 2s infinite;
}}
@keyframes bounce {{
  0%,100% {{ transform: translateY(0); }}
  50%      {{ transform: translateY(-5px); }}
}}
.navbar-toggler-custom {{
  display: none; flex-shrink: 0;
  background: rgba(255,255,255,0.15); border: 1.5px solid rgba(255,255,255,0.4);
  color: white; padding: 6px 11px; border-radius: 8px; font-size: 1.15rem;
  cursor: pointer; line-height: 1; transition: background 0.25s; order: -1;
}}
.navbar-toggler-custom:hover {{ background: rgba(255,255,255,0.28); }}
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
.btn-logout:hover {{ transform: translateY(-2px); color: white; }}

/* ===== SIDEBAR ===== */
.sidebar {{
  min-height: 100vh;
  background: linear-gradient(135deg, #052e16, #22c55e);
  box-shadow: 4px 0 20px rgba(0,0,0,0.3); padding: 20px 0;
}}
.sidebar-link {{
  display: block; padding: 14px 18px; color: #d1fae5; text-decoration: none;
  cursor: pointer; transition: all 0.3s ease; border-left: 4px solid transparent;
  font-weight: 500; margin: 6px 0;
}}
.sidebar-link:hover, .sidebar-link.active {{
  background: linear-gradient(90deg, #22c55e, transparent 100%);
  color: #fff; border-left: 4px solid #dcfce7; padding-left: 24px; 
}}
.sidebar-link i {{ margin-right: 12px; width: 22px; text-align: center; }}
.sidebar-overlay {{
  display: none; position: fixed; top:0; left:0;
  width:100%; height:100%; background:rgba(0,0,0,0.6); z-index:998; backdrop-filter:blur(2px);
}}
.sidebar-overlay.show {{ display: block; }}

/* ===== CONTENT ===== */
.main-content {{ padding: 30px 20px; min-height: 100vh; }}

/* ===== PROFILE CARD ===== */
.profile-card {{
  border-radius: 20px; box-shadow: 0 20px 60px rgba(166,193,238,0.25);
  overflow: hidden; background: white;
  border: 1px solid #c8eacc;
}}

/* ===== CARD HEADER — Rose Gradient ===== */
.card-header {{
  background: var(--pastel-gradient) !important;
  padding: 25px; border: none;
}}
.card-header h5 {{ margin:0; font-size:1.5rem; font-weight:700; color: var(--pastel-text) !important; text-shadow: 0 1px 2px rgba(255,255,255,0.6); }}

/* ===== PROFILE IMAGE ===== */
.profile-image-section {{
  text-align: center; padding: 30px 0 20px;
  background: linear-gradient(to bottom, #edf7ee 0%, white 100%);
}}
.profile-img {{
  width: 150px; height: 150px; object-fit: cover;
  border: 5px solid white;
  box-shadow: 0 10px 30px rgba(166,193,238,0.35); transition: transform 0.3s ease;
}}
.profile-img:hover {{ transform: scale(1.05); }}
.btn-change-photo {{
  background: var(--pastel-gradient); border: none; padding: 8px 20px;
  border-radius: 25px; color: var(--pastel-text); font-weight: 600; transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(166,193,238,0.4);
}}
.btn-change-photo:hover {{ transform: translateY(-2px); color: var(--pastel-text); opacity: 0.9; }}

/* ===== SECTION HEADERS — Rose Gradient ===== */
.section-header {{
  background: var(--pastel-gradient); color: var(--pastel-text);
  padding: 15px 20px; border-radius: 12px; margin: 30px 0 20px;
  box-shadow: 0 4px 15px rgba(166,193,238,0.3);
}}
.section-header h6 {{ margin:0; font-size:1.1rem; font-weight:700; color: var(--pastel-text); }}

/* ===== FORM ELEMENTS ===== */
.form-label {{ font-weight:600; color:var(--text-dark); margin-bottom:8px; font-size:0.9rem; }}
.form-control {{
  border: 2px solid var(--border-color); border-radius: 10px;
  padding: 10px 15px; transition: all 0.3s ease; background-color: #f7fdf8;
}}
.form-control:focus {{
  border-color: var(--pastel-start);
  box-shadow: 0 0 0 3px rgba(166,193,238,0.15); background-color: white;
}}
.input-group-text {{
  background: white; border: 2px solid var(--border-color);
  border-left: none; border-radius: 0 10px 10px 0; cursor: pointer; transition: all 0.3s ease;
}}
.input-group-text:hover {{ background: #edf7ee; }}
.input-group-text i {{ transition: transform 0.3s ease; color: var(--pastel-start) !important; }}
.input-group-text:hover i {{ transform: scale(1.2); }}
.input-group .form-control {{ border-right: none; border-radius: 10px 0 0 10px; }}

/* ===== TABLE STYLES — Rose Palette ===== */
.table {{
  border-radius: 12px; overflow: hidden;
  box-shadow: 0 4px 15px rgba(166,193,238,0.15);
  border: 1px solid var(--table-border);
}}
.table thead th {{
  background: var(--table-header-bg) !important;
  color: #3d2b5e; font-weight: 700; font-size: 0.9rem;
  letter-spacing: 0.5px; padding: 14px 16px;
  border: none; text-shadow: 0 1px 2px rgba(0,0,0,0.15);
}}
.table tbody tr:nth-child(odd)  {{ background-color: #ffffff; }}
.table tbody tr:nth-child(even) {{ background-color: var(--table-stripe); }}
.table tbody tr:hover {{ background-color: var(--table-hover); transition: background 0.2s; }}
.table tbody td {{
  padding: 12px 16px; vertical-align: middle;
  border-color: var(--table-border); color: var(--text-dark);
}}
.table-bordered {{ border-color: var(--table-border); }}
.table-bordered th,
.table-bordered td {{ border-color: var(--table-border); }}

/* ===== MODAL STYLES — Rose Gradient ===== */
.modal-content {{
  border-radius: 20px; border: none;
  box-shadow: 0 20px 60px rgba(166,193,238,0.3);
  overflow: hidden;
}}
.modal-header {{
  background: var(--pastel-gradient) !important;
  color: var(--pastel-text); border-radius: 0; padding: 20px 25px; border: none;
}}
.modal-title {{ font-weight:700; font-size:1.3rem; color: var(--pastel-text); }}
.btn-close {{ filter: brightness(0) saturate(100%) invert(22%) sepia(40%) saturate(600%) hue-rotate(60deg); opacity:1; }}
.modal-body {{ padding: 30px; background: #f4fbf5; }}
.modal-body .form-label {{ color:var(--text-dark); font-weight:600; }}
.modal-body .form-control,
.modal-body .form-select {{
  border: 2px solid #a8ddb0; border-radius: 10px; padding: 12px 15px;
  background: #f7fdf8;
}}
.modal-body .form-control:focus,
.modal-body .form-select:focus {{
  border-color: var(--pastel-start);
  box-shadow: 0 0 0 3px rgba(166,193,238,0.15);
}}

/* ===== BUTTONS ===== */
.btn-primary {{
  background: var(--pastel-gradient); border: none; padding: 10px 25px;
  border-radius: 10px; font-weight:700; color: var(--pastel-text);
  transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(166,193,238,0.35);
}}
.btn-primary:hover {{
  transform: translateY(-2px); color: var(--pastel-text);
  box-shadow: 0 8px 20px rgba(166,193,238,0.45); opacity: 0.92;
}}
.btn-secondary {{
  background: #6b7280; border: none; padding: 10px 25px;
  border-radius: 10px; font-weight:600; transition: all 0.3s ease;
}}
.btn-secondary:hover {{ background: #4b5563; transform: translateY(-2px); }}

.card-body {{ padding: 30px; }}
.row.g-3 {{ margin-bottom: 15px; }}

/* ===== RESPONSIVE ===== */
@media (max-width: 991.98px) {{
  .navbar-toggler-custom {{ display: flex; align-items: center; justify-content: center; }}
  .sidebar {{
    position: fixed; left: -100%; top: 0;
    width: 280px; height: 100vh; z-index: 999; transition: left 0.3s ease; overflow-y: auto;
  }}
  .sidebar.show {{ left: 0; }}
  .main-content {{ padding: 15px; }}
  .navbar-brand   {{ font-size: 1rem; letter-spacing: 1px; }}
  .navbar-brand i {{ font-size: 1.3rem; }}
}}
@media (max-width: 767.98px) {{
  .main-content {{ padding: 12px; }}
  .btn-logout {{ padding: 6px 16px; font-size: 0.85rem; }}
}}
@media (max-width: 575.98px) {{
  .navbar-brand   {{ font-size: 0.85rem; letter-spacing: 0.5px; }}
  .navbar-brand i {{ font-size: 1.1rem; margin-right: 6px; }}
  .btn-logout     {{ padding: 6px 12px; font-size: 0.8rem; }}
}}
@media (max-width: 400px) {{
  .navbar-brand {{ font-size: 0.75rem; }}
}}
</style>
</head>
<body>

<!-- NAVBAR -->
<nav class="navbar navbar-dark">
  <div class="container-fluid">
    <button class="navbar-toggler-custom" id="sidebarToggleBtn" onclick="toggleSidebar()">
      <i class="fas fa-bars"></i>
    </button>
    <span class="navbar-brand">
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
      <a href="parent_my_appointment.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fas fa-calendar-check"></i> My Appointments
      </a>
      <a href="parent_reminder.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fas fa-bell"></i> My Reminders
      </a>
      <a href="parent_profile.py?parent_id={parent_id}" class="sidebar-link active" onclick="closeSidebarMobile()">
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
    <div class="col-lg-10 col-md-9 main-content">
      <div class="card profile-card">
        <div class="card-header">
          <h5 class="mb-0"><i class="fas fa-user-circle me-2"></i>Parent Profile</h5>
        </div>
        <div class="card-body">

          <!-- Profile Image -->
          <div class="profile-image-section">
            <img src="image/{parent_profile_img}" class="rounded-circle profile-img" alt="Profile">
            <div></div>
            <button class="btn btn-change-photo mt-3" data-bs-toggle="modal" data-bs-target="#profilemodal">
              <i class="fa fa-camera me-2"></i>Change Photo
            </button>
          </div>

          <!-- Personal Information -->
          <div class="section-header">
            <h6 class="mb-0"><i class="fa fa-user me-2"></i>Personal Information</h6>
          </div>
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Parent Type</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{parent_type}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#parenttypemodal">
                  <i class="fa fa-pen"></i>
                </span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Parent Name</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{parent_name}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#parentnamemodal">
                  <i class="fa fa-pen"></i>
                </span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Gender</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{parent_gender}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#gendermodal">
                  <i class="fa fa-pen"></i>
                </span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Date of Birth</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{parent_dob}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#dobmodal">
                  <i class="fa fa-pen"></i>
                </span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Mobile Number</label>
              <div class="input-group">
                <input type="tel" class="form-control" value="{parent_mobile}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#mobilemodal">
                  <i class="fa fa-pen"></i>
                </span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Alternate Mobile</label>
              <div class="input-group">
                <input type="tel" class="form-control" value="{alternate_mobile}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#altmobilemodal">
                  <i class="fa fa-pen"></i>
                </span>
              </div>
            </div>
            <div class="col-md-12">
              <label class="form-label">Email ID</label>
              <div class="input-group">
                <input type="email" class="form-control" value="{email_id}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#emailmodal">
                  <i class="fa fa-pen"></i>
                </span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Child Order</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{child_order}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#childordermodal">
                  <i class="fa fa-pen"></i>
                </span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Password</label>
              <div class="input-group">
                <input type="password" class="form-control" placeholder="••••••••" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#passwordmodal">
                  <i class="fa fa-pen"></i>
                </span>
              </div>
            </div>
          </div>

          <!-- Address Information -->
          <div class="section-header">
            <h6 class="mb-0"><i class="fa fa-map-marker-alt me-2"></i>Address Information</h6>
          </div>
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Street</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{street}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#streetmodal">
                  <i class="fa fa-pen"></i>
                </span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Area</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{area}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#areamodal">
                  <i class="fa fa-pen"></i>
                </span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">City</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{city}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#citymodal">
                  <i class="fa fa-pen"></i>
                </span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">District</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{district}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#districtmodal">
                  <i class="fa fa-pen"></i>
                </span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">State</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{state}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#statemodal">
                  <i class="fa fa-pen"></i>
                </span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Pincode</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{pincode}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#pincodemodal">
                  <i class="fa fa-pen"></i>
                </span>
              </div>
            </div>
          </div>

          <!-- ID Proof Information -->
          <div class="section-header">
            <h6 class="mb-0"><i class="fa fa-id-card me-2"></i>ID Proof Information</h6>
          </div>
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">ID Type</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{id_type}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#idtypemodal">
                  <i class="fa fa-pen"></i>
                </span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">ID Number</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{id_number}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#idnumbermodal">
                  <i class="fa fa-pen"></i>
                </span>
              </div>
            </div>
            <div class="col-md-12">
              <label class="form-label">ID Proof Document</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{id_proof}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#idproofmodal">
                  <i class="fa fa-pen"></i>
                </span>
              </div>
            </div>
          </div>

        </div><!-- /card-body -->
      </div><!-- /profile-card -->
    </div><!-- /main-content -->
  </div><!-- /row -->
</div><!-- /container-fluid -->

<!-- ==================== MODALS ==================== -->

<!-- Profile Photo Modal -->
<div class="modal fade" id="profilemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-camera me-2"></i>Change Profile Photo</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py" enctype="multipart/form-data">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">Upload New Profile Photo</label>
          <input type="file" name="new_profile" class="form-control" accept="image/*" required>
          <small class="text-muted">Accepted formats: JPG, PNG, GIF, WEBP</small>
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="profileupdate" value="1">Update Photo</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- Parent Type Modal -->
<div class="modal fade" id="parenttypemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-users me-2"></i>Change Parent Type</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">Parent Type</label>
          <select class="form-select" name="up_parent_type" required>
            <option value="">Select Type</option>
            <option value="Mother" {"selected" if parent_type=="Mother" else ""}>Mother</option>
            <option value="Father" {"selected" if parent_type=="Father" else ""}>Father</option>
            <option value="Guardian" {"selected" if parent_type=="Guardian" else ""}>Guardian</option>
          </select>
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="parenttypeupdate" value="1">Update</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- Parent Name Modal -->
<div class="modal fade" id="parentnamemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-signature me-2"></i>Change Parent Name</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">Enter New Name</label>
          <input type="text" class="form-control" name="up_parent_name" value="{parent_name}" required>
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="parentnameupdate" value="1">Update</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- Gender Modal -->
<div class="modal fade" id="gendermodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-venus-mars me-2"></i>Change Gender</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">Gender</label>
          <select class="form-select" name="up_parent_gender" required>
            <option value="">Select Gender</option>
            <option value="Male"   {"selected" if parent_gender=="Male"   else ""}>Male</option>
            <option value="Female" {"selected" if parent_gender=="Female" else ""}>Female</option>
            <option value="Other"  {"selected" if parent_gender=="Other"  else ""}>Other</option>
          </select>
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="genderupdate" value="1">Update</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- Date of Birth Modal -->
<div class="modal fade" id="dobmodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-calendar me-2"></i>Change Date of Birth</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">Date of Birth</label>
          <input type="date" class="form-control" name="up_parent_dob" required>
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="dobupdate" value="1">Update</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- Mobile Modal -->
<div class="modal fade" id="mobilemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-phone me-2"></i>Change Mobile Number</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">Mobile Number</label>
          <input type="tel" class="form-control" name="up_parent_mobile" value="{parent_mobile}" pattern="[0-9]{{10}}" maxlength="10" required>
          <small class="text-muted">Enter 10-digit mobile number</small>
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="mobileupdate" value="1">Update</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- Alternate Mobile Modal -->
<div class="modal fade" id="altmobilemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-phone-alt me-2"></i>Change Alternate Mobile</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">Alternate Mobile Number</label>
          <input type="tel" class="form-control" name="up_alternate_mobile" value="{alternate_mobile}" pattern="[0-9]{{10}}" maxlength="10">
          <small class="text-muted">Enter 10-digit mobile number (optional)</small>
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="altmobileupdate" value="1">Update</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- Email Modal -->
<div class="modal fade" id="emailmodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-envelope me-2"></i>Change Email</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">Email Address</label>
          <input type="email" class="form-control" name="up_email_id" value="{email_id}" required>
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="emailupdate" value="1">Update</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- Child Order Modal -->
<div class="modal fade" id="childordermodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-sort-numeric-up me-2"></i>Change Child Order</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">Child Order</label>
          <select class="form-select" name="up_child_order" required>
            <option value="">Select Child Order</option>
            <option value="First Child"  {"selected" if child_order=="First Child"  else ""}>First Child</option>
            <option value="Second Child" {"selected" if child_order=="Second Child" else ""}>Second Child</option>
            <option value="Third Child"  {"selected" if child_order=="Third Child"  else ""}>Third Child</option>
            <option value="Fourth Child" {"selected" if child_order=="Fourth Child" else ""}>Fourth Child</option>
            <option value="Fifth Child"  {"selected" if child_order=="Fifth Child"  else ""}>Fifth Child</option>
          </select>
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="childorderupdate" value="1">Update</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- Password Modal -->
<div class="modal fade" id="passwordmodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-lock me-2"></i>Change Password</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">New Password</label>
          <input type="password" class="form-control" name="up_password" minlength="6" required>
          <small class="text-muted">Password must be at least 6 characters</small>
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="passwordupdate" value="1">Update</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- Street Modal -->
<div class="modal fade" id="streetmodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-road me-2"></i>Change Street</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">Street</label>
          <input type="text" class="form-control" name="up_street" value="{street}" required>
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="streetupdate" value="1">Update</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- Area Modal -->
<div class="modal fade" id="areamodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-map-signs me-2"></i>Change Area</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">Area</label>
          <input type="text" class="form-control" name="up_area" value="{area}" required>
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="areaupdate" value="1">Update</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- City Modal -->
<div class="modal fade" id="citymodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-city me-2"></i>Change City</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">City</label>
          <input type="text" class="form-control" name="up_city" value="{city}" required>
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="cityupdate" value="1">Update</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- District Modal -->
<div class="modal fade" id="districtmodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-map me-2"></i>Change District</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">District</label>
          <input type="text" class="form-control" name="up_district" value="{district}" required>
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="districtupdate" value="1">Update</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- State Modal -->
<div class="modal fade" id="statemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-flag me-2"></i>Change State</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">State</label>
          <input type="text" class="form-control" name="up_state" value="{state}" required>
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="stateupdate" value="1">Update</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- Pincode Modal -->
<div class="modal fade" id="pincodemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-map-pin me-2"></i>Change Pincode</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">Pincode</label>
          <input type="text" class="form-control" name="up_pincode" value="{pincode}" pattern="[0-9]{{6}}" maxlength="6">
          <small class="text-muted">Enter 6-digit pincode</small>
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="pincodeupdate" value="1">Update</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- ID Type Modal -->
<div class="modal fade" id="idtypemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-id-card me-2"></i>Change ID Type</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">ID Type</label>
          <select class="form-select" name="up_id_type">
            <option value="">Select ID Type</option>
            <option value="Aadhaar Card" {"selected" if id_type=="Aadhaar Card" else ""}>Aadhaar Card</option>
          </select>
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="idtypeupdate" value="1">Update</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- ID Number Modal -->
<div class="modal fade" id="idnumbermodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-hashtag me-2"></i>Change ID Number</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">ID Number</label>
          <input type="text" class="form-control" name="up_id_number" value="{id_number}">
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="idnumberupdate" value="1">Update</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- ID Proof Upload Modal -->
<div class="modal fade" id="idproofmodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-file-upload me-2"></i>Upload ID Proof</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form method="post" action="parent_profile.py" enctype="multipart/form-data">
          <input type="hidden" name="parent_id" value="{parent_id}">
          <label class="form-label">Upload ID Proof Document</label>
          <input type="file" name="new_id_proof" class="form-control" accept=".pdf,.jpg,.jpeg,.png" required>
          <small class="text-muted">Accepted formats: PDF, JPG, PNG</small>
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="submit" class="btn btn-primary" name="idproofupdate" value="1">Upload</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
<script>
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
document.addEventListener('click', function(e) {{
  var sidebar = document.getElementById('sidebar');
  var btn     = document.getElementById('sidebarToggleBtn');
  if (window.innerWidth < 992 &&
      sidebar.classList.contains('show') &&
      !sidebar.contains(e.target) &&
      !btn.contains(e.target)) {{
    closeSidebarMobile();
  }}
}});
</script>
</body>
</html>""")