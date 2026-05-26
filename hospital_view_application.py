#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgitb
import sys
import cgi
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")

FROM_EMAIL   = "childvaccinationsystem2026@gmail.com"
APP_PASSWORD = "wuxe lqii npcp nglf"


# ── EMAIL ────────────────────────────────────────────────────────────────────
def send_email(to_email, subject, body):
    try:
        if not to_email or to_email == "N/A" or "@" not in to_email:
            return False, f"Invalid email address: {to_email}"
        msg = MIMEMultipart('alternative')
        msg['From']    = f"Child Vaccination System <{FROM_EMAIL}>"
        msg['To']      = to_email
        msg['Subject'] = subject
        html_body = body.replace('\n', '<br>')
        html_content = f"""
        <html><head><style>
          body {{ font-family:Arial,sans-serif; line-height:1.6; color:#333; }}
          .container {{ max-width:600px; margin:0 auto; padding:20px; }}
          .header {{ background:linear-gradient(135deg,#7c3aed 0%,#a78bfa 100%);
                     color:white; padding:20px; text-align:center; border-radius:10px 10px 0 0; }}
          .content {{ background:#f9f9f9; padding:30px; border-radius:0 0 10px 10px; }}
          .footer  {{ text-align:center; color:#666; font-size:12px; margin-top:20px;
                     padding-top:20px; border-top:1px solid #ddd; }}
        </style></head><body>
          <div class="container">
            <div class="header"><h2>&#x1F489; Child Vaccination System</h2></div>
            <div class="content">{html_body}</div>
            <div class="footer">
              <p>This is an automated message from Child Vaccination System</p>
              <p>Support: {FROM_EMAIL}</p>
            </div>
          </div>
        </body></html>"""
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(FROM_EMAIL, APP_PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        server.quit()
        return True, "Email sent successfully"
    except smtplib.SMTPAuthenticationError as e:
        return False, f"SMTP Authentication failed: {str(e)}"
    except smtplib.SMTPRecipientsRefused as e:
        return False, f"Recipient email refused: {str(e)}"
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        return False, f"Email failed: {str(e)}"


# ── DB ───────────────────────────────────────────────────────────────────────
def get_db():
    try:
        con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
        return con, con.cursor()
    except Exception as e:
        return None, str(e)


# ── FORM PARAMS ──────────────────────────────────────────────────────────────
form            = cgi.FieldStorage()
app_id          = form.getvalue('app_id',          '').strip()
status          = form.getvalue('status',          '').strip().lower()
hospital_id     = form.getvalue('hospital_id',     '').strip()
filter_date     = form.getvalue('filter_date',     '').strip()
reschedule_date = form.getvalue('reschedule_date', '').strip()

active_tab = form.getvalue('tab', 'pending').strip().lower()
if active_tab not in ('pending', 'approved', 'rescheduled'):
    active_tab = 'pending'


# ============================================================
# POST HANDLER — status update (AJAX)
# ============================================================
if app_id and status:
    print("Content-Type: application/json\n")

    def send_json(ok, msg=""):
        print(json.dumps({"success": ok, "message": msg}))
        sys.exit()

    if not app_id.isdigit():
        send_json(False, "Invalid application ID.")
    if status not in ('approved', 'rescheduled'):
        send_json(False, "Invalid status value.")
    if status == 'rescheduled' and not reschedule_date:
        send_json(False, "Reschedule date is required.")

    con, cur = get_db()
    if con is None:
        send_json(False, f"Database connection failed: {cur}")

    try:
        cur.execute("SELECT * FROM parentform WHERE id = %s", (int(app_id),))
        row = cur.fetchone()
        if not row:
            con.close()
            send_json(False, f"No application found with ID {app_id}.")

        # ── parentform column indices (0-based) — from Image 2 ──────────
        # 0=id,       1=p_name,      2=p_type,          3=p_gender,
        # 4=mobile,   5=email,       6=aadhaar_number,
        # 7=c_name,   8=c_gender,    9=c_dob,            10=c_order,
        # 11=vaccin,  12=vaccin_age, 13=vaccination,
        # 14=appointment_date,       15=age_group,
        # 16=vaccine_name,           17=address,
        # 18=district, 19=pincode,   20=hospital_name,   21=status

        def col(idx, fallback=""):
            return str(row[idx]).strip() if len(row) > idx and row[idx] is not None else fallback

        p_name    = col(1,  "Parent")
        p_gender  = col(3,  "N/A")
        p_email   = col(5,  "")
        mobile    = col(4,  "N/A")
        c_name    = col(7,  "your child")
        c_gender  = col(8,  "N/A")
        c_dob     = col(9,  "N/A")
        appt_date = col(14, "N/A")
        age_group = col(15, "N/A")
        vacc_name = col(16, "N/A")
        hosp_name = col(20, "N/A")

        new_appt_date = reschedule_date if status == 'rescheduled' else appt_date

        # ── 1. Update parentform ─────────────────────────────────────────
        if status == 'rescheduled':
            cur.execute(
                "UPDATE parentform SET status=%s, appointment_date=%s WHERE id=%s",
                (status, reschedule_date, int(app_id))
            )
        else:
            cur.execute(
                "UPDATE parentform SET status=%s WHERE id=%s",
                (status, int(app_id))
            )
        con.commit()

        if cur.rowcount == 0:
            con.close()
            send_json(False, f"Update failed — no row matched ID {app_id}.")

        # ── 2. Upsert into hospital_appointment ─────────────────────────
        # hospital_appointment columns (0-based) — from Image 1:
        # 0=id,        1=p_name,     2=p_gender,    3=email_id,
        # 4=mobile,    5=c_name,     6=c_gender,    7=c_dob,
        # 8=age_group, 9=vaccination_name,           10=appointment_date,
        # 11=hospital_name, 12=status, 13=create_at

        ha_status = 'pending'

        cur.execute(
            """SELECT id FROM hospital_appointment
               WHERE p_name=%s AND c_name=%s AND hospital_name=%s
               LIMIT 1""",
            (p_name, c_name, hosp_name)
        )
        existing = cur.fetchone()

        if existing:
            cur.execute(
                """UPDATE hospital_appointment
                   SET p_gender=%s, email_id=%s, mobile=%s,
                       c_gender=%s, c_dob=%s, age_group=%s,
                       vaccination_name=%s, appointment_date=%s, status=%s
                   WHERE id=%s""",
                (p_gender, p_email, mobile,
                 c_gender, c_dob, age_group,
                 vacc_name, new_appt_date, ha_status,
                 existing[0])
            )
        else:
            cur.execute(
                """INSERT INTO hospital_appointment
                   (p_name, p_gender, email_id, mobile,
                    c_name, c_gender, c_dob,
                    age_group, vaccination_name,
                    appointment_date, hospital_name, status)
                   VALUES (%s, %s, %s, %s,
                           %s, %s, %s,
                           %s, %s,
                           %s, %s, %s)""",
                (p_name, p_gender, p_email, mobile,
                 c_name, c_gender, c_dob,
                 age_group, vacc_name,
                 new_appt_date, hosp_name, ha_status)
            )
        con.commit()

        # ── 3. Build email ───────────────────────────────────────────────
        if status == 'approved':
            subject = "\u2705 Vaccination Appointment APPROVED"
            body = f"""Dear {p_name},

We are pleased to inform you that your vaccination appointment has been APPROVED.

\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501
  APPOINTMENT DETAILS
\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501

  Child Name          : {c_name}
  Appointment Date    : {appt_date}
  Vaccination Name    : {vacc_name}
  Hospital            : {hosp_name}

\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501

Please arrive at the hospital on the scheduled date with:
  - This confirmation email (printed or on your phone)
  - Child's birth certificate or ID proof
  - Parent's Aadhaar card
  - Previous vaccination records (if any)

We look forward to helping keep {c_name} healthy!

Best regards,
{hosp_name}
Child Vaccination System
"""
        else:  # rescheduled
            subject = "\U0001f4c5 Vaccination Appointment RESCHEDULED"
            body = f"""Dear {p_name},

Your vaccination appointment for {c_name} has been RESCHEDULED to a new date.

\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501
  NEW APPOINTMENT DETAILS
\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501

  Child Name             : {c_name}
  Reschedule Date        : {reschedule_date}
  Vaccination Name       : {vacc_name}
  Hospital               : {hosp_name}

\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501

Your original appointment date could not be accommodated.
Please arrive at the hospital on the new scheduled date with:
  - This confirmation email (printed or on your phone)
  - Child's birth certificate or ID proof
  - Parent's Aadhaar card
  - Previous vaccination records (if any)

We apologise for any inconvenience caused.

Best regards,
{hosp_name}
Child Vaccination System
"""

        if p_email and "@" in p_email:
            email_sent, email_msg = send_email(p_email, subject, body)
        else:
            email_sent = False
            email_msg  = f"No valid email on record (found: '{p_email}')"

        result  = f"Application REG-{int(app_id):05d} marked as {status}. "
        result += "Saved to hospital appointment. "
        result += "Email sent to parent." if email_sent else f"Email not sent: {email_msg}"
        con.close()
        send_json(True, result)

    except Exception as e:
        try:
            con.rollback()
            con.close()
        except Exception:
            pass
        send_json(False, f"Database error: {str(e)}")


# ============================================================
# PAGE LOAD — GET
# ============================================================
print("Content-Type: text/html\n")

con, cur = get_db()
if con is None:
    print(f"<html><body><h2>Database Connection Failed!</h2><p>{cur}</p></body></html>")
    sys.exit()

hospital_name = ""
if hospital_id and hospital_id.isdigit():
    cur.execute("SELECT hospital_name FROM hospital WHERE id = %s", (int(hospital_id),))
    hosp_row = cur.fetchone()
    if hosp_row:
        hospital_name = hosp_row[0]

def fetch_rows(tab_status):
    if hospital_name and filter_date:
        cur.execute(
            "SELECT * FROM parentform WHERE hospital_name=%s AND status=%s AND appointment_date=%s",
            (hospital_name, tab_status, filter_date)
        )
    elif hospital_name:
        cur.execute(
            "SELECT * FROM parentform WHERE hospital_name=%s AND status=%s",
            (hospital_name, tab_status)
        )
    elif filter_date:
        cur.execute(
            "SELECT * FROM parentform WHERE status=%s AND appointment_date=%s",
            (tab_status, filter_date)
        )
    else:
        cur.execute("SELECT * FROM parentform WHERE status=%s", (tab_status,))
    return cur.fetchall()

pending_rows     = fetch_rows('pending')
approved_rows    = fetch_rows('approved')
rescheduled_rows = fetch_rows('rescheduled')

tab_cfg = {
    'pending':     {'badge': '<span class="badge-pending"><i class="fas fa-clock"></i> Pending</span>'},
    'approved':    {'badge': '<span class="badge-approved"><i class="fa-solid fa-calendar-check"></i> Approved</span>'},
    'rescheduled': {'badge': '<span class="badge-rejected"><i class="fa-solid fa-calendar-day"></i> Rescheduled</span>'},
}

hosp_subtitle = (
    f'<small style="font-size:0.85rem;color:#7c3aed;font-weight:500;'
    f'display:block;margin-top:5px;text-transform:none;">Hospital: {hospital_name}</small>'
    if hospital_name else ''
)

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Hospital - Parent Applications</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:linear-gradient(135deg,#083344,#22d3ee,#cffafe); min-height:100vh;
        font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif; overflow-x:hidden; }}
.navbar {{ box-shadow:0 4px 20px rgba(0,0,0,0.4); padding:15px 20px;
           background:linear-gradient(135deg,#083344,#22d3ee,#cffafe) !important; }}
.navbar .container-fluid {{ display:flex; flex-direction:row; align-items:center; flex-wrap:nowrap; position:relative; }}
.navbar-brand {{ font-weight:600; color:white !important; letter-spacing:2px; text-transform:uppercase; }}
.navbar-brand i {{ margin-right:10px; color:#e9d5ff; font-size:1.5rem; animation:bounce 2s infinite; }}
@keyframes bounce {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-5px)}} }}
.mobile-menu-toggle {{ display:none; flex-shrink:0; align-self:center;
  background:rgba(255,255,255,0.15); border:1.5px solid rgba(255,255,255,0.35); color:white;
  padding:6px 12px; border-radius:8px; font-size:1.2rem; cursor:pointer;
  transition:all 0.3s; backdrop-filter:blur(6px); line-height:1; margin-right:12px; }}
.mobile-menu-toggle:hover {{ background:rgba(255,255,255,0.28); color:white; }}
.btn-logout {{ flex-shrink:0; background:linear-gradient(135deg,#ee0979,#ff6a00); border:none;
  padding:8px 20px; border-radius:25px; color:white; font-weight:600;
  box-shadow:0 4px 15px rgba(238,9,121,0.4); font-size:0.9rem; white-space:nowrap; transition:all 0.3s; }}
.btn-logout:hover {{ transform:translateY(-2px); color:white; }}
.sidebar {{ min-height:100vh; background:linear-gradient(135deg,#083344,#22d3ee);
            box-shadow:4px 0 20px rgba(0,0,0,0.3); padding:20px 0; }}
.sidebar-link {{ display:block; padding:14px 18px; color:#e9d5ff; text-decoration:none;
  transition:all 0.3s; border-left:4px solid transparent; font-weight:500; margin:6px 0; }}
.sidebar-link:hover,.sidebar-link.active {{ background:linear-gradient(90deg,#22d3ee,transparent);
  color:#fff; border-left:4px solid #cffafe; padding-left:24px; }}
.sidebar-link i {{ margin-right:12px; width:22px; text-align:center; }}
.sidebar-overlay {{ display:none; position:fixed; top:0; left:0; width:100%; height:100%;
                    background:rgba(0,0,0,0.6); z-index:998; }}
.sidebar-overlay.show {{ display:block; }}
.content-wrap {{ padding:20px; }}
.page-title-card {{ background:white; border-radius:18px; padding:22px 25px; margin-bottom:20px;
  box-shadow:0 8px 25px rgba(0,0,0,0.12); border-left:6px solid #7c3aed; }}
.page-title {{ color:#0f172a; font-weight:700; font-size:1.5rem; text-transform:uppercase; letter-spacing:1px; margin:0; }}
.page-title i {{ margin-right:12px; color:#7c3aed; }}
.tab-nav {{ display:flex; gap:10px; margin-bottom:20px; flex-wrap:wrap; }}
.tab-btn {{ flex:1; min-width:130px; padding:14px 10px; border:none; border-radius:14px;
  font-weight:700; font-size:0.9rem; cursor:pointer; transition:all 0.3s;
  display:flex; align-items:center; justify-content:center; gap:8px;
  background:rgba(255,255,255,0.25); color:white;
  box-shadow:0 4px 12px rgba(0,0,0,0.15); backdrop-filter:blur(6px); }}
.tab-btn:hover {{ transform:translateY(-2px); background:rgba(255,255,255,0.35); }}
.tab-btn.active-pending  {{ background:linear-gradient(135deg,#d97706,#f59e0b); color:white; box-shadow:0 6px 18px rgba(245,158,11,0.5); }}
.tab-btn.active-approved {{ background:linear-gradient(135deg,#059669,#10b981); color:white; box-shadow:0 6px 18px rgba(16,185,129,0.5); }}
.tab-btn.active-rejected {{ background:linear-gradient(135deg,#dc2626,#ef4444); color:white; box-shadow:0 6px 18px rgba(220,38,38,0.5); }}
.tab-count {{ background:rgba(255,255,255,0.3); border-radius:20px; padding:2px 9px; font-size:0.8rem; font-weight:800; }}
.filter-card {{ background:white; border-radius:16px; padding:22px 25px; box-shadow:0 6px 20px rgba(0,0,0,0.10); margin-bottom:20px; }}
.filter-label {{ font-weight:600; color:#374151; font-size:0.9rem; margin-bottom:10px; display:block; }}
.filter-label i {{ margin-right:6px; color:#0ea5e9; }}
.filter-input {{ border:2px solid #e5e7eb; border-radius:10px; padding:11px 14px; font-size:0.95rem; width:100%; transition:border-color 0.3s; }}
.filter-input:focus {{ border-color:#7c3aed; outline:none; box-shadow:0 0 0 3px rgba(124,58,237,0.15); }}
.btn-filter {{ background:linear-gradient(135deg,#0ea5e9,#0284c7); border:none; border-radius:10px;
  padding:11px 0; color:white; font-weight:700; font-size:0.95rem; width:100%; transition:all 0.3s;
  box-shadow:0 4px 15px rgba(14,165,233,0.4); }}
.btn-filter:hover {{ transform:translateY(-2px); }}
.btn-clear {{ background:linear-gradient(135deg,#6b7280,#4b5563); border:none; border-radius:10px;
  padding:11px 0; color:white; font-weight:700; font-size:0.95rem; width:100%; transition:all 0.3s; }}
.btn-clear:hover {{ transform:translateY(-2px); }}
.tab-panel {{ display:none; }}
.tab-panel.active {{ display:block; }}
.table-container {{ background:linear-gradient(135deg,#fff,#f5f3ff); border-radius:18px;
  padding:25px; box-shadow:0 10px 30px rgba(0,0,0,0.15); border:1px solid rgba(124,58,237,0.2); }}
table {{ width:100%; border-collapse:separate; border-spacing:0; border-radius:12px; overflow:hidden; }}
table thead {{ background:#083344; color:white; }}
table thead th {{ padding:14px 10px; font-weight:600; text-transform:uppercase;
  letter-spacing:0.8px; font-size:0.82rem; white-space:nowrap; border:none; }}
table tbody tr {{ transition:all 0.3s; border-bottom:1px solid #ede9fe; background:white; }}
table tbody tr:hover {{ background:linear-gradient(90deg,#f5f3ff,#ede9fe); }}
table tbody td {{ padding:12px 10px; vertical-align:middle; font-size:0.88rem; color:#1e293b; }}
.no-data {{ text-align:center; padding:60px 20px; color:#64748b; }}
.badge-pending  {{ background:linear-gradient(135deg,#fef3c7,#fde68a); color:#92400e; border:1px solid #f59e0b; padding:5px 12px; border-radius:20px; font-weight:700; font-size:0.78rem; white-space:nowrap; }}
.badge-approved {{ background:linear-gradient(135deg,#d1fae5,#a7f3d0); color:#065f46; border:1px solid #10b981; padding:5px 12px; border-radius:20px; font-weight:700; font-size:0.78rem; white-space:nowrap; }}
.badge-rejected {{ background:linear-gradient(135deg,#fee2e2,#fecaca); color:#7f1d1d; border:1px solid #ef4444; padding:5px 12px; border-radius:20px; font-weight:700; font-size:0.78rem; white-space:nowrap; }}
.icon-badge {{ background:linear-gradient(135deg,#7c3aed,#a78bfa); color:white; padding:4px 10px; border-radius:12px; font-weight:700; font-size:0.82rem; }}
.btn-approve {{ background:linear-gradient(135deg,#059669,#10b981); color:white; border:none;
  padding:6px 14px; border-radius:18px; font-weight:600; cursor:pointer;
  transition:all 0.3s; box-shadow:0 3px 8px rgba(16,185,129,0.3); font-size:0.8rem; margin:2px; }}
.btn-approve:hover {{ transform:translateY(-2px); color:white; }}
.btn-reject {{ background:linear-gradient(135deg,#dc2626,#ef4444); color:white; border:none;
  padding:6px 14px; border-radius:18px; font-weight:600; cursor:pointer;
  transition:all 0.3s; box-shadow:0 3px 8px rgba(220,38,38,0.3); font-size:0.8rem; margin:2px; }}
.btn-reject:hover {{ transform:translateY(-2px); color:white; }}
.btn-view-det {{ background:linear-gradient(135deg,#0891b2,#06b6d4); color:white; border:none;
  padding:6px 14px; border-radius:18px; font-weight:600; cursor:pointer;
  transition:all 0.3s; box-shadow:0 3px 8px rgba(8,145,178,0.3); font-size:0.8rem; margin:2px; }}
.btn-view-det:hover {{ transform:translateY(-2px); color:white; }}
.modal-content {{ border-radius:18px; border:none; box-shadow:0 10px 40px rgba(0,0,0,0.3); }}
.modal-header {{ background:linear-gradient(135deg,#7c3aed,#a78bfa); color:white;
  border-radius:18px 18px 0 0; padding:18px 25px; border:none; }}
.modal-header.rh {{ background:linear-gradient(135deg,#dc2626,#f97316); }}
.modal-header .modal-title {{ font-weight:700; font-size:1.2rem; }}
.modal-header .btn-close {{ filter:brightness(0) invert(1); opacity:0.8; }}
.modal-body {{ padding:25px; background:#f5f3ff; max-height:70vh; overflow-y:auto; }}
.modal-footer {{ border:none; padding:15px 25px; background:#f5f3ff; border-radius:0 0 18px 18px; }}
.detail-section {{ background:white; border-radius:12px; padding:18px; margin-bottom:15px;
  border-left:4px solid #7c3aed; box-shadow:0 2px 6px rgba(0,0,0,0.05); }}
.detail-section h6 {{ color:#7c3aed; font-weight:700; margin-bottom:12px; font-size:1rem; }}
.detail-row {{ display:flex; padding:9px 0; border-bottom:1px solid #ede9fe; }}
.detail-row:last-child {{ border-bottom:none; }}
.detail-label {{ width:42%; color:#6d28d9; font-weight:600; font-size:0.87rem; }}
.detail-label i {{ margin-right:8px; width:16px; }}
.detail-value {{ width:58%; color:#1e293b; font-weight:500; font-size:0.9rem; }}
.reschedule-body {{ background:white !important; border-radius:0 0 18px 18px; padding:30px; }}
.rs-date-input {{ border:2px solid #e5e7eb; border-radius:12px; padding:13px 16px;
  font-size:1rem; width:100%; transition:all 0.3s; margin-top:8px; }}
.rs-date-input:focus {{ border-color:#dc2626; outline:none; box-shadow:0 0 0 3px rgba(220,38,38,0.15); }}
.btn-confirm-rs {{ background:linear-gradient(135deg,#dc2626,#f97316); border:none;
  border-radius:12px; padding:12px 0; color:white; font-weight:700; font-size:0.95rem;
  width:100%; transition:all 0.3s; box-shadow:0 4px 15px rgba(220,38,38,0.4); }}
.btn-confirm-rs:hover {{ transform:translateY(-2px); color:white; }}
.rs-error {{ color:#dc2626; font-size:0.82rem; margin-top:6px; display:none; }}
.toast-container {{ position:fixed; top:80px; right:20px; z-index:9999; }}
.toast-msg {{ border-radius:12px; padding:14px 22px; font-weight:600; min-width:320px;
  margin-bottom:10px; color:white; animation:slideInR 0.4s ease;
  box-shadow:0 6px 20px rgba(0,0,0,0.2); display:flex; align-items:center; gap:10px; }}
.toast-success {{ background:linear-gradient(135deg,#059669,#10b981); }}
.toast-error   {{ background:linear-gradient(135deg,#dc2626,#ef4444); }}
.toast-warning {{ background:linear-gradient(135deg,#d97706,#f59e0b); }}
@keyframes slideInR {{ from{{transform:translateX(120%);opacity:0}} to{{transform:translateX(0);opacity:1}} }}
@media (max-width:991.98px) {{
  .mobile-menu-toggle {{ display:flex; align-items:center; justify-content:center; }}
  .sidebar {{ position:fixed; left:-100%; top:0; width:280px; height:100vh; z-index:999; transition:left 0.3s; overflow-y:auto; }}
  .sidebar.show {{ left:0; }}
  .content-wrap {{ padding:10px; }}
  .navbar-brand {{ position:absolute; left:50%; transform:translateX(-50%); margin:0 !important; font-size:1rem; letter-spacing:1px; }}
}}
@media (max-width:767.98px) {{
  table thead th {{ font-size:0.72rem; padding:10px 5px; }}
  table tbody td {{ font-size:0.78rem; padding:10px 5px; }}
  .tab-btn {{ font-size:0.8rem; padding:11px 8px; min-width:100px; }}
}}
@media (max-width:575.98px) {{ .btn-logout {{ padding:6px 14px; font-size:0.8rem; }} }}
</style>
</head>
<body>

<script>const HOSPITAL_ID = "{hospital_id}"; const ACTIVE_TAB = "{active_tab}";</script>
<div class="toast-container" id="toastContainer"></div>

<!-- RESCHEDULE MODAL -->
<div class="modal fade" id="rescheduleModal" tabindex="-1" aria-hidden="true"
     data-bs-backdrop="static" data-bs-keyboard="false">
  <div class="modal-dialog modal-dialog-centered" style="max-width:460px;">
    <div class="modal-content">
      <div class="modal-header rh">
        <h5 class="modal-title"><i class="fas fa-calendar-alt"></i>&nbsp; Reschedule Appointment</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="reschedule-body">
        <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:10px;padding:12px 16px;margin-bottom:18px;">
          <i class="fas fa-file-alt" style="color:#dc2626;"></i>&nbsp;Application:&nbsp;
          <strong id="rsAppLabel" style="color:#dc2626;"></strong>
          &nbsp;&nbsp;|&nbsp;&nbsp;
          <i class="fas fa-baby" style="color:#7c3aed;"></i>
          &nbsp;<span id="rsChildLabel" style="color:#7c3aed;font-weight:600;"></span>
        </div>
        <p style="color:#6b7280;font-size:0.88rem;margin-bottom:18px;">
          <i class="fas fa-info-circle" style="color:#f97316;"></i>
          &nbsp;Select a <strong>future date</strong> for the new appointment.
          The parent will receive an email automatically.
        </p>
        <label style="font-weight:700;color:#374151;font-size:0.9rem;display:block;">
          <i class="fas fa-calendar-day" style="color:#dc2626;"></i>&nbsp;New Appointment Date
        </label>
        <input type="date" id="rsDateInput" class="rs-date-input" placeholder="Select new date">
        <div id="rsDateError" class="rs-error">
          <i class="fas fa-exclamation-circle"></i>&nbsp;Please select a future date.
        </div>
        <div class="d-flex gap-2 mt-4">
          <button class="btn-confirm-rs" onclick="confirmReschedule()">
            <i class="fas fa-calendar-check"></i>&nbsp; Confirm Reschedule &amp; Send Email
          </button>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal"
                  style="border-radius:12px;padding:12px 18px;font-weight:600;white-space:nowrap;">
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- NAVBAR -->
<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container-fluid">
    <button class="mobile-menu-toggle" onclick="toggleSidebar()"><i class="fas fa-bars"></i></button>
    <span class="navbar-brand"><i class="fa-solid fa-hospital"></i> CVS - Hospital</span>
    <button class="btn btn-logout ms-auto" onclick="logout()"><i class="fas fa-sign-out-alt"></i> Logout</button>
  </div>
</nav>

<div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

<div class="container-fluid">
  <div class="row">
    <div class="col-lg-2 col-md-3 sidebar p-0" id="sidebar">
      <a href="hospital_dashboard.py?hospital_id={hospital_id}" class="sidebar-link"><i class="fas fa-home"></i> Home</a>
      <a href="hospital_vaccination.py?hospital_id={hospital_id}" class="sidebar-link"><i class="fa-solid fa-circle-info"></i> Vaccination Info</a>
      <a href="hospital_view_application.py?hospital_id={hospital_id}" class="sidebar-link active"><i class="fa-solid fa-user-pen"></i> Parent Application</a>
      <a href="hospital_view_appointment.py?hospital_id={hospital_id}" class="sidebar-link"><i class="fas fa-calendar-alt"></i> View Appointments</a>
      <a href="hospital_profile.py?hospital_id={hospital_id}" class="sidebar-link"><i class="fas fa-user-circle"></i> My Profile</a>
      <a href="hospital_feedback.py?hospital_id={hospital_id}" class="sidebar-link"><i class="fas fa-comment-dots"></i> Feedback</a>
      <a href="hospital_chat.py?hospital_id={hospital_id}" class="sidebar-link">
        <i class="fas fa-notes-medical"></i> Chats
      </a>
      <a href="hospital_help.py?hospital_id={hospital_id}" class="sidebar-link"><i class="fas fa-circle-question"></i> Help &amp; Support</a>
    </div>

    <div class="col-lg-10 col-md-9 col-12 content-wrap">
      <div class="page-title-card">
        <h4 class="page-title">
          <i class="fa-solid fa-user-pen"></i> Parent Applications
          {hosp_subtitle}
        </h4>
      </div>

      <div class="tab-nav">
        <button class="tab-btn {'active-pending' if active_tab=='pending' else ''}" onclick="switchTab('pending')">
          <i class="fa-regular fa-clock"></i> Pending <span class="tab-count">{len(pending_rows)}</span>
        </button>
        <button class="tab-btn {'active-approved' if active_tab=='approved' else ''}" onclick="switchTab('approved')">
          <i class="fa-regular fa-calendar-check"></i> Approved <span class="tab-count">{len(approved_rows)}</span>
        </button>
        <button class="tab-btn {'active-rejected' if active_tab=='rescheduled' else ''}" onclick="switchTab('rescheduled')">
          <i class="fa-solid fa-calendar-day"></i> Rescheduled <span class="tab-count">{len(rescheduled_rows)}</span>
        </button>
      </div>

      <div class="filter-card">
        <span class="filter-label"><i class="fas fa-filter"></i> Filter by Appointment Date</span>
        <div class="row g-3 align-items-end">
          <div class="col-md-5">
            <input type="date" class="filter-input" id="filterDate" value="{filter_date}">
          </div>
          <div class="col-md-3">
            <button class="btn-filter" onclick="applyFilter()"><i class="fas fa-search"></i> Filter</button>
          </div>
          <div class="col-md-3">
            <button class="btn-clear" onclick="clearFilter()"><i class="fas fa-redo"></i> Clear</button>
          </div>
        </div>
      </div>
""")

def render_panel(tab_key, rows):
    badge = tab_cfg[tab_key]['badge']

    def action_btns(row_id, child_name):
        safe_child = child_name.replace("'", "\\'")
        if tab_key == 'pending':
            return (
                f'<button class="btn-approve" onclick="approveApp({row_id})">'
                f'<i class="fas fa-check"></i> Approve</button>'
                f'<button class="btn-reject" onclick="openRescheduleModal({row_id}, \'{safe_child}\')">'
                f'<i class="fas fa-calendar-xmark"></i> Reschedule</button>'
            )
        elif tab_key == 'approved':
            return (
                f'<button class="btn-reject" onclick="openRescheduleModal({row_id}, \'{safe_child}\')">'
                f'<i class="fas fa-calendar-xmark"></i> Reschedule</button>'
            )
        return ''

    active_cls = 'active' if tab_key == active_tab else ''
    print(f'<div class="tab-panel {active_cls}" id="panel-{tab_key}">')
    print('<div class="table-container"><div style="overflow-x:auto;">')
    print('''<table><thead><tr>
      <th><i class="fas fa-hashtag"></i> ID</th>
      <th><i class="fas fa-user"></i> Parent Name</th>
      <th><i class="fas fa-user-tag"></i> Type</th>
      <th><i class="fas fa-phone"></i> Mobile</th>
      <th><i class="fas fa-envelope"></i> Email</th>
      <th><i class="fas fa-map-marker-alt"></i> District</th>
      <th><i class="fas fa-baby"></i> Child Name</th>
      <th><i class="fas fa-calendar"></i> Appt. Date</th>
      <th><i class="fas fa-hospital"></i> Hospital</th>
      <th><i class="fas fa-info-circle"></i> Status</th>
      <th><i class="fas fa-cogs"></i> Actions</th>
    </tr></thead><tbody>''')

    if not rows:
        print(f'<tr><td colspan="11" class="no-data">'
              f'<i class="fas fa-inbox" style="font-size:3rem;color:#ccc;margin-bottom:15px;display:block;"></i>'
              f'No {tab_key.capitalize()} Applications Found...!</td></tr>')
    else:
        for i in rows:
            def val(idx, fallback="N/A"):
                return str(i[idx]).strip() if len(i) > idx and i[idx] is not None else fallback

            # parentform (0-based) — Image 2:
            # 0=id, 1=p_name, 2=p_type, 3=p_gender, 4=mobile, 5=email,
            # 6=aadhaar_number, 7=c_name, 8=c_gender, 9=c_dob, 10=c_order,
            # 11=vaccin, 12=vaccin_age, 13=vaccination, 14=appointment_date,
            # 15=age_group, 16=vaccine_name, 17=address, 18=district,
            # 19=pincode, 20=hospital_name, 21=status

            row_id      = i[0]
            p_name      = val(1);   p_type      = val(2);   p_gender    = val(3)
            mobile      = val(4);   email       = val(5);   aadhaar     = val(6)
            c_name      = val(7);   c_gender    = val(8);   c_dob       = val(9)
            c_order     = val(10);  vaccin      = val(11);  vaccin_age  = val(12)
            vaccination = val(13);  appt_date   = val(14);  age_group   = val(15)
            vacc_name   = val(16);  address     = val(17);  district    = val(18)
            pincode     = val(19);  hosp_name   = val(20);  row_status  = val(21)

            abtns = action_btns(row_id, c_name)

            print(f"""<tr>
              <td><span class="icon-badge">{row_id}</span></td>
              <td><strong>{p_name}</strong></td>
              <td>{p_type}</td>
              <td>{mobile}</td>
              <td style="font-size:0.82rem;">{email}</td>
              <td>{district}</td>
              <td><strong>{c_name}</strong></td>
              <td>{appt_date}</td>
              <td>{hosp_name}</td>
              <td>{badge}</td>
              <td style="white-space:nowrap;">
                <button class="btn-view-det" data-bs-toggle="modal" data-bs-target="#modal-{tab_key}-{row_id}">
                  <i class="fas fa-eye"></i> View
                </button>
              </td>
            </tr>

            <div class="modal fade" id="modal-{tab_key}-{row_id}" tabindex="-1" aria-hidden="true">
              <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
                <div class="modal-content">
                  <div class="modal-header">
                    <h5 class="modal-title">
                      <i class="fas fa-user-circle"></i> Application Details &mdash; REG-{row_id:05d}
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                  </div>
                  <div class="modal-body">
                    <div class="detail-section">
                      <h6><i class="fas fa-user"></i> Parent Information</h6>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-user"></i> Parent Name</div><div class="detail-value">{p_name}</div></div>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-user-tag"></i> Parent Type</div><div class="detail-value">{p_type}</div></div>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-venus-mars"></i> Gender</div><div class="detail-value">{p_gender}</div></div>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-phone"></i> Mobile</div><div class="detail-value">{mobile}</div></div>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-envelope"></i> Email</div><div class="detail-value">{email}</div></div>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-id-card"></i> Aadhaar</div><div class="detail-value">{aadhaar}</div></div>
                    </div>
                    <div class="detail-section">
                      <h6><i class="fas fa-baby"></i> Child Information</h6>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-baby"></i> Child Name</div><div class="detail-value">{c_name}</div></div>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-venus-mars"></i> Gender</div><div class="detail-value">{c_gender}</div></div>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-birthday-cake"></i> DOB</div><div class="detail-value">{c_dob}</div></div>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-sort-numeric-up"></i> Child Order</div><div class="detail-value">{c_order}</div></div>
                    </div>
                    <div class="detail-section">
                      <h6><i class="fas fa-syringe"></i> Vaccination Information</h6>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-question-circle"></i> Vacc. Status</div><div class="detail-value">{vaccin}</div></div>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-layer-group"></i> Vacc. Age Group</div><div class="detail-value">{vaccin_age}</div></div>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-list-check"></i> Vaccines Received</div><div class="detail-value">{vaccination}</div></div>
                    </div>
                    <div class="detail-section">
                      <h6><i class="fas fa-map-marked-alt"></i> Address</h6>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-home"></i> Address</div><div class="detail-value">{address}</div></div>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-map-marker-alt"></i> District</div><div class="detail-value">{district}</div></div>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-mail-bulk"></i> Pincode</div><div class="detail-value">{pincode}</div></div>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-hospital"></i> Hospital</div><div class="detail-value">{hosp_name}</div></div>
                    </div>
                    <div class="detail-section">
                      <h6><i class="fas fa-calendar"></i> Appointment Information</h6>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-calendar-day"></i> Appt. Date</div><div class="detail-value">{appt_date}</div></div>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-arrow-down-short-wide"></i> Age Group</div><div class="detail-value">{age_group}</div></div>
                      <div class="detail-row"><div class="detail-label"><i class="fas fa-notes-medical"></i> Vaccine Name</div><div class="detail-value">{vacc_name}</div></div>
                    </div>
                  </div>
                  <div class="modal-footer d-flex justify-content-between align-items-center">
                    <div>Status: {badge}</div>
                    <div class="d-flex gap-2 flex-wrap">
                      {abtns}
                      <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">
                        <i class="fas fa-times"></i> Close
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>""")

    print('</tbody></table></div></div></div>')


render_panel('pending',     pending_rows)
render_panel('approved',    approved_rows)
render_panel('rescheduled', rescheduled_rows)

print(f"""
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
let _rsAppId = null;

function openRescheduleModal(appId, childName) {{
  document.querySelectorAll('.modal.show').forEach(function(m) {{
    const inst = bootstrap.Modal.getInstance(m);
    if (inst) inst.hide();
  }});
  _rsAppId = appId;
  const padId = String(appId).padStart(5, '0');
  document.getElementById('rsAppLabel').textContent   = 'REG-' + padId;
  document.getElementById('rsChildLabel').textContent = childName;
  document.getElementById('rsDateInput').value        = '';
  document.getElementById('rsDateError').style.display = 'none';
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  document.getElementById('rsDateInput').min = tomorrow.toISOString().split('T')[0];
  setTimeout(function() {{
    new bootstrap.Modal(document.getElementById('rescheduleModal')).show();
  }}, 350);
}}

function confirmReschedule() {{
  const dateVal = document.getElementById('rsDateInput').value;
  const errDiv  = document.getElementById('rsDateError');
  if (!dateVal) {{
    errDiv.style.display = 'block';
    errDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i>&nbsp;Please select a new appointment date.';
    return;
  }}
  const chosen = new Date(dateVal);
  const today  = new Date(); today.setHours(0,0,0,0);
  if (chosen <= today) {{
    errDiv.style.display = 'block';
    errDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i>&nbsp;Please select a future date.';
    return;
  }}
  errDiv.style.display = 'none';
  const rsModal = bootstrap.Modal.getInstance(document.getElementById('rescheduleModal'));
  if (rsModal) rsModal.hide();
  _sendUpdate(_rsAppId, 'rescheduled', dateVal);
}}

function approveApp(appId) {{
  const padId = String(appId).padStart(5, '0');
  if (!confirm('\u2705 Approve application REG-' + padId + '?\\n\\nAn email will be sent to the parent automatically.')) return;
  document.querySelectorAll('.modal.show').forEach(function(m) {{
    const inst = bootstrap.Modal.getInstance(m); if (inst) inst.hide();
  }});
  _sendUpdate(appId, 'approved', '');
}}

function _sendUpdate(appId, newStatus, rescheduleDate) {{
  if (!appId) {{ showToast('<i class="fas fa-times-circle"></i> Invalid application ID.', 'error'); return; }}
  const lt = document.createElement('div');
  lt.id = 'toast-loading'; lt.className = 'toast-msg toast-warning';
  lt.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing &amp; sending email to parent...';
  document.getElementById('toastContainer').appendChild(lt);
  const params = new URLSearchParams({{
    app_id: appId, status: newStatus, hospital_id: HOSPITAL_ID, reschedule_date: rescheduleDate
  }});
  fetch(window.location.pathname, {{
    method: 'POST', headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }}, body: params.toString()
  }})
  .then(function(r) {{ if (!r.ok) throw new Error('HTTP ' + r.status); return r.text(); }})
  .then(function(text) {{
    const loader = document.getElementById('toast-loading');
    if (loader) loader.remove();
    let data;
    try {{ data = JSON.parse(text); }} catch(e) {{
      showToast('<i class="fas fa-times-circle"></i> Server error — check CGI logs.', 'error'); return;
    }}
    if (data.success) {{
      const emailOk = data.message.includes('Email sent');
      showToast('<i class="fas fa-' + (emailOk ? 'envelope-circle-check' : 'check-circle') + '"></i> ' + data.message,
                emailOk ? 'success' : 'warning');
      setTimeout(function() {{ location.reload(); }}, 2600);
    }} else {{
      showToast('<i class="fas fa-times-circle"></i> ' + data.message, 'error');
    }}
  }})
  .catch(function(err) {{
    const loader = document.getElementById('toast-loading');
    if (loader) loader.remove();
    showToast('<i class="fas fa-times-circle"></i> Request failed: ' + err.message, 'error');
  }});
}}

const TAB_COLORS = {{ pending:'active-pending', approved:'active-approved', rescheduled:'active-rejected' }};
function switchTab(tab) {{
  document.querySelectorAll('.tab-panel').forEach(function(p) {{ p.classList.remove('active'); }});
  document.querySelectorAll('.tab-btn').forEach(function(b) {{
    b.classList.remove('active-pending','active-approved','active-rejected');
  }});
  const panel = document.getElementById('panel-' + tab);
  if (panel) panel.classList.add('active');
  const idx = ['pending','approved','rescheduled'].indexOf(tab);
  if (idx >= 0) document.querySelectorAll('.tab-btn')[idx].classList.add(TAB_COLORS[tab]);
  const url = new URL(window.location.href);
  url.searchParams.set('tab', tab);
  history.replaceState(null, '', url.toString());
}}

function applyFilter() {{
  const date = document.getElementById('filterDate').value;
  if (!date) {{ alert('Please select a date to filter.'); return; }}
  const url = new URL(window.location.href);
  url.searchParams.set('filter_date', date);
  window.location.href = url.toString();
}}
function clearFilter() {{
  const url = new URL(window.location.href);
  url.searchParams.delete('filter_date');
  window.location.href = url.toString();
}}
function showToast(html, type) {{
  const t = document.createElement('div');
  t.className = 'toast-msg toast-' + type; t.innerHTML = html;
  document.getElementById('toastContainer').appendChild(t);
  setTimeout(function() {{ t.remove(); }}, 4500);
}}
function toggleSidebar() {{
  document.getElementById('sidebar').classList.toggle('show');
  document.getElementById('sidebarOverlay').classList.toggle('show');
}}
document.addEventListener('click', function(e) {{
  const sb = document.getElementById('sidebar');
  const mt = document.querySelector('.mobile-menu-toggle');
  if (window.innerWidth < 992 && sb && mt &&
      !sb.contains(e.target) && !mt.contains(e.target) && sb.classList.contains('show')) {{
    sb.classList.remove('show');
    document.getElementById('sidebarOverlay').classList.remove('show');
  }}
}});
function logout() {{
  if (confirm('Are you sure you want to logout?')) window.location.href = 'main.py';
}}
document.addEventListener('DOMContentLoaded', function() {{ switchTab(ACTIVE_TAB); }});
</script>
</body>
</html>
""")

con.close()