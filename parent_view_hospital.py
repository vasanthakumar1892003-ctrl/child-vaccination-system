#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgitb
import sys
import cgi
import json
from datetime import datetime

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")

try:
    con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
    cur = con.cursor()
except Exception as e:
    print("Content-Type: application/json\r\n\r\n")
    print(json.dumps({"error": str(e)}))
    sys.exit()

today     = datetime.now().strftime("%Y-%m-%d")
form      = cgi.FieldStorage()
parent_id = form.getvalue("parent_id", "").strip()
ajax      = form.getvalue("ajax",      "").strip()

# ────────────────────────────────────────────────────────────────────────────
# AJAX: send message
# ────────────────────────────────────────────────────────────────────────────
if ajax == "send":
    print("Content-Type: application/json\r\n\r\n")
    hospital_id = form.getvalue("hospital_id", "").strip()
    msg_text    = form.getvalue("message",     "").strip()
    try:
        hospital_name_reply = "Hospital"
        try:
            cur.execute("SELECT hospital_name FROM hospital WHERE id=%s", (hospital_id,))
            hrow = cur.fetchone()
            if hrow:
                hospital_name_reply = hrow[0]
        except:
            pass

        cur.execute(
            """SELECT COUNT(*) FROM chat_messages
               WHERE parent_id=%s AND hospital_id=%s AND sender_role='parent'""",
            (parent_id, hospital_id)
        )
        is_first = (cur.fetchone()[0] == 0)

        cur.execute(
            """INSERT INTO chat_messages (parent_id, hospital_id, sender_role, message, status)
               VALUES (%s, %s, 'parent', %s, 'sent')""",
            (parent_id, hospital_id, msg_text)
        )
        con.commit()
        cur.execute("SELECT LAST_INSERT_ID()")
        new_id = cur.fetchone()[0]

        auto_reply = None
        if is_first:
            auto_text = f"Hi! This is {hospital_name_reply}. How can I help you? \U0001f60a"
            cur.execute(
                """INSERT INTO chat_messages (parent_id, hospital_id, sender_role, message, status)
                   VALUES (%s, %s, 'hospital', %s, 'sent')""",
                (parent_id, hospital_id, auto_text)
            )
            con.commit()
            cur.execute("SELECT LAST_INSERT_ID()")
            ar_id = cur.fetchone()[0]
            cur.execute(
                "SELECT id, message, sender_role, sent_at FROM chat_messages WHERE id=%s",
                (ar_id,)
            )
            ar = cur.fetchone()
            if ar:
                auto_reply = {"id": ar[0], "message": ar[1],
                              "role": ar[2], "time": str(ar[3])}

        cur.execute(
            """SELECT id, message, sender_role, sent_at
               FROM chat_messages
               WHERE id=%s AND parent_id=%s AND hospital_id=%s""",
            (new_id, parent_id, hospital_id)
        )
        row = cur.fetchone()
        if row:
            print(json.dumps({
                "ok": True, "id": row[0], "message": row[1],
                "role": row[2], "time": str(row[3]),
                "auto_reply": auto_reply
            }))
        else:
            print(json.dumps({"error": "Message not found"}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
    con.close(); sys.exit()

# ────────────────────────────────────────────────────────────────────────────
# AJAX: load full chat history
# ────────────────────────────────────────────────────────────────────────────
if ajax == "load":
    print("Content-Type: application/json\r\n\r\n")
    hospital_id = form.getvalue("hospital_id", "").strip()
    try:
        cur.execute(
            """UPDATE chat_messages SET status='seen'
               WHERE parent_id=%s AND hospital_id=%s
                 AND sender_role='hospital' AND status='sent'""",
            (parent_id, hospital_id)
        )
        con.commit()
        cur.execute(
            """SELECT id, message, sender_role, sent_at
               FROM chat_messages
               WHERE parent_id=%s AND hospital_id=%s
               ORDER BY sent_at ASC""",
            (parent_id, hospital_id)
        )
        rows = cur.fetchall()
        msgs = [{"id": r[0], "message": r[1], "role": r[2], "time": str(r[3])} for r in rows]
        print(json.dumps({"ok": True, "messages": msgs}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
    con.close(); sys.exit()

# ────────────────────────────────────────────────────────────────────────────
# AJAX: poll new messages
# ────────────────────────────────────────────────────────────────────────────
if ajax == "poll":
    print("Content-Type: application/json\r\n\r\n")
    hospital_id = form.getvalue("hospital_id", "").strip()
    last_id     = form.getvalue("last_id",     "0").strip()
    try:
        cur.execute(
            """UPDATE chat_messages SET status='seen'
               WHERE parent_id=%s AND hospital_id=%s
                 AND sender_role='hospital' AND status='sent'""",
            (parent_id, hospital_id)
        )
        con.commit()
        cur.execute(
            """SELECT id, message, sender_role, sent_at
               FROM chat_messages
               WHERE parent_id=%s AND hospital_id=%s AND id>%s
               ORDER BY sent_at ASC""",
            (parent_id, hospital_id, last_id)
        )
        rows = cur.fetchall()
        msgs = [{"id": r[0], "message": r[1], "role": r[2], "time": str(r[3])} for r in rows]
        print(json.dumps({"ok": True, "messages": msgs}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
    con.close(); sys.exit()

# ────────────────────────────────────────────────────────────────────────────
# PAGE render
# ────────────────────────────────────────────────────────────────────────────
print("Content-Type: text/html\r\n\r\n")

# ── Fetch parent data from DB ─────────────────────────────────────────────────
parent_data = {}
if parent_id:
    try:
        cur.execute("""
            SELECT id, parent_type, parent_name, parent_gender, parent_dob,
                   parent_mobile, email_id, alternate_mobile, state, district,
                   city, pincode, street, area, id_type, id_number, child_order, status
            FROM parent WHERE id = %s
        """, (parent_id,))
        pr = cur.fetchone()
        if pr:
            parent_data = {
                "id"              : pr[0],
                "parent_type"     : pr[1]  or "",
                "parent_name"     : pr[2]  or "",
                "parent_gender"   : pr[3]  or "",
                "parent_dob"      : str(pr[4]) if pr[4] else "",
                "mobile"          : pr[5]  or "",
                "email_id"        : pr[6]  or "",
                "alternate_mobile": pr[7]  or "",
                "state"           : pr[8]  or "",
                "district"        : pr[9]  or "",
                "city"            : pr[10] or "",
                "pincode"         : pr[11] or "",
                "street"          : pr[12] or "",
                "area"            : pr[13] or "",
                "id_type"         : pr[14] or "",
                "id_number"       : pr[15] or "",
                "child_order"     : pr[16] or "",
                "status"          : pr[17] or "",
            }
            parent_name = parent_data["parent_name"]
        else:
            parent_name = "Parent"
    except Exception as ex:
        parent_data = {}
        parent_name = "Parent"
else:
    parent_name = "Parent"

# ── Fetch ALL children for this parent email ─────────────────────────────────
all_children = []
child_data   = {}
if parent_data.get("email_id"):
    try:
        cur.execute("""
            SELECT id, child_name, child_dob, child_gender,
                   done_vaccin, vaccin_age, vaccin_name, last_vaccinedate
            FROM manage_child
            WHERE email_id = %s
            ORDER BY id ASC
        """, (parent_data["email_id"],))
        for cr in cur.fetchall():
            all_children.append({
                "id"              : cr[0],
                "child_name"      : cr[1] or "",
                "child_dob"       : str(cr[2]) if cr[2] else "",
                "child_gender"    : cr[3] or "",
                "done_vaccin"     : str(cr[4]) if cr[4] is not None else "None",
                "vaccin_age"      : cr[5] or "None",
                "vaccin_name"     : cr[6] or "None",
                "last_vaccinedate": str(cr[7]) if cr[7] else "None",
            })
        if all_children:
            child_data = all_children[0]   # default: first child
    except:
        all_children = []
        child_data   = {}

# ── Build address string from parent data ────────────────────────────────────
address_parts = [
    parent_data.get("street", ""),
    parent_data.get("area", ""),
    parent_data.get("city", ""),
]
address_str = ", ".join(p for p in address_parts if p)

# ── Unread counts per hospital ────────────────────────────────────────────────
unread_by_hospital = {}
if parent_id:
    try:
        cur.execute(
            """SELECT hospital_id, COUNT(*)
               FROM chat_messages
               WHERE parent_id=%s AND sender_role='hospital' AND status='sent'
               GROUP BY hospital_id""",
            (parent_id,)
        )
        for hid, cnt in cur.fetchall():
            unread_by_hospital[int(hid)] = cnt
    except:
        pass

# ── Fetch approved hospitals ──────────────────────────────────────────────────
cur.execute("SELECT * FROM hospital WHERE status = 'approved'")
rows = cur.fetchall()

# ── Fetch vaccines from vaccination_schedule grouped by age_group ─────────────
vaccines_by_age = {}
try:
    cur.execute("SELECT age_group, vaccine_name FROM vaccination_schedule ORDER BY age_group, vaccine_name")
    for age_grp, vac_nm in cur.fetchall():
        vaccines_by_age.setdefault(age_grp, []).append(vac_nm)
except:
    vaccines_by_age = {}
vaccines_by_age_json = json.dumps(vaccines_by_age)

con.close()

# ── Helper: safe JS string ────────────────────────────────────────────────────
def js_str(s):
    return str(s or "").replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ").replace("\r", "")

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>View Hospital - Parent</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:linear-gradient(135deg,#052e16,#22c55e,#dcfce7); min-height:100vh; font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif; overflow-x:hidden; }}
.navbar {{ box-shadow:0 4px 20px rgba(0,0,0,0.4); padding:15px 20px; background:linear-gradient(135deg,#052e16,#22c55e,#dcfce7) !important; }}
.navbar .container-fluid {{ display:flex; flex-direction:row; align-items:center; flex-wrap:nowrap; }}
.navbar-brand {{ font-weight:600; color:white !important; letter-spacing:2px; text-transform:uppercase; }}
.navbar-brand i {{ margin-right:10px; color:#d1fae5; font-size:1.5rem; animation:bounce 2s infinite; }}
@keyframes bounce {{ 0%,100%{{transform:translateY(0);}} 50%{{transform:translateY(-5px);}} }}
.navbar-toggler-custom {{ display:none; flex-shrink:0; align-self:center; background:rgba(255,255,255,0.15); border:1.5px solid rgba(255,255,255,0.4); color:white; padding:6px 11px; border-radius:8px; font-size:1.15rem; cursor:pointer; line-height:1; transition:background 0.25s; order:-1; }}
.navbar-toggler-custom:hover {{ background:rgba(255,255,255,0.28); }}
.btn-logout {{ flex-shrink:0; background:linear-gradient(135deg,#ee0979 0%,#ff6a00 100%); border:none; padding:8px 20px; border-radius:25px; color:white; font-weight:600; box-shadow:0 4px 15px rgba(238,9,121,0.4); font-size:0.9rem; white-space:nowrap; transition:all 0.3s ease; }}
.btn-logout:hover {{ transform:translateY(-2px); color:white; }}
.sidebar {{ min-height:100vh; background:linear-gradient(135deg,#052e16,#22c55e); box-shadow:4px 0 20px rgba(0,0,0,0.3); padding:20px 0; }}
.sidebar-link {{ display:block; padding:14px 18px; color:#d1fae5; text-decoration:none; cursor:pointer; transition:all 0.3s ease; border-left:4px solid transparent; font-weight:500; margin:6px 0; }}
.sidebar-link:hover, .sidebar-link.active {{ background:linear-gradient(90deg,#22c55e,transparent 100%); color:#fff; border-left:4px solid #dcfce7; padding-left:24px; }}
.sidebar-link i {{ margin-right:12px; width:22px; text-align:center; }}
.sidebar-overlay {{ display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.6); z-index:998; backdrop-filter:blur(2px); }}
.sidebar-overlay.show {{ display:block; }}
.table-container {{ background:linear-gradient(135deg,#ffffff 0%,#f0fdf4 100%); border-radius:18px; padding:25px; box-shadow:0 10px 30px rgba(0,0,0,0.15); overflow-x:auto; border:1px solid rgba(16,185,129,0.2); margin:20px; }}
.page-title {{ color:#0f172a; font-weight:700; font-size:1.6rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:25px; padding-bottom:15px; border-bottom:3px solid #10b981; }}
.page-title i {{ margin-right:12px; color:#22c55e; }}
table {{ width:100%; border-collapse:separate; border-spacing:0; border-radius:12px; overflow:hidden; }}
table thead {{ background:linear-gradient(135deg,#052e16,#22c55e 70%); color:white; }}
table thead th {{ padding:14px; font-weight:600; text-transform:uppercase; letter-spacing:0.8px; font-size:0.85rem; white-space:nowrap; border:none; }}
table tbody tr {{ transition:all 0.3s ease; border-bottom:1px solid #d1fae5; background:white; }}
table tbody tr:hover {{ background:linear-gradient(90deg,#f0fdf4 0%,#d1fae5 100%); transform:scale(1.01); box-shadow:0 4px 12px rgba(16,185,129,0.15); }}
table tbody td {{ padding:14px; vertical-align:middle; font-size:0.9rem; color:#1e293b; }}
.btn-view {{ background:linear-gradient(135deg,#059669 0%,#10b981 100%); color:white; border:none; padding:8px 18px; border-radius:20px; font-weight:600; transition:all 0.3s ease; box-shadow:0 4px 10px rgba(16,185,129,0.3); font-size:0.85rem; }}
.btn-view:hover {{ transform:translateY(-2px); box-shadow:0 6px 15px rgba(16,185,129,0.5); color:white; }}

/* ── Chat button ── */
.btn-chat-wrap {{ position:relative; display:inline-flex; }}
.btn-chat {{ background:linear-gradient(135deg,#0891b2 0%,#22d3ee 100%); color:white; border:none; padding:8px 14px; border-radius:20px; font-weight:600; transition:all 0.3s ease; box-shadow:0 4px 10px rgba(8,145,178,0.3); font-size:0.85rem; display:inline-flex; align-items:center; gap:5px; cursor:pointer; }}
.btn-chat:hover {{ transform:translateY(-2px); box-shadow:0 6px 15px rgba(8,145,178,0.5); color:white; }}
.btn-chat.has-unread {{ background:linear-gradient(135deg,#dc2626 0%,#ef4444 100%); box-shadow:0 4px 10px rgba(239,68,68,0.4); animation:chat-pulse 1.5s infinite; }}
.btn-chat.has-unread:hover {{ box-shadow:0 6px 15px rgba(239,68,68,0.6); }}
@keyframes chat-pulse {{ 0%,100% {{ box-shadow:0 4px 10px rgba(239,68,68,0.4); }} 50% {{ box-shadow:0 4px 18px rgba(239,68,68,0.8); }} }}
.chat-notif-badge {{ position:absolute; top:-7px; right:-7px; background:#ef4444; color:#fff; border-radius:50%; min-width:20px; height:20px; font-size:0.65rem; font-weight:700; display:flex; align-items:center; justify-content:center; padding:0 4px; border:2px solid white; animation:badge-pop 1.5s infinite; box-shadow:0 2px 6px rgba(239,68,68,0.5); }}
@keyframes badge-pop {{ 0%,100% {{ transform:scale(1); }} 50% {{ transform:scale(1.2); }} }}
.icon-badge {{ background:linear-gradient(135deg,#083344,#22d3ee 60%); color:white; padding:5px 12px; border-radius:15px; font-weight:700; font-size:0.85rem; }}
mark.hl {{ background:#fef08a; color:#713f12; border-radius:3px; padding:1px 2px; font-weight:700; }}

/* ── Modal ── */
.modal-content {{ border-radius:18px; border:none; box-shadow:0 10px 40px rgba(0,0,0,0.3); }}
.reg-modal .modal-header {{ background:linear-gradient(135deg,#059669 0%,#10b981 100%); color:white; border-radius:18px 18px 0 0; padding:18px 25px; border:none; }}
.reg-modal .modal-header .modal-title {{ font-weight:700; font-size:1.3rem; letter-spacing:0.5px; }}
.reg-modal .modal-header .btn-close {{ filter:brightness(0) invert(1); opacity:0.8; }}
.reg-modal .modal-body {{ padding:30px; background:#f0fdf4; max-height:70vh; overflow-y:auto; }}
.reg-modal .modal-footer {{ border:none; padding:15px 25px; background:#f0fdf4; border-radius:0 0 18px 18px; }}

/* ── Form sections ── */
.form-section {{ background:white; padding:20px; border-radius:12px; margin-bottom:20px; border-left:4px solid #10b981; box-shadow:0 2px 8px rgba(0,0,0,0.05); }}
.form-section h5 {{ color:#059669; font-weight:700; margin-bottom:15px; font-size:1.1rem; }}
.form-section.appointment-section {{ border-left:4px solid #f59e0b; }}
.form-section.appointment-section h5 {{ color:#d97706; }}
.form-label {{ font-weight:600; color:#0f172a; margin-bottom:8px; font-size:0.9rem; }}
.form-label i {{ margin-right:6px; color:#10b981; width:18px; }}
.form-control, .form-select {{ border:2px solid #d1fae5; border-radius:10px; padding:10px 14px; font-size:0.9rem; transition:all 0.3s; }}
.form-control:focus, .form-select:focus {{ border-color:#10b981; box-shadow:0 0 0 4px rgba(16,185,129,0.1); }}

/* Readonly fields — clearly pre-filled, not editable */
.form-control[readonly], .form-control:disabled {{ 
  background:#e8f5e9; 
  color:#1b5e20; 
  font-weight:600;
  border:2px solid #a5d6a7;
  cursor:not-allowed;
}}
.readonly-note {{
  font-size:0.72rem; color:#6b7280; margin-top:3px; display:flex; align-items:center; gap:4px;
}}
.readonly-note i {{ color:#10b981; font-size:0.7rem; }}

/* Prefilled section header badge */
.prefilled-badge {{
  display:inline-block; background:#d1fae5; color:#065f46;
  font-size:0.72rem; font-weight:700; padding:2px 10px; border-radius:10px;
  margin-left:10px; vertical-align:middle; letter-spacing:.3px;
}}

/* Appointment section editable highlight */
.appt-input {{
  border:2px solid #fde68a !important;
  background:#fffbeb !important;
}}
.appt-input:focus {{
  border-color:#f59e0b !important;
  box-shadow:0 0 0 4px rgba(245,158,11,0.15) !important;
}}

/* Vaccination status info card */
.vac-status-card {{
  background:#f0fdf4; border:1.5px solid #a7f3d0; border-radius:10px;
  padding:14px 18px; margin-bottom:10px;
}}
.vac-status-row {{ display:flex; align-items:center; gap:10px; margin-bottom:8px; flex-wrap:wrap; }}
.vac-status-row:last-child {{ margin-bottom:0; }}
.vac-label {{ font-size:0.78rem; font-weight:700; color:#6b7280; text-transform:uppercase; letter-spacing:.4px; min-width:140px; }}
.vac-value {{ font-size:0.9rem; font-weight:600; color:#1e293b; }}
.vac-value.none-val {{ color:#94a3b8; font-style:italic; }}
.vac-done-badge {{ background:#d1fae5; color:#065f46; padding:3px 12px; border-radius:12px; font-size:0.82rem; font-weight:700; border:1px solid #6ee7b7; }}

/* Editable child fields */
.child-select {{
  border:2px solid #bfdbfe !important; background:#eff6ff !important;
  color:#1e3a8a !important; font-weight:600; border-radius:10px;
  padding:10px 14px; font-size:0.9rem; width:100%;
  transition:all 0.3s; cursor:pointer;
}}
.child-select:focus {{
  border-color:#3b82f6 !important; box-shadow:0 0 0 4px rgba(59,130,246,0.15) !important; outline:none;
}}
.editable-note {{
  font-size:0.72rem; color:#3b82f6; margin-top:3px; display:flex; align-items:center; gap:4px;
}}
.editable-note i {{ color:#3b82f6; font-size:0.7rem; }}

/* Filter bar */
.filter-bar {{ background:linear-gradient(135deg,#ecfdf5,#d1fae5); border:1.5px solid #6ee7b7; border-radius:14px; padding:16px 20px; margin-bottom:22px; display:flex; align-items:center; gap:12px; flex-wrap:wrap; box-shadow:0 3px 12px rgba(16,185,129,0.12); }}
.search-icon-wrap {{ background:linear-gradient(135deg,#052e16,#22c55e); color:white; width:42px; height:42px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:1.1rem; flex-shrink:0; }}
.filter-input-wrap {{ position:relative; flex:1; min-width:180px; }}
.filter-input-wrap i {{ position:absolute; left:12px; top:50%; transform:translateY(-50%); color:#10b981; font-size:0.9rem; pointer-events:none; }}
.filter-input {{ width:100%; padding:9px 12px 9px 36px; border:2px solid #a7f3d0; border-radius:10px; font-size:0.88rem; background:white; color:#0f172a; transition:all 0.25s; outline:none; }}
.filter-input:focus {{ border-color:#10b981; box-shadow:0 0 0 3px rgba(16,185,129,0.15); }}
.filter-input::placeholder {{ color:#94a3b8; }}
.filter-divider {{ width:1px; height:36px; background:#6ee7b7; flex-shrink:0; }}
.result-count {{ font-size:0.82rem; background:linear-gradient(135deg,#059669,#10b981); color:white; padding:5px 14px; border-radius:20px; font-weight:600; white-space:nowrap; }}
.btn-clear-filter {{ background:linear-gradient(135deg,#dc2626,#ef4444); color:white; border:none; padding:9px 16px; border-radius:10px; font-weight:600; font-size:0.83rem; cursor:pointer; transition:all 0.25s; white-space:nowrap; display:flex; align-items:center; gap:6px; }}
.btn-clear-filter:hover {{ transform:translateY(-1px); }}

/* Hospital info card */
.hospital-info {{ background:linear-gradient(135deg,#dbeafe 0%,#bfdbfe 100%); border-left:5px solid #3b82f6; border-radius:12px; padding:15px; margin-bottom:20px; }}
.hospital-info h6 {{ color:#1e3a8a; font-weight:700; margin-bottom:8px; }}
.hospital-info p {{ color:#1e40af; margin:4px 0; font-size:0.9rem; }}

.btn-submit {{ background:linear-gradient(135deg,#052e16,#22c55e 70%); color:white; border:none; padding:12px 35px; border-radius:25px; font-weight:700; transition:all 0.3s; box-shadow:0 6px 15px rgba(16,185,129,0.3); font-size:1rem; text-transform:uppercase; letter-spacing:1px; }}
.btn-submit:hover {{ transform:translateY(-3px); color:white; }}
.btn-cancel {{ background:linear-gradient(135deg,#6c757d 0%,#adb5bd 100%); color:white; border:none; padding:12px 35px; border-radius:25px; font-weight:700; transition:all 0.3s; font-size:1rem; }}
.btn-cancel:hover {{ transform:translateY(-3px); color:white; }}
.no-data {{ text-align:center; padding:40px 20px; color:#64748b; }}

/* ── Chat modal ── */
#chatModal .modal-header {{ background:linear-gradient(135deg,#083344,#0891b2); border-radius:18px 18px 0 0; padding:14px 20px; border:none; display:flex; align-items:center; gap:10px; }}
#chatModal .modal-header .btn-close {{ filter:brightness(0) invert(1); margin-left:auto; }}
#chatModal .chat-avatar {{ width:42px; height:42px; border-radius:50%; background:linear-gradient(135deg,#0891b2,#67e8f9); display:flex; align-items:center; justify-content:center; color:#fff; font-size:1.1rem; font-weight:700; flex-shrink:0; }}
#chatModal .chat-head-info h6 {{ margin:0; font-weight:700; font-size:0.95rem; color:#fff; }}
#chatModal .chat-head-info small {{ color:rgba(255,255,255,0.8); font-size:0.75rem; }}
.chat-modal-body {{ display:flex; flex-direction:column; height:480px; padding:0 !important; }}
.chat-messages {{ flex:1; overflow-y:auto; padding:16px 18px; background:#f8fafc; }}
.chat-input-bar {{ padding:10px 14px; border-top:1px solid #e2e8f0; background:#fff; display:flex; align-items:flex-end; gap:9px; flex-shrink:0; }}
.chat-input-bar textarea {{ flex:1; resize:none; border:1.5px solid #cbd5e1; border-radius:22px; padding:9px 15px; font-size:0.88rem; outline:none; max-height:100px; min-height:42px; line-height:1.45; font-family:inherit; transition:0.2s; background:#f8fafc; }}
.chat-input-bar textarea:focus {{ border-color:#0891b2; box-shadow:0 0 0 3px rgba(8,145,178,0.12); background:#fff; }}
.btn-send-chat {{ width:42px; height:42px; border-radius:50%; border:none; background:linear-gradient(135deg,#0369a1,#0891b2); color:#fff; font-size:0.95rem; cursor:pointer; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 12px rgba(8,145,178,0.4); transition:0.2s; flex-shrink:0; }}
.btn-send-chat:hover {{ transform:scale(1.08); }}
.btn-send-chat:disabled {{ opacity:0.5; cursor:not-allowed; transform:none; }}
.bubble-row {{ display:flex; margin-bottom:10px; align-items:flex-end; gap:6px; }}
.bubble-row.mine   {{ justify-content:flex-end; }}
.bubble-row.theirs {{ justify-content:flex-start; }}
.bubble-wrap {{ display:flex; flex-direction:column; max-width:70%; }}
.bubble-row.mine   .bubble-wrap {{ align-items:flex-end; }}
.bubble-row.theirs .bubble-wrap {{ align-items:flex-start; }}
.sender-label {{ font-size:0.68rem; color:#64748b; margin-bottom:2px; font-weight:600; }}
.bubble {{ padding:9px 13px; border-radius:18px; font-size:0.88rem; line-height:1.5; word-break:break-word; }}
.bubble.mine   {{ background:linear-gradient(135deg,#0369a1,#0891b2); color:#fff; border-bottom-right-radius:4px; box-shadow:0 2px 8px rgba(8,145,178,0.3); }}
.bubble.theirs {{ background:#fff; color:#1e293b; border-bottom-left-radius:4px; box-shadow:0 1px 6px rgba(0,0,0,0.08); border:1px solid #e2e8f0; }}
.bubble.auto-reply {{ background:linear-gradient(135deg,#0d9488,#14b8a6); color:#fff; border-bottom-left-radius:4px; box-shadow:0 2px 8px rgba(20,184,166,0.35); border-left:3px solid #5eead4; }}
.bubble-time {{ font-size:0.65rem; margin-top:4px; display:block; }}
.bubble.mine        .bubble-time {{ text-align:right; color:rgba(255,255,255,0.85); }}
.bubble.theirs      .bubble-time {{ text-align:left; color:#94a3b8; }}
.bubble.auto-reply  .bubble-time {{ text-align:left; color:rgba(255,255,255,0.8); }}
.date-divider {{ text-align:center; margin:10px 0; }}
.date-divider span {{ background:#e2e8f0; color:#64748b; font-size:0.7rem; padding:3px 14px; border-radius:20px; font-weight:500; }}
.chat-empty-hint {{ text-align:center; padding:40px 20px; color:#94a3b8; font-size:0.85rem; }}
.chat-empty-hint i {{ font-size:2.5rem; display:block; margin-bottom:8px; opacity:0.25; }}
.chat-messages::-webkit-scrollbar {{ width:4px; }}
.chat-messages::-webkit-scrollbar-thumb {{ background:#cbd5e1; border-radius:4px; }}
.typing-indicator {{ display:flex; align-items:center; gap:6px; padding:8px 14px; background:#f1f5f9; border-radius:18px; border-bottom-left-radius:4px; width:fit-content; margin-bottom:10px; box-shadow:0 1px 4px rgba(0,0,0,0.08); }}
.typing-indicator span {{ width:7px; height:7px; border-radius:50%; background:#94a3b8; display:inline-block; animation:typingDot 1.2s infinite; }}
.typing-indicator span:nth-child(2) {{ animation-delay:0.2s; }}
.typing-indicator span:nth-child(3) {{ animation-delay:0.4s; }}
@keyframes typingDot {{ 0%,60%,100% {{ transform:translateY(0); opacity:0.5; }} 30% {{ transform:translateY(-5px); opacity:1; }} }}

@media (max-width:991.98px) {{
  .navbar-toggler-custom {{ display:flex; align-items:center; justify-content:center; }}
  .sidebar {{ position:fixed; left:-100%; top:0; width:280px; height:100vh; z-index:999; transition:left 0.3s ease; overflow-y:auto; }}
  .sidebar.show {{ left:0; }}
  .table-container {{ margin:10px; padding:15px; }}
}}
@media (max-width:767.98px) {{
  table thead th {{ font-size:0.75rem; padding:10px 6px; }}
  table tbody td {{ font-size:0.8rem; padding:10px 6px; }}
  .filter-bar {{ flex-direction:column; align-items:stretch; }}
  .filter-divider {{ display:none; }}
  .filter-input-wrap {{ min-width:100%; }}
  .btn-logout {{ padding:6px 16px; font-size:0.85rem; }}
  .chat-modal-body {{ height:400px; }}
  .vac-status-row {{ flex-direction:column; align-items:flex-start; gap:4px; }}
}}
@media (max-width:575.98px) {{
  .navbar-brand {{ font-size:0.85rem; letter-spacing:0.5px; }}
  .navbar-brand i {{ font-size:1.1rem; margin-right:6px; }}
  .btn-logout {{ padding:6px 14px; font-size:0.8rem; }}
}}
</style>
</head>
<body>
""")

print(f"""
<nav class="navbar navbar-dark">
  <div class="container-fluid">
    <button class="navbar-toggler-custom" id="sidebarToggleBtn" onclick="toggleSidebar()"><i class="fas fa-bars"></i></button>
    <span class="navbar-brand"><i class="fa-solid fa-users"></i> CVS - Parent</span>
    <button class="btn-logout" onclick="doLogout()"><i class="fas fa-sign-out-alt"></i> Logout</button>
  </div>
</nav>
<div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>
<div class="container-fluid">
  <div class="row">
    <div class="col-lg-2 col-md-3 sidebar p-0" id="sidebar">
      <a href="parent_dashboard.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-home"></i> Home</a>
      <a href="parent_vaccination.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fa-solid fa-circle-info"></i> Vaccination Info</a>
      <a href="parent_manage_child.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-baby"></i> Manage Children</a>
      <a href="parent_view_hospital.py?parent_id={parent_id}" class="sidebar-link active" onclick="closeSidebarMobile()"><i class="fa-solid fa-eye"></i> View Hospital</a>
      <a href="parent_booked_appointment.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fa-solid fa-calendar-day"></i> Booked Appointments
      </a>
      <a href="parent_my_appointment.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-calendar-check"></i> My Appointments</a>
      <a href="parent_reminder.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-bell"></i> My Reminders</a>
      <a href="parent_profile.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-user-circle"></i> My Profile</a>
      <a href="parent_feedback.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()"><i class="fas fa-comment-dots"></i> Feedback</a>
      <a href="parent_help.py?parent_id={parent_id}" class="sidebar-link"><i class="fas fa-circle-question"></i> Help &amp; Support</a>
    </div>
    <div class="col-lg-10 col-md-9 col-12">
      <div class="table-container">
        <h2 class="page-title"><i class="fa-solid fa-house-medical-circle-check"></i> Approved Hospital Registrations</h2>
        <div class="filter-bar">
          <div class="search-icon-wrap"><i class="fas fa-search"></i></div>
          <div class="filter-input-wrap"><i class="fas fa-hospital"></i><input type="text" id="filterName" class="filter-input" placeholder="Search by Hospital Name..." oninput="applyFilters()"></div>
          <div class="filter-divider"></div>
          <div class="filter-input-wrap"><i class="fas fa-map-marker-alt"></i><input type="text" id="filterDistrict" class="filter-input" placeholder="Search by District..." oninput="applyFilters()"></div>
          <div class="filter-divider"></div>
          <div class="filter-input-wrap"><i class="fas fa-location-dot"></i><input type="text" id="filterArea" class="filter-input" placeholder="Search by Area..." oninput="applyFilters()"></div>
          <div class="filter-divider"></div>
          <span class="result-count" id="resultCount">0 Results</span>
          <button class="btn-clear-filter" onclick="clearFilters()"><i class="fas fa-times"></i> Clear</button>
        </div>
        <table>
          <thead>
            <tr>
              <th><i class="fas fa-hashtag"></i> No</th>
              <th><i class="fas fa-hospital"></i> Hospital Name</th>
              <th><i class="fas fa-building"></i> Type</th>
              <th><i class="fas fa-map-marker-alt"></i> District</th>
              <th><i class="fas fa-location-dot"></i> Area</th>
              <th><i class="fas fa-envelope"></i> Email</th>
              <th><i class="fas fa-phone"></i> Mobile</th>
              <th style="text-align:center;"><i class="fas fa-cogs"></i> Actions</th>
            </tr>
          </thead>
          <tbody id="hospitalTableBody">
""")

modals_html = []
children_js_json = json.dumps({})   # safe default if no hospital rows

if not rows:
    print("""<tr><td colspan='8' class='no-data'>
      <i class="fas fa-inbox" style="font-size:3rem;color:#ccc;margin-bottom:15px;display:block;"></i>No Hospital Found...!
    </td></tr>""")
else:
    # ── Pre-compute safe values for the form (fetched from DB) ────────────────
    p_name    = parent_data.get("parent_name", "")
    p_type    = parent_data.get("parent_type", "")
    p_gender  = parent_data.get("parent_gender", "")
    p_mobile  = parent_data.get("mobile", "")
    p_email   = parent_data.get("email_id", "")
    p_aadhaar = parent_data.get("id_number", "")
    p_dist    = parent_data.get("district", "")
    p_pin     = parent_data.get("pincode", "")
    p_order   = str(parent_data.get("child_order", ""))

    c_name    = child_data.get("child_name", "")
    c_dob     = child_data.get("child_dob", "")
    c_gender  = child_data.get("child_gender", "")
    c_order   = p_order

    dv        = child_data.get("done_vaccin",      "None")
    v_age     = child_data.get("vaccin_age",       "None")
    v_name    = child_data.get("vaccin_name",      "None")
    v_last    = child_data.get("last_vaccinedate", "None")

    # Display helper: blank → "None"
    def disp(v):
        s = str(v).strip() if v is not None else ""
        return s if s and s.lower() not in ("", "none", "null") else "None"

    dv_disp    = disp(dv)
    v_age_disp = disp(v_age)
    v_nm_disp  = disp(v_name)
    v_last_disp= disp(v_last)

    # Child order display
    order_map = {"1":"First Child","2":"Second Child","3":"Third Child","4":"Fourth Child","5":"Fifth Child"}

    # ── Build child name <option> list (all children of this parent) ──────────
    child_name_options_html = ""
    for ch in all_children:
        sel = 'selected' if ch["child_name"] == c_name else ''
        child_name_options_html += f'<option value="{ch["child_name"]}" {sel}>{ch["child_name"]}</option>\n'

    # ── Build all_children JS map: child_name → {dob, gender, done_vaccin, vaccin_age, vaccin_name, last_vaccinedate} ─
    children_js_map = {}
    for ch in all_children:
        children_js_map[ch["child_name"]] = {
            "dob"       : ch["child_dob"],
            "gender"    : ch["child_gender"],
            "done_vaccin"     : ch["done_vaccin"],
            "vaccin_age"      : ch["vaccin_age"],
            "vaccin_name"     : ch["vaccin_name"],
            "last_vaccinedate": ch["last_vaccinedate"],
        }
    children_js_json = json.dumps(children_js_map)
    c_order_disp = order_map.get(str(c_order), c_order) if c_order else "None"

    row_num = 0
    for i in rows:
        row_num += 1
        uid = row_num

        def val(idx):
            return str(i[idx]) if len(i) > idx and i[idx] else "N/A"

        hospital_name  = val(1)
        hospital_type  = val(2)
        email_id       = val(7)
        mobile_number  = val(8)
        district       = val(11)
        area           = val(15)
        hospital_db_id = i[0]
        hosp_initial   = hospital_name[0].upper() if hospital_name and hospital_name != "N/A" else "H"
        hosp_name_js   = js_str(hospital_name)

        unread = unread_by_hospital.get(int(hospital_db_id), 0)
        unread_cls   = "has-unread" if unread else ""
        unread_badge = f'<span class="chat-notif-badge">{unread}</span>' if unread else ""

        print(f"""
          <tr class="hospital-row" data-name="{hospital_name.lower()}" data-district="{district.lower()}" data-area="{area.lower()}">
            <td><span class="icon-badge row-num">{uid}</span></td>
            <td class="cell-name"><strong>{hospital_name}</strong></td>
            <td>{hospital_type}</td>
            <td class="cell-district">{district}</td>
            <td class="cell-area">{area}</td>
            <td>{email_id}</td>
            <td>{mobile_number}</td>
            <td style="white-space:nowrap; text-align:center;">
              <button type="button" class="btn btn-view" data-bs-toggle="modal" data-bs-target="#registrationModal{uid}">
                <i class="fas fa-user-plus"></i> Apply
              </button>
              <span class="btn-chat-wrap ms-1" id="chatWrap_{hospital_db_id}">
                <button type="button" class="btn-chat {unread_cls}"
                  id="chatBtn_{hospital_db_id}"
                  onclick="openChatModal({hospital_db_id}, '{hosp_name_js}', '{hosp_initial}')"
                  title="Chat with {hospital_name}">
                  <i class="fas fa-comments"></i> Chat
                </button>
                {unread_badge}
              </span>
            </td>
          </tr>
        """)

        # ── Vaccination status HTML block ─────────────────────────────────────
        vac_status_html = f"""
          <div class="vac-status-card" id="vacCard_{uid}">
            <div class="vac-status-row">
              <span class="vac-label"><i class="fas fa-check-circle me-1" style="color:#059669;"></i> Vaccinations Done</span>
              <span class="vac-value">
                {'<span class="vac-done-badge">' + dv_disp + ' Done</span>' if dv_disp != 'None' else '<span class="none-val">None</span>'}
              </span>
            </div>
            <div class="vac-status-row">
              <span class="vac-label"><i class="fas fa-layer-group me-1" style="color:#0891b2;"></i> Last Vaccine Age Group</span>
              <span class="vac-value {'none-val' if v_age_disp == 'None' else ''}">{v_age_disp}</span>
            </div>
            <div class="vac-status-row">
              <span class="vac-label"><i class="fas fa-syringe me-1" style="color:#7c3aed;"></i> Last Vaccine Name</span>
              <span class="vac-value {'none-val' if v_nm_disp == 'None' else ''}">{v_nm_disp}</span>
            </div>
            <div class="vac-status-row">
              <span class="vac-label"><i class="fas fa-calendar-alt me-1" style="color:#d97706;"></i> Last Vaccine Date</span>
              <span class="vac-value {'none-val' if v_last_disp == 'None' else ''}">{v_last_disp}</span>
            </div>
          </div>
          <div class="readonly-note"><i class="fas fa-lock"></i> Fetched from your child's vaccination records</div>
        """

        modals_html.append(f"""
        <div class="modal fade reg-modal" id="registrationModal{uid}" tabindex="-1" aria-hidden="true">
          <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title"><i class="fas fa-user-plus"></i> Parent Registration Form</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
              </div>
              <div class="modal-body">

                <!-- Hospital info -->
                <div class="hospital-info">
                  <h6><i class="fas fa-hospital"></i> Selected Hospital Information</h6>
                  <p><strong>Hospital Name:</strong> {hospital_name}</p>
                  <p><strong>Type:</strong> {hospital_type} &nbsp;|&nbsp; <strong>District:</strong> {district} &nbsp;|&nbsp; <strong>Area:</strong> {area}</p>
                </div>

                <form id="parentRegistrationForm{uid}" method="post"
                      action="process_parent_registration.py?parent_id={parent_id}">
                  <input type="hidden" name="hospital_name" value="{hospital_name}">
                  <input type="hidden" name="parent_id"     value="{parent_id}">

                  <!-- ══ PARENT INFORMATION (pre-filled, readonly) ══ -->
                  <div class="form-section">
                    <h5>
                      <i class="fas fa-user me-2"></i> Parent Information
                      <span class="prefilled-badge"><i class="fas fa-database me-1"></i>Auto-filled from your profile</span>
                    </h5>
                    <div class="row">
                      <div class="col-md-6 mb-3">
                        <label class="form-label"><i class="fas fa-user"></i> Parent Name</label>
                        <input type="text" class="form-control" name="p_name" value="{p_name}" readonly>
                        <div class="readonly-note"><i class="fas fa-lock"></i> From your profile</div>
                      </div>
                      <div class="col-md-6 mb-3">
                        <label class="form-label"><i class="fas fa-user-tag"></i> Parent Type</label>
                        <input type="text" class="form-control" name="p_type" value="{p_type}" readonly>
                        <div class="readonly-note"><i class="fas fa-lock"></i> From your profile</div>
                      </div>
                    </div>
                    <div class="row">
                      <div class="col-md-6 mb-3">
                        <label class="form-label"><i class="fa-solid fa-users"></i> Gender</label>
                        <input type="text" class="form-control" name="p_gender" value="{p_gender}" readonly>
                        <div class="readonly-note"><i class="fas fa-lock"></i> From your profile</div>
                      </div>
                      <div class="col-md-6 mb-3">
                        <label class="form-label"><i class="fas fa-phone"></i> Mobile Number</label>
                        <input type="text" class="form-control" name="mobile" value="{p_mobile}" readonly>
                        <div class="readonly-note"><i class="fas fa-lock"></i> From your profile</div>
                      </div>
                    </div>
                    <div class="row">
                      <div class="col-md-6 mb-3">
                        <label class="form-label"><i class="fas fa-envelope"></i> Email Address</label>
                        <input type="text" class="form-control" name="email" value="{p_email}" readonly>
                        <div class="readonly-note"><i class="fas fa-lock"></i> From your profile</div>
                      </div>
                      <div class="col-md-6 mb-3">
                        <label class="form-label"><i class="fas fa-id-card"></i> Aadhaar / ID Number</label>
                        <input type="text" class="form-control" name="aadhaar_number" value="{p_aadhaar}" readonly>
                        <div class="readonly-note"><i class="fas fa-lock"></i> From your profile</div>
                      </div>
                    </div>
                  </div>

                  <!-- ══ CHILD INFORMATION (child name & order editable) ══ -->
                  <div class="form-section">
                    <h5>
                      <i class="fas fa-baby me-2"></i> Child Information
                      <span class="prefilled-badge"><i class="fas fa-database me-1"></i>Auto-filled from child records</span>
                    </h5>
                    <div class="row">
                      <div class="col-md-6 mb-3">
                        <label class="form-label"><i class="fas fa-baby"></i> Child Name <span style="color:red;">*</span></label>
                        <select class="child-select" name="c_name" id="childSelect_{uid}" onchange="onChildChange({uid}, this.value)" required>
                          <option value="">-- Select Child --</option>
                          {child_name_options_html}
                        </select>
                        <div class="editable-note"><i class="fas fa-pen"></i> Select your child</div>
                      </div>
                      <div class="col-md-6 mb-3">
                        <label class="form-label"><i class="fa-solid fa-user-group"></i> Gender</label>
                        <input type="text" class="form-control" name="c_gender" id="childGender_{uid}" value="{c_gender}" readonly>
                        <div class="readonly-note"><i class="fas fa-lock"></i> Auto-filled on child selection</div>
                      </div>
                    </div>
                    <div class="row">
                      <div class="col-md-6 mb-3">
                        <label class="form-label"><i class="fas fa-birthday-cake"></i> Child Date of Birth</label>
                        <input type="text" class="form-control" name="c_dob" id="childDob_{uid}" value="{c_dob}" readonly>
                        <div class="readonly-note"><i class="fas fa-lock"></i> Auto-filled on child selection</div>
                      </div>
                      <div class="col-md-6 mb-3">
                        <label class="form-label"><i class="fas fa-sort-numeric-up"></i> Child Order <span style="color:red;">*</span></label>
                        <select class="child-select" name="c_order" id="childOrder_{uid}" required>
                          <option value="">-- Select Order --</option>
                          <option value="1">First Child</option>
                          <option value="2">Second Child</option>
                          <option value="3">Third Child</option>
                          <option value="4">Fourth Child</option>
                          <option value="5">Fifth Child</option>
                        </select>
                        <div class="editable-note"><i class="fas fa-pen"></i> Select child order</div>
                      </div>
                    </div>
                  </div>

                  <!-- ══ VACCINATION STATUS (read-only display from DB) ══ -->
                  <div class="form-section">
                    <h5>
                      <i class="fas fa-syringe me-2"></i> Vaccination Status
                      <span class="prefilled-badge"><i class="fas fa-database me-1"></i>Auto-filled from vaccination records</span>
                    </h5>
                    {vac_status_html}
                    <!-- Hidden fields to submit vaccination data -->
                    <input type="hidden" id="hDoneVaccin_{uid}"      name="done_vaccin"      value="{dv if dv != 'None' else ''}">
                    <input type="hidden" id="hVaccinAge_{uid}"       name="vaccin_age"       value="{v_age if v_age != 'None' else ''}">
                    <input type="hidden" id="hVaccinName_{uid}"      name="vaccin_name"      value="{v_name if v_name != 'None' else ''}">
                    <input type="hidden" id="hLastVaccinedate_{uid}" name="last_vaccinedate" value="{v_last if v_last != 'None' else ''}">
                  </div>

                  <!-- ══ ADDRESS INFORMATION (pre-filled, readonly) ══ -->
                  <div class="form-section">
                    <h5>
                      <i class="fas fa-map-marked-alt me-2"></i> Address Information
                      <span class="prefilled-badge"><i class="fas fa-database me-1"></i>Auto-filled from your profile</span>
                    </h5>
                    <div class="row">
                      <div class="col-md-12 mb-3">
                        <label class="form-label"><i class="fas fa-home"></i> Address</label>
                        <input type="text" class="form-control" name="address" value="{address_str}" readonly>
                        <div class="readonly-note"><i class="fas fa-lock"></i> From your profile</div>
                      </div>
                    </div>
                    <div class="row">
                      <div class="col-md-6 mb-3">
                        <label class="form-label"><i class="fas fa-map-marker-alt"></i> District</label>
                        <input type="text" class="form-control" name="district" value="{p_dist}" readonly>
                        <div class="readonly-note"><i class="fas fa-lock"></i> From your profile</div>
                      </div>
                      <div class="col-md-6 mb-3">
                        <label class="form-label"><i class="fas fa-mail-bulk"></i> Pin Code</label>
                        <input type="text" class="form-control" name="pincode" value="{p_pin}" readonly>
                        <div class="readonly-note"><i class="fas fa-lock"></i> From your profile</div>
                      </div>
                    </div>
                  </div>

                  <!-- ══ APPOINTMENT INFORMATION (editable by parent) ══ -->
                  <div class="form-section appointment-section">
                    <h5>
                      <i class="fas fa-calendar-check me-2"></i> Appointment Information
                      <span class="prefilled-badge" style="background:#fef3c7;color:#92400e;">
                        <i class="fas fa-pen me-1"></i>Fill in below
                      </span>
                    </h5>
                    <p style="font-size:0.82rem;color:#92400e;margin-bottom:14px;">
                      <i class="fas fa-info-circle me-1"></i>
                      Please fill in your appointment details below.
                    </p>
                    <div class="row">
                      <div class="col-md-6 mb-3">
                        <label class="form-label" style="color:#d97706;"><i class="fas fa-calendar-alt" style="color:#f59e0b;"></i> Appointment Date <span style="color:red;">*</span></label>
                        <input type="date" class="form-control appt-input" name="appointment_date" required min="{today}">
                      </div>
                      <div class="col-md-6 mb-3">
                        <label class="form-label" style="color:#d97706;"><i class="fas fa-arrow-down-short-wide" style="color:#f59e0b;"></i> Age Group <span style="color:red;">*</span></label>
                        <select class="form-select appt-input" name="age_group" id="ageGroupSel_{uid}" onchange="filterVaccines({uid}, this.value)" required>
                          <option value="">-- Select Age Group --</option>
                          <option>At Birth</option><option>6 Weeks</option><option>10 Weeks</option>
                          <option>14 Weeks</option><option>6 Months</option><option>9 Months</option>
                          <option>12 Months</option><option>15 Months</option><option>18 Months</option>
                          <option>2 Years</option><option>4-6 Years</option><option>10 Years</option>
                        </select>
                      </div>
                    </div>
                    <div class="row">
                      <div class="col-md-12 mb-3">
                        <label class="form-label" style="color:#d97706;"><i class="fas fa-syringe" style="color:#f59e0b;"></i> Vaccine Name <span style="color:red;">*</span></label>
                        <select class="form-select appt-input" name="vaccine_name" id="vaccineSel_{uid}" required>
                          <option value="">-- Select Age Group first --</option>
                        </select>
                        <div style="font-size:0.72rem;color:#92400e;margin-top:3px;display:flex;align-items:center;gap:4px;">
                          <i class="fas fa-info-circle"></i> Vaccines update based on selected age group
                        </div>
                      </div>
                    </div>
                  </div>

                </form>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-cancel" data-bs-dismiss="modal"><i class="fas fa-times"></i> Cancel</button>
                <button type="submit" form="parentRegistrationForm{uid}" class="btn btn-submit"><i class="fas fa-paper-plane"></i> Submit Registration</button>
              </div>
            </div>
          </div>
        </div>
        """)

print("""
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
""")

for modal in modals_html:
    print(modal)

# ── Chat modal ────────────────────────────────────────────────────────────────
print(f"""
<div class="modal fade" id="chatModal" tabindex="-1" aria-hidden="true">
  <div class="modal-dialog modal-lg modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <div class="chat-avatar" id="chatAvatar">H</div>
        <div class="chat-head-info ms-2">
          <h6 id="chatHospName">Hospital</h6>
          <small><i class="fa fa-circle text-success me-1" style="font-size:.55rem;"></i>Online</small>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="chat-modal-body modal-body">
        <div class="chat-messages" id="chatMessages">
          <div class="chat-empty-hint"><i class="fas fa-comments"></i> Loading messages...</div>
        </div>
        <div class="chat-input-bar">
          <textarea id="chatInput" rows="1" placeholder="Type a message…"
                    onkeydown="chatHandleKey(event)" oninput="chatAutoResize(this)"></textarea>
          <button class="btn-send-chat" id="chatSendBtn" onclick="chatSend()">
            <i class="fas fa-paper-plane"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
var PARENT_ID   = "{parent_id}";
var PARENT_NAME = {json.dumps(parent_name)};
var CHILDREN_MAP  = {children_js_json};
var VACCINES_BY_AGE = {vaccines_by_age_json};

// ── Filter vaccine dropdown based on selected age group ───────────────────────
function filterVaccines(uid, ageGroup) {{
  var sel = document.getElementById('vaccineSel_' + uid);
  if (!sel) return;
  sel.innerHTML = '';
  if (!ageGroup || !VACCINES_BY_AGE[ageGroup] || !VACCINES_BY_AGE[ageGroup].length) {{
    sel.innerHTML = '<option value="">-- No vaccines found for this age group --</option>';
    return;
  }}
  var defOpt = document.createElement('option');
  defOpt.value = ''; defOpt.textContent = '-- Select Vaccine --';
  sel.appendChild(defOpt);
  VACCINES_BY_AGE[ageGroup].forEach(function(vname) {{
    var opt = document.createElement('option');
    opt.value = vname; opt.textContent = vname;
    sel.appendChild(opt);
  }});
}}

// ── Update child details when a child is selected from dropdown ───────────────
function onChildChange(uid, childName) {{
  var ch = CHILDREN_MAP[childName];
  if (!ch) return;

  // Update readonly fields
  var dobEl    = document.getElementById('childDob_'    + uid);
  var genderEl = document.getElementById('childGender_' + uid);
  if (dobEl)    dobEl.value    = ch.dob    || '';
  if (genderEl) genderEl.value = ch.gender || '';

  // Update vaccination status display + hidden fields
  var vCard = document.getElementById('vacCard_' + uid);
  if (vCard) {{
    var def = function(v) {{ return (v && v !== 'None' && v !== 'null' && v.trim() !== '') ? v : null; }};
    var dv   = def(ch.done_vaccin);
    var vage = def(ch.vaccin_age);
    var vnm  = def(ch.vaccin_name);
    var vlst = def(ch.last_vaccinedate);

    vCard.innerHTML =
      '<div class="vac-status-row">' +
        '<span class="vac-label"><i class="fas fa-check-circle me-1" style="color:#059669;"></i> Vaccinations Done</span>' +
        '<span class="vac-value">' +
          (dv ? '<span class="vac-done-badge">' + dv + ' Done</span>'
              : '<span class="none-val">None</span>') +
        '</span>' +
      '</div>' +
      '<div class="vac-status-row">' +
        '<span class="vac-label"><i class="fas fa-layer-group me-1" style="color:#0891b2;"></i> Last Vaccine Age Group</span>' +
        '<span class="vac-value' + (vage ? '' : ' none-val') + '">' + (vage || 'None') + '</span>' +
      '</div>' +
      '<div class="vac-status-row">' +
        '<span class="vac-label"><i class="fas fa-syringe me-1" style="color:#7c3aed;"></i> Last Vaccine Name</span>' +
        '<span class="vac-value' + (vnm ? '' : ' none-val') + '">' + (vnm || 'None') + '</span>' +
      '</div>' +
      '<div class="vac-status-row">' +
        '<span class="vac-label"><i class="fas fa-calendar-alt me-1" style="color:#d97706;"></i> Last Vaccine Date</span>' +
        '<span class="vac-value' + (vlst ? '' : ' none-val') + '">' + (vlst || 'None') + '</span>' +
      '</div>';

    // Update hidden inputs
    var hDv   = document.getElementById('hDoneVaccin_'     + uid);
    var hVage = document.getElementById('hVaccinAge_'      + uid);
    var hVnm  = document.getElementById('hVaccinName_'     + uid);
    var hVlst = document.getElementById('hLastVaccinedate_'+ uid);
    if (hDv)   hDv.value   = dv   || '';
    if (hVage) hVage.value = vage || '';
    if (hVnm)  hVnm.value  = vnm  || '';
    if (hVlst) hVlst.value = vlst || '';
  }}
}}

// ── Chat state ────────────────────────────────────────────────────────────────
var _chatHospId   = null;
var _chatHospName = "";
var _chatLastId   = 0;
var _chatTimer    = null;

function openChatModal(hospId, hospName, initial) {{
  _chatHospId   = hospId;
  _chatHospName = hospName;
  _chatLastId   = 0;
  document.getElementById('chatAvatar').textContent   = initial;
  document.getElementById('chatHospName').textContent = hospName;
  document.getElementById('chatInput').value = '';
  chatAutoResize(document.getElementById('chatInput'));
  document.getElementById('chatMessages').innerHTML =
    '<div class="chat-empty-hint"><i class="fas fa-spinner fa-spin"></i><br>Loading...</div>';
  clearChatBadge(hospId);
  new bootstrap.Modal(document.getElementById('chatModal')).show();
  chatLoadHistory();
}}

function clearChatBadge(hospId) {{
  var wrap  = document.getElementById('chatWrap_'  + hospId);
  var btn   = document.getElementById('chatBtn_'   + hospId);
  var badge = wrap ? wrap.querySelector('.chat-notif-badge') : null;
  if (badge) badge.remove();
  if (btn)   btn.classList.remove('has-unread');
}}

document.getElementById('chatModal').addEventListener('hidden.bs.modal', function() {{
  if (_chatTimer) {{ clearInterval(_chatTimer); _chatTimer = null; }}
  _chatHospId = null;
}});

async function chatLoadHistory() {{
  try {{
    var fd = new FormData();
    fd.append('ajax',        'load');
    fd.append('parent_id',   PARENT_ID);
    fd.append('hospital_id', _chatHospId);
    var data = await (await fetch('parent_view_hospital.py', {{method:'POST', body:fd}})).json();
    var box  = document.getElementById('chatMessages');
    box.innerHTML = '';
    if (data.ok && data.messages.length) {{
      var prevDate = null;
      data.messages.forEach(function(m) {{
        var d = m.time.slice(0, 10);
        if (d !== prevDate) {{ chatAddDateDivider(box, d); prevDate = d; }}
        var isAuto = m.role === 'hospital' && String(m.message).startsWith('Hi! This is');
        chatAppendBubble(box, m.id, m.message,
          m.role === 'parent' ? 'mine' : 'theirs',
          m.time,
          m.role === 'parent' ? PARENT_NAME : _chatHospName,
          isAuto);
        if (m.id > _chatLastId) _chatLastId = m.id;
      }});
    }} else {{
      box.innerHTML = '<div class="chat-empty-hint"><i class="fas fa-comments"></i><br>No messages yet. Say hello to <strong>' + chatEsc(_chatHospName) + '</strong>!</div>';
    }}
    chatScrollBottom();
    if (_chatTimer) clearInterval(_chatTimer);
    _chatTimer = setInterval(chatPoll, 3000);
  }} catch(e) {{ console.error(e); }}
}}

async function chatPoll() {{
  if (!_chatHospId) return;
  try {{
    var fd = new FormData();
    fd.append('ajax',        'poll');
    fd.append('parent_id',   PARENT_ID);
    fd.append('hospital_id', _chatHospId);
    fd.append('last_id',     _chatLastId);
    var data = await (await fetch('parent_view_hospital.py', {{method:'POST', body:fd}})).json();
    if (data.ok && data.messages && data.messages.length) {{
      var box = document.getElementById('chatMessages');
      var ph  = box.querySelector('.chat-empty-hint'); if (ph) ph.remove();
      data.messages.forEach(function(m) {{
        if (!document.querySelector('#chatMessages [data-id="' + m.id + '"]')) {{
          var isAuto = m.role === 'hospital' && String(m.message).startsWith('Hi! This is');
          chatAppendBubble(box, m.id, m.message,
            m.role === 'parent' ? 'mine' : 'theirs',
            m.time,
            m.role === 'parent' ? PARENT_NAME : _chatHospName,
            isAuto);
          if (m.id > _chatLastId) _chatLastId = m.id;
        }}
      }});
      chatScrollBottom();
    }}
  }} catch(e) {{}}
}}

async function chatSend() {{
  if (!_chatHospId) return;
  var inp  = document.getElementById('chatInput');
  var text = inp.value.trim();
  if (!text) return;
  var btn  = document.getElementById('chatSendBtn');
  btn.disabled = true; inp.value = ''; chatAutoResize(inp);
  var box = document.getElementById('chatMessages');
  var ph  = box.querySelector('.chat-empty-hint'); if (ph) ph.remove();
  try {{
    var fd = new FormData();
    fd.append('ajax',        'send');
    fd.append('parent_id',   PARENT_ID);
    fd.append('hospital_id', _chatHospId);
    fd.append('message',     text);
    var data = await (await fetch('parent_view_hospital.py', {{method:'POST', body:fd}})).json();
    if (data.ok) {{
      chatAppendBubble(box, data.id, data.message, 'mine', data.time, PARENT_NAME, false);
      _chatLastId = data.id;
      chatScrollBottom();
      if (data.auto_reply) {{
        var typingDiv = document.createElement('div');
        typingDiv.id = 'typingIndicator';
        typingDiv.className = 'bubble-row theirs';
        typingDiv.innerHTML =
          '<div class="bubble-wrap">' +
            '<span class="sender-label">' + chatEsc(_chatHospName) + '</span>' +
            '<div class="typing-indicator"><span></span><span></span><span></span></div>' +
          '</div>';
        box.appendChild(typingDiv);
        chatScrollBottom();
        setTimeout(function() {{
          var ti = document.getElementById('typingIndicator');
          if (ti) ti.remove();
          var ar = data.auto_reply;
          chatAppendBubble(box, ar.id, ar.message, 'theirs', ar.time, _chatHospName, true);
          if (ar.id > _chatLastId) _chatLastId = ar.id;
          chatScrollBottom();
        }}, 1500);
      }}
    }} else {{
      alert('Send failed. Please try again.');
      inp.value = text; chatAutoResize(inp);
    }}
  }} catch(e) {{ inp.value = text; chatAutoResize(inp); }}
  btn.disabled = false; inp.focus();
}}

function chatAppendBubble(box, id, text, side, timeStr, label, isAutoReply) {{
  var t    = new Date(timeStr);
  var hhmm = isNaN(t.getTime()) ? timeStr.slice(11,16) : t.toLocaleTimeString([],{{hour:'2-digit',minute:'2-digit'}});
  var div  = document.createElement('div');
  div.className  = 'bubble-row ' + side;
  div.dataset.id = id;
  var extraCls   = isAutoReply ? ' auto-reply' : '';
  div.innerHTML  =
    '<div class="bubble-wrap">' +
      '<span class="sender-label">' + (isAutoReply ? '🤖 ' : '') + chatEsc(label) + '</span>' +
      '<div class="bubble ' + side + extraCls + '">' + chatEsc(text) +
        '<span class="bubble-time">' + hhmm + '</span>' +
      '</div>' +
    '</div>';
  box.appendChild(div);
}}
function chatAddDateDivider(box, dateStr) {{
  var months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  var p   = dateStr.split('-');
  var lbl = months[parseInt(p[1])-1] + ' ' + parseInt(p[2]) + ', ' + p[0];
  var div = document.createElement('div');
  div.className = 'date-divider';
  div.innerHTML = '<span>' + lbl + '</span>';
  box.appendChild(div);
}}
function chatScrollBottom() {{ var b = document.getElementById('chatMessages'); if (b) b.scrollTop = b.scrollHeight; }}
function chatHandleKey(e) {{ if (e.key==='Enter' && !e.shiftKey) {{ e.preventDefault(); chatSend(); }} }}
function chatAutoResize(el) {{ el.style.height='auto'; el.style.height=Math.min(el.scrollHeight,100)+'px'; }}
function chatEsc(s) {{ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }}

// ── Filter ────────────────────────────────────────────────────────────────────
function applyFilters() {{
  var nameQ     = document.getElementById('filterName').value.trim().toLowerCase();
  var districtQ = document.getElementById('filterDistrict').value.trim().toLowerCase();
  var areaQ     = document.getElementById('filterArea').value.trim().toLowerCase();
  var trs       = document.querySelectorAll('#hospitalTableBody .hospital-row');
  var visible   = 0;
  var oldMsg    = document.getElementById('noResultsRow');
  if (oldMsg) oldMsg.remove();
  trs.forEach(function(row) {{
    var match = (!nameQ||row.dataset.name.includes(nameQ)) &&
                (!districtQ||row.dataset.district.includes(districtQ)) &&
                (!areaQ||row.dataset.area.includes(areaQ));
    row.style.display = match ? '' : 'none';
    if (match) {{
      visible++;
      var badge = row.querySelector('.row-num'); if (badge) badge.textContent = visible;
      highlightCell(row.querySelector('.cell-name'),     nameQ);
      highlightCell(row.querySelector('.cell-district'), districtQ);
      highlightCell(row.querySelector('.cell-area'),     areaQ);
    }}
  }});
  document.getElementById('resultCount').textContent = visible + ' Result' + (visible!==1?'s':'');
  if (visible===0 && trs.length>0) {{
    var tbody = document.getElementById('hospitalTableBody');
    var tr = document.createElement('tr');
    tr.id = 'noResultsRow';
    tr.innerHTML = '<td colspan="8" style="text-align:center;padding:50px 20px;color:#64748b;"><i class="fas fa-search" style="font-size:2.5rem;color:#d1fae5;display:block;margin-bottom:12px;"></i><div style="font-size:1rem;font-weight:600;">No hospitals found matching your search.</div></td>';
    tbody.appendChild(tr);
  }}
}}
function highlightCell(cell, query) {{
  if (!cell) return;
  cell.innerHTML = cell.textContent;
  if (!query) return;
  cell.innerHTML = cell.innerHTML.replace(new RegExp('('+escapeRegex(query)+')','gi'),'<mark class="hl">$1</mark>');
}}
function escapeRegex(s) {{ return s.replace(/[.*+?^${{}}()|[\\]\\\\]/g,'\\\\$&'); }}
function clearFilters() {{
  document.getElementById('filterName').value='';
  document.getElementById('filterDistrict').value='';
  document.getElementById('filterArea').value='';
  applyFilters();
}}
window.addEventListener('DOMContentLoaded', applyFilters);

// ── Sidebar & logout ──────────────────────────────────────────────────────────
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
function doLogout() {{
  if (!confirm('Are you sure you want to logout?')) return;
  if (_chatTimer) clearInterval(_chatTimer);
  var open = document.querySelector('.modal.show');
  if (open) {{
    var inst = bootstrap.Modal.getInstance(open);
    if (inst) {{ inst.hide(); open.addEventListener('hidden.bs.modal', function() {{ window.location.href='main.py'; }}, {{once:true}}); return; }}
  }}
  window.location.href = 'main.py';
}}
document.addEventListener('click', function(e) {{
  var sb  = document.getElementById('sidebar');
  var btn = document.getElementById('sidebarToggleBtn');
  if (window.innerWidth<992 && sb.classList.contains('show') && !sb.contains(e.target) && !btn.contains(e.target))
    closeSidebarMobile();
}});

// ── Form submit validation ────────────────────────────────────────────────────
document.querySelectorAll('form[id^="parentRegistrationForm"]').forEach(function(form) {{
  form.addEventListener('submit', function(e) {{
    e.preventDefault();
    if (confirm('Are you sure you want to submit this registration?')) this.submit();
  }});
}});
</script>
</body>
</html>
""")