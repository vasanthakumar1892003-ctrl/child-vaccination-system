#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgi
import cgitb
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dateutil.relativedelta import relativedelta

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")
print("Content-Type: text/html\r\n\r\n")

# ─────────────────────────────────────────────
# EMAIL CONFIG
# ─────────────────────────────────────────────
SENDER_EMAIL    = "childvaccinationsystem2026@gmail.com"
SENDER_PASSWORD = "wuxe lqii npcp nglf"
# ─────────────────────────────────────────────

# ── Milestone order ───────────────────────────────────────────────────────────
AGE_MILESTONES_ORDER = [
    "At Birth", "6 Weeks", "10 Weeks", "14 Weeks",
    "6 Months", "9 Months", "12 Months", "15 Months",
    "18 Months", "2 Years", "4-6 Years", "10 Years"
]

def age_index(age_str):
    s = (age_str or "").strip().lower()
    for i, a in enumerate(AGE_MILESTONES_ORDER):
        if a.lower() == s:
            return i
    return 999

def parse_age_str(age_str):
    """Convert age-group string to relativedelta offset from DOB."""
    if not age_str:
        return None
    s = age_str.strip().lower()
    if s in ("at birth", "0"):
        return relativedelta()
    if s == "4-6 years":
        return relativedelta(years=4)
    parts = s.split()
    if len(parts) == 2:
        try:
            num = int(parts[0])
        except ValueError:
            return None
        unit = parts[1]
        if "week"  in unit: return relativedelta(weeks=num)
        if "month" in unit: return relativedelta(months=num)
        if "year"  in unit: return relativedelta(years=num)
    return None

# ── DB Connection ─────────────────────────────────────────────────────────────
try:
    con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
    cur = con.cursor()
except Exception as e:
    print(f"<h2 style='color:red;'>Database Connection Failed!</h2><pre>{e}</pre>")
    sys.exit()

form = cgi.FieldStorage()

def get_form_value(form, key, default=""):
    val = form.getvalue(key, default)
    if isinstance(val, list):
        val = val[0] if val else default
    return (val or default).strip()

parent_id = get_form_value(form, "parent_id")
action    = get_form_value(form, "action")
msg       = ""

# ── Fetch parent data ─────────────────────────────────────────────────────────
parent_data = {}
if parent_id:
    try:
        cur.execute(
            "SELECT id, parent_type, parent_name, parent_gender, email_id "
            "FROM parent WHERE id = %s", (parent_id,)
        )
        row = cur.fetchone()
        if row:
            parent_data = {
                "id"           : row[0],
                "parent_type"  : row[1] or "",
                "parent_name"  : row[2] or "",
                "parent_gender": row[3] or "",
                "email_id"     : row[4] or "",
            }
        else:
            msg += f"<div class='alert alert-warning'>No parent record found for ID: {parent_id}</div>"
    except Exception as e:
        msg += f"<div class='alert alert-danger'>Error fetching parent data: {e}</div>"
else:
    msg += "<div class='alert alert-danger'>Missing parent_id.</div>"


# ══════════════════════════════════════════════════════════════════════════════
#  CORE: build_vaccination_schedule
#
#  Queries the vaccination table (columns: vaccine_name, vaccine_age,
#  dose_number, description) and splits into done / remaining based on
#  manage_child fields:
#
#    done_vaccin > 0  → vaccines at age groups UP TO vaccin_age = done_rows
#                       vaccines AFTER vaccin_age = remaining_rows
#    done_vaccin == 0 → ALL vaccines go to remaining_rows
#
#  Each returned row dict has:
#    { vaccine_age, vaccine_name, dose_number, scheduled_date }
# ══════════════════════════════════════════════════════════════════════════════
def build_vaccination_schedule(child_dob, done_vaccin_int,
                               vaccin_age, vaccin_name, last_vaccinedate):
    # ── 1. Parse DOB (handles YYYY-MM-DD and DD-MM-YYYY) ─────────────────
    dob = None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            dob = datetime.strptime(str(child_dob).strip(), fmt).date()
            break
        except Exception:
            continue
    if dob is None:
        return [], []

    # ── 2. Fetch vaccination master table ─────────────────────────────────
    #       Columns: vaccine_name, vaccine_age, dose_number, description
    try:
        vc = con.cursor()
        # Actual vaccination table columns: vaccine_name, age_group, dose_number
        vc.execute("""
            SELECT vaccine_name, age_group, dose_number
            FROM   vaccination_schedule
            ORDER  BY id
        """)
        raw = vc.fetchall()
        vc.close()
    except Exception:
        # Fallback: auto-detect column names via SELECT *
        try:
            vc2 = con.cursor()
            vc2.execute("SELECT * FROM vaccination_schedule ORDER BY id")
            all_rows = vc2.fetchall()
            cols = [d[0].lower() for d in vc2.description]
            vc2.close()
            # Find age column: prefer "age_group" > any col with "age"
            age_c  = next((i for i,c in enumerate(cols) if c == "age_group"), None)
            if age_c is None:
                age_c = next((i for i,c in enumerate(cols) if "age" in c), None)
            # Find name column: prefer "vaccine_name" > any col with "name"
            name_c = next((i for i,c in enumerate(cols) if c == "vaccine_name"), None)
            if name_c is None:
                name_c = next((i for i,c in enumerate(cols) if "name" in c), None)
            dose_c = next((i for i,c in enumerate(cols) if "dose" in c), None)
            if age_c is None or name_c is None:
                return [], []
            raw = [
                (r[name_c], r[age_c], r[dose_c] if dose_c is not None else "")
                for r in all_rows
            ]
        except Exception:
            return [], []

    if not raw:
        return [], []

    # ── 3. Sort by milestone order then vaccine name ──────────────────────
    raw = sorted(raw, key=lambda r: (age_index(r[1]), (r[0] or "").lower()))

    # ── 4. Determine how many vaccines are DONE from done_vaccin count ──────
    #
    #  done_vaccin (from manage_child.done_vaccin) = exact number of vaccines
    #  already given to the child.
    #
    #  Strategy:
    #    • Sort all vaccines by milestone order (already done in step 3).
    #    • The first `done_vaccin` rows → done_rows
    #    • The rest                     → remaining_rows
    #
    #  Secondary check: if vaccin_age is also provided, we additionally verify
    #  that done rows do not exceed the vaccin_age milestone — we take the
    #  MINIMUM of the two to avoid over-counting.
    try:
        dv = int(done_vaccin_int)
    except (TypeError, ValueError):
        dv = 0

    # Build all vaccine rows first (with dates)
    all_rows_built = []
    for vax_name_raw, vax_age_raw, dose_raw in raw:
        vax_name_str = (vax_name_raw or "").strip()
        age_grp      = (vax_age_raw  or "").strip()
        dose_num     = (dose_raw     or "").strip() if dose_raw is not None else ""

        if not vax_name_str or not age_grp:
            continue

        rd = parse_age_str(age_grp)
        sched_date_str = (dob + rd).strftime("%d-%m-%Y") if rd is not None else "—"

        all_rows_built.append({
            "vaccine_age"    : age_grp,
            "vaccine_name"   : vax_name_str,
            "dose_number"    : dose_num,
            "scheduled_date" : sched_date_str,
        })

    # ── 5. Split by done_vaccin count ────────────────────────────────────
    #  If vaccin_age is also set, cap done count at that milestone boundary
    if dv > 0 and vaccin_age:
        milestone_idx = age_index(str(vaccin_age).strip())
        # Count how many vaccines fall within the milestone boundary
        milestone_cap = sum(
            1 for r in all_rows_built
            if age_index(r["vaccine_age"]) <= milestone_idx
        )
        # Use the smaller of done_vaccin count vs milestone cap
        actual_done = min(dv, milestone_cap)
    else:
        actual_done = dv  # Use done_vaccin directly (0 = all upcoming)

    done_rows      = all_rows_built[:actual_done]
    remaining_rows = all_rows_built[actual_done:]

    return done_rows, remaining_rows


# ══════════════════════════════════════════════════════════════════════════════
#  EMAIL: send_vaccination_email
# ══════════════════════════════════════════════════════════════════════════════
def send_vaccination_email(to_email, parent_name, child_name, child_dob,
                           done_rows, remaining_rows):

    def build_rows_html(rows, even_bg, odd_bg, empty_msg):
        if not rows:
            return (f"<tr><td colspan='4' style='text-align:center;color:#6b7280;"
                    f"padding:16px;font-style:italic;'>{empty_msg}</td></tr>")
        html  = ""
        prev_age = None
        for i, r in enumerate(rows):
            bg = even_bg if i % 2 == 0 else odd_bg
            if r["vaccine_age"] != prev_age:
                age_td = (f'<td style="padding:9px 12px;border-bottom:1px solid #e5e7eb;'
                          f'font-weight:700;color:#065f46;white-space:nowrap;">'
                          f'{r["vaccine_age"]}</td>')
            else:
                age_td = (f'<td style="padding:9px 12px;border-bottom:1px solid #e5e7eb;'
                          f'color:#9ca3af;font-size:.8rem;">↳</td>')
            prev_age = r["vaccine_age"]

            dose_badge = ""
            if r["dose_number"]:
                dose_badge = (f'<span style="display:inline-block;padding:2px 8px;'
                              f'border-radius:8px;background:#e0f2fe;color:#0369a1;'
                              f'font-size:.75rem;font-weight:600;margin-left:6px;">'
                              f'{r["dose_number"]}</span>')

            html += (
                f'<tr style="background:{bg};">'
                f'{age_td}'
                f'<td style="padding:9px 12px;border-bottom:1px solid #e5e7eb;'
                f'font-weight:600;color:#1e293b;">'
                f'{r["vaccine_name"]}{dose_badge}</td>'
                f'<td style="padding:9px 12px;border-bottom:1px solid #e5e7eb;'
                f'color:#374151;white-space:nowrap;">{r["scheduled_date"]}</td>'
                f'</tr>'
            )
        return html

    done_count      = len(done_rows)       # matches manage_child.done_vaccin
    remaining_count = len(remaining_rows)  # total vaccines minus done

    done_html      = build_rows_html(done_rows,      "#f0fdf4", "#ffffff",
                                     "No vaccinations recorded as done yet.")
    remaining_html = build_rows_html(remaining_rows, "#fff7ed", "#ffffff",
                                     "All vaccinations completed — excellent work!")

    th = ("padding:10px 12px;text-align:left;font-weight:700;"
          "font-size:.78rem;text-transform:uppercase;letter-spacing:.5px;color:#fff;")

    # Format DOB for display
    dob_display = str(child_dob)
    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            dob_display = datetime.strptime(str(child_dob).strip(), fmt).strftime("%d %b %Y")
            break
        except Exception:
            continue

    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif;">
<div style="max-width:680px;margin:30px auto;background:#fff;border-radius:16px;
            overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.12);">

  <!-- HEADER -->
  <div style="background:linear-gradient(135deg,#052e16,#16a34a);padding:32px 36px;text-align:center;">
    <div style="font-size:2.2rem;margin-bottom:8px;">&#128137;</div>
    <h1 style="color:#fff;margin:0;font-size:1.5rem;letter-spacing:1px;">
      Child Vaccination Schedule
    </h1>
    <p style="color:#bbf7d0;margin:6px 0 0;font-size:.9rem;">
      CVS &mdash; Child Vaccination System
    </p>
  </div>

  <!-- GREETING -->
  <div style="padding:28px 36px 0;">
    <p style="font-size:.95rem;color:#374151;line-height:1.7;margin:0 0 20px;">
      Dear <strong style="color:#052e16;">{parent_name}</strong>,<br><br>
      Your child <strong style="background:#dcfce7;color:#15803d;padding:2px 10px;
      border-radius:10px;border:1px solid #86efac;">{child_name}</strong>
      (DOB: <strong>{dob_display}</strong>) has been successfully registered in the CVS system.
      <br><br>
      Below is the complete vaccination schedule based on your child's date of birth,
      showing <span style="color:#059669;font-weight:600;">completed</span> milestones
      and <span style="color:#f97316;font-weight:600;">upcoming</span> vaccinations.
    </p>

    <!-- SUMMARY BADGES -->
    <div style="display:flex;gap:12px;margin-bottom:24px;flex-wrap:wrap;">
      <div style="flex:1;min-width:140px;background:#f0fdf4;border:1px solid #bbf7d0;
                  border-radius:10px;padding:12px 16px;text-align:center;">
        <div style="font-size:1.5rem;font-weight:800;color:#059669;">{done_count}</div>
        <div style="font-size:.78rem;color:#065f46;font-weight:600;text-transform:uppercase;
                    letter-spacing:.5px;">Vaccinations Done</div>
      </div>
      <div style="flex:1;min-width:140px;background:#fff7ed;border:1px solid #fed7aa;
                  border-radius:10px;padding:12px 16px;text-align:center;">
        <div style="font-size:1.5rem;font-weight:800;color:#ea580c;">{remaining_count}</div>
        <div style="font-size:.78rem;color:#7c2d12;font-weight:600;text-transform:uppercase;
                    letter-spacing:.5px;">Upcoming Vaccines</div>
      </div>
    </div>
  </div>

  <!-- DONE TABLE -->
  <div style="padding:0 36px 20px;">
    <div style="display:inline-block;background:#d1fae5;color:#065f46;padding:7px 16px;
                border-radius:8px;font-size:.82rem;font-weight:700;text-transform:uppercase;
                letter-spacing:.8px;margin-bottom:10px;">
      &#10003;&nbsp; Vaccinations Already Done
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:.85rem;">
      <thead>
        <tr>
          <td style="{th}background:#059669;">Age Group</td>
          <td style="{th}background:#059669;">Vaccine Name &amp; Dose</td>
          <td style="{th}background:#059669;">Scheduled Date</td>
        </tr>
      </thead>
      <tbody>{done_html}</tbody>
    </table>
  </div>

  <!-- UPCOMING TABLE -->
  <div style="padding:0 36px 28px;">
    <div style="display:inline-block;background:#ffedd5;color:#7c2d12;padding:7px 16px;
                border-radius:8px;font-size:.82rem;font-weight:700;text-transform:uppercase;
                letter-spacing:.8px;margin-bottom:10px;">
      &#9200;&nbsp; Upcoming Vaccinations
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:.85rem;">
      <thead>
        <tr>
          <td style="{th}background:#ea580c;">Age Group</td>
          <td style="{th}background:#ea580c;">Vaccine Name &amp; Dose</td>
          <td style="{th}background:#ea580c;">Scheduled Date</td>
        </tr>
      </thead>
      <tbody>{remaining_html}</tbody>
    </table>
  </div>

  <!-- NOTE -->
  <div style="margin:0 36px 28px;padding:14px 16px;background:#f8fafc;
              border-left:4px solid #059669;border-radius:6px;
              font-size:.82rem;color:#64748b;line-height:1.6;">
    <strong style="color:#374151;">&#128204; Note:</strong>
    Scheduled dates are calculated from your child's date of birth and are approximate.
    Please confirm exact appointment dates with your healthcare provider.
    Keep this email for your records.
  </div>

  <!-- FOOTER -->
  <div style="background:#f0fdf4;padding:16px 36px;text-align:center;
              font-size:.78rem;color:#6b7280;border-top:1px solid #d1fae5;">
    &copy; CVS &mdash; Child Vaccination System &nbsp;|&nbsp;
    This is an automated message, please do not reply.
  </div>
</div>
</body>
</html>"""

    try:
        mail = MIMEMultipart("alternative")
        mail["Subject"] = f"CVS – Vaccination Schedule for {child_name}"
        mail["From"]    = SENDER_EMAIL
        mail["To"]      = to_email
        mail.attach(MIMEText(html_body, "html", "utf-8"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, mail.as_string())
        return True, ""
    except Exception as ex:
        return False, str(ex)


# ══════════════════════════════════════════════════════════════════════════════
#  HANDLE ADD
# ══════════════════════════════════════════════════════════════════════════════
if action == "add":
    child_name       = form.getvalue("child_name",       "").strip()
    child_dob        = form.getvalue("child_dob",        "").strip()
    child_gender     = form.getvalue("child_gender",     "").strip()
    done_vaccin      = (form.getvalue("done_vaccin",     "") or "0").strip()
    vaccin_age       = form.getvalue("vaccin_age",       "").strip()
    last_vaccinedate = form.getvalue("last_vaccinedate", "").strip()
    vaccin_name      = form.getvalue("vaccin_name",      "").strip()

    try:
        dv_int = int(done_vaccin) if done_vaccin.isdigit() else 0
    except ValueError:
        dv_int = 0

    # Resolve parent email — parent_data first, then DB fallback
    to_email    = (parent_data.get("email_id") or "").strip()
    parent_name = (parent_data.get("parent_name") or "Parent").strip()

    if not to_email and parent_id:
        try:
            cur.execute(
                "SELECT email_id, parent_name FROM parent WHERE id=%s LIMIT 1",
                (parent_id,)
            )
            fb = cur.fetchone()
            if fb:
                to_email    = (fb[0] or "").strip()
                parent_name = (fb[1] or parent_name).strip()
        except Exception:
            pass

    try:
        cur.execute("""
            INSERT INTO manage_child
                (child_name, child_dob, child_gender, done_vaccin, vaccin_age,
                 last_vaccinedate, vaccin_name,
                 parent_name, parent_type, parent_gender, email_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            child_name, child_dob, child_gender, done_vaccin, vaccin_age,
            last_vaccinedate, vaccin_name,
            parent_data.get("parent_name", ""),
            parent_data.get("parent_type", ""),
            parent_data.get("parent_gender", ""),
            to_email or parent_data.get("email_id", "")
        ))
        con.commit()
        msg = "<div class='alert alert-success'>&#10003; Child added successfully!</div>"

        # ── Build schedule ─────────────────────────────────────────────────
        done_rows, remaining_rows = build_vaccination_schedule(
            child_dob, dv_int, vaccin_age, vaccin_name, last_vaccinedate
        )

        # Last-resort email fallback from manage_child row just inserted
        if not to_email:
            try:
                cur.execute("""
                    SELECT email_id, parent_name FROM manage_child
                    WHERE child_name=%s AND email_id IS NOT NULL AND email_id != ''
                    ORDER BY id DESC LIMIT 1
                """, (child_name,))
                fb2 = cur.fetchone()
                if fb2:
                    to_email    = (fb2[0] or "").strip()
                    parent_name = (fb2[1] or parent_name).strip()
            except Exception:
                pass

        if to_email:
            ok, err = send_vaccination_email(
                to_email, parent_name, child_name, child_dob,
                done_rows, remaining_rows
            )
            if ok:
                msg += (f"<div class='alert alert-info'>"
                        f"&#9993; Vaccination schedule emailed to "
                        f"<strong>{to_email}</strong> &nbsp;"
                        f"({len(done_rows)} done, {len(remaining_rows)} upcoming)</div>")
            else:
                msg += (f"<div class='alert alert-warning'>"
                        f"&#9888; Child added but email failed: {err}</div>")
        else:
            msg += ("<div class='alert alert-warning'>"
                    "&#9888; No email address found – schedule email skipped.</div>")

    except Exception as e:
        msg = f"<div class='alert alert-danger'>Error adding child: {e}</div>"


# ── Handle UPDATE ─────────────────────────────────────────────────────────────
if action == "update":
    child_id         = form.getvalue("child_id",         "").strip()
    child_name       = form.getvalue("child_name",       "").strip()
    child_dob        = form.getvalue("child_dob",        "").strip()
    child_gender     = form.getvalue("child_gender",     "").strip()
    done_vaccin      = (form.getvalue("done_vaccin",     "") or "0").strip()
    vaccin_age       = form.getvalue("vaccin_age",       "").strip()
    last_vaccinedate = form.getvalue("last_vaccinedate", "").strip()
    vaccin_name      = form.getvalue("vaccin_name",      "").strip()
    try:
        cur.execute("""
            UPDATE manage_child
            SET child_name=%s, child_dob=%s, child_gender=%s,
                done_vaccin=%s, vaccin_age=%s, last_vaccinedate=%s, vaccin_name=%s
            WHERE id=%s
        """, (child_name, child_dob, child_gender, done_vaccin,
              vaccin_age, last_vaccinedate, vaccin_name, child_id))
        con.commit()
        msg = "<div class='alert alert-success'>&#10003; Child updated successfully!</div>"
    except Exception as e:
        msg = f"<div class='alert alert-danger'>Error updating child: {e}</div>"


# ── Handle DELETE ─────────────────────────────────────────────────────────────
if action == "delete":
    child_id = form.getvalue("child_id", "")
    try:
        cur.execute("DELETE FROM manage_child WHERE id=%s", (child_id,))
        con.commit()
        msg = "<div class='alert alert-success'>&#10003; Child deleted successfully!</div>"
    except Exception as e:
        msg = f"<div class='alert alert-danger'>Error deleting child: {e}</div>"


# ── SELECT all children for this parent ───────────────────────────────────────
children_rows = []
try:
    if parent_data.get("email_id"):
        cur.execute("""
            SELECT id, child_name, child_dob, child_gender, done_vaccin,
                   vaccin_age, vaccin_name, last_vaccinedate,
                   parent_name, parent_type, parent_gender, email_id
            FROM manage_child
            WHERE email_id = %s
            ORDER BY id
        """, (parent_data["email_id"],))
        children_rows = cur.fetchall()
except Exception as e:
    msg += f"<div class='alert alert-warning'>Could not load children: {e}</div>"


# ── vax_table_html: for modal vaccination schedule tab ───────────────────────
def vax_table_html(rows, empty_msg):
    if not rows:
        return (f"<tr><td colspan='4' style='text-align:center;color:#888;"
                f"padding:12px;font-style:italic;'>{empty_msg}</td></tr>")
    out = ""
    prev_age = None
    for r in rows:
        if r["vaccine_age"] != prev_age:
            age_cell = (f"<td style='font-weight:700;color:#065f46;"
                        f"white-space:nowrap;'>{r['vaccine_age']}</td>")
        else:
            age_cell = "<td style='color:#9ca3af;font-size:.8rem;'>↳</td>"
        prev_age = r["vaccine_age"]

        dose_badge = ""
        if r.get("dose_number"):
            dose_badge = (f"<span style='display:inline-block;padding:1px 7px;"
                          f"border-radius:8px;background:#e0f2fe;color:#0369a1;"
                          f"font-size:.75rem;font-weight:600;margin-left:6px;'>"
                          f"{r['dose_number']}</span>")
        out += (
            f"<tr>"
            f"{age_cell}"
            f"<td>{r['vaccine_name']}{dose_badge}</td>"
            f"<td style='white-space:nowrap;'>{r['scheduled_date']}</td>"
            f"</tr>"
        )
    return out


# ══════════════════════════════════════════════════════════════════════════════
#  HTML OUTPUT
# ══════════════════════════════════════════════════════════════════════════════
print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Manage Children - CVS</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  background:linear-gradient(135deg,#052e16,#22c55e,#dcfce7);
  min-height:100vh; font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif; overflow-x:hidden;
}}
.navbar {{
  box-shadow:0 4px 20px rgba(0,0,0,.4); padding:15px 20px;
  background:linear-gradient(135deg,#052e16,#22c55e,#dcfce7) !important;
}}
.navbar .container-fluid {{ display:flex;flex-direction:row;align-items:center;flex-wrap:nowrap; }}
.navbar-brand {{ font-weight:600;color:white !important;letter-spacing:2px;text-transform:uppercase; }}
.navbar-brand i {{ margin-right:10px;color:#d1fae5;font-size:1.5rem;animation:bounce 2s infinite; }}
@keyframes bounce {{ 0%,100%{{transform:translateY(0);}} 50%{{transform:translateY(-5px);}} }}
.mobile-menu-toggle {{
  display:none; flex-shrink:0; align-self:center;
  background:rgba(255,255,255,0.15); border:1.5px solid rgba(255,255,255,0.35);
  color:white; padding:6px 12px; border-radius:8px; font-size:1.2rem;
  cursor:pointer; transition:all 0.3s ease; line-height:1; margin-right:12px;
}}
.mobile-menu-toggle:hover {{ background:rgba(255,255,255,0.28);color:white; }}
.btn-logout {{
  flex-shrink:0; background:linear-gradient(135deg,#ee0979 0%,#ff6a00 100%);
  border:none; padding:8px 20px; border-radius:25px; color:white; font-weight:600;
  transition:all 0.3s ease; box-shadow:0 4px 15px rgba(238,9,121,0.4);
  font-size:.9rem; white-space:nowrap;
}}
.btn-logout:hover {{ transform:translateY(-2px);color:white; }}
.sidebar {{
  min-height:100vh; background:linear-gradient(135deg,#052e16,#22c55e);
  box-shadow:4px 0 20px rgba(0,0,0,.3); padding:20px 0;
}}
.sidebar-link {{
  display:block; padding:14px 18px; color:#d1fae5; text-decoration:none;
  transition:all .3s; border-left:4px solid transparent; font-weight:500; margin:6px 0;
}}
.sidebar-link:hover,.sidebar-link.active {{
  background:linear-gradient(90deg,#22c55e,transparent 100%);
  color:#fff; border-left:4px solid #dcfce7; padding-left:24px;
}}
.sidebar-link i {{ margin-right:12px;width:22px;text-align:center; }}
.sidebar-overlay {{
  display:none; position:fixed; top:0; left:0;
  width:100%; height:100%; background:rgba(0,0,0,0.6); z-index:998;
}}
.sidebar-overlay.show {{ display:block; }}
.content-area {{ padding:25px;min-height:100vh; }}
.page-header {{
  background:white; border-radius:16px; padding:22px 28px; margin-bottom:22px;
  box-shadow:0 4px 20px rgba(0,0,0,.1); display:flex; align-items:center; gap:15px;
}}
.page-header i {{ color:#059669;font-size:2rem; }}
.page-header h4 {{ margin:0;font-weight:700;color:#1e293b;font-size:1.5rem; }}
.btn-add {{
  background:linear-gradient(135deg,#22c55e 50%,#dcfce7); border:none; padding:10px 24px;
  border-radius:25px; color:white; font-weight:600; font-size:.95rem; transition:all .3s;
  box-shadow:0 4px 15px rgba(5,150,105,.4); margin-bottom:20px;
}}
.btn-add:hover {{ transform:translateY(-2px);color:white; }}
.table-container {{
  background:white; border-radius:16px; padding:25px; box-shadow:0 4px 20px rgba(0,0,0,.1);
}}
.table thead th {{
  background:linear-gradient(135deg,#052e16,#22c55e); color:white; font-weight:600;
  font-size:.85rem; letter-spacing:.5px; text-transform:uppercase; border:none; padding:14px 12px;
}}
.table tbody tr:hover {{ background:#f0fdf4; }}
.table tbody td {{ padding:14px 12px;vertical-align:middle;color:#374151; }}
.badge-done {{ padding:6px 14px;border-radius:20px;font-weight:600;font-size:.82rem; }}
.badge-green  {{ background:#d1fae5;color:#059669;border:2px solid #6ee7b7; }}
.badge-yellow {{ background:#fef9c3;color:#b45309;border:2px solid #fde047; }}
.badge-gray   {{ background:#f1f5f9;color:#64748b;border:2px solid #cbd5e1; }}
.btn-view {{
  background:linear-gradient(135deg,#0891b2,#06b6d4); border:none; padding:6px 14px;
  border-radius:20px; color:white; font-size:.82rem; font-weight:600; transition:all .3s;
}}
.btn-view:hover {{ transform:translateY(-1px);color:white;box-shadow:0 4px 12px rgba(8,145,178,.4); }}
.modal-content {{ border-radius:14px;border:none;box-shadow:0 20px 60px rgba(0,0,0,.3);overflow:hidden; }}
.modal-header {{ background:linear-gradient(135deg,#047857,#059669);color:white; }}
.modal-header .btn-close {{ filter:invert(1); }}
.modal-body {{ background:#f0fdf4;padding:28px 32px; }}
.modal-footer {{ background:#f0fdf4;border-top:1px solid #a7f3d0; }}
.form-label {{ font-weight:600;color:#065f46;font-size:.88rem;margin-bottom:4px; }}
.form-control,.form-select {{ border:2px solid #a7f3d0;border-radius:10px;padding:9px 13px;font-size:.9rem; }}
.form-control:focus,.form-select:focus {{ border-color:#059669;box-shadow:0 0 0 3px rgba(5,150,105,.2);outline:none; }}
.form-control[readonly] {{ background:#e2f5ec;color:#374151;font-weight:500;cursor:not-allowed; }}
.section-title {{
  font-size:.8rem;font-weight:700;color:#047857;text-transform:uppercase;
  letter-spacing:.8px;margin:15px 0 10px;padding-bottom:6px;border-bottom:2px solid #a7f3d0;
}}
.lock-note {{ font-size:.75rem;color:#6b7280;margin-top:3px; }}
.lock-note i {{ color:#059669; }}
.btn-cancel  {{ background:linear-gradient(135deg,#64748b,#94a3b8);border:none;padding:10px 22px;border-radius:20px;color:white;font-weight:600; }}
.btn-confirm {{ background:linear-gradient(135deg,#059669,#10b981);border:none;padding:10px 22px;border-radius:20px;color:white;font-weight:600; }}
.view-modal-body {{ background:#f0f9ff;padding:24px 28px; }}
.view-modal-footer {{ background:#f0f9ff;border-top:1px solid #bae6fd; }}
.modal-tab-btns {{ display:flex;gap:8px;margin-bottom:18px;flex-wrap:wrap; }}
.tab-btn {{
  flex:1;min-width:90px;padding:9px;border:2px solid #bae6fd;border-radius:10px;
  background:white;color:#0891b2;font-weight:600;font-size:.82rem;
  cursor:pointer;transition:all .25s;text-align:center;
}}
.tab-btn.active {{
  background:linear-gradient(135deg,#0891b2,#06b6d4);color:white;border-color:transparent;
}}
.tab-panel {{ display:none; }}
.tab-panel.active {{ display:block; }}
.info-grid {{ display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:10px; }}
.info-card {{
  background:white;border-radius:12px;padding:14px 16px;
  border-left:4px solid #10b981;box-shadow:0 2px 8px rgba(0,0,0,.06);
}}
.info-card.blue {{ border-left-color:#0891b2; }}
.info-card.pink {{ border-left-color:#ec4899; }}
.info-card label {{ font-size:.72rem;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px;display:block; }}
.info-card .value {{ font-size:.93rem;font-weight:600;color:#1e293b; }}
.info-card .value.badge-val {{
  display:inline-block;padding:3px 10px;border-radius:12px;
  background:#d1fae5;color:#059669;border:1px solid #6ee7b7;font-size:.82rem;
}}
.view-section-title {{
  font-size:.78rem;font-weight:700;color:#0891b2;text-transform:uppercase;
  letter-spacing:.8px;margin:16px 0 10px;padding-bottom:6px;border-bottom:2px solid #bae6fd;
}}
.view-section-title i {{ margin-right:6px; }}
.edit-form-label {{ font-weight:600;color:#0c4a6e;font-size:.85rem;margin-bottom:4px; }}
.edit-form-control,.edit-form-select {{
  border:2px solid #bae6fd;border-radius:10px;padding:9px 13px;
  font-size:.9rem;width:100%;background:white;
}}
.edit-form-control:focus,.edit-form-select:focus {{
  border-color:#0891b2;box-shadow:0 0 0 3px rgba(8,145,178,.2);outline:none;
}}
.btn-update {{
  background:linear-gradient(135deg,#0891b2,#06b6d4);border:none;padding:10px 26px;
  border-radius:20px;color:white;font-weight:600;font-size:.95rem;transition:all .3s;
}}
.btn-update:hover {{ transform:translateY(-1px);box-shadow:0 6px 18px rgba(8,145,178,.4);color:white; }}
.btn-delete-modal {{
  background:linear-gradient(135deg,#dc2626,#ef4444);border:none;padding:10px 26px;
  border-radius:20px;color:white;font-weight:600;font-size:.95rem;transition:all .3s;
}}
.btn-delete-modal:hover {{ transform:translateY(-1px);box-shadow:0 6px 18px rgba(220,38,38,.4);color:white; }}
.btn-close-modal {{ background:linear-gradient(135deg,#64748b,#94a3b8);border:none;padding:10px 22px;border-radius:20px;color:white;font-weight:600; }}
/* Vaccination schedule tables in modal */
.vax-table {{ width:100%;border-collapse:collapse;font-size:.83rem;margin-top:6px; }}
.vax-table thead th {{
  padding:9px 10px;text-align:left;font-weight:700;font-size:.76rem;
  text-transform:uppercase;letter-spacing:.5px;color:#fff;
}}
.vax-table-done thead {{ background:#059669; }}
.vax-table-rem  thead {{ background:#ea580c; }}
.vax-table tbody td {{ padding:8px 10px;border-bottom:1px solid #e5e7eb;color:#374151; }}
.vax-table tbody tr:nth-child(even) {{ background:#f9fafb; }}
.no-data {{ text-align:center;padding:40px;color:#64748b; }}
.no-data i {{ font-size:4rem;color:#cbd5e1;margin-bottom:15px;display:block; }}
@media (max-width:991.98px) {{
  .mobile-menu-toggle {{ display:flex;align-items:center;justify-content:center; }}
  .sidebar {{
    position:fixed;left:-100%;top:0;width:280px;height:100vh;
    z-index:999;transition:left 0.3s ease;overflow-y:auto;
  }}
  .sidebar.show {{ left:0; }}
  .content-area {{ padding:15px;margin-left:0 !important; }}
}}
@media (max-width:767.98px) {{
  .info-grid {{ grid-template-columns:1fr; }}
  .modal-tab-btns {{ flex-direction:column; }}
}}
@media (max-width:575.98px) {{
  .navbar-brand {{ font-size:.85rem;letter-spacing:.5px; }}
  .btn-logout {{ padding:6px 14px;font-size:.8rem; }}
}}
</style>
</head>
<body>

<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container-fluid">
    <button class="mobile-menu-toggle" onclick="toggleSidebar()"><i class="fas fa-bars"></i></button>
    <span class="navbar-brand ms-2"><i class="fa-solid fa-users"></i> CVS - Parent</span>
    <button class="btn btn-logout" onclick="logout()"><i class="fas fa-sign-out-alt"></i> Logout</button>
  </div>
</nav>

<div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

<div class="container-fluid">
  <div class="row">
    <div class="col-lg-2 col-md-3 sidebar p-0" id="sidebar">
      <a href="parent_dashboard.py?parent_id={parent_id}"      class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-home"></i> Home</a>
      <a href="parent_vaccination.py?parent_id={parent_id}"    class="sidebar-link" onclick="closeSidebarMobile()"><i class="fa-solid fa-circle-info"></i> Vaccination Info</a>
      <a href="parent_manage_child.py?parent_id={parent_id}"   class="sidebar-link active" onclick="closeSidebarMobile()"><i class="fas fa-baby"></i> Manage Children</a>
      <a href="parent_view_hospital.py?parent_id={parent_id}"  class="sidebar-link" onclick="closeSidebarMobile()"><i class="fa-solid fa-eye"></i> View Hospital</a>
      <a href="parent_booked_appointment.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fa-solid fa-calendar-day"></i> Booked Appointments
      </a>
      <a href="parent_my_appointment.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-calendar-check"></i> My Appointments</a>
      <a href="parent_reminder.py?parent_id={parent_id}"       class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-bell"></i> My Reminders</a>
      <a href="parent_profile.py?parent_id={parent_id}"        class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-user-circle"></i> My Profile</a>
      <a href="parent_feedback.py?parent_id={parent_id}"       class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-comment-dots"></i> Feedback</a>
      <a href="parent_help.py?parent_id={parent_id}"           class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-circle-question"></i> Help &amp; Support</a>
    </div>

    <div class="col-lg-10 col-md-9 col-12 content-area">
      {msg}
      <div class="page-header">
        <i class="fas fa-baby"></i>
        <h4>MANAGE CHILDREN DATA</h4>
      </div>
      <button class="btn btn-add" data-bs-toggle="modal" data-bs-target="#addChildModal">
        <i class="fas fa-plus"></i> Add New Child
      </button>
      <div class="table-container">
        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead>
              <tr>
                <th><i class="fas fa-hashtag"></i> #</th>
                <th><i class="fas fa-baby"></i> CHILD NAME</th>
                <th><i class="fas fa-birthday-cake"></i> DATE OF BIRTH</th>
                <th><i class="fas fa-venus-mars"></i> GENDER</th>
                <th><i class="fas fa-heart-pulse"></i> VACCINATIONS</th>
                <th><i class="fas fa-syringe"></i> VACCINE NAME</th>
                <th><i class="fas fa-cog"></i> ACTIONS</th>
              </tr>
            </thead>
            <tbody>
""")

view_modals = []

def gender_option(val, opt): return "selected" if val == opt else ""
def age_option(val, opt):    return "selected" if val == opt else ""

if children_rows:
    for i, row in enumerate(children_rows, 1):
        (child_id, child_name, child_dob, child_gender, done_vaccin,
         vaccin_age, vaccin_name, last_vaccinedate,
         par_name, par_type, par_gender, email_id) = row

        try:
            dv_int = int(done_vaccin) if done_vaccin is not None else 0
        except (ValueError, TypeError):
            dv_int = 0

        badge_class = "badge-green" if dv_int >= 2 else ("badge-yellow" if dv_int == 1 else "badge-gray")

        child_dob_val        = str(child_dob)        if child_dob        else ""
        last_vaccinedate_val = str(last_vaccinedate) if last_vaccinedate else ""
        vaccin_age_disp      = vaccin_age   or "—"
        vaccin_name_disp     = vaccin_name  or "—"
        par_name_disp        = par_name     or "—"
        par_type_disp        = par_type     or "—"
        par_gender_disp      = par_gender   or "—"
        email_id_disp        = email_id     or "—"
        last_vac_disp        = last_vaccinedate_val or "—"

        # Build schedule for modal
        done_rows_m, remaining_rows_m = build_vaccination_schedule(
            child_dob_val, dv_int, vaccin_age, vaccin_name, last_vaccinedate_val
        )
        done_trs      = vax_table_html(done_rows_m,      "No vaccinations recorded as done.")
        remaining_trs = vax_table_html(remaining_rows_m, "All vaccinations completed — great job!")

        print(f"""
              <tr>
                <td><strong>{i}</strong></td>
                <td>{child_name}</td>
                <td>{child_dob_val}</td>
                <td>{child_gender}</td>
                <td><span class="badge-done {badge_class}">{dv_int} DONE</span></td>
                <td>{vaccin_name_disp}</td>
                <td>
                  <button class="btn btn-view"
                    data-bs-toggle="modal" data-bs-target="#viewModal_{child_id}">
                    <i class="fas fa-eye"></i> View More
                  </button>
                </td>
              </tr>
        """)

        view_modals.append(f"""
<div class="modal fade" id="viewModal_{child_id}" tabindex="-1" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered modal-dialog-scrollable" style="max-width:720px;">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-baby me-2"></i> {child_name}</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" style="filter:invert(1);"></button>
      </div>
      <div class="modal-body view-modal-body">
        <div class="modal-tab-btns">
          <button class="tab-btn active" onclick="switchTab(this,'viewTab_{child_id}','{child_id}')">
            <i class="fas fa-eye me-1"></i> View Details
          </button>
          <button class="tab-btn" onclick="switchTab(this,'scheduleTab_{child_id}','{child_id}')">
            <i class="fas fa-syringe me-1"></i> Vaccination Schedule
          </button>
          <button class="tab-btn" onclick="switchTab(this,'editTab_{child_id}','{child_id}')">
            <i class="fas fa-pen me-1"></i> Edit / Update
          </button>
        </div>

        <!-- VIEW TAB -->
        <div class="tab-panel active" id="viewTab_{child_id}">
          <div class="view-section-title"><i class="fas fa-baby"></i> Child Information</div>
          <div class="info-grid">
            <div class="info-card blue"><label>Child Name</label><div class="value">{child_name}</div></div>
            <div class="info-card blue"><label>Date of Birth</label><div class="value">{child_dob_val}</div></div>
            <div class="info-card blue"><label>Gender</label><div class="value">{child_gender}</div></div>
            <div class="info-card pink"><label>Vaccinations Done</label><div class="value"><span class="badge-val">{dv_int} DONE</span></div></div>
            <div class="info-card pink"><label>Vaccine Age Group</label><div class="value">{vaccin_age_disp}</div></div>
            <div class="info-card pink"><label>Last Vaccine Date</label><div class="value">{last_vac_disp}</div></div>
            <div class="info-card pink"><label>Vaccine Name</label><div class="value">{vaccin_name_disp}</div></div>
          </div>
          <div class="view-section-title"><i class="fas fa-user-circle"></i> Parent Information</div>
          <div class="info-grid">
            <div class="info-card"><label>Parent Name</label><div class="value">{par_name_disp}</div></div>
            <div class="info-card"><label>Parent Type</label><div class="value">{par_type_disp}</div></div>
            <div class="info-card"><label>Parent Gender</label><div class="value">{par_gender_disp}</div></div>
            <div class="info-card"><label>Email ID</label><div class="value" style="word-break:break-all;">{email_id_disp}</div></div>
          </div>
        </div>

        <!-- VACCINATION SCHEDULE TAB -->
        <div class="tab-panel" id="scheduleTab_{child_id}">
          <div class="view-section-title" style="color:#059669;">
            <i class="fas fa-check-circle"></i> Vaccinations Already Done
          </div>
          <div style="overflow-x:auto;">
            <table class="vax-table vax-table-done">
              <thead><tr><th>Age Group</th><th>Vaccine &amp; Dose</th><th>Scheduled Date</th></tr></thead>
              <tbody>{done_trs}</tbody>
            </table>
          </div>
          <div class="view-section-title" style="color:#ea580c;margin-top:20px;">
            <i class="fas fa-clock"></i> Upcoming Vaccinations
          </div>
          <div style="overflow-x:auto;">
            <table class="vax-table vax-table-rem">
              <thead><tr><th>Age Group</th><th>Vaccine &amp; Dose</th><th>Scheduled Date</th></tr></thead>
              <tbody>{remaining_trs}</tbody>
            </table>
          </div>
          <p style="margin-top:12px;font-size:.76rem;color:#6b7280;">
            <i class="fas fa-info-circle"></i>
            Dates calculated from date of birth — confirm with your healthcare provider.
          </p>
        </div>

        <!-- EDIT TAB -->
        <div class="tab-panel" id="editTab_{child_id}">
          <form method="POST" action="parent_manage_child.py?parent_id={parent_id}">
            <input type="hidden" name="parent_id" value="{parent_id}">
            <input type="hidden" name="action"    value="update">
            <input type="hidden" name="child_id"  value="{child_id}">
            <div class="view-section-title"><i class="fas fa-baby"></i> Edit Child Information</div>
            <div class="mb-3">
              <label class="edit-form-label">Child Name</label>
              <input type="text" name="child_name" class="edit-form-control" value="{child_name}" required>
            </div>
            <div class="row mb-3">
              <div class="col-6">
                <label class="edit-form-label">Date of Birth</label>
                <input type="date" name="child_dob" class="edit-form-control" value="{child_dob_val}" required>
              </div>
              <div class="col-6">
                <label class="edit-form-label">Gender</label>
                <select name="child_gender" class="edit-form-select" required>
                  <option value="">-- Select --</option>
                  <option value="Male"   {gender_option(child_gender,"Male")}>Male</option>
                  <option value="Female" {gender_option(child_gender,"Female")}>Female</option>
                </select>
              </div>
            </div>
            <div class="row mb-3">
              <div class="col-6">
                <label class="edit-form-label">Vaccinations Done</label>
                <input type="number" name="done_vaccin" class="edit-form-control" value="{dv_int}" min="0" required>
              </div>
              <div class="col-6">
                <label class="edit-form-label">Age Group (Last Done)</label>
                <select name="vaccin_age" class="edit-form-select">
                  <option value="">--Select--</option>
                  <option value="At Birth"  {age_option(vaccin_age,"At Birth")}>At Birth</option>
                  <option value="6 Weeks"   {age_option(vaccin_age,"6 Weeks")}>6 Weeks</option>
                  <option value="10 Weeks"  {age_option(vaccin_age,"10 Weeks")}>10 Weeks</option>
                  <option value="14 Weeks"  {age_option(vaccin_age,"14 Weeks")}>14 Weeks</option>
                  <option value="6 Months"  {age_option(vaccin_age,"6 Months")}>6 Months</option>
                  <option value="9 Months"  {age_option(vaccin_age,"9 Months")}>9 Months</option>
                  <option value="12 Months" {age_option(vaccin_age,"12 Months")}>12 Months</option>
                  <option value="15 Months" {age_option(vaccin_age,"15 Months")}>15 Months</option>
                  <option value="18 Months" {age_option(vaccin_age,"18 Months")}>18 Months</option>
                  <option value="2 Years"   {age_option(vaccin_age,"2 Years")}>2 Years</option>
                  <option value="4-6 Years" {age_option(vaccin_age,"4-6 Years")}>4-6 Years</option>
                  <option value="10 Years"  {age_option(vaccin_age,"10 Years")}>10 Years</option>
                </select>
              </div>
            </div>
            <div class="row mb-3">
              <div class="col-6">
                <label class="edit-form-label">Last Vaccine Date</label>
                <input type="date" name="last_vaccinedate" class="edit-form-control" value="{last_vaccinedate_val}">
              </div>
              <div class="col-6">
                <label class="edit-form-label">Vaccine Name</label>
                <input type="text" name="vaccin_name" class="edit-form-control"
                       value="{vaccin_name if vaccin_name else ''}">
              </div>
            </div>
            <div class="d-flex justify-content-end mt-3">
              <button type="submit" class="btn btn-update">
                <i class="fas fa-save me-1"></i> Save Changes
              </button>
            </div>
          </form>
        </div>
      </div>

      <div class="modal-footer view-modal-footer d-flex justify-content-between" id="viewFooter_{child_id}">
        <button type="button" class="btn btn-close-modal" data-bs-dismiss="modal">
          <i class="fas fa-times me-1"></i> Close
        </button>
        <a href="parent_manage_child.py?parent_id={parent_id}&action=delete&child_id={child_id}"
           class="btn btn-delete-modal"
           onclick="return confirm('Delete {child_name}? This cannot be undone.')">
          <i class="fas fa-trash-alt me-1"></i> Delete Child
        </a>
      </div>
    </div>
  </div>
</div>
""")

else:
    print("""
              <tr><td colspan="7">
                <div class="no-data">
                  <i class="fas fa-baby"></i>
                  <p>No children records found. Click <strong>Add New Child</strong> to get started.</p>
                </div>
              </td></tr>
    """)

print(f"""
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ADD CHILD MODAL -->
<div class="modal fade" id="addChildModal" tabindex="-1" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title"><i class="fas fa-baby me-2"></i> Add New Child</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <form method="POST" action="parent_manage_child.py?parent_id={parent_id}">
        <input type="hidden" name="parent_id" value="{parent_id}">
        <input type="hidden" name="action"    value="add">
        <div class="modal-body">
          <div class="section-title"><i class="fas fa-user-circle"></i> Parent Information</div>
          <div class="mb-3">
            <label class="form-label"><i class="fas fa-user me-1"></i> Parent Name</label>
            <input type="text" class="form-control" value="{parent_data.get('parent_name','')}" readonly>
            <div class="lock-note"><i class="fas fa-lock"></i> Auto-filled from your profile</div>
          </div>
          <div class="row mb-3">
            <div class="col-6">
              <label class="form-label">Parent Type</label>
              <input type="text" class="form-control" value="{parent_data.get('parent_type','')}" readonly>
            </div>
            <div class="col-6">
              <label class="form-label">Parent Gender</label>
              <input type="text" class="form-control" value="{parent_data.get('parent_gender','')}" readonly>
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label"><i class="fas fa-envelope me-1"></i> Email ID</label>
            <input type="text" class="form-control" value="{parent_data.get('email_id','')}" readonly>
          </div>
          <div class="section-title"><i class="fas fa-baby"></i> Child Information</div>
          <div class="mb-3">
            <label class="form-label">Child Name</label>
            <input type="text" name="child_name" class="form-control" placeholder="Enter child's full name" required>
          </div>
          <div class="row mb-3">
            <div class="col-6">
              <label class="form-label">Date of Birth</label>
              <input type="date" name="child_dob" class="form-control" required>
            </div>
            <div class="col-6">
              <label class="form-label">Gender</label>
              <select name="child_gender" class="form-select" required>
                <option value="">-- Select --</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
              </select>
            </div>
          </div>
          <div class="row mb-3">
            <div class="col-6">
              <label class="form-label"><i class="fas fa-syringe me-1"></i> Vaccinations Done</label>
              <input type="number" name="done_vaccin" class="form-control" value="0" min="0">
            </div>
            <div class="col-6">
              <label class="form-label"><i class="fas fa-calendar me-1"></i> Last Vaccine Date</label>
              <input type="date" name="last_vaccinedate" class="form-control">
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label">Age Group of Last Vaccine</label>
            <select class="form-select" name="vaccin_age">
              <option value="">--Select Age Group--</option>
              <option>At Birth</option><option>6 Weeks</option><option>10 Weeks</option>
              <option>14 Weeks</option><option>6 Months</option><option>9 Months</option>
              <option>12 Months</option><option>15 Months</option><option>18 Months</option>
              <option>2 Years</option><option>4-6 Years</option><option>10 Years</option>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label">Last Vaccine Name</label>
            <input type="text" name="vaccin_name" class="form-control" placeholder="e.g. BCG, Polio">
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-cancel" data-bs-dismiss="modal">
            <i class="fas fa-times me-1"></i> Cancel
          </button>
          <button type="submit" class="btn btn-confirm">
            <i class="fas fa-check me-1"></i> Add Child
          </button>
        </div>
      </form>
    </div>
  </div>
</div>
""")

for modal_html in view_modals:
    print(modal_html)

print(f"""
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
  function switchTab(btn, tabId, childId) {{
    const modal = btn.closest('.modal-content');
    modal.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    modal.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(tabId).classList.add('active');
    const footer = document.getElementById('viewFooter_' + childId);
    if (footer) footer.style.display = tabId.startsWith('editTab') ? 'none' : 'flex';
  }}
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
    const sb = document.getElementById('sidebar');
    const mt = document.querySelector('.mobile-menu-toggle');
    if (window.innerWidth < 992 && sb && mt &&
        !sb.contains(e.target) && !mt.contains(e.target) && sb.classList.contains('show'))
      closeSidebarMobile();
  }});
</script>
</body>
</html>
""")

con.close()