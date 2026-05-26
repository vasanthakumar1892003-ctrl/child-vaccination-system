#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe
# parent_reminder.py — Vaccination Reminders (corrected section logic)

import pymysql
import cgi
import cgitb
import sys
import os
from datetime import datetime, date, timedelta

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")
print("Content-Type: text/html\r\n\r\n")

try:
    con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
    cur = con.cursor(pymysql.cursors.DictCursor)
except Exception as e:
    print(f"<h2 style='color:red;font-family:Arial;padding:20px;'>DB Error: {e}</h2>")
    sys.exit()

form      = cgi.FieldStorage()
parent_id = form.getvalue("parent_id", "").strip()
if not parent_id:
    qs = os.environ.get("QUERY_STRING", "")
    for part in qs.split("&"):
        if part.startswith("parent_id="):
            parent_id = part.split("=", 1)[1].strip()
            break

cur.execute("SELECT id, parent_name, email_id, parent_mobile FROM parent WHERE id = %s LIMIT 1", (parent_id,))
prow = cur.fetchone()

if not prow:
    cur.execute("SELECT COUNT(*) AS total FROM parent")
    total = cur.fetchone()['total']
    cur.execute("SELECT id, parent_name, email_id FROM parent LIMIT 5")
    samples = cur.fetchall()
    td = "padding:6px 10px;border:1px solid #ddd;font-size:12px;"
    th = "padding:7px 10px;border:1px solid #ddd;background:#f1f5f9;font-size:12px;font-weight:bold;"
    sr = "".join(f"<tr><td style='{td}'>{s['id']}</td><td style='{td}'>{s['parent_name']}</td><td style='{td}'>{s['email_id']}</td></tr>" for s in samples)
    print(f"""<div style='font-family:Arial;padding:30px;'>
      <div style='background:#fef2f2;border-left:5px solid #ef4444;padding:20px;border-radius:8px;max-width:600px;'>
        <h3 style='color:#dc2626;'>Parent not found (id={parent_id}). Total rows: {total}</h3>
        <table style='border-collapse:collapse;margin-top:10px;'>
          <tr><th style='{th}'>id</th><th style='{th}'>parent_name</th><th style='{th}'>email_id</th></tr>{sr}
        </table>
        <p style='margin-top:12px;font-size:13px;'>URL must include: <code>parent_reminder.py?parent_id=X</code></p>
      </div></div>""")
    con.close(); sys.exit()

parent_email = prow['email_id']
parent_name  = prow['parent_name']

cur.execute("""
    SELECT id, p_name, email_id, mobile, c_name, c_dob,
           vaccination_name, appointment_date, hospital_name, status, create_at
    FROM hospital_appointment
    WHERE email_id = %s
    ORDER BY STR_TO_DATE(appointment_date, '%%Y-%%m-%%d') ASC
""", (parent_email,))
rows = cur.fetchall()

debug_html = ""
if not rows:
    cur.execute("SELECT COUNT(*) AS total FROM hospital_appointment")
    ha_total = cur.fetchone()['total']
    cur.execute("SELECT id, p_name, email_id, appointment_date, status FROM hospital_appointment LIMIT 6")
    ha_samples = cur.fetchall()
    td = "padding:6px 10px;border:1px solid #e5e7eb;font-size:12px;"
    th = "padding:7px 10px;border:1px solid #e5e7eb;background:#f9fafb;font-size:12px;font-weight:bold;"
    sr = "".join(f"<tr><td style='{td}'>{r['id']}</td><td style='{td}'>{r['p_name']}</td><td style='{td};color:#dc2626;font-weight:600;'>{r['email_id']}</td><td style='{td}'>{r['appointment_date']}</td><td style='{td}'>{r['status']}</td></tr>" for r in ha_samples) or f"<tr><td colspan='5' style='{td}color:#9ca3af;text-align:center;'>Table is empty</td></tr>"
    debug_html = f"""<div style="background:#fffbeb;border:1.5px solid #f59e0b;border-radius:12px;padding:18px 22px;margin-bottom:24px;font-family:'Segoe UI',sans-serif;">
      <strong style="color:#92400e;">🔍 No records matched for email: {parent_email} &nbsp;|&nbsp; Total rows in hospital_appointment: {ha_total}</strong>
      <table style="border-collapse:collapse;width:100%;margin-top:12px;">
        <tr><th style="{th}">id</th><th style="{th}">p_name</th><th style="{th}">email_id (hospital_appointment)</th><th style="{th}">date</th><th style="{th}">status</th></tr>{sr}
      </table>
      <p style="margin-top:10px;font-size:12px;color:#92400e;background:#fef9c3;padding:8px 12px;border-radius:6px;">
        💡 The <code>email_id</code> in <code>parent</code> table must exactly match <code>email_id</code> in <code>hospital_appointment</code>.
      </p></div>"""

con.close()

today  = date.today()
now_dt = datetime.now()

def parse_date(s):
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try: return datetime.strptime(str(s).strip(), fmt).date()
        except: pass
    return None

def smart_ago(val):
    if not val:
        return None
    s = str(val).strip()
    if not s or s.lower() in ('none', 'null', ''):
        return None
    formats = [
        "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d",
        "%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M", "%d-%m-%Y",
        "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y",
        "%m/%d/%Y %H:%M:%S", "%m/%d/%Y",
        "%Y/%m/%d %H:%M:%S", "%Y/%m/%d",
    ]
    dt = None
    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
            break
        except ValueError:
            pass
    if not dt:
        return None
    diff       = now_dt - dt
    total_secs = int(diff.total_seconds())
    if total_secs < 0:    return "just now"
    if total_secs < 60:   return "just now"
    if total_secs < 3600:
        m = total_secs // 60
        return f"{m} min{'s' if m > 1 else ''} ago"
    if total_secs < 86400:
        h = total_secs // 3600
        return f"{h} hr{'s' if h > 1 else ''} ago"
    d = diff.days
    if d == 1:    return "yesterday"
    if d < 7:     return f"{d} days ago"
    if d < 30:    return f"{d // 7} week{'s' if d // 7 > 1 else ''} ago"
    if d < 365:   return f"{d // 30} month{'s' if d // 30 > 1 else ''} ago"
    yr = d // 365
    return f"{yr} year{'s' if yr > 1 else ''} ago"

# ══════════════════════════════════════════════════════════════
#  SECTION LOGIC
#
#  pending_today  → appointment date == TODAY (any status)
#  upcoming       → appointment date >= TOMORROW (future, sorted by date)
#  due            → missed by 1–7 days (appointment date between yesterday and 7 days ago)
#  overdue        → missed by more than 7 days (appointment date older than 7 days ago)
#
#  "missed" = appointment date is in the past AND status is NOT completed/cancelled
# ══════════════════════════════════════════════════════════════

pending_today = []   # today's appointments
upcoming      = []   # tomorrow and beyond (future)
due           = []   # missed 1–7 days ago
overdue       = []   # missed more than 7 days ago

for r in rows:
    apt = parse_date(r['appointment_date'])
    if not apt:
        continue
    days = (apt - today).days          # positive = future, 0 = today, negative = past
    missed_days = abs(days)            # how many days ago (for past)
    st = (r['status'] or 'pending').lower().strip()
    completed_or_cancelled = st in ('completed', 'cancelled')

    r['_apt']  = apt
    r['_days'] = days
    r['_ago']  = smart_ago(r.get('create_at'))

    if days == 0:
        # Today's appointment → Pending Today
        pending_today.append(r)

    elif days > 0:
        # Future appointment → Upcoming (sorted by date ascending already)
        upcoming.append(r)

    elif days < 0 and not completed_or_cancelled:
        # Past and not completed/cancelled → missed
        if missed_days <= 7:
            # Missed within last 7 days → Due
            due.append(r)
        else:
            # Missed more than 7 days ago → Overdue
            overdue.append(r)

# Sort upcoming by date ascending (closest first)
upcoming.sort(key=lambda r: r['_apt'])
# Sort due by date descending (most recent missed first)
due.sort(key=lambda r: r['_apt'], reverse=True)
# Sort overdue by date descending (most recently missed first)
overdue.sort(key=lambda r: r['_apt'], reverse=True)

counter = [0]

def vcard(r, theme, badge_cls, badge_icon, badge_text, cd_cls):
    d    = r['_apt']
    days = int(r['_days'])
    ago  = r.get('_ago')

    if days == 0:
        cd_num, cd_sub = "!", "TODAY"
    elif days == 1:
        cd_num, cd_sub = "1", "DAY LEFT"
    elif days > 1:
        cd_num, cd_sub = str(days), "DAYS LEFT"
    else:
        # past (negative days)
        n = abs(days)
        if n <= 7:
            cd_num, cd_sub = str(n), f"DAY{'S' if n > 1 else ''} AGO"
        elif n < 31:
            w = n // 7
            cd_num, cd_sub = str(w), f"WK{'S' if w > 1 else ''} AGO"
        elif n < 365:
            mo = n // 30
            cd_num, cd_sub = str(mo), f"MO{'S' if mo > 1 else ''} AGO"
        else:
            yr = n // 365
            cd_num, cd_sub = str(yr), f"YR{'S' if yr > 1 else ''} AGO"

    delay = f"{counter[0]*0.07:.2f}s"
    counter[0] += 1

    submitted_chip = ""
    if ago:
        submitted_chip = f"""
        <div class="submitted-chip">
          <i class="fas fa-clock"></i> Submitted: <strong>{ago}</strong>
        </div>"""

    return f"""
    <div class="vcard theme-{theme}" style="animation-delay:{delay}">
      <div class="vcard-left">
        <div class="vcard-dd">{d.strftime('%d')}</div>
        <div class="vcard-mmm">{d.strftime('%b').upper()}</div>
        <div class="vcard-dow">{d.strftime('%a').upper()}</div>
        <div class="vcard-yr">{d.strftime('%Y')}</div>
      </div>
      <div class="vcard-content">
        <div class="vcard-badge badge-{badge_cls}">
          <i class="fas {badge_icon}"></i> {badge_text}
        </div>
        <div class="vcard-title">
          <span class="child-highlight">{r['c_name']}</span>'s </div>
        <div class="vcard-title">  
          <span class="vacc-highlight">{r['vaccination_name']}</span> Vaccination
        </div>
        <br>
        <div class="info-pills">
          <div class="info-pill pill-green">
            <i class="fas fa-hospital-alt"></i>
            <div class="pill-text">
              <span class="pill-label">Hospital</span>
              <span class="pill-val">{r['hospital_name']}</span>
            </div>
          </div>
          <div class="info-pill pill-blue">
            <i class="fas fa-user-circle"></i>
            <div class="pill-text">
              <span class="pill-label">Parent</span>
              <span class="pill-val">{r['p_name']}</span>
            </div>
          </div>
          <div class="info-pill pill-purple">
            <i class="fas fa-phone-alt"></i>
            <div class="pill-text">
              <span class="pill-label">Mobile</span>
              <span class="pill-val">{r['mobile']}</span>
            </div>
          </div>
          <div class="info-pill pill-pink">
            <i class="fas fa-birthday-cake"></i>
            <div class="pill-text">
              <span class="pill-label">Date of Birth</span>
              <span class="pill-val">{r['c_dob']}</span>
            </div>
          </div>
        </div>
        {submitted_chip}
      </div>
      <div class="vcard-right">
        <div class="countdown cd-{cd_cls}">
          <div class="cd-num">{cd_num}</div>
          <div class="cd-lbl">{cd_sub}</div>
        </div>
      </div>
    </div>"""

# ═══════════════════════ HTML ═════════════════════════════════
print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>My Reminders - CVS</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  background: linear-gradient(135deg, #052e16, #22c55e, #dcfce7);
  min-height:100vh; font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif; overflow-x:hidden;
}}

/* ===== NAVBAR ===== */
.navbar {{
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  padding: 15px 20px;
  background: linear-gradient(135deg, #052e16, #22c55e, #dcfce7) !important;
}}
.navbar .container-fluid {{
  display: flex; flex-direction: row; align-items: center; flex-wrap: nowrap; gap: 10px;
}}
.navbar-brand {{
  font-weight: 600; color: white !important; letter-spacing: 2px; text-transform: uppercase;
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
  border: none; padding: 8px 20px; border-radius: 25px; color: white;
  font-weight: 600; transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(238, 9, 121, 0.4);
  font-size: 0.9rem; white-space: nowrap;
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
  background: linear-gradient(90deg,#22c55e,transparent 100%);
  color: #fff; border-left: 4px solid #dcfce7; padding-left: 24px;
}}
.sidebar-link i {{ margin-right: 12px; width: 22px; text-align: center; }}
.sidebar-overlay {{
  display: none; position: fixed; top:0; left:0;
  width:100%; height:100%; background:rgba(0,0,0,0.6); z-index:998; backdrop-filter:blur(2px);
}}
.sidebar-overlay.show {{ display: block; }}

/* ===== CONTENT ===== */
.content-area {{ padding: 24px; }}
.page-header {{
  background: white; border-radius: 20px; padding: 20px 26px; margin-bottom: 20px;
  display: flex; align-items: center; gap: 16px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.1);
}}
.bell-wrap {{
  width: 52px; height: 52px; border-radius: 14px;
  background: linear-gradient(135deg, #052e16, #22c55e);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 14px rgba(5,150,105,0.4); flex-shrink: 0;
}}
.bell-wrap i {{ color: white; font-size: 1.4rem; }}
.page-header h4 {{
  font-size: 1.4rem; font-weight: 900; color: #0f172a;
  margin: 0; letter-spacing: 1px; text-transform: uppercase;
}}
.page-header .sub {{ font-size: 0.78rem; color: #64748b; margin-top: 2px; font-weight: 600; }}

/* STATS */
.stats-row {{
  display: grid; grid-template-columns: repeat(4,1fr); gap: 12px; margin-bottom: 22px;
}}
.stat-card {{
  background: white; border-radius: 16px; padding: 14px 16px;
  display: flex; align-items: center; gap: 12px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.07); transition: transform 0.2s;
}}
.stat-card:hover {{ transform: translateY(-2px); }}
.stat-icon {{
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; font-size: 1.1rem;
}}
.si-orange {{ background:#fdf2f8; color:#db2777; }}
.si-red    {{ background:#fef2f2; color:#ef4444; }}
.si-blue   {{ background:#eff6ff; color:#3b82f6; }}
.si-green  {{ background:#fffbeb; color:#f59e0b; }}
.stat-num {{ font-size:1.7rem; font-weight:900; color:#0f172a; line-height:1; }}
.stat-lbl {{ font-size:0.68rem; color:#64748b; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; margin-top:1px; }}
.sb-orange {{ border-top:3px solid #db2777; }}
.sb-red    {{ border-top:3px solid #ef4444; }}
.sb-blue   {{ border-top:3px solid #3b82f6; }}
.sb-green  {{ border-top:3px solid #f59e0b; }}

/* SECTION DIVIDER */
.sec-label {{ display:flex; align-items:center; gap:10px; margin:20px 0 12px; }}
.sec-label .line {{ flex:1; height:1.5px; background:rgba(255,255,255,0.3); }}
.sec-label span {{
  background:rgba(255,255,255,0.15); backdrop-filter:blur(8px);
  color:white; padding:5px 14px; border-radius:20px;
  font-size:0.72rem; font-weight:800; letter-spacing:1.5px; text-transform:uppercase;
}}

/* VCARD */
.vcard {{
  background:white; border-radius:18px; margin-bottom:14px; overflow:hidden;
  box-shadow:0 4px 20px rgba(0,0,0,0.08); display:flex;
  transition:transform 0.2s,box-shadow 0.2s; animation:fadeUp 0.4s ease both;
}}
.vcard:hover {{ transform:translateY(-3px); box-shadow:0 12px 32px rgba(0,0,0,0.13); }}
@keyframes fadeUp {{
  from {{ opacity:0; transform:translateY(14px); }}
  to   {{ opacity:1; transform:translateY(0); }}
}}
.vcard-left {{
  width:76px; flex-shrink:0;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  padding:16px 0; gap:1px;
}}
.vcard-dd  {{ font-size:2.2rem; font-weight:900; color:white; line-height:1; }}
.vcard-mmm {{ font-size:0.65rem; font-weight:800; color:rgba(255,255,255,.9); letter-spacing:1.5px; }}
.vcard-dow {{ font-size:0.58rem; font-weight:700; color:rgba(255,255,255,.7); letter-spacing:1px; margin-top:2px; }}
.vcard-yr  {{ font-size:0.58rem; font-weight:600; color:rgba(255,255,255,.55); margin-top:1px; }}

/* Theme colours */
.theme-today    .vcard-left {{ background:linear-gradient(160deg,#be185d,#ec4899); }}
.theme-upcoming .vcard-left {{ background:linear-gradient(160deg,#d97706,#fbbf24); }}
.theme-due      .vcard-left {{ background:linear-gradient(160deg,#1d4ed8,#3b82f6); }}
.theme-overdue  .vcard-left {{ background:linear-gradient(160deg,#991b1b,#dc2626); }}
.theme-today    {{ border-left:4px solid #ec4899; }}
.theme-upcoming {{ border-left:4px solid #fbbf24; }}
.theme-due      {{ border-left:4px solid #3b82f6; }}
.theme-overdue  {{ border-left:4px solid #dc2626; }}

.vcard-content {{
  flex:1; padding:14px 18px;
  display:flex; flex-direction:column; gap:10px; justify-content:center;
}}
.vcard-badge {{
  display:inline-flex; align-items:center; gap:5px;
  padding:3px 10px; border-radius:20px;
  font-size:0.68rem; font-weight:800; letter-spacing:0.8px; text-transform:uppercase; width:fit-content;
}}
.badge-today    {{ background:#fef2f2; color:#dc2626; border:1px solid #fca5a5; }}
.badge-upcoming {{ background:#fffbeb; color:#b45309; border:1px solid #fde68a; }}
.badge-due      {{ background:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe; }}
.badge-overdue  {{ background:#fef2f2; color:#dc2626; border:1px solid #fca5a5; }}
.vcard-title     {{ font-size:1.05rem; font-weight:800; color:#0f172a; line-height:1.3; }}
.child-highlight {{ color:#059669; font-size:1.1rem; }}
.vacc-highlight  {{ color:#0369a1; }}

/* INFO PILLS */
.info-pills {{ display:grid; grid-template-columns:repeat(2,1fr); gap:8px; }}
.info-pill {{
  display:flex; align-items:center; gap:10px; padding:8px 6px; border-radius:10px;
}}
.info-pill i  {{ font-size:1rem; flex-shrink:0; width:20px; text-align:center; }}
.pill-text    {{ display:flex; flex-direction:column; min-width:0; }}
.pill-label   {{ font-size:0.62rem; font-weight:800; text-transform:uppercase; letter-spacing:0.8px; opacity:0.7; }}
.pill-val     {{ font-size:0.85rem; font-weight:700; color:#1e293b; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.pill-green  {{ background:#f0fdf4; }} .pill-green i  {{ color:#16a34a; }} .pill-green .pill-label  {{ color:#16a34a; }}
.pill-blue   {{ background:#eff6ff; }} .pill-blue i   {{ color:#3b82f6; }} .pill-blue .pill-label   {{ color:#3b82f6; }}
.pill-purple {{ background:#faf5ff; }} .pill-purple i {{ color:#9333ea; }} .pill-purple .pill-label {{ color:#9333ea; }}
.pill-pink   {{ background:#fdf2f8; }} .pill-pink i   {{ color:#db2777; }} .pill-pink .pill-label   {{ color:#db2777; }}

/* SUBMITTED CHIP */
.submitted-chip {{
  display:inline-flex; align-items:center; gap:6px;
  background:#f8fafc; border:1px solid #e2e8f0;
  padding:4px 12px; border-radius:20px;
  font-size:0.72rem; font-weight:600; color:#64748b; width:fit-content;
}}
.submitted-chip i      {{ font-size:0.65rem; color:#94a3b8; }}
.submitted-chip strong {{ color:#334155; font-weight:800; }}

/* COUNTDOWN */
.vcard-right {{
  display:flex; align-items:center; justify-content:center;
  padding:0 20px; flex-shrink:0; min-width:90px;
}}
.countdown {{ text-align:center; }}
.cd-num    {{ font-size:2.4rem; font-weight:900; line-height:1; }}
.cd-lbl    {{ font-size:0.55rem; font-weight:800; text-transform:uppercase; letter-spacing:0.8px; color:#94a3b8; margin-top:3px; line-height:1.4; }}
.cd-pink   .cd-num {{ color:#ec4899; }}  
.cd-orange .cd-num {{ color:#3b82f6; }}
.cd-red    .cd-num {{ color:#dc2626; }}
.cd-green  .cd-num {{ color:#f59e0b; }}
.cd-gray   .cd-num {{ color:#94a3b8; }}

/* INFO BANNER */
.info-banner {{
  background:linear-gradient(135deg,#eff6ff,#dbeafe);
  border:1.5px solid #bfdbfe; border-radius:16px; padding:16px 22px;
  display:flex; align-items:center; gap:14px; margin-top:20px;
  box-shadow:0 2px 12px rgba(59,130,246,0.1);
}}
.info-banner i {{ font-size:1.4rem; color:#3b82f6; flex-shrink:0; }}
.info-banner p {{ margin:0; font-size:0.87rem; color:#1e40af; font-weight:600; }}

/* EMPTY STATE */
.empty-box {{
  background:white; border-radius:18px; padding:48px 20px;
  text-align:center; box-shadow:0 4px 20px rgba(0,0,0,0.07);
}}
.empty-box i {{ font-size:3.5rem; color:#d1d5db; display:block; margin-bottom:14px; }}
.empty-box p {{ color:#9ca3af; font-size:1rem; font-weight:700; }}

/* ===== RESPONSIVE ===== */
@media (max-width:991.98px) {{
  .navbar-toggler-custom {{ display:flex; align-items:center; justify-content:center; }}
  .sidebar {{
    position:fixed; left:-100%; top:0;
    width:280px; height:100vh; z-index:999; transition:left 0.3s ease; overflow-y:auto;
  }}
  .sidebar.show {{ left:0; }}
  .content-area {{ padding:14px; }}
  .stats-row {{ grid-template-columns:repeat(2,1fr); }}
  .navbar-brand {{ font-size:1rem; letter-spacing:1px; }}
  .navbar-brand i {{ font-size:1.3rem; }}
}}
@media (max-width:767.98px) {{
  .page-header h4 {{ font-size:1.3rem; }}
  .page-header     {{ padding:18px 20px; }}
  .content-area    {{ padding:12px; }}
  .btn-logout {{ padding:6px 16px; font-size:0.85rem; }}
}}
@media (max-width:575.98px) {{
  .navbar-brand  {{ font-size:0.85rem; letter-spacing:0.5px; }}
  .navbar-brand i {{ font-size:1.1rem; margin-right:6px; }}
  .btn-logout    {{ padding:6px 12px; font-size:0.8rem; }}
  .stats-row {{ grid-template-columns:repeat(2,1fr); gap:8px; }}
  .vcard-left    {{ width:62px; }}
  .vcard-dd      {{ font-size:1.7rem; }}
  .vcard-content {{ padding:12px; }}
  .vcard-right   {{ padding:0 12px; min-width:70px; }}
  .cd-num        {{ font-size:1.8rem; }}
  .info-pills    {{ grid-template-columns:1fr; }}
  .page-header h4 {{ font-size:1.1rem; }}
}}
@media (max-width:400px) {{
  .navbar-brand {{ font-size:0.75rem; }}
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

<!-- Sidebar Overlay -->
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
      <a href="parent_reminder.py?parent_id={parent_id}" class="sidebar-link active" onclick="closeSidebarMobile()">
        <i class="fas fa-bell"></i> My Reminders
      </a>
      <a href="parent_profile.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
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
    <div class="col-lg-10 col-md-9 content-area">
      <div class="page-header">
        <div class="bell-wrap"><i class="fas fa-bell"></i></div>
        <div>
          <h4>My Reminders</h4>
          <div class="sub">Vaccination schedule · {today.strftime('%d %B %Y')}</div>
        </div>
      </div>
      {debug_html}
""")

# ── Stats row ─────────────────────────────────────────────────────────────────
print(f"""
      <div class="stats-row">
        <div class="stat-card sb-orange">
          <div class="stat-icon si-orange"><i class="fas fa-bell"></i></div>
          <div><div class="stat-num">{len(pending_today)}</div><div class="stat-lbl">Today</div></div>
        </div>
        <div class="stat-card sb-green">
          <div class="stat-icon si-green"><i class="fas fa-calendar-alt"></i></div>
          <div><div class="stat-num">{len(upcoming)}</div><div class="stat-lbl">Upcoming</div></div>
        </div>
        <div class="stat-card sb-blue">
          <div class="stat-icon si-blue"><i class="fas fa-hourglass-half"></i></div>
          <div><div class="stat-num">{len(due)}</div><div class="stat-lbl">Due (missed ≤7d)</div></div>
        </div>
        <div class="stat-card sb-red">
          <div class="stat-icon si-red"><i class="fas fa-exclamation-circle"></i></div>
          <div><div class="stat-num">{len(overdue)}</div><div class="stat-lbl">Overdue (&gt;7d)</div></div>
        </div>
      </div>
""")

# ── Sections ──────────────────────────────────────────────────────────────────

# 1. TODAY
if pending_today:
    print('<div class="sec-label"><div class="line"></div><span>📅 Today\'s Appointments</span><div class="line"></div></div>')
    for r in pending_today:
        print(vcard(r, "today", "today", "fa-bell", "TODAY", "pink"))

# 2. UPCOMING (tomorrow onwards, sorted by date)
if upcoming:
    print('<div class="sec-label"><div class="line"></div><span>⏳ Upcoming Appointments</span><div class="line"></div></div>')
    for r in upcoming:
        days_left = int(r['_days'])
        if days_left == 1:
            badge_text = "TOMORROW"
        else:
            badge_text = f"IN {days_left} DAYS"
        print(vcard(r, "upcoming", "upcoming", "fa-calendar-check", badge_text, "green"))

# 3. DUE — missed 1 to 7 days ago
if due:
    print('<div class="sec-label"><div class="line"></div><span>📌 Due — Missed (1–7 Days)</span><div class="line"></div></div>')
    for r in due:
        print(vcard(r, "due", "due", "fa-exclamation-triangle", "MISSED", "orange"))

# 4. OVERDUE — missed more than 7 days ago
if overdue:
    print('<div class="sec-label"><div class="line"></div><span>⚠️ Overdue — Missed (&gt;7 Days)</span><div class="line"></div></div>')
    for r in overdue:
        print(vcard(r, "overdue", "overdue", "fa-times-circle", "OVERDUE", "red"))

if not pending_today and not upcoming and not due and not overdue and not debug_html:
    print('<div class="empty-box"><i class="fas fa-bell-slash"></i><p>No vaccination reminders right now. All up to date!</p></div>')

print("""
      <div class="info-banner">
        <i class="fas fa-lightbulb"></i>
        <p>You will receive email and SMS notifications 24 hours before each scheduled vaccination.</p>
      </div>

    </div><!-- /content-area -->
  </div><!-- /row -->
</div><!-- /container-fluid -->

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('show');
  document.getElementById('sidebarOverlay').classList.toggle('show');
}
function closeSidebarMobile() {
  if (window.innerWidth < 992) {
    document.getElementById('sidebar').classList.remove('show');
    document.getElementById('sidebarOverlay').classList.remove('show');
  }
}
function logout() {
  if (confirm('Are you sure you want to logout?')) window.location.href = 'main.py';
}
document.addEventListener('click', function(e) {
  var sidebar = document.getElementById('sidebar');
  var btn     = document.getElementById('sidebarToggleBtn');
  if (window.innerWidth < 992 &&
      sidebar.classList.contains('show') &&
      !sidebar.contains(e.target) &&
      !btn.contains(e.target)) {
    closeSidebarMobile();
  }
});
</script>
</body>
</html>""")