#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import pymysql.cursors
import cgi
import cgitb
import sys
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date, timedelta, datetime

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")

# ── EMAIL CONFIG ──────────────────────────────────────────────────────────────
FROM_EMAIL   = "childvaccinationsystem2026@gmail.com"
APP_PASSWORD = "wuxe lqii npcp nglf"

# ── FORM DATA ─────────────────────────────────────────────────────────────────
form     = cgi.FieldStorage()
admin_id = (form.getvalue("admin_id") or "").strip()
action   = (form.getvalue("action")   or "").strip()

# ── DB CONNECTION ─────────────────────────────────────────────────────────────
try:
    con = pymysql.connect(
        host="localhost", user="root", password="",
        database="cvsdp",
        cursorclass=pymysql.cursors.DictCursor
    )
    cur = con.cursor()
except Exception as e:
    print("Content-Type: text/html\n")
    print(f"<html><body><h2 style='color:red;'>DB Connection Failed: {e}</h2></body></html>")
    sys.exit()


# ── HELPERS ───────────────────────────────────────────────────────────────────
def to_date(val):
    if isinstance(val, date):
        return val
    try:
        return datetime.strptime(str(val), "%Y-%m-%d").date()
    except Exception:
        return None


# ── EMAIL BUILDER & SENDER ────────────────────────────────────────────────────
def send_reminder_email(to_email, p_name, c_name, appt_date_str, vacc_name, hosp_name, days_left):
    if not to_email or "@" not in to_email:
        return False, "Invalid email address"

    if days_left == 0:
        tag   = "TODAY"
        emoji = "🔔"
        color = "#dc2626"
        band  = "#fee2e2"
        msg   = (f"This is an urgent reminder that <strong>{c_name}'s</strong> vaccination appointment "
                 f"is scheduled for <strong>TODAY</strong>. Please visit the hospital on time.")
    elif days_left == 1:
        tag   = "TOMORROW"
        emoji = "⏰"
        color = "#d97706"
        band  = "#fffbeb"
        msg   = (f"This is a reminder that <strong>{c_name}'s</strong> vaccination appointment is "
                 f"<strong>TOMORROW</strong>. Please make the necessary preparations.")
    elif days_left == 2:
        tag   = "IN 2 DAYS"
        emoji = "📅"
        color = "#7c3aed"
        band  = "#ede9fe"
        msg   = (f"This is a reminder that <strong>{c_name}'s</strong> vaccination appointment is "
                 f"<strong>in 2 days</strong>. Please plan your visit accordingly.")
    else:
        tag   = "IN 3 DAYS"
        emoji = "📋"
        color = "#16a34a"
        band  = "#d1fae5"
        msg   = (f"This is an advance reminder that <strong>{c_name}'s</strong> vaccination appointment is "
                 f"<strong>in 3 days</strong>. Please mark your calendar.")

    subject = f"{emoji} Appointment Reminder – {tag} | Child: {c_name}"

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8">
<style>
  body{{margin:0;padding:0;background:#f3f4f6;font-family:'Segoe UI',Arial,sans-serif;}}
  .wrap{{max-width:600px;margin:30px auto;background:#fff;border-radius:18px;
         overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,.13);}}
  .hdr{{background:linear-gradient(135deg,#3b021f,#ec4899);padding:28px 24px;text-align:center;}}
  .hdr h1{{margin:0;color:#fff;font-size:1.4rem;letter-spacing:1px;}}
  .hdr p{{margin:6px 0 0;color:#fce7f3;font-size:.85rem;}}
  .urgency{{background:{band};border-left:6px solid {color};padding:16px 24px;
            display:flex;align-items:center;gap:14px;}}
  .urgency .big-emoji{{font-size:2.2rem;line-height:1;}}
  .urgency .tag{{font-size:1.15rem;font-weight:800;color:{color};letter-spacing:1px;}}
  .urgency .sub{{font-size:.85rem;color:#374151;margin-top:2px;}}
  .body{{padding:28px 30px;color:#374151;}}
  .body p{{margin:0 0 14px;line-height:1.7;font-size:.92rem;}}
  .detail-box{{background:#fdf4ff;border:1.5px solid #e9d5ff;border-radius:12px;
               padding:18px 22px;margin:18px 0;}}
  .dr{{display:flex;justify-content:space-between;align-items:center;
       padding:8px 0;border-bottom:1px dashed #e9d5ff;font-size:.88rem;}}
  .dr:last-child{{border-bottom:none;}}
  .dlabel{{color:#7c3aed;font-weight:700;}}
  .dval{{color:#111827;font-weight:600;text-align:right;max-width:58%;}}
  .checklist{{background:#f0fdf4;border-left:4px solid #16a34a;border-radius:0 10px 10px 0;
              padding:14px 18px 14px 20px;margin:16px 0;}}
  .checklist li{{margin:7px 0;font-size:.88rem;color:#374151;}}
  .note{{background:#fef9c3;border:1px solid #fde68a;border-radius:10px;
         padding:12px 16px;font-size:.83rem;color:#92400e;margin-top:14px;}}
  .footer{{background:#fdf4ff;text-align:center;padding:18px;
           font-size:.76rem;color:#9ca3af;border-top:1px solid #e9d5ff;}}
</style>
</head>
<body>
<div class="wrap">

  <div class="hdr">
    <h1>&#x1F489; Child Vaccination System</h1>
    <p>Appointment Reminder &mdash; Sent by Admin</p>
  </div>

  <div class="urgency">
    <div class="big-emoji">{emoji}</div>
    <div>
      <div class="tag">APPOINTMENT {tag}</div>
      <div class="sub">Scheduled Date: <strong>{appt_date_str}</strong></div>
    </div>
  </div>

  <div class="body">
    <p>Dear <strong>{p_name}</strong>,</p>
    <p>{msg}</p>
    <p>Please find the appointment details below:</p>

    <div class="detail-box">
      <div class="dr">
        <span class="dlabel">&#128100; Child Name</span>
        <span class="dval">{c_name}</span>
      </div>
      <div class="dr">
        <span class="dlabel">&#128197; Appointment Date</span>
        <span class="dval">{appt_date_str}</span>
      </div>
      <div class="dr">
        <span class="dlabel">&#128137; Vaccination</span>
        <span class="dval">{vacc_name}</span>
      </div>
      <div class="dr">
        <span class="dlabel">&#127973; Hospital</span>
        <span class="dval">{hosp_name}</span>
      </div>
    </div>

    <p><strong>Please bring the following documents on the day of appointment:</strong></p>
    <ul class="checklist">
      <li>&#9989; This reminder email (printed or on your phone)</li>
      <li>&#9989; Child's birth certificate or ID proof</li>
      <li>&#9989; Parent's Aadhaar card</li>
      <li>&#9989; Previous vaccination records (if any)</li>
    </ul>

    <div class="note">
      &#9888; If you need to reschedule or have any questions, please contact the hospital directly as soon as possible.
    </div>
  </div>

  <div class="footer">
    &copy; 2026 Child Vaccination System &nbsp;|&nbsp;
    This is an automated reminder. Please do not reply to this email.<br>
    Support: {FROM_EMAIL}
  </div>
</div>
</body></html>"""

    try:
        msg_obj            = MIMEMultipart("alternative")
        msg_obj["From"]    = f"Child Vaccination System <{FROM_EMAIL}>"
        msg_obj["To"]      = to_email
        msg_obj["Subject"] = subject
        msg_obj.attach(MIMEText(html, "html", "utf-8"))
        srv = smtplib.SMTP("smtp.gmail.com", 587)
        srv.starttls()
        srv.login(FROM_EMAIL, APP_PASSWORD)
        srv.sendmail(FROM_EMAIL, to_email, msg_obj.as_string())
        srv.quit()
        return True, ""
    except Exception as ex:
        return False, str(ex)


# ── AJAX: SEND SINGLE REMINDER ────────────────────────────────────────────────
if action == "send_single":
    print("Content-Type: application/json\n")
    appt_id = (form.getvalue("appt_id") or "").strip()
    if not appt_id.isdigit():
        print(json.dumps({"success": False, "message": "Invalid appointment ID"}))
        con.close(); sys.exit()
    try:
        cur.execute("""
            SELECT id, p_name, email_id, c_name, vaccination_name, appointment_date, hospital_name
            FROM hospital_appointment WHERE id = %s
        """, (int(appt_id),))
        row = cur.fetchone()
        if not row:
            print(json.dumps({"success": False, "message": "Appointment not found"}))
            con.close(); sys.exit()
        appt_d    = to_date(row["appointment_date"])
        today_d   = date.today()
        days_left = (appt_d - today_d).days if appt_d else 0
        date_str  = appt_d.strftime("%d %b %Y") if appt_d else str(row["appointment_date"])
        ok, err   = send_reminder_email(
            row["email_id"], row["p_name"], row["c_name"],
            date_str, row["vaccination_name"], row["hospital_name"], days_left
        )
        if ok:
            print(json.dumps({"success": True,  "message": f"Reminder sent successfully to {row['email_id']}"}))
        else:
            print(json.dumps({"success": False, "message": f"Email failed: {err}"}))
    except Exception as ex:
        print(json.dumps({"success": False, "message": str(ex)}))
    con.close(); sys.exit()


# ── AJAX: SEND ALL REMINDERS ──────────────────────────────────────────────────
if action == "send_all":
    print("Content-Type: application/json\n")
    today_d      = date.today()
    target_dates = [today_d + timedelta(days=d) for d in [0, 1, 2, 3]]
    sent = failed = skipped = 0
    try:
        cur.execute("""
            SELECT id, p_name, email_id, c_name, vaccination_name, appointment_date, hospital_name
            FROM hospital_appointment
            WHERE appointment_date IN (%s, %s, %s, %s)
              AND (status IS NULL OR status IN ('pending', 'approved'))
        """, tuple(d.strftime("%Y-%m-%d") for d in target_dates))
        rows = cur.fetchall()
        for row in rows:
            email = (row["email_id"] or "").strip()
            if not email or "@" not in email:
                skipped += 1
                continue
            appt_d    = to_date(row["appointment_date"])
            days_left = (appt_d - today_d).days if appt_d else 0
            date_str  = appt_d.strftime("%d %b %Y") if appt_d else str(row["appointment_date"])
            ok, _     = send_reminder_email(
                email, row["p_name"], row["c_name"],
                date_str, row["vaccination_name"], row["hospital_name"], days_left
            )
            if ok: sent += 1
            else:  failed += 1
        msg = (f"Done! &nbsp; Sent: <strong>{sent}</strong> &nbsp;|&nbsp; "
               f"Failed: <strong>{failed}</strong> &nbsp;|&nbsp; "
               f"Skipped (no email): <strong>{skipped}</strong>")
        print(json.dumps({"success": True, "message": msg, "sent": sent, "failed": failed, "skipped": skipped}))
    except Exception as ex:
        print(json.dumps({"success": False, "message": str(ex)}))
    con.close(); sys.exit()


# ── PAGE RENDER ───────────────────────────────────────────────────────────────
print("Content-Type: text/html\r\n\r\n")

today_d      = date.today()
target_dates = [today_d + timedelta(days=d) for d in [0, 1, 2, 3]]

try:
    cur.execute("""
        SELECT id, p_name, email_id, c_name, vaccination_name, appointment_date, hospital_name,
               COALESCE(status, 'pending') AS status
        FROM hospital_appointment
        WHERE appointment_date IN (%s, %s, %s, %s)
          AND (status IS NULL OR status IN ('pending', 'approved'))
        ORDER BY appointment_date ASC, id ASC
    """, tuple(d.strftime("%Y-%m-%d") for d in target_dates))
    appointments = cur.fetchall()
except Exception:
    appointments = []

# Count per bucket
cnt = {0: 0, 1: 0, 2: 0, 3: 0}
for a in appointments:
    d = to_date(a["appointment_date"])
    if d:
        diff = (d - today_d).days
        if diff in cnt:
            cnt[diff] += 1

total_appts = len(appointments)

# Build table rows
rows_html = ""
for i, appt in enumerate(appointments, 1):
    appt_d    = to_date(appt["appointment_date"])
    diff      = (appt_d - today_d).days if appt_d else -1
    date_str  = appt_d.strftime("%d %b %Y") if appt_d else str(appt["appointment_date"])
    email_val = (appt["email_id"] or "").strip()
    search_str = f"{(appt['p_name'] or '').lower()} {(appt['c_name'] or '').lower()} {(appt['vaccination_name'] or '').lower()} {(appt['hospital_name'] or '').lower()}"

    if diff == 0:
        badge = '<span class="badge-today"><i class="fas fa-bell me-1"></i>Today</span>'
    elif diff == 1:
        badge = '<span class="badge-1"><i class="fas fa-clock me-1"></i>In 1 Day</span>'
    elif diff == 2:
        badge = '<span class="badge-2"><i class="fas fa-calendar-day me-1"></i>In 2 Days</span>'
    else:
        badge = '<span class="badge-3"><i class="fas fa-calendar-week me-1"></i>In 3 Days</span>'

    if email_val and "@" in email_val:
        send_btn   = f'<button class="btn-send-row" onclick="sendSingle({appt["id"]}, this)"><i class="fas fa-paper-plane me-1"></i>Send</button>'
        email_disp = f'<span class="email-cell">{email_val}</span>'
    else:
        send_btn   = '<button class="btn-send-row no-email-btn" disabled><i class="fas fa-ban me-1"></i>No Email</button>'
        email_disp = '<span class="no-email-label"><i class="fas fa-exclamation-triangle me-1"></i>No Email</span>'

    rows_html += f"""
    <tr data-diff="{diff}" data-search="{search_str}">
      <td class="text-center fw-bold" style="color:#7c3aed;">{i}</td>
      <td><i class="fas fa-user me-1" style="color:#ec4899;"></i>{appt['p_name'] or '—'}</td>
      <td>{email_disp}</td>
      <td><i class="fas fa-baby me-1" style="color:#7c3aed;"></i>{appt['c_name'] or '—'}</td>
      <td>{appt['vaccination_name'] or '—'}</td>
      <td><i class="fas fa-calendar me-1" style="color:#ec4899;"></i>{date_str}</td>
      <td>{appt['hospital_name'] or '—'}</td>
      <td class="text-center">{badge}</td>
      <td class="text-center">{send_btn}</td>
    </tr>"""

if not rows_html:
    rows_html = """
    <tr><td colspan="9" class="text-center py-5" style="color:#9ca3af;">
      <i class="fas fa-calendar-check fa-3x mb-3 d-block" style="color:#e9d5ff;"></i>
      <strong>No appointments found for today or the next 3 days.</strong>
    </td></tr>"""

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Appointment Reminders – CVS Admin</title>
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

/* NAVBAR */
.navbar {{
  background: linear-gradient(135deg, #3b021f, #ec4899, #fdf2f8) !important;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  padding: 15px 20px;
}}
.navbar-brand {{ font-weight:600; color:white!important; letter-spacing:2px; text-transform:uppercase; }}
.navbar-brand i {{ margin-right:10px; color:#fda4af; font-size:1.5rem; animation:pulse 2s infinite; }}
@keyframes pulse {{ 0%,100%{{transform:scale(1);}} 50%{{transform:scale(1.1);}} }}

.mobile-menu-toggle {{
  display:none; background:rgba(255,255,255,.15);
  border:1.5px solid rgba(255,255,255,.35); color:white;
  padding:6px 12px; border-radius:8px; font-size:1.2rem;
  cursor:pointer; transition:all .3s; line-height:1;
}}
.mobile-menu-toggle:hover {{ background:rgba(255,255,255,.28); }}

.btn-logout {{
  background: linear-gradient(135deg, #ee0979, #ff6a00);
  border:none; padding:8px 20px; border-radius:25px; color:white;
  font-weight:600; transition:all .3s; box-shadow:0 4px 15px rgba(238,9,121,.4); font-size:.9rem;
}}
.btn-logout:hover {{ transform:translateY(-2px); box-shadow:0 6px 20px rgba(238,9,121,.6); color:white; }}

/* SIDEBAR */
.sidebar {{
  min-height:100vh;
  background: linear-gradient(135deg, #3b021f, #ec4899);
  box-shadow: 4px 0 15px rgba(0,0,0,.2);
  padding: 20px 0;
}}
.sidebar-overlay {{ display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,.5); z-index:998; }}
.sidebar-overlay.show {{ display:block; }}
.sidebar-link {{
  display:block; padding:12px 15px; color:#ecf0f1; text-decoration:none;
  transition:all .3s; border-left:4px solid transparent;
  font-weight:500; margin:5px 0; font-size:.95rem;
}}
.sidebar-link:hover, .sidebar-link.active {{
  background: linear-gradient(90deg, #ec4899, transparent);
  color:#fff; border-left:4px solid #fdf2f8; padding-left:20px;
}}
.sidebar-link i {{ margin-right:10px; width:20px; text-align:center; }}

/* CONTENT */
.content-area {{ padding:25px; min-height:100vh; }}

/* PAGE HEADER */
.page-header {{
  background:white; padding:22px 25px; border-radius:18px;
  margin-bottom:20px; box-shadow:0 8px 25px rgba(0,0,0,.12);
  border-left:6px solid #ec4899;
}}
.page-header h4 {{
  margin:0; color:#0f172a; font-weight:700; font-size:1.5rem;
  text-transform:uppercase; letter-spacing:1px;
}}
.page-header h4 i {{ margin-right:12px; color:#3b021f; }}
.page-header .sub {{ font-size:.82rem; color:#6b7280; margin-top:6px; }}

/* STAT CARDS */
.count-card {{
  border-radius:16px; padding:20px 24px; box-shadow:0 6px 20px rgba(0,0,0,.10);
  display:flex; align-items:center; gap:16px; margin-bottom:20px;
}}
.count-card .card-icon {{
  font-size:1.6rem; width:52px; height:52px; border-radius:12px;
  display:flex; align-items:center; justify-content:center; flex-shrink:0;
}}
.count-card .card-num   {{ font-size:2rem; font-weight:800; line-height:1; }}
.count-card .card-label {{ font-size:.78rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; opacity:.8; margin-top:2px; }}
.card-today     {{ background:#fee2e2; color:#991b1b; }}
.card-today     .card-icon {{ background:#fca5a5; color:#991b1b; }}
.card-1day      {{ background:#fffbeb; color:#92400e; }}
.card-1day      .card-icon {{ background:#fde68a; color:#b45309; }}
.card-2day      {{ background:#ede9fe; color:#4c1d95; }}
.card-2day      .card-icon {{ background:#c4b5fd; color:#4c1d95; }}
.card-3day      {{ background:#d1fae5; color:#065f46; }}
.card-3day      .card-icon {{ background:#6ee7b7; color:#065f46; }}

/* FILTER TABS */
.filter-tabs {{
  display:flex; flex-wrap:wrap; gap:10px; background:white; border-radius:16px;
  padding:16px 20px; box-shadow:0 6px 20px rgba(0,0,0,.10); margin-bottom:20px; align-items:center;
}}
.tab-btn {{
  border:2px solid #8e2de2; border-radius:25px; padding:7px 18px;
  font-size:.83rem; font-weight:700; cursor:pointer;
  background:transparent; color:#8e2de2; transition:all .25s;
}}
.tab-btn:hover, .tab-btn.active {{
  background:linear-gradient(135deg,#8e2de2,#ec4899); color:#fff; border-color:transparent;
}}
.showing-label {{ margin-left:auto; font-size:.82rem; color:#6b7280; font-weight:600; }}

/* TABLE CARD */
.table-card {{
  background:white; border-radius:16px; padding:22px 25px;
  box-shadow:0 6px 20px rgba(0,0,0,.10); margin-bottom:20px;
}}
.table-card-header {{
  display:flex; flex-wrap:wrap; align-items:center;
  justify-content:space-between; gap:12px; margin-bottom:16px;
}}
.table-card-title {{ font-size:1rem; font-weight:700; color:#0f172a; border-left:4px solid #ec4899; padding-left:12px; }}

.search-box {{
  border:2px solid #e5e7eb; border-radius:10px; padding:8px 14px;
  font-size:.85rem; outline:none; width:200px; transition:.2s;
}}
.search-box:focus {{ border-color:#8e2de2; box-shadow:0 0 0 3px rgba(142,45,226,.15); }}

.btn-send-all {{
  background:linear-gradient(135deg,#3b021f,#ec4899);
  border:none; border-radius:25px; padding:9px 22px;
  color:white; font-weight:700; font-size:.88rem; cursor:pointer;
  box-shadow:0 4px 15px rgba(236,72,153,.35); transition:all .3s; white-space:nowrap;
}}
.btn-send-all:hover {{ transform:translateY(-2px); box-shadow:0 6px 20px rgba(236,72,153,.5); }}
.btn-send-all:disabled {{ opacity:.7; transform:none; cursor:not-allowed; }}

/* TABLE */
.table thead th {{
  background:linear-gradient(135deg,#3b021f,#9d174d);
  color:#fff; font-size:.78rem; text-transform:uppercase;
  letter-spacing:.5px; padding:12px 10px; white-space:nowrap; border:none;
}}
.table tbody tr:hover {{ background:#fdf4ff; }}
.table td {{ font-size:.85rem; vertical-align:middle; padding:10px; border-color:#f3e8ff; }}

/* BADGES */
.badge-today {{ background:#fee2e2; color:#dc2626; border:1.5px solid #fca5a5; border-radius:20px; padding:4px 12px; font-size:.75rem; font-weight:700; white-space:nowrap; }}
.badge-1     {{ background:#fffbeb; color:#d97706; border:1.5px solid #fcd34d; border-radius:20px; padding:4px 12px; font-size:.75rem; font-weight:700; white-space:nowrap; }}
.badge-2     {{ background:#ede9fe; color:#7c3aed; border:1.5px solid #c4b5fd; border-radius:20px; padding:4px 12px; font-size:.75rem; font-weight:700; white-space:nowrap; }}
.badge-3     {{ background:#d1fae5; color:#16a34a; border:1.5px solid #6ee7b7; border-radius:20px; padding:4px 12px; font-size:.75rem; font-weight:700; white-space:nowrap; }}

/* ROW BUTTON */
.btn-send-row {{
  background:linear-gradient(135deg,#8e2de2,#ec4899);
  border:none; border-radius:20px; padding:5px 14px;
  color:#fff; font-size:.78rem; font-weight:700; cursor:pointer; transition:all .25s; white-space:nowrap;
}}
.btn-send-row:hover {{ transform:translateY(-1px); opacity:.9; }}
.btn-send-row.sent-ok  {{ background:linear-gradient(135deg,#16a34a,#4ade80)!important; cursor:default; }}
.btn-send-row.sent-err {{ background:linear-gradient(135deg,#dc2626,#f87171)!important; }}
.no-email-btn  {{ background:#e5e7eb!important; color:#9ca3af!important; cursor:not-allowed; border:none; border-radius:20px; padding:5px 14px; font-size:.78rem; font-weight:700; }}
.no-email-label {{ color:#9ca3af; font-size:.8rem; font-style:italic; }}
.email-cell {{ font-size:.8rem; color:#374151; word-break:break-all; }}

/* RESULT BAR */
.result-bar {{
  display:none; border-radius:12px; padding:14px 20px;
  font-weight:600; font-size:.9rem; margin-bottom:16px;
  animation:fadeSlide .4s ease;
}}
.result-bar.success {{ background:#d1fae5; color:#065f46; border-left:5px solid #16a34a; }}
.result-bar.error   {{ background:#fee2e2; color:#991b1b; border-left:5px solid #dc2626; }}
@keyframes fadeSlide {{ from{{opacity:0;transform:translateY(-8px);}} to{{opacity:1;transform:translateY(0);}} }}

/* MOBILE */
@media(max-width:992px) {{
  .mobile-menu-toggle {{ display:block; }}
  .sidebar {{
    position:fixed; top:0; left:-260px; width:240px;
    height:100%; z-index:999; transition:left .3s; padding-top:60px;
  }}
  .sidebar.show {{ left:0; }}
  .content-area {{ padding:15px; }}
  .search-box {{ width:130px; }}
  .showing-label {{ display:none; }}
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
      <a href="admin_vaccination_schedule.py" class="sidebar-link"><i class="fa-solid fa-syringe"></i> Vaccination Schedule</a>
      <a href="admin_appointment_reminder.py" class="sidebar-link active"><i class="fas fa-bell"></i> Appointment Reminders</a>
      <a href="admin_export_data.py" class="sidebar-link"><i class="fas fa-file-export"></i> Export Data</a>
      <a href="admin_view_feedback.py" class="sidebar-link"><i class="fas fa-comment-dots"></i> Feedback</a>
    </div>

    <!-- CONTENT -->
    <div class="col-lg-10 col-md-9 col-12 content-area">

      <!-- PAGE HEADER -->
      <div class="page-header">
        <h4><i class="fas fa-bell"></i> Appointment Reminders</h4>
        <div class="sub">
          <i class="fas fa-calendar-alt me-1"></i>
          Appointments from <strong>{today_d.strftime("%d %b %Y")}</strong>
          to <strong>{(today_d + timedelta(days=3)).strftime("%d %b %Y")}</strong>
          &nbsp;&mdash;&nbsp; <strong>{total_appts}</strong> appointment(s) found
        </div>
      </div>

      <!-- STAT CARDS -->
      <div class="row g-3 mb-2">
        <div class="col-6 col-lg-3">
          <div class="count-card card-today">
            <div class="card-icon"><i class="fas fa-bell"></i></div>
            <div><div class="card-num">{cnt[0]}</div><div class="card-label">Today</div></div>
          </div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="count-card card-1day">
            <div class="card-icon"><i class="fas fa-clock"></i></div>
            <div><div class="card-num">{cnt[1]}</div><div class="card-label">In 1 Day</div></div>
          </div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="count-card card-2day">
            <div class="card-icon"><i class="fas fa-calendar-day"></i></div>
            <div><div class="card-num">{cnt[2]}</div><div class="card-label">In 2 Days</div></div>
          </div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="count-card card-3day">
            <div class="card-icon"><i class="fas fa-calendar-week"></i></div>
            <div><div class="card-num">{cnt[3]}</div><div class="card-label">In 3 Days</div></div>
          </div>
        </div>
      </div>

      <!-- FILTER TABS -->
      <div class="filter-tabs">
        <button class="tab-btn active" id="tab-all" onclick="filterTab('all', this)">
          <i class="fas fa-list me-1"></i> All ({total_appts})
        </button>
        <button class="tab-btn" id="tab-0" onclick="filterTab('0', this)">
          <i class="fas fa-bell me-1"></i> Today ({cnt[0]})
        </button>
        <button class="tab-btn" id="tab-1" onclick="filterTab('1', this)">
          <i class="fas fa-clock me-1"></i> In 1 Day ({cnt[1]})
        </button>
        <button class="tab-btn" id="tab-2" onclick="filterTab('2', this)">
          <i class="fas fa-calendar-day me-1"></i> In 2 Days ({cnt[2]})
        </button>
        <button class="tab-btn" id="tab-3" onclick="filterTab('3', this)">
          <i class="fas fa-calendar-week me-1"></i> In 3 Days ({cnt[3]})
        </button>
        <span class="showing-label" id="showingLabel">Showing: {total_appts} of {total_appts}</span>
      </div>

      <!-- RESULT BAR -->
      <div class="result-bar" id="resultBar"></div>

      <!-- TABLE CARD -->
      <div class="table-card">
        <div class="table-card-header">
          <div class="table-card-title">
            <i class="fas fa-paper-plane me-2" style="color:#ec4899;"></i>
            Email Reminder Notifications
          </div>
          <div class="d-flex gap-2 align-items-center flex-wrap">
            <input type="text" class="search-box" id="searchInput"
                   placeholder="&#128269; Search..." oninput="searchTable()">
            <button class="btn-send-all" id="sendAllBtn" onclick="sendAllReminders()">
              <i class="fas fa-paper-plane me-1"></i> Send All Reminders
            </button>
          </div>
        </div>

        <div class="table-responsive">
          <table class="table table-hover align-middle" id="reminderTable">
            <thead>
              <tr>
                <th class="text-center" style="width:45px;">#</th>
                <th><i class="fas fa-user me-1"></i> Parent Name</th>
                <th><i class="fas fa-envelope me-1"></i> Email</th>
                <th><i class="fas fa-baby me-1"></i> Child Name</th>
                <th><i class="fas fa-syringe me-1"></i> Vaccination</th>
                <th><i class="fas fa-calendar me-1"></i> Appt. Date</th>
                <th><i class="fas fa-hospital me-1"></i> Hospital</th>
                <th class="text-center"><i class="fas fa-clock me-1"></i> Reminder</th>
                <th class="text-center"><i class="fas fa-paper-plane me-1"></i> Action</th>
              </tr>
            </thead>
            <tbody id="tableBody">
              {rows_html}
            </tbody>
          </table>
        </div>

        <div style="font-size:.8rem; color:#9ca3af; margin-top:6px;">
          <i class="fas fa-info-circle me-1"></i>
          Showing <strong id="visibleCount">{total_appts}</strong> record(s)
          &nbsp;|&nbsp; Reminder emails are sent to parents whose appointments fall today, tomorrow, in 2 days, or in 3 days.
        </div>
      </div>

    </div><!-- /content -->
  </div><!-- /row -->
</div><!-- /container -->

<script>
const ADMIN_ID = "{admin_id}";

// ── Result Bar ────────────────────────────────────────────────────────────────
function showResult(msg, type) {{
  const bar = document.getElementById('resultBar');
  const icon = type === 'success' ? 'check-circle' : 'exclamation-circle';
  bar.innerHTML = `<i class="fas fa-${{icon}} me-2"></i>${{msg}}`;
  bar.className = 'result-bar ' + type;
  bar.style.display = 'block';
  bar.scrollIntoView({{ behavior:'smooth', block:'nearest' }});
  setTimeout(() => {{ bar.style.display = 'none'; }}, 7000);
}}

// ── Send Single Reminder ──────────────────────────────────────────────────────
async function sendSingle(apptId, btn) {{
  btn.disabled  = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Sending...';
  try {{
    const fd = new FormData();
    fd.append('action',   'send_single');
    fd.append('appt_id',  apptId);
    fd.append('admin_id', ADMIN_ID);
    const res  = await fetch('admin_appointment_reminder.py', {{ method: 'POST', body: fd }});
    const data = await res.json();
    if (data.success) {{
      btn.innerHTML = '<i class="fas fa-check me-1"></i>Sent!';
      btn.classList.add('sent-ok');
      showResult(data.message, 'success');
    }} else {{
      btn.innerHTML = '<i class="fas fa-redo me-1"></i>Retry';
      btn.classList.add('sent-err');
      btn.disabled = false;
      showResult(data.message, 'error');
    }}
  }} catch(e) {{
    btn.innerHTML = '<i class="fas fa-redo me-1"></i>Retry';
    btn.disabled  = false;
    showResult('Network error: ' + e, 'error');
  }}
}}

// ── Send All Reminders ────────────────────────────────────────────────────────
async function sendAllReminders() {{
  const total = parseInt(document.getElementById('visibleCount').textContent) || 0;
  if (total === 0) {{
    showResult('No appointments to send reminders for.', 'error');
    return;
  }}
  if (!confirm(`Send reminder emails to ALL parents with appointments today or in the next 3 days?`)) return;

  const btn = document.getElementById('sendAllBtn');
  btn.disabled  = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Sending...';

  try {{
    const fd = new FormData();
    fd.append('action',   'send_all');
    fd.append('admin_id', ADMIN_ID);
    const res  = await fetch('admin_appointment_reminder.py', {{ method: 'POST', body: fd }});
    const data = await res.json();
    showResult(data.message, data.success ? 'success' : 'error');
    if (data.success && data.sent > 0) {{
      document.querySelectorAll('.btn-send-row:not(.no-email-btn)').forEach(b => {{
        b.innerHTML = '<i class="fas fa-check me-1"></i>Sent!';
        b.classList.add('sent-ok');
        b.disabled = true;
      }});
    }}
  }} catch(e) {{
    showResult('Network error: ' + e, 'error');
  }}
  btn.disabled  = false;
  btn.innerHTML = '<i class="fas fa-paper-plane me-1"></i> Send All Reminders';
}}

// ── Filter Tabs ───────────────────────────────────────────────────────────────
function filterTab(diff, btn) {{
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const rows = document.querySelectorAll('#tableBody tr[data-diff]');
  let count  = 0;
  rows.forEach(r => {{
    const show = diff === 'all' || r.dataset.diff === diff;
    r.style.display = show ? '' : 'none';
    if (show) count++;
  }});
  document.getElementById('visibleCount').textContent = count;
  document.getElementById('showingLabel').textContent = `Showing: ${{count}} of {total_appts}`;
  document.getElementById('searchInput').value = '';
}}

// ── Search ────────────────────────────────────────────────────────────────────
function searchTable() {{
  const q    = document.getElementById('searchInput').value.toLowerCase();
  const rows = document.querySelectorAll('#tableBody tr[data-diff]');
  let count  = 0;
  rows.forEach(r => {{
    const show = q === '' || r.dataset.search.includes(q);
    r.style.display = show ? '' : 'none';
    if (show) count++;
  }});
  document.getElementById('visibleCount').textContent = count;
  document.getElementById('showingLabel').textContent = `Showing: ${{count}} of {total_appts}`;
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-all').classList.add('active');
}}

// ── Sidebar ───────────────────────────────────────────────────────────────────
function toggleSidebar() {{
  document.getElementById('sidebar').classList.toggle('show');
  document.getElementById('sidebarOverlay').classList.toggle('show');
}}
document.addEventListener('click', function(e) {{
  const sb  = document.getElementById('sidebar');
  const btn = document.querySelector('.mobile-menu-toggle');
  if (window.innerWidth < 992 && btn && !sb.contains(e.target) && !btn.contains(e.target) && sb.classList.contains('show')) {{
    sb.classList.remove('show');
    document.getElementById('sidebarOverlay').classList.remove('show');
  }}
}});

// ── Logout ────────────────────────────────────────────────────────────────────
function logout() {{
  if (confirm('Are you sure you want to logout?'))
    window.location.href = 'main.py';
}}
</script>
</body>
</html>
""")

con.close()