#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgi
import cgitb
import sys
import csv
import io
from datetime import datetime
from urllib.parse import quote

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")

# ── Read form data BEFORE printing any headers ──
form = cgi.FieldStorage()
export_action   = (form.getvalue("export_action")   or "").strip()
filter_date     = (form.getvalue("filter_date")     or "").strip()
filter_hospital = (form.getvalue("filter_hospital") or "").strip()
filter_status   = (form.getvalue("filter_status")   or "").strip()

# ── Database Connection ──
try:
    con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
    cur = con.cursor()
except Exception as e:
    print("Content-Type: text/html\r\n\r\n")
    print(f"<h2 style='color:red;'>Database Connection Failed!</h2><pre>{e}</pre>")
    sys.exit()

# ── Build query with optional filters ──
def build_query(params_list):
    sql = """
        SELECT id, p_name, p_gender, email_id, mobile,
               c_name, c_gender, c_dob,
               vaccination_name, appointment_date,
               hospital_name, COALESCE(status, 'pending') AS status
        FROM hospital_appointment
        WHERE 1=1
    """
    if filter_date:
        sql += " AND appointment_date = %s"
        params_list.append(filter_date)
    if filter_hospital:
        sql += " AND hospital_name LIKE %s"
        params_list.append(f"%{filter_hospital}%")
    if filter_status:
        sql += " AND status = %s"
        params_list.append(filter_status)
    sql += " ORDER BY id DESC"
    return sql

# ── Helper: safe cell value ──
def safe(row, idx):
    return str(row[idx]).strip() if len(row) > idx and row[idx] not in (None, "") else "N/A"

# ══════════════════════════════════════════════
#  CSV EXPORT
# ══════════════════════════════════════════════
if export_action == "csv":
    params = []
    sql = build_query(params)
    cur.execute(sql, params)
    rows = cur.fetchall()
    con.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Parent Name", "Parent Gender", "Email", "Mobile",
        "Child Name", "Child Gender", "Child DOB",
        "Vaccine Name", "Appointment Date", "Hospital Name", "Status"
    ])
    for r in rows:
        writer.writerow([v if v is not None else "" for v in r])

    csv_bytes = output.getvalue().encode("utf-8")
    sys.stdout.buffer.write(b"Content-Type: text/csv\r\n")
    sys.stdout.buffer.write(b"Content-Disposition: attachment; filename=vaccination_appointments.csv\r\n")
    sys.stdout.buffer.write(b"\r\n")
    sys.stdout.buffer.write(csv_bytes)
    sys.stdout.buffer.flush()
    sys.exit()

# ══════════════════════════════════════════════
#  REPORT EXPORT (Styled HTML → opens in Word/Browser as Report)
# ══════════════════════════════════════════════
if export_action == "report":
    params = []
    sql = build_query(params)
    cur.execute(sql, params)
    rows = cur.fetchall()
    con.close()

    total_count     = len(rows)
    pending_count   = sum(1 for r in rows if str(r[11]).strip().lower() == "pending")
    completed_count = sum(1 for r in rows if str(r[11]).strip().lower() == "completed")
    cancelled_count = sum(1 for r in rows if str(r[11]).strip().lower() == "cancelled")
    generated_on    = datetime.now().strftime("%d %B %Y, %I:%M %p")

    # Build filter description
    filter_parts = []
    if filter_date:     filter_parts.append(f"Date: {filter_date}")
    if filter_hospital: filter_parts.append(f"Hospital: {filter_hospital}")
    if filter_status:   filter_parts.append(f"Status: {filter_status.capitalize()}")
    filter_desc = " | ".join(filter_parts) if filter_parts else "All Records (No Filter Applied)"

    # Build table rows HTML
    table_rows_html = ""
    if rows:
        for i, r in enumerate(rows, start=1):
            status = safe(r, 11).lower() if safe(r, 11) != "N/A" else "pending"
            if status == "completed":
                badge_style = "background:#d1fae5;color:#065f46;border:1px solid #6ee7b7;"
            elif status == "cancelled":
                badge_style = "background:#fee2e2;color:#991b1b;border:1px solid #fca5a5;"
            else:
                badge_style = "background:#fef9c3;color:#92400e;border:1px solid #fde68a;"
            table_rows_html += f"""
            <tr>
              <td style="text-align:center;font-weight:700;">{i}</td>
              <td><strong>{safe(r,1)}</strong></td>
              <td style="text-align:center;">{safe(r,2)}</td>
              <td>{safe(r,3)}</td>
              <td style="text-align:center;">{safe(r,4)}</td>
              <td><strong>{safe(r,5)}</strong></td>
              <td style="text-align:center;">{safe(r,6)}</td>
              <td style="text-align:center;">{safe(r,7)}</td>
              <td>{safe(r,8)}</td>
              <td style="text-align:center;"><strong>{safe(r,9)}</strong></td>
              <td>{safe(r,10)}</td>
              <td style="text-align:center;">
                <span style="padding:3px 10px;border-radius:20px;font-size:0.75rem;font-weight:700;text-transform:uppercase;{badge_style}">
                  {status.capitalize()}
                </span>
              </td>
            </tr>"""
    else:
        table_rows_html = '<tr><td colspan="12" style="text-align:center;padding:40px;color:#94a3b8;font-size:1rem;">No Records Found</td></tr>'

    report_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Vaccination Appointment Report</title>
<style>
  @page {{ size: A4 landscape; margin: 15mm; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background:#fff; color:#1e293b; font-size:11pt; }}

  /* ── HEADER ── */
  .report-header {{
    background: linear-gradient(135deg, #3b021f, #ec4899, #fdf2f8);
    color: white;
    padding: 24px 30px;
    border-radius: 10px 10px 0 0;
    margin-bottom: 0;
  }}
  .report-header .org-name {{
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 4px;
  }}
  .report-header .report-title {{
    font-size: 1.1rem;
    font-weight: 600;
    opacity: 0.9;
  }}
  .report-header .meta {{
    margin-top: 10px;
    font-size: 0.82rem;
    opacity: 0.8;
  }}
  .report-header .meta span {{ margin-right: 24px; }}

  /* ── SUMMARY CARDS ── */
  .summary-bar {{
    display: flex;
    gap: 0;
    margin-bottom: 20px;
    border-radius: 0 0 10px 10px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0,0,0,0.10);
  }}
  .sum-card {{
    flex: 1;
    padding: 16px 20px;
    text-align: center;
  }}
  .sum-card .num  {{ font-size: 2rem; font-weight: 800; line-height: 1; }}
  .sum-card .lbl  {{ font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; opacity: 0.85; }}
  .sum-total     {{ background: #ede9fe; color: #4c1d95; }}
  .sum-pending   {{ background: #fef9c3; color: #92400e; }}
  .sum-completed {{ background: #d1fae5; color: #065f46; }}
  .sum-cancelled {{ background: #fee2e2; color: #991b1b; }}

  /* ── TABLE ── */
  .data-table {{ width: 100%; border-collapse: collapse; font-size: 0.8rem; box-shadow: 0 2px 10px rgba(0,0,0,0.07); border-radius: 10px; overflow: hidden; }}
  .data-table thead tr {{
    background: linear-gradient(135deg, #3a1c71 0%, #d76d77 100%);
    color: white;
  }}
  .data-table thead th {{
  padding: 14px 12px;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  white-space: nowrap;
  border: none;
}}
  .data-table tbody tr:nth-child(even) {{ background: #fdf4ff; }}
  .data-table tbody tr:hover {{ background: #f3e8ff; }}
  .data-table tbody td {{
    padding: 9px 9px;
    border-bottom: 1px solid #f0f0f0;
    vertical-align: middle;
    color: #374151;
  }}

  /* ── FOOTER ── */
  .report-footer {{
    margin-top: 24px;
    padding-top: 14px;
    border-top: 2px solid #e2e8f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.78rem;
    color: #94a3b8;
  }}
  .report-footer .left {{ font-weight: 600; }}
  .report-footer .right {{ text-align: right; }}

  /* ── PAGE BREAK ── */
  @media print {{
    body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .no-print {{ display: none !important; }}
  }}

  /* ── DOWNLOAD BAR (visible only on screen) ── */
  .download-bar {{
    background: #1e293b;
    color: white;
    padding: 12px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.9rem;
    margin-bottom: 20px;
    border-radius: 8px;
  }}
  .download-bar .btn-save {{
    background: linear-gradient(135deg, #059669, #10b981);
    border: none; border-radius: 8px; padding: 8px 20px;
    color: white; font-weight: 700; font-size: 0.85rem; cursor: pointer;
    transition: all 0.2s;
  }}
  .download-bar .btn-save:hover {{ opacity: 0.9; }}
  @media print {{ .download-bar {{ display: none !important; }} }}
</style>
</head>
<body>

<!-- Download Bar (screen only) -->
<div class="download-bar no-print">
  <span>&#128196; <strong>Vaccination Appointment Report</strong> &mdash; Ready to save as PDF</span>
  <button class="btn-save" onclick="window.print()">&#128462; Save as PDF / Print Report</button>
</div>

<!-- Report Header -->
<div class="report-header">
  <div class="org-name">&#9679; Child Vaccination System (CVS)</div>
  <div class="report-title">Vaccination Appointment Report</div>
  <div class="meta">
    <span>&#128197; Generated On: {generated_on}</span>
    <span>&#128203; Total Records: {total_count}</span>
  </div>
</div>

<!-- Summary Bar -->
<div class="summary-bar">
  <div class="sum-card sum-total">
    <div class="num">{total_count}</div>
    <div class="lbl">Total</div>
  </div>
  <div class="sum-card sum-pending">
    <div class="num">{pending_count}</div>
    <div class="lbl">Pending</div>
  </div>
  <div class="sum-card sum-completed">
    <div class="num">{completed_count}</div>
    <div class="lbl">Completed</div>
  </div>
  <div class="sum-card sum-cancelled">
    <div class="num">{cancelled_count}</div>
    <div class="lbl">Cancelled</div>
  </div>
</div>

<!-- Data Table -->
<table class="data-table">
  <thead>
    <tr>
      <th>#</th>
      <th>Parent Name</th>
      <th>P. Gender</th>
      <th>Email</th>
      <th>Mobile</th>
      <th>Child Name</th>
      <th>C. Gender</th>
      <th>Child DOB</th>
      <th>Vaccine</th>
      <th>Appt. Date</th>
      <th>Hospital</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    {table_rows_html}
  </tbody>
</table>

<!-- Footer -->
<div class="report-footer">
  <div class="left">Child Vaccination System (CVS) &mdash; Confidential Report</div>
  <div class="right">Generated: {generated_on}<br>This report is system generated.</div>
</div>

</body>
</html>"""

    report_bytes = report_html.encode("utf-8")
    sys.stdout.buffer.write(b"Content-Type: text/html; charset=utf-8\r\n")
    sys.stdout.buffer.write(b"Content-Disposition: attachment; filename=vaccination_report.html\r\n")
    sys.stdout.buffer.write(b"\r\n")
    sys.stdout.buffer.write(report_bytes)
    sys.stdout.buffer.flush()
    sys.exit()


# ══════════════════════════════════════════════
#  HTML PAGE
# ══════════════════════════════════════════════
print("Content-Type: text/html\r\n\r\n")

params = []
sql = build_query(params)
try:
    cur.execute(sql, params)
    rows = cur.fetchall()
except Exception:
    rows = []

total_count     = len(rows)
pending_count   = sum(1 for r in rows if str(r[11]).strip().lower() == "pending")
completed_count = sum(1 for r in rows if str(r[11]).strip().lower() == "completed")
cancelled_count = sum(1 for r in rows if str(r[11]).strip().lower() == "cancelled")

# Build CSV export URL with URL-encoded filters
def build_export_url(action):
    url = f"admin_export_data.py?export_action={action}"
    if filter_date:     url += f"&filter_date={quote(filter_date)}"
    if filter_hospital: url += f"&filter_hospital={quote(filter_hospital)}"
    if filter_status:   url += f"&filter_status={quote(filter_status)}"
    return url

export_csv_url    = build_export_url("csv")
export_report_url = build_export_url("report")

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Admin - Export Data</title>
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
  50%       {{ transform: scale(1.1); }}
}}

/* ── MOBILE HAMBURGER ── */
.mobile-menu-toggle {{
  display: none;
  background: rgba(255,255,255,0.15);
  border: 1.5px solid rgba(255,255,255,0.35);
  color: white;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(6px);
  line-height: 1;
}}
.mobile-menu-toggle:hover {{
  background: rgba(255,255,255,0.28);
  border-color: rgba(255,255,255,0.6);
  color: white;
}}

/* ── LOGOUT ── */
.btn-logout {{
  background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
  border: none;
  padding: 8px 20px;
  border-radius: 25px;
  color: white;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(238,9,121,0.4);
  font-size: 0.9rem;
}}
.btn-logout:hover {{
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(238,9,121,0.6);
  color: white;
}}

/* ── SIDEBAR ── */
.sidebar {{
  min-height: 100vh;
  background: linear-gradient(135deg, #3b021f, #ec4899);
  box-shadow: 4px 0 15px rgba(0,0,0,0.2);
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
.sidebar-link i {{ margin-right: 10px; width: 20px; text-align: center; }}

/* ── SIDEBAR OVERLAY ── */
.sidebar-overlay {{
  display: none;
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.5);
  z-index: 998;
}}
.sidebar-overlay.show {{ display: block; }}

/* ── CONTENT ── */
.content-area {{ padding: 25px; min-height: 100vh; }}

/* ── PAGE HEADER ── */
.page-header {{
  background: white;
  padding: 22px 25px;
  border-radius: 18px;
  margin-bottom: 20px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.12);
  border-left: 6px solid #ec4899;
}}
.page-header h4 {{
  margin: 0;
  color: #0f172a;
  font-weight: 700;
  font-size: 1.5rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}}
.page-header h4 i {{ margin-right: 12px; color: #3b021f; }}

/* ── COUNT CARDS ── */
.count-card {{
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.10);
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}}
.count-card .card-icon {{
  font-size: 1.6rem;
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}}
.count-card .card-num   {{ font-size: 2rem; font-weight: 800; line-height: 1; }}
.count-card .card-label {{ font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8; margin-top: 2px; }}
.card-total     {{ background: #ede9fe; color: #4c1d95; }}
.card-total     .card-icon {{ background: #c4b5fd; color: #4c1d95; }}
.card-pending   {{ background: #fef9c3; color: #92400e; }}
.card-pending   .card-icon {{ background: #fde68a; color: #b45309; }}
.card-completed {{ background: #d1fae5; color: #065f46; }}
.card-completed .card-icon {{ background: #6ee7b7; color: #065f46; }}
.card-cancelled {{ background: #fee2e2; color: #991b1b; }}
.card-cancelled .card-icon {{ background: #fca5a5; color: #991b1b; }}

/* ── EXPORT CARD ── */
.export-card {{
  background: white;
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.10);
  margin-bottom: 20px;
}}
.export-card h5 {{
  font-weight: 700;
  color: #1e293b;
  font-size: 1.1rem;
  margin-bottom: 18px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f1f5f9;
}}
.export-card h5 i {{ margin-right: 8px; color: #8e2de2; }}

/* ── FILTER ── */
.filter-label {{ font-weight: 600; color: #374151; font-size: 0.88rem; margin-bottom: 6px; display: block; }}
.filter-label i {{ margin-right: 5px; color: #8e2de2; }}
.filter-input {{
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  padding: 9px 13px;
  font-size: 0.9rem;
  width: 100%;
  transition: border-color 0.3s;
  background: white;
}}
.filter-input:focus {{ border-color: #8e2de2; outline: none; box-shadow: 0 0 0 3px rgba(142,45,226,0.12); }}

/* ── EXPORT BUTTONS ── */
.btn-export-csv {{
  background: linear-gradient(135deg, #059669, #10b981);
  border: none; border-radius: 12px; padding: 13px 28px;
  color: white; font-weight: 700; font-size: 1rem; transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(16,185,129,0.4);
  display: inline-flex; align-items: center; gap: 10px; text-decoration: none;
}}
.btn-export-csv:hover {{ transform: translateY(-3px); color: white; box-shadow: 0 8px 25px rgba(16,185,129,0.5); }}

.btn-export-report {{
  background:  #ec4899;
  border: none; border-radius: 12px; padding: 13px 28px;
  color: white; font-weight: 700; font-size: 1rem; transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(124,58,237,0.4);
  display: inline-flex; align-items: center; gap: 10px; text-decoration: none;
}}
.btn-export-report:hover {{ transform: translateY(-3px); color: white; box-shadow: 0 8px 25px rgba(124,58,237,0.5); }}

.btn-filter-apply {{
  background: linear-gradient(135deg, #3b021f, #ec4899);
  border: none; border-radius: 10px; padding: 10px 0;
  color: white; font-weight: 700; width: 100%; transition: all 0.3s;
}}
.btn-filter-apply:hover {{ transform: translateY(-2px); }}
.btn-filter-clear {{
  background: linear-gradient(135deg, #6b7280, #4b5563);
  border: none; border-radius: 10px; padding: 10px 0;
  color: white; font-weight: 700; width: 100%; transition: all 0.3s;
}}
.btn-filter-clear:hover {{ transform: translateY(-2px); }}

/* ── EXPORT INFO BOX ── */
.export-info {{
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-left: 4px solid #8e2de2;
  border-radius: 8px;
  padding: 12px 16px;
  margin-top: 16px;
  font-size: 0.84rem;
  color: #475569;
}}
.export-info i {{ color: #8e2de2; margin-right: 5px; }}

/* ── TABLE ── */
.table-card {{
  background: white;
  border-radius: 18px;
  padding: 25px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.12);
  overflow-x: auto;
}}
.table-card-title {{
  font-weight: 700; color: #1e293b; font-size: 1.05rem; margin-bottom: 16px;
  padding-bottom: 12px; border-bottom: 2px solid #f1f5f9;
  display: flex; justify-content: space-between; align-items: center;
}}
.appt-table {{ width: 100%; border-collapse: collapse; }}
.appt-table thead th {{
  background: linear-gradient(135deg, #3b021f, #ec4899 50%);
  color: white; padding: 13px 11px; font-size: 0.76rem;
  text-transform: uppercase; letter-spacing: 0.8px; white-space: nowrap; border: none;
}}
.appt-table thead th:first-child {{ border-radius: 10px 0 0 10px; }}
.appt-table thead th:last-child  {{ border-radius: 0 10px 10px 0; }}
.appt-table tbody tr:nth-child(even) {{ background: #fdf4ff; }}
.appt-table tbody tr:hover {{ background: #f3e8ff; }}
.appt-table tbody td {{
  padding: 12px 11px; font-size: 0.85rem; color: #374151;
  vertical-align: middle; white-space: nowrap; border-bottom: 1px solid #f0f0f0;
}}
.badge-pending   {{ background: #fef9c3; color: #b45309; border: 1px solid #fde68a; border-radius: 20px; padding: 3px 10px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }}
.badge-completed {{ background: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; border-radius: 20px; padding: 3px 10px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }}
.badge-cancelled {{ background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; border-radius: 20px; padding: 3px 10px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }}
.empty-state {{ text-align: center; padding: 70px 20px; }}
.empty-state i {{ font-size: 5rem; color: #d1d5db; display: block; margin-bottom: 18px; }}
.empty-state p {{ font-size: 1.1rem; color: #94a3b8; font-weight: 600; }}

/* ── RESPONSIVE ── */
@media (max-width: 991.98px) {{
  .mobile-menu-toggle {{
    display: inline-flex !important;
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
  .sidebar.show {{ left: 0; }}
  .content-area {{ padding: 15px; margin-left: 0 !important; }}
  .navbar-brand {{ font-size: 1rem; }}
  .navbar-brand i {{ font-size: 1.3rem; }}
}}
@media (max-width: 767.98px) {{
  .page-header h4 {{ font-size: 1.2rem; }}
  .content-area {{ padding: 10px; }}
  .btn-logout {{ padding: 6px 15px; font-size: 0.8rem; }}
}}
@media (max-width: 575.98px) {{
  .navbar-brand {{ font-size: 0.85rem; }}
  .navbar-brand i {{ font-size: 1.1rem; }}
  .page-header h4 {{ font-size: 1rem; }}
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
      <a href="admin_dashboard.py" class="sidebar-link">
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
      <a class="sidebar-link active" href="admin_export_data.py">
        <i class="fas fa-file-export"></i> Export Data
      </a>
      <a href="admin_view_feedback.py" class="sidebar-link">
        <i class="fas fa-comment-dots"></i> Feedback
      </a>
    </div>

    <!-- CONTENT -->
    <div class="col-lg-10 col-md-9 col-12 content-area">

      <div class="page-header">
        <h4><i class="fas fa-file-export"></i> Export Appointment Data</h4>
      </div>

      <!-- COUNT CARDS -->
      <div class="row g-3 mb-3">
        <div class="col-6 col-lg-3">
          <div class="count-card card-total">
            <div class="card-icon"><i class="fas fa-clipboard-list"></i></div>
            <div><div class="card-num">{total_count}</div><div class="card-label">Total Records</div></div>
          </div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="count-card card-pending">
            <div class="card-icon"><i class="fas fa-hourglass-half"></i></div>
            <div><div class="card-num">{pending_count}</div><div class="card-label">Pending</div></div>
          </div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="count-card card-completed">
            <div class="card-icon"><i class="fas fa-check-circle"></i></div>
            <div><div class="card-num">{completed_count}</div><div class="card-label">Completed</div></div>
          </div>
        </div>
        <div class="col-6 col-lg-3">
          <div class="count-card card-cancelled">
            <div class="card-icon"><i class="fas fa-times-circle"></i></div>
            <div><div class="card-num">{cancelled_count}</div><div class="card-label">Cancelled</div></div>
          </div>
        </div>
      </div>

      <!-- FILTER + EXPORT CARD -->
      <div class="export-card">
        <h5><i class="fas fa-filter"></i> Filter &amp; Export</h5>
        <div class="row g-3 align-items-end">
          <div class="col-md-3">
            <label class="filter-label"><i class="fas fa-calendar"></i> By Date</label>
            <input type="date" class="filter-input" id="filterDate" value="{filter_date}">
          </div>
          <div class="col-md-3">
            <label class="filter-label"><i class="fas fa-hospital"></i> By Hospital</label>
            <input type="text" class="filter-input" id="filterHospital"
                   placeholder="Type hospital name..." value="{filter_hospital}">
          </div>
          <div class="col-md-2">
            <label class="filter-label"><i class="fas fa-info-circle"></i> By Status</label>
            <select class="filter-input" id="filterStatus">
              <option value="">-- All --</option>
              <option value="pending"   {"selected" if filter_status == "pending"   else ""}>Pending</option>
              <option value="completed" {"selected" if filter_status == "completed" else ""}>Completed</option>
              <option value="cancelled" {"selected" if filter_status == "cancelled" else ""}>Cancelled</option>
            </select>
          </div>
          <div class="col-md-2">
            <button class="btn-filter-apply" onclick="applyFilter()">
              <i class="fas fa-search"></i> Preview
            </button>
          </div>
          <div class="col-md-2">
            <button class="btn-filter-clear" onclick="clearFilter()">
              <i class="fas fa-redo"></i> Clear
            </button>
          </div>
        </div>

        <!-- EXPORT ACTION BUTTONS -->
        <div class="mt-4 d-flex flex-wrap gap-3">
          <a href="{export_csv_url}" class="btn-export-csv">
            <i class="fas fa-file-csv"></i> Download CSV
          </a>
          <a href="{export_report_url}" class="btn-export-report" target="_blank">
            <i class="fas fa-file-alt"></i> Download Report
          </a>
        </div>

        <!-- EXPORT INFO -->
        <div class="export-info">
          <i class="fas fa-info-circle"></i>
          <strong>CSV</strong> &mdash; Spreadsheet format, opens in Excel &nbsp;|&nbsp;
          <strong>Report</strong> &mdash; Formatted report with summary, opens in browser &mdash; use <em>"Save as PDF"</em> from the report page to save as PDF
        </div>
      </div>

      <!-- DATA PREVIEW TABLE -->
      <div class="table-card">
        <div class="table-card-title">
          <span><i class="fas fa-table" style="color:#8e2de2;margin-right:8px;"></i> Data Preview</span>
          <span style="font-size:0.85rem;color:#64748b;font-weight:500;">{total_count} record(s) found</span>
        </div>
""")

if not rows:
    print("""
        <div class="empty-state">
          <i class="fas fa-inbox"></i>
          <p>No Records Found...!</p>
        </div>
    """)
else:
    print("""
        <table class="appt-table">
          <thead>
            <tr>
              <th>#</th>
              <th><i class="fas fa-user"></i> Parent Name</th>
              <th><i class="fas fa-venus-mars"></i> P. Gender</th>
              <th><i class="fas fa-envelope"></i> Email</th>
              <th><i class="fas fa-phone"></i> Mobile</th>
              <th><i class="fas fa-child"></i> Child Name</th>
              <th><i class="fas fa-venus-mars"></i> C. Gender</th>
              <th><i class="fas fa-birthday-cake"></i> Child DOB</th>
              <th><i class="fas fa-syringe"></i> Vaccine</th>
              <th><i class="fas fa-calendar-alt"></i> Appt. Date</th>
              <th><i class="fas fa-hospital"></i> Hospital</th>
              <th><i class="fas fa-info-circle"></i> Status</th>
            </tr>
          </thead>
          <tbody>
    """)
    for i, r in enumerate(rows, start=1):
        status    = safe(r, 11).lower() if safe(r, 11) != "N/A" else "pending"
        badge_cls = f"badge-{status}"
        print(f"""
            <tr>
              <td><strong>{i}</strong></td>
              <td><strong>{safe(r,1)}</strong></td>
              <td>{safe(r,2)}</td>
              <td>{safe(r,3)}</td>
              <td>{safe(r,4)}</td>
              <td><strong>{safe(r,5)}</strong></td>
              <td>{safe(r,6)}</td>
              <td>{safe(r,7)}</td>
              <td><strong>{safe(r,8)}</strong></td>
              <td><strong>{safe(r,9)}</strong></td>
              <td>{safe(r,10)}</td>
              <td><span class="{badge_cls}">{status.capitalize()}</span></td>
            </tr>
        """)
    print("  </tbody></table>")

print("""
      </div><!-- /table-card -->
    </div><!-- /content-area -->
  </div><!-- /row -->
</div><!-- /container-fluid -->

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
function applyFilter() {
  const date     = document.getElementById('filterDate').value;
  const hospital = document.getElementById('filterHospital').value.trim();
  const status   = document.getElementById('filterStatus').value;
  let url = 'admin_export_data.py?';
  if (date)     url += 'filter_date='     + encodeURIComponent(date)     + '&';
  if (hospital) url += 'filter_hospital=' + encodeURIComponent(hospital) + '&';
  if (status)   url += 'filter_status='   + encodeURIComponent(status)   + '&';
  window.location.href = url;
}

function clearFilter() {
  window.location.href = 'admin_export_data.py';
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('show');
  document.getElementById('sidebarOverlay').classList.toggle('show');
}

document.addEventListener('click', function(e) {
  const sb = document.getElementById('sidebar');
  const mt = document.querySelector('.mobile-menu-toggle');
  if (window.innerWidth < 992 &&
      mt && !sb.contains(e.target) &&
      !mt.contains(e.target) &&
      sb.classList.contains('show')) {
    sb.classList.remove('show');
    document.getElementById('sidebarOverlay').classList.remove('show');
  }
});

function logout() {
  if (confirm('Are you sure you want to logout?'))
    window.location.href = 'logout.py';
}
</script>
</body>
</html>""")

con.close()