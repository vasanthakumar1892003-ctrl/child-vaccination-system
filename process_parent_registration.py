#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgitb
import sys
import cgi
from datetime import datetime

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")
print("Content-Type: text/html\n")

form = cgi.FieldStorage()

# ── Safely extract parent_id ──
_pid      = form.getvalue("parent_id") or ""
parent_id = (_pid[0] if isinstance(_pid, list) else _pid).strip()

# ── Guard: redirect to login if parent_id is missing or invalid ──
if not parent_id or not parent_id.isdigit():
    print('<script>alert("Session expired or invalid access. Please login again.");window.location.href="main.py";</script>')
    sys.exit()

try:
    con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
    cur = con.cursor()
except Exception as e:
    print("<html><body><h2>Database Connection Failed!</h2><p>Error:</p>", e, "</body></html>")
    sys.exit()

try:
    # ── Read ALL form fields using EXACT name="" values from parent_view_hospital.py ──
    hospital_name    = form.getvalue("hospital_name",    "").strip()

    # Parent fields
    p_name           = form.getvalue("p_name",           "").strip()
    p_type           = form.getvalue("p_type",           "").strip()
    p_gender         = form.getvalue("p_gender",         "").strip()
    mobile           = form.getvalue("mobile",           "").strip()
    email            = form.getvalue("email",            "").strip()
    aadhaar_number   = form.getvalue("aadhaar_number",   "").strip()

    # Child fields
    c_name           = form.getvalue("c_name",           "").strip()
    c_gender         = form.getvalue("c_gender",         "").strip()
    c_dob            = form.getvalue("c_dob",            "").strip()
    c_order          = form.getvalue("c_order",          "").strip()

    # Vaccination fields
    vaccin           = form.getvalue("vaccin",           "No").strip()
    vaccin_age       = form.getvalue("vaccin_age",       "").strip()

    checks_list      = form.getlist("vaccination_checks")
    vaccination      = ", ".join(checks_list) if checks_list else "None"
    if vaccin == "No":
        vaccination  = "None"
        vaccin_age   = ""

    # Appointment fields
    appointment_date = form.getvalue("appointment_date", "").strip()
    age_group        = form.getvalue("age_group",        "").strip()
    vaccine_name     = form.getvalue("vaccine_name",     "").strip()

    # Address fields
    address          = form.getvalue("address",          "").strip()
    district         = form.getvalue("district",         "").strip()
    pincode          = form.getvalue("pincode",          "").strip()

    # Auto fields
    status           = "pending"
    created_at       = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ── INSERT into parentform table ──
    insert_query = """
        INSERT INTO parentform
          (p_name, p_type, p_gender, mobile, email, aadhaar_number,
           c_name, c_gender, c_dob, c_order,
           vaccin, vaccin_age, vaccination,
           appointment_date, age_group, vaccine_name,
           address, district, pincode,
           hospital_name, status, created_at)
        VALUES
          (%s, %s, %s, %s, %s, %s,
           %s, %s, %s, %s,
           %s, %s, %s,
           %s, %s, %s,
           %s, %s, %s,
           %s, %s, %s)
    """
    values = (
        p_name, p_type, p_gender, mobile, email, aadhaar_number,
        c_name, c_gender, c_dob, c_order,
        vaccin, vaccin_age, vaccination,
        appointment_date, age_group, vaccine_name,
        address, district, pincode,
        hospital_name, status, created_at
    )

    cur.execute(insert_query, values)
    con.commit()
    registration_id = cur.lastrowid

    # ── SUCCESS PAGE ──
    print(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Registration Success</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <style>
    body {{ background:linear-gradient(135deg,#059669 0%,#10b981 50%,#34d399 100%); min-height:100vh; display:flex; align-items:center; justify-content:center; font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif; padding:20px; }}
    .success-container {{ background:white; border-radius:20px; padding:40px; box-shadow:0 10px 40px rgba(0,0,0,0.2); max-width:700px; width:100%; text-align:center; animation:slideIn 0.5s ease-out; }}
    @keyframes slideIn {{ from{{opacity:0;transform:translateY(-30px);}} to{{opacity:1;transform:translateY(0);}} }}
    .success-icon {{ width:100px; height:100px; background:linear-gradient(135deg,#059669 0%,#10b981 100%); border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 25px; animation:scaleIn 0.6s ease-out 0.2s both; }}
    @keyframes scaleIn {{ from{{transform:scale(0);}} to{{transform:scale(1);}} }}
    .success-icon i {{ font-size:50px; color:white; }}
    h2 {{ color:#059669; font-weight:700; margin-bottom:15px; font-size:2rem; }}
    .registration-id {{ background:linear-gradient(135deg,#dbeafe 0%,#bfdbfe 100%); padding:20px; border-radius:12px; margin:25px 0; border-left:5px solid #3b82f6; }}
    .registration-id strong {{ color:#1e3a8a; font-size:1.1rem; }}
    .registration-id .id-value {{ color:#1e40af; font-size:2rem; font-weight:700; display:block; margin-top:8px; letter-spacing:2px; }}
    .info-box {{ background:#f0fdf4; padding:25px; border-radius:12px; margin:20px 0; border-left:4px solid #10b981; text-align:left; }}
    .info-box h5 {{ color:#059669; font-weight:700; margin-bottom:15px; font-size:1.2rem; border-bottom:2px solid #d1fae5; padding-bottom:10px; }}
    .info-row {{ display:flex; padding:10px 0; border-bottom:1px solid #e8f5f1; }}
    .info-row:last-child {{ border-bottom:none; }}
    .info-label {{ width:40%; color:#64748b; font-weight:600; font-size:0.9rem; }}
    .info-label i {{ color:#10b981; width:20px; margin-right:8px; }}
    .info-value {{ width:60%; color:#1e293b; font-weight:500; font-size:0.95rem; }}
    .alert-info {{ background:linear-gradient(135deg,#fef3c7 0%,#fde68a 100%); border-left:5px solid #f59e0b; padding:15px 20px; border-radius:10px; margin:20px 0; text-align:left; }}
    .alert-info i {{ color:#f59e0b; margin-right:10px; font-size:1.2rem; }}
    .alert-info p {{ margin:5px 0; color:#78350f; font-size:0.95rem; }}
    .btn-home {{ background:linear-gradient(135deg,#059669 0%,#10b981 100%); color:white; border:none; padding:12px 35px; border-radius:25px; font-weight:700; transition:all 0.3s ease; box-shadow:0 6px 15px rgba(16,185,129,0.3); font-size:1rem; text-transform:uppercase; letter-spacing:1px; text-decoration:none; display:inline-block; margin:10px; }}
    .btn-home:hover {{ transform:translateY(-3px); box-shadow:0 8px 20px rgba(16,185,129,0.5); color:white; }}
    .btn-more {{ background:linear-gradient(135deg,#0891b2 0%,#06b6d4 100%); color:white; border:none; padding:12px 35px; border-radius:25px; font-weight:700; transition:all 0.3s ease; box-shadow:0 6px 15px rgba(8,145,178,0.3); font-size:1rem; text-decoration:none; display:inline-block; margin:10px; }}
    .btn-more:hover {{ transform:translateY(-3px); box-shadow:0 8px 20px rgba(6,182,212,0.5); color:white; }}
    @media (max-width:768px) {{ .success-container{{padding:25px;}} .info-row{{flex-direction:column;}} .info-label,.info-value{{width:100%;}} .info-value{{margin-top:5px;padding-left:28px;}} }}
  </style>
</head>
<body>
  <div class="success-container">
    <div class="success-icon"><i class="fas fa-check"></i></div>
    <h2>Registration Successful!</h2>
    <p style="color:#64748b;font-size:1.1rem;">Your registration has been submitted successfully.</p>
    <div class="registration-id">
      <strong><i class="fas fa-id-card"></i> Your Registration ID</strong>
      <span class="id-value">REG-{registration_id:05d}</span>
    </div>
    <div class="info-box">
      <h5><i class="fas fa-clipboard-check"></i> Registration Summary</h5>
      <div class="info-row"><div class="info-label"><i class="fas fa-user"></i> Parent Name</div><div class="info-value">{p_name}</div></div>
      <div class="info-row"><div class="info-label"><i class="fas fa-user-tag"></i> Parent Type</div><div class="info-value">{p_type}</div></div>
      <div class="info-row"><div class="info-label"><i class="fa-solid fa-users"></i> Parent Gender</div><div class="info-value">{p_gender}</div></div>
      <div class="info-row"><div class="info-label"><i class="fas fa-phone"></i> Mobile</div><div class="info-value">{mobile}</div></div>
      <div class="info-row"><div class="info-label"><i class="fas fa-envelope"></i> Email</div><div class="info-value">{email}</div></div>
      <div class="info-row"><div class="info-label"><i class="fas fa-baby"></i> Child Name</div><div class="info-value">{c_name}</div></div>
      <div class="info-row"><div class="info-label"><i class="fa-solid fa-user-group"></i> Child Gender</div><div class="info-value">{c_gender}</div></div>
      <div class="info-row"><div class="info-label"><i class="fas fa-birthday-cake"></i> Child DOB</div><div class="info-value">{c_dob}</div></div>
      <div class="info-row"><div class="info-label"><i class="fas fa-sort-numeric-up"></i> Child Order</div><div class="info-value">{c_order}</div></div>
      <div class="info-row"><div class="info-label"><i class="fas fa-hospital"></i> Hospital</div><div class="info-value">{hospital_name}</div></div>
      <div class="info-row"><div class="info-label"><i class="fas fa-syringe"></i> Vaccinations</div><div class="info-value">{vaccin}</div></div>
      <div class="info-row"><div class="info-label"><i class="fas fa-layer-group"></i> Age Group</div><div class="info-value">{vaccin_age if vaccin_age else "N/A"}</div></div>
      <div class="info-row"><div class="info-label"><i class="fas fa-list-check"></i> Vaccines Given</div><div class="info-value">{vaccination}</div></div>
      <div class="info-row"><div class="info-label"><i class="fas fa-calendar-alt"></i> Appointment Date</div><div class="info-value">{appointment_date}</div></div>
      <div class="info-row"><div class="info-label"><i class="fas fa-arrow-down-short-wide"></i> Age</div><div class="info-value">{age_group}</div></div>
      <div class="info-row"><div class="info-label"><i class="fas fa-notes-medical"></i> Vaccine Name</div><div class="info-value">{vaccine_name}</div></div>
      <div class="info-row"><div class="info-label"><i class="fas fa-map-marker-alt"></i> District</div><div class="info-value">{district}</div></div>
      <div class="info-row"><div class="info-label"><i class="fas fa-mail-bulk"></i> Pincode</div><div class="info-value">{pincode}</div></div>
      <div class="info-row"><div class="info-label"><i class="fas fa-clock"></i> Status</div><div class="info-value"><span style="background:#fef9c3;color:#b45309;padding:3px 10px;border-radius:10px;font-weight:600;">Pending</span></div></div>
    </div>
    <div class="alert-info">
      <i class="fas fa-info-circle"></i>
      <p><strong>What's Next?</strong></p>
      <p>&#x2022; Your registration ID is <strong>REG-{registration_id:05d}</strong> — keep it for reference</p>
      <p>&#x2022; The hospital will review your application and contact you</p>
      <p>&#x2022; Check your appointment status in <strong>My Appointments</strong></p>
    </div>
    <div style="margin-top:30px;">
      <a href="parent_dashboard.py?parent_id={parent_id}" class="btn-home">
        <i class="fas fa-home"></i> Back to Home
      </a>
      <a href="parent_view_hospital.py?parent_id={parent_id}" class="btn-more">
        <i class="fas fa-hospital"></i> View More Hospitals
      </a>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")

except Exception as e:
    con.rollback()
    print(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Registration Error</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <style>
    body {{ background:linear-gradient(135deg,#dc2626 0%,#ef4444 50%,#f87171 100%); min-height:100vh; display:flex; align-items:center; justify-content:center; font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif; padding:20px; }}
    .error-container {{ background:white; border-radius:20px; padding:40px; box-shadow:0 10px 40px rgba(0,0,0,0.2); max-width:600px; width:100%; text-align:center; }}
    .error-icon {{ width:100px; height:100px; background:linear-gradient(135deg,#dc2626 0%,#ef4444 100%); border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 25px; }}
    .error-icon i {{ font-size:50px; color:white; }}
    h2 {{ color:#dc2626; font-weight:700; margin-bottom:15px; }}
    .error-details {{ background:#fee; padding:20px; border-radius:8px; margin:20px 0; color:#991b1b; text-align:left; font-family:monospace; font-size:0.9rem; border-left:4px solid #dc2626; max-height:200px; overflow-y:auto; }}
    .btn-back {{ background:linear-gradient(135deg,#059669 0%,#10b981 100%); color:white; border:none; padding:12px 35px; border-radius:25px; font-weight:700; transition:all 0.3s ease; box-shadow:0 6px 15px rgba(16,185,129,0.3); font-size:1rem; text-decoration:none; display:inline-block; margin-top:20px; }}
    .btn-back:hover {{ transform:translateY(-3px); color:white; }}
  </style>
</head>
<body>
  <div class="error-container">
    <div class="error-icon"><i class="fas fa-times"></i></div>
    <h2>Registration Failed!</h2>
    <p style="color:#64748b;">An error occurred while saving your registration.</p>
    <div class="error-details"><strong>Error Details:</strong><br>{str(e)}</div>
    <p style="color:#64748b;margin-top:20px;">
      <i class="fas fa-exclamation-triangle" style="color:#f59e0b;"></i><br>
      Please check your input and try again.<br>If the problem persists, contact support.
    </p>
    <a href="parent_view_hospital.py?parent_id={parent_id}" class="btn-back">
      <i class="fas fa-arrow-left"></i> Go Back and Try Again
    </a>
  </div>
</body>
</html>
""")

finally:
    if 'con' in locals():
        con.close()