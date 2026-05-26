#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgi
import cgitb
import sys
import json

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")

form        = cgi.FieldStorage()
hospital_id = form.getvalue("hospital_id", "").strip()
parent_id   = form.getvalue("parent_id",   "").strip()
ajax        = form.getvalue("ajax",        "").strip()
msg_text    = form.getvalue("message",     "").strip()
last_id     = form.getvalue("last_id",     "0").strip()

# ── Database ──────────────────────────────────────────────────────────────────
try:
    con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
    cur = con.cursor()
except Exception as e:
    print("Content-Type: application/json\r\n\r\n")
    print(json.dumps({"error": str(e)}))
    sys.exit()

# ── AJAX: send message ────────────────────────────────────────────────────────
if ajax == "send" and hospital_id and parent_id and msg_text:
    # Hospital → Parent message
    print("Content-Type: application/json\r\n\r\n")
    try:
        cur.execute(
            """INSERT INTO chat_messages (parent_id, hospital_id, sender_role, message, status)
               VALUES (%s, %s, 'hospital', %s, 'sent')""",
            (parent_id, hospital_id, msg_text)
        )
        con.commit()
        cur.execute("SELECT LAST_INSERT_ID()")
        new_id = cur.fetchone()[0]
        cur.execute(
            """SELECT id, message, sender_role, sent_at
               FROM chat_messages
               WHERE id=%s AND parent_id=%s AND hospital_id=%s""",
            (new_id, parent_id, hospital_id)
        )
        row = cur.fetchone()
        if row:
            print(json.dumps({"ok": True, "id": row[0], "message": row[1],
                              "role": row[2], "time": str(row[3])}))
        else:
            print(json.dumps({"error": "Message not found"}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
    con.close()
    sys.exit()

# ── AJAX: parent sends message → auto-reply on first message ─────────────────
if ajax == "parent_send" and hospital_id and parent_id and msg_text:
    print("Content-Type: application/json\r\n\r\n")
    try:
        # Get hospital name for the auto-reply text
        hospital_name_reply = "Hospital"
        try:
            cur.execute("SELECT hospital_name FROM hospital WHERE id=%s", (hospital_id,))
            hrow = cur.fetchone()
            if hrow:
                hospital_name_reply = hrow[0]
        except:
            pass

        # Count ONLY parent messages BEFORE inserting (0 = first ever message)
        cur.execute(
            """SELECT COUNT(*) FROM chat_messages
               WHERE parent_id=%s AND hospital_id=%s AND sender_role='parent'""",
            (parent_id, hospital_id)
        )
        is_first = (cur.fetchone()[0] == 0)

        # Insert the parent's message
        cur.execute(
            """INSERT INTO chat_messages (parent_id, hospital_id, sender_role, message, status)
               VALUES (%s, %s, 'parent', %s, 'sent')""",
            (parent_id, hospital_id, msg_text)
        )
        con.commit()
        cur.execute("SELECT LAST_INSERT_ID()")
        new_id = cur.fetchone()[0]

        # Auto-reply only on the very first parent message
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
            "SELECT id, message, sender_role, sent_at FROM chat_messages WHERE id=%s",
            (new_id,)
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
    con.close()
    sys.exit()

# ── AJAX: poll new messages ───────────────────────────────────────────────────
if ajax == "poll" and hospital_id and parent_id:
    print("Content-Type: application/json\r\n\r\n")
    try:
        # ── Auto-reply: if parent sent first message and hospital never replied ──
        cur.execute(
            """SELECT COUNT(*) FROM chat_messages
               WHERE parent_id=%s AND hospital_id=%s AND sender_role='parent'""",
            (parent_id, hospital_id)
        )
        parent_msg_count = cur.fetchone()[0]
        cur.execute(
            """SELECT COUNT(*) FROM chat_messages
               WHERE parent_id=%s AND hospital_id=%s AND sender_role='hospital'""",
            (parent_id, hospital_id)
        )
        hospital_msg_count = cur.fetchone()[0]

        if parent_msg_count > 0 and hospital_msg_count == 0:
            hosp_name_auto = "Hospital"
            try:
                cur.execute("SELECT hospital_name FROM hospital WHERE id=%s", (hospital_id,))
                hn = cur.fetchone()
                if hn:
                    hosp_name_auto = hn[0]
            except:
                pass
            auto_text = f"Hi! This is {hosp_name_auto}. How can I help you? \U0001f60a"
            cur.execute(
                """INSERT INTO chat_messages (parent_id, hospital_id, sender_role, message, status)
                   VALUES (%s, %s, 'hospital', %s, 'sent')""",
                (parent_id, hospital_id, auto_text)
            )
            con.commit()

        cur.execute(
            """UPDATE chat_messages SET status='seen'
               WHERE parent_id=%s AND hospital_id=%s
                 AND sender_role='parent' AND status='sent'""",
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
    con.close()
    sys.exit()

# ── PAGE render ───────────────────────────────────────────────────────────────
print("Content-Type: text/html\r\n\r\n")

hospital_name = "Hospital"
if hospital_id:
    try:
        cur.execute("SELECT hospital_name FROM hospital WHERE id=%s", (hospital_id,))
        hrow = cur.fetchone()
        if hrow:
            hospital_name = hrow[0]
    except:
        pass

# ── Parents linked to THIS hospital only ─────────────────────────────────────
parents      = []
existing_ids = set()

try:
    cur.execute("""
        SELECT DISTINCT p.id, p.parent_name, p.email_id
        FROM parent p
        INNER JOIN parentform pf ON pf.email = p.email_id
        INNER JOIN hospital h   ON h.hospital_name = pf.hospital_name
        WHERE h.id = %s
        ORDER BY p.parent_name
    """, (hospital_id,))
    for row in cur.fetchall():
        if row[0] not in existing_ids:
            parents.append(row)
            existing_ids.add(row[0])
except:
    pass

try:
    cur.execute("""
        SELECT DISTINCT p.id, p.parent_name, p.email_id
        FROM parent p
        INNER JOIN hospital_appointment ha ON ha.email_id = p.email_id
        INNER JOIN hospital h              ON h.hospital_name = ha.hospital_name
        WHERE h.id = %s
        ORDER BY p.parent_name
    """, (hospital_id,))
    for row in cur.fetchall():
        if row[0] not in existing_ids:
            parents.append(row)
            existing_ids.add(row[0])
except:
    pass

try:
    cur.execute("""
        SELECT DISTINCT p.id, p.parent_name, p.email_id
        FROM parent p
        INNER JOIN chat_messages cm ON cm.parent_id = p.id
        WHERE cm.hospital_id = %s
    """, (hospital_id,))
    for row in cur.fetchall():
        if row[0] not in existing_ids:
            parents.append(row)
            existing_ids.add(row[0])
except:
    pass

# ── Unread counts ─────────────────────────────────────────────────────────────
unread_counts = {}
if hospital_id:
    try:
        cur.execute(
            """SELECT parent_id, COUNT(*)
               FROM chat_messages
               WHERE hospital_id=%s AND sender_role='parent' AND status='sent'
               GROUP BY parent_id""",
            (hospital_id,)
        )
        for pid, cnt in cur.fetchall():
            unread_counts[pid] = cnt
    except:
        pass

# ── Sort: unread first, then alphabetically ───────────────────────────────────
parents = sorted(parents, key=lambda x: (-unread_counts.get(x[0], 0), (x[1] or "").lower()))

if parent_id and hospital_id:
    allowed = {str(p[0]) for p in parents}
    if parent_id not in allowed:
        parent_id = ""

messages              = []
selected_parent_name  = ""
selected_parent_email = ""

if parent_id:
    try:
        cur.execute("SELECT parent_name, email_id FROM parent WHERE id=%s", (parent_id,))
        prow = cur.fetchone()
        if prow:
            selected_parent_name  = prow[0]
            selected_parent_email = prow[1]

        cur.execute(
            """UPDATE chat_messages SET status='seen'
               WHERE parent_id=%s AND hospital_id=%s
                 AND sender_role='parent' AND status='sent'""",
            (parent_id, hospital_id)
        )
        con.commit()

        if int(parent_id) in unread_counts:
            del unread_counts[int(parent_id)]
        try:
            if str(parent_id) in unread_counts:
                del unread_counts[str(parent_id)]
        except:
            pass

        cur.execute(
            """SELECT id, message, sender_role, sent_at
               FROM chat_messages
               WHERE parent_id=%s AND hospital_id=%s
               ORDER BY sent_at ASC""",
            (parent_id, hospital_id)
        )
        messages = cur.fetchall()
    except:
        pass

con.close()

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<title>Hospital Chat - CVS</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  background: linear-gradient(135deg, #083344, #22d3ee, #cffafe);
  min-height: 100vh; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overflow-x: hidden;
}}
.navbar {{
  box-shadow: 0 4px 20px rgba(0,0,0,0.4); padding: 15px 20px;
  background: linear-gradient(135deg, #083344, #22d3ee, #cffafe) !important;
}}
.navbar .container-fluid {{ display: flex; flex-direction: row; align-items: center; flex-wrap: nowrap; }}
.navbar-brand {{ font-weight: 600; color: white !important; letter-spacing: 2px; text-transform: uppercase; }}
.navbar-brand i {{ margin-right: 10px; color: #e9d5ff; font-size: 1.5rem; animation: bounce 2s infinite; }}
@keyframes bounce {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-5px); }} }}
.mobile-menu-toggle {{
  display: none; flex-shrink: 0; align-self: center;
  background: rgba(255,255,255,0.15); border: 1.5px solid rgba(255,255,255,0.35);
  color: white; padding: 6px 12px; border-radius: 8px; font-size: 1.2rem;
  cursor: pointer; transition: all 0.3s ease; backdrop-filter: blur(6px); line-height: 1; margin-right: 12px;
}}
.mobile-menu-toggle:hover {{ background: rgba(255,255,255,0.28); border-color: rgba(255,255,255,0.6); }}
.btn-logout {{
  flex-shrink: 0; background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
  border: none; padding: 8px 20px; border-radius: 25px; color: white; font-weight: 600;
  box-shadow: 0 4px 15px rgba(238,9,121,0.4); font-size: 0.9rem; white-space: nowrap; transition: all 0.3s ease;
}}
.btn-logout:hover {{ transform: translateY(-2px); color: white; box-shadow: 0 6px 20px rgba(238,9,121,0.6); }}
.sidebar {{
  min-height: 100vh; background: linear-gradient(135deg, #083344, #22d3ee);
  box-shadow: 4px 0 20px rgba(0,0,0,0.3); padding: 20px 0;
}}
.sidebar-link {{
  display: block; padding: 14px 18px; color: #e9d5ff; text-decoration: none;
  transition: all 0.3s ease; border-left: 4px solid transparent; font-weight: 500; margin: 6px 0;
}}
.sidebar-link:hover, .sidebar-link.active {{
  background: linear-gradient(90deg, #22d3ee, transparent 100%);
  color: #fff; border-left: 4px solid #cffafe; padding-left: 24px;
}}
.sidebar-link i {{ margin-right: 12px; width: 22px; text-align: center; }}
.sidebar-overlay {{
  display: none; position: fixed; top: 0; left: 0;
  width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 998;
}}
.sidebar-overlay.show {{ display: block; }}
.content-area {{ padding: 20px; }}
.chat-wrapper {{ display: flex; gap: 16px; height: calc(100vh - 115px); }}
.contact-panel {{
  width: 400px; min-width: 260px; background: rgba(255,255,255,0.97);
  border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.18);
  display: flex; flex-direction: column; overflow: hidden;
}}
.contact-header {{
  background: linear-gradient(135deg, #083344, #0891b2); color: #fff; padding: 16px 18px;
  font-weight: 700; font-size: 0.95rem; letter-spacing: 0.5px;
  display: flex; align-items: center; justify-content: space-between; flex-shrink: 0;
}}
.contact-count {{
  font-size: 0.73rem; font-weight: 400; opacity: 0.85;
  background: rgba(255,255,255,0.2); padding: 3px 10px; border-radius: 20px;
}}
.contact-search {{ padding: 10px 12px; border-bottom: 1px solid #e5e7eb; }}
.contact-search input {{
  width: 100%; padding: 8px 12px 8px 34px; border-radius: 20px;
  border: 1.5px solid #d1d5db; font-size: 0.85rem; outline: none; transition: 0.2s;
  background: #f9fafb url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='13' height='13' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'/%3E%3C/svg%3E") no-repeat 11px center;
}}
.contact-search input:focus {{ border-color: #22d3ee; background: #fff; }}
.contact-list {{ flex: 1; overflow-y: auto; }}
.contact-item {{
  display: flex; align-items: center; gap: 11px; padding: 12px 14px; cursor: pointer;
  border-bottom: 1px solid #f3f4f6; transition: 0.2s; text-decoration: none; color: inherit;
}}
.contact-item:hover {{ background: #f0f9ff; }}
.contact-item.active {{ background: #e0f2fe; border-left: 4px solid #22d3ee; }}
.contact-item.has-unread {{
  background: #fff7ed; border-left: 4px solid #ef4444; animation: pulse-row 2s infinite;
}}
.contact-item.has-unread:hover {{ background: #fff0e0; }}
.contact-item.has-unread .c-name {{ color: #991b1b; font-weight: 700; }}
.contact-item.has-unread .c-avatar {{
  background: linear-gradient(135deg, #ef4444, #f97316);
  box-shadow: 0 0 0 3px rgba(239,68,68,0.25);
}}
@keyframes pulse-row {{
  0%,100% {{ box-shadow: inset 3px 0 0 #ef4444; }}
  50%      {{ box-shadow: inset 3px 0 0 #f97316; }}
}}
.c-avatar {{
  width: 42px; height: 42px; border-radius: 50%;
  background: linear-gradient(135deg, #0891b2, #67e8f9);
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 1rem; font-weight: 700; flex-shrink: 0;
}}
.c-info {{ flex: 1; min-width: 0; }}
.c-name {{ font-weight: 600; font-size: 0.88rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #0f172a; }}
.c-sub  {{ font-size: 0.73rem; color: #6b7280; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 1px; }}
.badge-wrap {{ display: flex; flex-direction: column; align-items: center; gap: 2px; flex-shrink: 0; }}
.badge-unread {{
  background: #ef4444; color: #fff; border-radius: 50%; min-width: 22px; height: 22px;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.7rem; font-weight: 700; padding: 0 5px; animation: pulse-b 1.5s infinite;
}}
.badge-new-label {{
  font-size: 0.6rem; color: #b91c1c; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
}}
@keyframes pulse-b {{
  0%,100% {{ box-shadow: 0 0 0 0 rgba(239,68,68,0.5); }}
  50%      {{ box-shadow: 0 0 0 5px rgba(239,68,68,0); }}
}}
.no-contacts {{ padding: 40px 20px; text-align: center; color: #9ca3af; font-size: 0.85rem; line-height: 2; }}
.no-contacts i {{ font-size: 2.5rem; color: #d1d5db; display: block; margin-bottom: 8px; }}
.chat-panel {{
  flex: 1; background: rgba(255,255,255,0.97); border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18); display: flex; flex-direction: column; overflow: hidden;
}}
.chat-head {{
  background: linear-gradient(135deg, #083344, #0891b2); color: #fff; padding: 14px 20px;
  display: flex; align-items: center; gap: 12px; flex-shrink: 0;
}}
.chat-head .c-avatar {{ width: 38px; height: 38px; font-size: 0.9rem; }}
.chat-head-info h6 {{ margin: 0; font-weight: 700; font-size: 0.92rem; }}
.chat-head-info small {{ opacity: 0.75; font-size: 0.76rem; }}
.online-dot {{ width: 10px; height: 10px; border-radius: 50%; background: #4ade80; border: 2px solid #fff; margin-left: auto; flex-shrink: 0; }}
.chat-body {{
  flex: 1; overflow-y: auto; padding: 16px 18px;
  background: #f8fafc url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40'%3E%3Ccircle cx='20' cy='20' r='1' fill='%23e2e8f0' opacity='.6'/%3E%3C/svg%3E") repeat;
}}
.bubble-row {{ display: flex; margin-bottom: 10px; align-items: flex-end; gap: 6px; }}
.bubble-row.mine   {{ justify-content: flex-end; }}
.bubble-row.theirs {{ justify-content: flex-start; }}
.bubble-wrap {{ display: flex; flex-direction: column; max-width: 68%; }}
.bubble-row.mine   .bubble-wrap {{ align-items: flex-end; }}
.bubble-row.theirs .bubble-wrap {{ align-items: flex-start; }}
.sender-label {{ font-size: 0.68rem; color: #64748b; margin-bottom: 2px; font-weight: 600; }}
.bubble {{ padding: 9px 13px; border-radius: 18px; font-size: 0.88rem; line-height: 1.5; word-break: break-word; }}
.bubble.mine {{
  background: linear-gradient(135deg, #0369a1, #0891b2); color: #fff;
  border-bottom-right-radius: 4px; box-shadow: 0 2px 8px rgba(8,145,178,0.3);
}}
.bubble.theirs {{
  background: #fff; color: #1e293b; border-bottom-left-radius: 4px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;
}}

/* ── Auto-reply bubble: special teal bot style ── */
.bubble.auto-reply {{
  background: linear-gradient(135deg, #0d9488, #14b8a6);
  color: #fff; border-bottom-right-radius: 4px;
  box-shadow: 0 2px 8px rgba(20,184,166,0.35);
  border-left: 3px solid #5eead4;
}}
.bubble.auto-reply::before {{
  content: '🤖 ';
}}

.bubble-time {{ font-size: 0.65rem; margin-top: 4px; display: block; }}
.bubble.mine   .bubble-time {{ text-align:right; color:rgba(255,255,255,0.85); }}
.bubble.theirs .bubble-time {{ text-align:left;  color:#94a3b8; }}
.bubble.auto-reply .bubble-time {{ text-align:right; color:rgba(255,255,255,0.8); }}
.date-divider {{ text-align: center; margin: 14px 0; }}
.date-divider span {{ background: #e2e8f0; color: #64748b; font-size: 0.71rem; padding: 3px 14px; border-radius: 20px; font-weight: 500; }}
.chat-footer {{
  padding: 10px 14px; border-top: 1px solid #e2e8f0; background: #fff;
  display: flex; align-items: flex-end; gap: 9px; flex-shrink: 0;
}}
.chat-footer textarea {{
  flex: 1; resize: none; border: 1.5px solid #cbd5e1; border-radius: 22px;
  padding: 9px 15px; font-size: 0.88rem; outline: none;
  max-height: 100px; min-height: 42px; line-height: 1.45; font-family: inherit; transition: 0.2s; background: #f8fafc;
}}
.chat-footer textarea:focus {{ border-color: #0891b2; box-shadow: 0 0 0 3px rgba(8,145,178,0.12); background: #fff; }}
.btn-send {{
  width: 42px; height: 42px; border-radius: 50%; border: none;
  background: linear-gradient(135deg, #0369a1, #0891b2); color: #fff; font-size: 0.95rem;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 12px rgba(8,145,178,0.4); transition: 0.2s; flex-shrink: 0;
}}
.btn-send:hover {{ transform: scale(1.08); }}
.btn-send:disabled {{ opacity:0.5; cursor:not-allowed; transform:none; }}
.chat-empty {{
  flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
  color: #94a3b8; gap: 12px; padding: 40px; text-align: center;
}}
.chat-empty i  {{ font-size: 3.5rem; opacity: 0.25; }}
.chat-empty h5 {{ color: #374151; font-weight: 700; margin: 0; font-size: 1rem; }}
.chat-empty p  {{ font-size: 0.85rem; margin: 0; max-width: 260px; line-height: 1.6; }}
.unread-pill {{
  background: #fef2f2; border: 1px solid #fecaca; color: #b91c1c;
  padding: 7px 16px; border-radius: 20px; font-size: 0.82rem; font-weight: 600;
}}
.chat-body::-webkit-scrollbar, .contact-list::-webkit-scrollbar {{ width: 4px; }}
.chat-body::-webkit-scrollbar-thumb    {{ background: #cbd5e1; border-radius: 4px; }}
.contact-list::-webkit-scrollbar-thumb {{ background: #bae6fd; border-radius: 4px; }}
@media (max-width: 991.98px) {{
  .mobile-menu-toggle {{ display: flex; align-items: center; justify-content: center; }}
  .sidebar {{ position: fixed; left: -100%; top: 0; width: 280px; height: 100vh; z-index: 999; transition: left 0.3s ease; overflow-y: auto; }}
  .sidebar.show {{ left: 0; }}
  .content-area {{ margin-left: 0 !important; }}
}}
@media (max-width: 767.98px) {{
  .chat-wrapper {{ flex-direction: column; height: auto; }}
  .contact-panel {{ width: 100%; height: 220px; min-height: 220px; }}
  .chat-panel    {{ height: 65vh; }}
  .btn-logout    {{ padding: 6px 16px; font-size: 0.85rem; }}
}}
@media (max-width: 575.98px) {{
  .navbar-brand {{ font-size: 0.85rem; letter-spacing: 0.5px; }}
  .navbar-brand i {{ font-size: 1.1rem; margin-right: 6px; }}
  .btn-logout {{ padding: 6px 14px; font-size: 0.8rem; }}
}}
@media (max-width: 400px) {{ .navbar-brand {{ font-size: 0.75rem; }} }}
</style>
</head>
<body>

<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container-fluid">
    <button class="mobile-menu-toggle" onclick="toggleSidebar()"><i class="fas fa-bars"></i></button>
    <span class="navbar-brand ms-2"><i class="fa-solid fa-hospital"></i> CVS - Hospital</span>
    <button class="btn btn-logout ms-auto" onclick="logout()"><i class="fas fa-sign-out-alt"></i> Logout</button>
  </div>
</nav>
<div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

<div class="container-fluid">
  <div class="row">
    <div class="col-lg-2 col-md-3 sidebar p-0" id="sidebar">
      <a href="hospital_dashboard.py?hospital_id={hospital_id}" class="sidebar-link"><i class="fas fa-home"></i> Home</a>
      <a href="hospital_vaccination.py?hospital_id={hospital_id}" class="sidebar-link"><i class="fa-solid fa-circle-info"></i> Vaccination Info</a>
      <a href="hospital_view_application.py?hospital_id={hospital_id}" class="sidebar-link"><i class="fa-solid fa-user-pen"></i> Parent Application</a>
      <a href="hospital_view_appointment.py?hospital_id={hospital_id}" class="sidebar-link"><i class="fas fa-calendar-alt"></i> View Appointments</a>
      <a href="hospital_profile.py?hospital_id={hospital_id}" class="sidebar-link"><i class="fas fa-user-circle"></i> My Profile</a>
      <a href="hospital_feedback.py?hospital_id={hospital_id}" class="sidebar-link"><i class="fas fa-comment-dots"></i> Feedback</a>
      <a href="hospital_chat.py?hospital_id={hospital_id}" class="sidebar-link active"><i class="fas fa-notes-medical"></i> Chats</a>
      <a href="hospital_help.py?hospital_id={hospital_id}" class="sidebar-link"><i class="fas fa-circle-question"></i> Help &amp; Support</a>
    </div>

    <div class="col-lg-10 col-md-9 col-12 content-area">
      <div class="chat-wrapper">

        <div class="contact-panel">
          <div class="contact-header">
            <span><i class="fa fa-users me-2"></i>Parents</span>
            <span class="contact-count">{len(parents)} contact{"s" if len(parents)!=1 else ""}</span>
          </div>
          <div class="contact-search">
            <input type="text" id="searchInput" placeholder="Search parent name…" oninput="filterContacts()">
          </div>
          <div class="contact-list" id="contactList">
""")

if parents:
    for p in parents:
        pid, pname, pemail = p
        initial    = pname[0].upper() if pname else "P"
        unread     = unread_counts.get(pid, 0)
        is_active  = str(pid) == str(parent_id)

        if is_active:
            has_unread = ""
            badge_html = ""
        else:
            has_unread = "has-unread" if unread else ""
            if unread:
                badge_html = f"""<div class="badge-wrap">
              <span class="badge-unread">{unread}</span>
              <span class="badge-new-label">New</span>
            </div>"""
            else:
                badge_html = ""

        active_cls = "active" if is_active else has_unread
        safe_name  = (pname  or "").replace('"','&quot;')
        safe_email = (pemail or "").replace('"','&quot;')

        print(f"""            <a href="hospital_chat.py?hospital_id={hospital_id}&parent_id={pid}"
               class="contact-item {active_cls}" data-name="{safe_name.lower()}">
              <div class="c-avatar">{initial}</div>
              <div class="c-info">
                <div class="c-name">{safe_name}</div>
                <div class="c-sub">{safe_email}</div>
              </div>
              {badge_html}
            </a>""")
else:
    print("""            <div class="no-contacts">
              <i class="fa fa-user-slash"></i>
              <strong style="color:#475569;font-size:.9rem;">No parents yet</strong><br>
              Parents who apply to your hospital<br>will appear here.
            </div>""")

print("""          </div>
        </div>

        <div class="chat-panel">""")

if parent_id and selected_parent_name:
    initial_p = selected_parent_name[0].upper() if selected_parent_name else "P"
    print(f"""          <div class="chat-head">
            <div class="c-avatar">{initial_p}</div>
            <div class="chat-head-info">
              <h6>{selected_parent_name}</h6>
              <small><i class="fa fa-envelope me-1" style="font-size:.6rem;"></i>{selected_parent_email}</small>
            </div>
            <div class="online-dot" title="Active"></div>
          </div>
          <div class="chat-body" id="chatBody">""")

    prev_date = None
    for msg in messages:
        mid, text, role, sent_at = msg
        msg_date  = sent_at.strftime("%B %d, %Y") if hasattr(sent_at,'strftime') else str(sent_at)[:10]
        msg_time  = sent_at.strftime("%I:%M %p")  if hasattr(sent_at,'strftime') else str(sent_at)[11:16]
        if msg_date != prev_date:
            print(f'            <div class="date-divider"><span>{msg_date}</span></div>')
            prev_date = msg_date
        side      = "mine" if role == "hospital" else "theirs"
        label     = hospital_name if role == "hospital" else selected_parent_name
        safe_text = str(text).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        # Mark auto-reply bubbles (they start with the robot emoji prefix)
        extra_cls = " auto-reply" if (role == "hospital" and str(text).startswith(f"Hi! This is")) else ""
        print(f"""            <div class="bubble-row {side}" data-id="{mid}">
              <div class="bubble-wrap">
                <span class="sender-label">{label}</span>
                <div class="bubble {side}{extra_cls}">{safe_text}<span class="bubble-time">{msg_time}</span></div>
              </div>
            </div>""")

    if not messages:
        print(f"""            <div style="text-align:center;padding:30px;color:#94a3b8;font-size:.85rem;">
              <i class="fa fa-comments fa-2x mb-2" style="display:block;opacity:.3;"></i>
              No messages yet. Start the conversation with <strong>{selected_parent_name}</strong>.
            </div>""")

    print(f"""          </div>
          <div class="chat-footer">
            <textarea id="msgInput" rows="1" placeholder="Reply to {selected_parent_name}…"
                      onkeydown="handleKey(event)" oninput="autoResize(this)"></textarea>
            <button class="btn-send" id="sendBtn" onclick="sendMessage()" title="Send (Enter)">
              <i class="fa fa-paper-plane"></i>
            </button>
          </div>""")
else:
    total_unread = sum(unread_counts.values())
    unread_html  = (f'<div class="unread-pill mt-1"><i class="fa fa-bell me-1"></i>'
                    f'{total_unread} unread message{"s" if total_unread!=1 else ""} waiting</div>'
                    if total_unread else "")
    print(f"""          <div class="chat-empty">
            <i class="fa fa-comments"></i>
            <h5>Select a Parent to Chat</h5>
            <p>Pick a parent from the contact list on the left to view messages and send replies.</p>
            {unread_html}
          </div>""")

print(f"""        </div>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
const HOSPITAL_ID = "{hospital_id}";
const PARENT_ID   = "{parent_id}";
const HOSP_NAME   = {json.dumps(hospital_name)};
const PAR_NAME    = {json.dumps(selected_parent_name)};
let   lastId      = {messages[-1][0] if messages else 0};

function escapeHtml(s) {{
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}
function scrollBottom() {{ const b=document.getElementById('chatBody'); if(b) b.scrollTop=b.scrollHeight; }}
function autoResize(el)  {{ el.style.height='auto'; el.style.height=Math.min(el.scrollHeight,100)+'px'; }}
function handleKey(e)    {{ if(e.key==='Enter'&&!e.shiftKey){{ e.preventDefault(); sendMessage(); }} }}

function appendBubble(id, text, side, timeStr, label, isAutoReply) {{
  const body = document.getElementById('chatBody');
  if (!body) return;
  const t    = new Date(timeStr);
  const hhmm = isNaN(t) ? (timeStr.slice(11,16)||timeStr) : t.toLocaleTimeString([],{{hour:'2-digit',minute:'2-digit'}});
  const div  = document.createElement('div');
  div.className  = 'bubble-row ' + side;
  div.dataset.id = id;
  const extraCls = isAutoReply ? ' auto-reply' : '';
  div.innerHTML  = '<div class="bubble-wrap"><span class="sender-label">'+escapeHtml(label)+'</span>'
                 + '<div class="bubble '+side+extraCls+'">'+escapeHtml(text)
                 + '<span class="bubble-time">'+hhmm+'</span></div></div>';
  body.appendChild(div);
}}

async function sendMessage() {{
  if (!PARENT_ID) return;
  const inp  = document.getElementById('msgInput');
  const text = inp.value.trim();
  if (!text) return;
  const btn  = document.getElementById('sendBtn');
  btn.disabled = true; inp.value = ''; autoResize(inp);
  try {{
    const fd = new FormData();
    fd.append('ajax',        'send');   // hospital → parent
    fd.append('hospital_id', HOSPITAL_ID);
    fd.append('parent_id',   PARENT_ID);
    fd.append('message',     text);
    const res  = await fetch('hospital_chat.py', {{method:'POST', body:fd}});
    const data = await res.json();
    if (data.ok) {{
      appendBubble(data.id, data.message, 'mine', data.time, HOSP_NAME, false);
      lastId = data.id;
      scrollBottom();
    }} else {{
      alert('Send failed. Please try again.'); inp.value = text; autoResize(inp);
    }}
  }} catch(err) {{ console.error(err); }}
  btn.disabled = false; inp.focus();
}}

async function pollMessages() {{
  if (!PARENT_ID) return;
  try {{
    const fd = new FormData();
    fd.append('ajax',        'poll');
    fd.append('hospital_id', HOSPITAL_ID);
    fd.append('parent_id',   PARENT_ID);
    fd.append('last_id',     lastId);
    const res  = await fetch('hospital_chat.py', {{method:'POST', body:fd}});
    const data = await res.json();
    if (data.ok && data.messages && data.messages.length) {{
      data.messages.forEach(m => {{
        if (!document.querySelector('[data-id="'+m.id+'"]')) {{
          const isAuto = m.role === 'hospital' && String(m.message).startsWith('Hi! This is');
          appendBubble(m.id, m.message,
                       m.role === 'hospital' ? 'mine' : 'theirs',
                       m.time,
                       m.role === 'hospital' ? HOSP_NAME : PAR_NAME,
                       isAuto);
          lastId = m.id;
        }}
      }});
      scrollBottom();
    }}
  }} catch(e) {{}}
}}

function filterContacts() {{
  const q = document.getElementById('searchInput').value.toLowerCase();
  document.querySelectorAll('.contact-item').forEach(el => {{
    el.style.display = el.dataset.name.includes(q) ? '' : 'none';
  }});
}}
function toggleSidebar() {{
  document.getElementById('sidebar').classList.toggle('show');
  document.getElementById('sidebarOverlay').classList.toggle('show');
}}
function logout() {{ if(confirm("Are you sure you want to logout?")) window.location.href="main.py"; }}
document.addEventListener('click', function(e) {{
  const sidebar = document.getElementById('sidebar');
  const toggle  = document.querySelector('.mobile-menu-toggle');
  if (window.innerWidth<992 && sidebar.classList.contains('show')
      && !sidebar.contains(e.target) && !toggle.contains(e.target)) {{
    sidebar.classList.remove('show');
    document.getElementById('sidebarOverlay').classList.remove('show');
  }}
}});
window.addEventListener('DOMContentLoaded', function() {{
  scrollBottom();
  if (PARENT_ID) {{
    setInterval(pollMessages, 3000);
    const inp = document.getElementById('msgInput');
    if (inp) inp.focus();
  }}
}});
</script>
</body>
</html>
""")