#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgitb
import sys
import cgi

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")

# ── FORM PARAMS ───────────────────────────────────────────────────────────────
form       = cgi.FieldStorage()
active_tab = form.getvalue('tab', 'parent').strip().lower()
if active_tab not in ('parent', 'hospital'):
    active_tab = 'parent'

print("Content-Type: text/html\n")

# ── DB CONNECTION ─────────────────────────────────────────────────────────────
try:
    con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
    cur = con.cursor()
except Exception as e:
    print(f"<html><body><h2>Database Connection Failed!</h2><p>{e}</p></body></html>")
    sys.exit()

# ── FETCH PARENT FEEDBACK ─────────────────────────────────────────────────────
try:
    cur.execute("""SELECT id, parent_name, email, child_name, hospital_name,
                          rating, category, feedback_text, created_at
                   FROM parent_feedback ORDER BY id DESC""")
    parent_feedbacks = cur.fetchall()
except:
    try:
        cur.execute("""SELECT id, parent_name, email, child_name, hospital_name,
                              rating, category, feedback_text
                       FROM parent_feedback ORDER BY id DESC""")
        parent_feedbacks = [row + (None,) for row in cur.fetchall()]
    except:
        parent_feedbacks = []

# ── FETCH HOSPITAL FEEDBACK ───────────────────────────────────────────────────
try:
    cur.execute("""SELECT id, hospital_name, email, contact_person,
                          rating, category, feedback_text, suggestion, created_at
                   FROM hospital_feedback ORDER BY id DESC""")
    hospital_feedbacks = cur.fetchall()
except:
    try:
        cur.execute("""SELECT id, hospital_name, email, contact_person,
                              rating, category, feedback_text, suggestion
                       FROM hospital_feedback ORDER BY id DESC""")
        hospital_feedbacks = [row + (None,) for row in cur.fetchall()]
    except:
        hospital_feedbacks = []

# ── STATS — PARENT ────────────────────────────────────────────────────────────
p_total      = len(parent_feedbacks)
p_avg        = round(sum(int(r[5]) for r in parent_feedbacks if r[5]) / p_total, 1) if p_total else 0
p_five_star  = sum(1 for r in parent_feedbacks if str(r[5]) == '5')
p_one_star   = sum(1 for r in parent_feedbacks if str(r[5]) == '1')

# ── STATS — HOSPITAL ──────────────────────────────────────────────────────────
h_total      = len(hospital_feedbacks)
h_avg        = round(sum(int(r[4]) for r in hospital_feedbacks if r[4]) / h_total, 1) if h_total else 0
h_five_star  = sum(1 for r in hospital_feedbacks if str(r[4]) == '5')
h_one_star   = sum(1 for r in hospital_feedbacks if str(r[4]) == '1')

# ── RATING HELPERS ────────────────────────────────────────────────────────────
rating_labels = {5: "Excellent", 4: "Good", 3: "Average", 2: "Poor", 1: "Very Poor"}

def stars_html(rating):
    return "".join(
        '<i class="fas fa-star"></i>' if s <= rating else '<i class="fas fa-star empty"></i>'
        for s in range(1, 6)
    )

# ─────────────────────────────────────────────────────────────────────────────
print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<title>View Feedback - Admin CVS</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
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
  box-shadow: 0 4px 15px rgba(0,0,0,0.3); padding: 15px 20px;
}}
.navbar .container-fluid {{
  display: flex; flex-direction: row; align-items: center;
  flex-wrap: nowrap; position: relative;
}}
.navbar-brand {{
  font-weight: 600; color: white !important; letter-spacing: 2px; text-transform: uppercase;
}}
.navbar-brand i {{
  margin-right: 10px; color: #fda4af; font-size: 1.5rem; animation: pulse 2s infinite;
}}
@keyframes pulse {{ 0%,100%{{transform:scale(1)}} 50%{{transform:scale(1.1)}} }}

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
  border: none; padding: 8px 20px; border-radius: 25px; color: white; font-weight: 600;
  transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(238,9,121,0.4);
  font-size: 0.9rem; white-space: nowrap;
}}
.btn-logout:hover {{ transform:translateY(-2px); box-shadow:0 6px 20px rgba(238,9,121,0.6); color:white; }}

/* ── SIDEBAR ── */
.sidebar {{
  min-height: 100vh;
  background: linear-gradient(135deg, #3b021f, #ec4899);
  box-shadow: 4px 0 15px rgba(0,0,0,0.2); padding: 20px 0;
}}
.sidebar-link {{
  display: block; padding: 12px 15px; color: #ecf0f1; text-decoration: none;
  transition: all 0.3s ease; border-left: 4px solid transparent;
  font-weight: 500; margin: 5px 0; font-size: 0.95rem;
}}
.sidebar-link:hover, .sidebar-link.active {{
  background: linear-gradient(90deg, #ec4899, transparent);
  color: #fff; border-left: 4px solid #fdf2f8; padding-left: 20px;
}}
.sidebar-link i {{ margin-right: 10px; width: 20px; text-align: center; }}

.sidebar-overlay {{
  display: none; position: fixed; top: 0; left: 0;
  width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 998;
}}
.sidebar-overlay.show {{ display: block; }}

/* ── CONTENT ── */
.content-area {{ padding: 25px; min-height: 100vh; }}

/* ── PAGE HEADER ── */
.page-header {{
  background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.1); border-left: 5px solid #ec4899;
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 10px;
}}
.page-header h4 {{
  margin: 0; color: #2c3e50; font-weight: 700; font-size: 1.5rem;
  text-transform: uppercase; letter-spacing: 1px;
}}
.page-header h4 i {{ margin-right: 10px; color: #ec4899; }}

/* ── TABS ── */
.tab-nav {{ display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }}
.tab-btn {{
  flex: 1; min-width: 140px; padding: 14px 10px; border: none; border-radius: 14px;
  font-weight: 700; font-size: 0.9rem; cursor: pointer; transition: all 0.3s;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  background: rgba(255,255,255,0.25); color: white;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15); backdrop-filter: blur(6px);
}}
.tab-btn:hover {{ transform: translateY(-2px); background: rgba(255,255,255,0.35); }}
.tab-btn.active-parent {{
  background: linear-gradient(135deg, #667eea, #764ba2);
  box-shadow: 0 6px 18px rgba(102,126,234,0.5);
}}
.tab-btn.active-hospital {{
  background: linear-gradient(135deg, #0f4c81, #1a73e8);
  box-shadow: 0 6px 18px rgba(26,115,232,0.5);
}}
.tab-count {{
  background: rgba(255,255,255,0.3); border-radius: 20px;
  padding: 2px 9px; font-size: 0.8rem; font-weight: 800;
}}

/* ── TAB PANELS ── */
.tab-panel {{ display: none; }}
.tab-panel.active {{ display: block; }}

/* ── STAT CARDS ── */
.stat-card {{
  border-radius: 20px; padding: 25px; color: white; text-align: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2); transition: all 0.4s ease;
  position: relative; overflow: hidden; min-height: 160px;
  display: flex; flex-direction: column; justify-content: center;
  align-items: center; margin-bottom: 15px;
}}
.stat-card::before {{
  content: ''; position: absolute; top: -50%; right: -50%;
  width: 200%; height: 200%; background: rgba(255,255,255,0.1);
  transform: rotate(45deg); transition: all 0.6s ease;
}}
.stat-card:hover::before {{ top: -100%; right: -100%; }}
.stat-card:hover {{ transform: translateY(-5px) scale(1.02); box-shadow: 0 15px 40px rgba(0,0,0,0.3); }}
.stat-card h3 {{
  font-size: 3rem; font-weight: 800; margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.2); position: relative; z-index: 1;
}}
.stat-card p {{
  font-size: 1rem; font-weight: 600; margin: 0; text-transform: uppercase;
  letter-spacing: 1px; position: relative; z-index: 1;
}}
.stat-icon {{ position: absolute; top: 15px; right: 15px; font-size: 2.5rem; opacity: 0.7; z-index: 0; }}
.bg-total    {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
.bg-avgstar  {{ background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%); }}
.bg-fivestar {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
.bg-onestar  {{ background: linear-gradient(135deg, #833ab4 0%, #fd1d1d 100%); }}
.bg-total-h  {{ background: linear-gradient(135deg, #0f4c81 0%, #1a73e8 100%); }}

/* ── SEARCH/FILTER ── */
.search-filter-box {{
  background: white; border-radius: 15px; padding: 20px;
  margin-bottom: 20px; box-shadow: 0 5px 20px rgba(0,0,0,0.1);
}}
.search-filter-box .form-control,
.search-filter-box .form-select {{
  border: 2px solid #e2e8f0; border-radius: 10px;
  padding: 10px 14px; font-size: 0.9rem; transition: all 0.3s;
}}
.search-filter-box .form-control:focus,
.search-filter-box .form-select:focus {{
  border-color: #ec4899; box-shadow: 0 0 0 3px rgba(236,72,153,0.2);
}}

/* ── FEEDBACK CARDS ── */
.feedback-card {{
  background: white; border-radius: 15px; padding: 20px; margin-bottom: 18px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.08); border-left: 5px solid #667eea;
  transition: all 0.3s ease;
}}
.feedback-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,0,0,0.15); }}
.feedback-card.rating-5 {{ border-left-color: #10b981; }}
.feedback-card.rating-4 {{ border-left-color: #3b82f6; }}
.feedback-card.rating-3 {{ border-left-color: #f59e0b; }}
.feedback-card.rating-2 {{ border-left-color: #f97316; }}
.feedback-card.rating-1 {{ border-left-color: #ef4444; }}

.feedback-header {{
  display: flex; align-items: flex-start; justify-content: space-between;
  flex-wrap: wrap; gap: 10px; margin-bottom: 12px;
}}
.user-avatar {{
  width: 44px; height: 44px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 700; font-size: 1rem; flex-shrink: 0;
}}
.user-info {{ flex: 1; min-width: 0; margin-left: 12px; }}
.user-info h6 {{ font-weight: 700; color: #2c3e50; margin: 0 0 2px; font-size: 0.95rem; }}
.user-info small {{ color: #6b7280; font-size: 0.8rem; }}
.stars {{ color: #f59e0b; font-size: 1rem; }}
.stars .empty {{ color: #d1d5db; }}
.badge-category {{
  padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;
  background: #f3f4f6; color: #374151; border: 1px solid #d1d5db;
}}
.feedback-meta {{ display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 12px; }}
.feedback-meta span {{ font-size: 0.82rem; color: #6b7280; }}
.feedback-meta span i {{ margin-right: 4px; color: #ec4899; }}
.feedback-text {{
  background: #f8fafc; border-radius: 10px; padding: 12px 15px;
  color: #374151; font-size: 0.9rem; line-height: 1.6;
  border-left: 3px solid #e5e7eb; margin-bottom: 10px;
}}
.suggestion-box {{
  background: #eff6ff; border-radius: 10px; padding: 12px 15px;
  color: #1e3a8a; font-size: 0.88rem; line-height: 1.6; border-left: 3px solid #93c5fd;
}}
.suggestion-box .sug-label {{
  font-weight: 700; font-size: 0.78rem; text-transform: uppercase;
  letter-spacing: 0.5px; color: #1a73e8; margin-bottom: 4px; display: block;
}}
.no-data {{
  background: white; border-radius: 15px; padding: 60px 20px;
  text-align: center; box-shadow: 0 5px 20px rgba(0,0,0,0.08);
}}
.no-data i {{ font-size: 4rem; color: #d1d5db; margin-bottom: 15px; display: block; }}

/* ── RESPONSIVE ── */
@media (max-width: 991.98px) {{
  .mobile-menu-toggle {{ display: flex; align-items: center; justify-content: center; }}
  .sidebar {{
    position: fixed; left: -100%; top: 0; width: 280px; height: 100vh;
    z-index: 999; transition: left 0.3s ease; overflow-y: auto;
  }}
  .sidebar.show {{ left: 0; }}
  .content-area {{ padding: 15px; }}
  .navbar-brand {{
    position: absolute; left: 50%; transform: translateX(-50%);
    margin: 0 !important; font-size: 1rem;
  }}
  .navbar-brand i {{ font-size: 1.3rem; }}
}}
@media (max-width: 767.98px) {{
  .stat-card h3 {{ font-size: 2.5rem; }}
  .stat-card p {{ font-size: 0.9rem; }}
  .page-header h4 {{ font-size: 1.2rem; }}
  .feedback-header {{ flex-direction: column; }}
  .btn-logout {{ padding: 6px 15px; font-size: 0.8rem; }}
  .tab-btn {{ font-size: 0.8rem; padding: 11px 8px; min-width: 120px; }}
}}
@media (max-width: 575.98px) {{
  .navbar-brand {{ font-size: 0.85rem; }}
  .navbar-brand i {{ font-size: 1.1rem; }}
  .stat-card h3 {{ font-size: 2rem; }}
  .stat-card {{ min-height: 130px; padding: 15px; }}
  .stat-icon {{ font-size: 2rem; top: 10px; right: 10px; }}
}}
</style>
</head>
<body>

<script>const ACTIVE_TAB = "{active_tab}";</script>

<!-- NAVBAR -->
<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container-fluid">
    <button class="mobile-menu-toggle" onclick="toggleSidebar()">
      <i class="fas fa-bars"></i>
    </button>
    <span class="navbar-brand">
      <i class="fa-solid fa-hands-holding-child"></i> CVS - Admin
    </span>
    <button class="btn btn-logout ms-auto" onclick="logout()">
      <i class="fas fa-sign-out-alt"></i> Logout
    </button>
  </div>
</nav>

<div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

<div class="container-fluid">
  <div class="row">

    <!-- SIDEBAR -->
    <div class="col-lg-2 col-md-3 sidebar p-0" id="sidebar">
      <a href="admin_dashboard.py" class="sidebar-link"><i class="fas fa-home"></i> Home</a>
      <a href="admin_vaccination.py" class="sidebar-link"><i class="fa-solid fa-circle-info"></i> Add Vaccination Info</a>
      <a href="admin_hospital_registration.py" class="sidebar-link">
        <i class="fas fa-hospital"></i> Hospital Registration
      </a>
      
      <a href="admin_parent_registration.py" class="sidebar-link">
        <i class="fas fa-user"></i> Parent Registration
      </a>
      <a href="admin_view_child.py" class="sidebar-link"><i class="fas fa-baby"></i> View Children</a>
      <a href="admin_view_appointment.py" class="sidebar-link"><i class="fas fa-calendar-check"></i> View Appointments</a>
      <a href="admin_vaccination_schedule.py" class="sidebar-link"><i class="fa-solid fa-syringe"></i> Vaccination Schedule</a>
      <a href="admin_appointment_reminder.py" class="sidebar-link"><i class="fas fa-bell"></i> Appointment Reminders</a>
      <a class="sidebar-link" href="admin_export_data.py"><i class="fas fa-file-export"></i> Export Data</a>
      <a href="admin_view_feedback.py" class="sidebar-link active">
        <i class="fas fa-comment-dots"></i> Feedback
      </a>
    </div>

    <!-- MAIN CONTENT -->
    <div class="col-lg-10 col-md-9 col-12 content-area">

      <!-- PAGE HEADER -->
      <div class="page-header">
        <h4><i class="fas fa-comment-dots"></i> View Feedback</h4>
        <span style="background:#ec4899;color:white;padding:6px 16px;border-radius:20px;font-size:0.9rem;font-weight:600;">
          <i class="fas fa-list me-1"></i>
          Parent: {p_total} &nbsp;|&nbsp; Hospital: {h_total}
        </span>
      </div>

      <!-- TAB BUTTONS -->
      <div class="tab-nav">
        <button class="tab-btn {'active-parent' if active_tab=='parent' else ''}"
                onclick="switchTab('parent')">
          <i class="fas fa-users"></i> Parent Feedback
          <span class="tab-count">{p_total}</span>
        </button>
        <button class="tab-btn {'active-hospital' if active_tab=='hospital' else ''}"
                onclick="switchTab('hospital')">
          <i class="fas fa-hospital"></i> Hospital Feedback
          <span class="tab-count">{h_total}</span>
        </button>
      </div>
""")

# ─────────────────────────────────────────────────────────────────────────────
# ── PARENT FEEDBACK PANEL ────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
p_active = 'active' if active_tab == 'parent' else ''
print(f'<div class="tab-panel {p_active}" id="panel-parent">')

# Parent Stats
print(f"""
  <div class="row mb-3">
    <div class="col-lg-3 col-md-6 col-6">
      <div class="stat-card bg-total">
        <i class="fas fa-comments stat-icon"></i>
        <h3>{p_total}</h3><p>Total Feedback</p>
      </div>
    </div>
    <div class="col-lg-3 col-md-6 col-6">
      <div class="stat-card bg-avgstar">
        <i class="fas fa-star stat-icon"></i>
        <h3>{p_avg}</h3><p>Avg Rating</p>
      </div>
    </div>
    <div class="col-lg-3 col-md-6 col-6">
      <div class="stat-card bg-fivestar">
        <i class="fas fa-smile stat-icon"></i>
        <h3>{p_five_star}</h3><p>5-Star Reviews</p>
      </div>
    </div>
    <div class="col-lg-3 col-md-6 col-6">
      <div class="stat-card bg-onestar">
        <i class="fas fa-frown stat-icon"></i>
        <h3>{p_one_star}</h3><p>1-Star Reviews</p>
      </div>
    </div>
  </div>
""")

# Parent Search/Filter
print(f"""
  <div class="search-filter-box">
    <div class="row g-3 align-items-end">
      <div class="col-md-5">
        <label class="form-label fw-bold mb-1"><i class="fas fa-search me-1"></i> Search</label>
        <input type="text" class="form-control" id="p_searchInput" onkeyup="filterFeedback('parent')"
               placeholder="Search by name, email, hospital...">
      </div>
      <div class="col-md-3">
        <label class="form-label fw-bold mb-1"><i class="fas fa-star me-1"></i> Rating</label>
        <select class="form-select" id="p_ratingFilter" onchange="filterFeedback('parent')">
          <option value="">All Ratings</option>
          <option value="5">5 - Excellent</option>
          <option value="4">4 - Good</option>
          <option value="3">3 - Average</option>
          <option value="2">2 - Poor</option>
          <option value="1">1 - Very Poor</option>
        </select>
      </div>
      <div class="col-md-3">
        <label class="form-label fw-bold mb-1"><i class="fas fa-tags me-1"></i> Category</label>
        <select class="form-select" id="p_categoryFilter" onchange="filterFeedback('parent')">
          <option value="">All Categories</option>
          <option value="Vaccination Service">Vaccination Service</option>
          <option value="Staff Behaviour">Staff Behaviour</option>
          <option value="Hospital Facility">Hospital Facility</option>
          <option value="App / Website">App / Website</option>
          <option value="Appointment Booking">Appointment Booking</option>
          <option value="General">General</option>
        </select>
      </div>
      <div class="col-md-1">
        <button class="btn w-100" onclick="resetFilters('parent')"
          style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;border-radius:10px;padding:10px;"
          title="Reset Filters"><i class="fas fa-redo"></i>
        </button>
      </div>
    </div>
  </div>
  <p class="text-white mb-3" style="font-weight:600;">
    Showing <span id="p_countNum">{p_total}</span> feedback(s)
  </p>
  <div id="p_feedbackContainer">
""")

if not parent_feedbacks:
    print("""
    <div class="no-data">
      <i class="fas fa-comment-slash"></i>
      <h5 class="text-muted">No Parent Feedback Yet</h5>
      <p class="text-muted">Parent feedback will appear here once submitted.</p>
    </div>""")
else:
    avatar_colors = ["#667eea","#764ba2","#ee0979","#10b981","#f59e0b","#3b82f6"]
    for idx, fb in enumerate(parent_feedbacks):
        fid, pname, email, cname, hname, rating, category, ftext, *rest = fb
        created  = rest[0] if rest and rest[0] else ""
        rating   = int(rating) if rating else 0
        initials = (pname[:2] if pname else "??").upper()
        color    = avatar_colors[idx % len(avatar_colors)]
        rlabel   = rating_labels.get(rating, "")
        date_str = str(created)[:16] if created else "N/A"

        meta_parts = []
        if cname:    meta_parts.append(f'<span><i class="fas fa-baby"></i> {cname}</span>')
        if hname:    meta_parts.append(f'<span><i class="fas fa-hospital"></i> {hname}</span>')
        if category: meta_parts.append(f'<span><i class="fas fa-tags"></i> <span class="badge-category">{category}</span></span>')
        meta_parts.append(f'<span><i class="fas fa-clock"></i> {date_str}</span>')
        meta_parts.append(f'<span><i class="fas fa-hashtag"></i> {fid}</span>')

        print(f"""
    <div class="feedback-card rating-{rating}"
         data-panel="parent"
         data-name="{(pname or '').lower()}"
         data-email="{(email or '').lower()}"
         data-hospital="{(hname or '').lower()}"
         data-text="{(ftext or '').lower()}"
         data-rating="{rating}"
         data-category="{category or ''}">
      <div class="feedback-header">
        <div class="d-flex align-items-center">
          <div class="user-avatar" style="background:{color};">{initials}</div>
          <div class="user-info">
            <h6>{pname or 'N/A'}</h6>
            <small><i class="fas fa-envelope me-1"></i>{email or 'N/A'}</small>
          </div>
        </div>
        <div class="text-end">
          <div class="stars mb-1">{stars_html(rating)}</div>
          <small class="text-muted fw-bold">{rating}/5 &bull; {rlabel}</small>
        </div>
      </div>
      <div class="feedback-meta">{''.join(meta_parts)}</div>
      <div class="feedback-text">
        <i class="fas fa-quote-left text-muted me-2" style="font-size:0.8rem;"></i>
        {ftext or 'No feedback text provided.'}
      </div>
    </div>""")

print("  </div>")  # /p_feedbackContainer
print("</div>")    # /panel-parent

# ─────────────────────────────────────────────────────────────────────────────
# ── HOSPITAL FEEDBACK PANEL ──────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
h_active = 'active' if active_tab == 'hospital' else ''
print(f'<div class="tab-panel {h_active}" id="panel-hospital">')

# Hospital Stats
print(f"""
  <div class="row mb-3">
    <div class="col-lg-3 col-md-6 col-6">
      <div class="stat-card bg-total-h">
        <i class="fas fa-hospital stat-icon"></i>
        <h3>{h_total}</h3><p>Total Feedback</p>
      </div>
    </div>
    <div class="col-lg-3 col-md-6 col-6">
      <div class="stat-card bg-avgstar">
        <i class="fas fa-star stat-icon"></i>
        <h3>{h_avg}</h3><p>Avg Rating</p>
      </div>
    </div>
    <div class="col-lg-3 col-md-6 col-6">
      <div class="stat-card bg-fivestar">
        <i class="fas fa-smile stat-icon"></i>
        <h3>{h_five_star}</h3><p>5-Star Reviews</p>
      </div>
    </div>
    <div class="col-lg-3 col-md-6 col-6">
      <div class="stat-card bg-onestar">
        <i class="fas fa-frown stat-icon"></i>
        <h3>{h_one_star}</h3><p>1-Star Reviews</p>
      </div>
    </div>
  </div>
""")

# Hospital Search/Filter
print(f"""
  <div class="search-filter-box">
    <div class="row g-3 align-items-end">
      <div class="col-md-5">
        <label class="form-label fw-bold mb-1"><i class="fas fa-search me-1"></i> Search</label>
        <input type="text" class="form-control" id="h_searchInput" onkeyup="filterFeedback('hospital')"
               placeholder="Search by hospital, email, contact person...">
      </div>
      <div class="col-md-3">
        <label class="form-label fw-bold mb-1"><i class="fas fa-star me-1"></i> Rating</label>
        <select class="form-select" id="h_ratingFilter" onchange="filterFeedback('hospital')">
          <option value="">All Ratings</option>
          <option value="5">5 - Excellent</option>
          <option value="4">4 - Good</option>
          <option value="3">3 - Average</option>
          <option value="2">2 - Poor</option>
          <option value="1">1 - Very Poor</option>
        </select>
      </div>
      <div class="col-md-3">
        <label class="form-label fw-bold mb-1"><i class="fas fa-tags me-1"></i> Category</label>
        <select class="form-select" id="h_categoryFilter" onchange="filterFeedback('hospital')">
          <option value="">All Categories</option>
          <option value="Appointment System">Appointment System</option>
          <option value="Vaccine Management">Vaccine Management</option>
          <option value="Parent Communication">Parent Communication</option>
          <option value="App / Website">App / Website</option>
          <option value="Reports &amp; Data">Reports &amp; Data</option>
          <option value="General">General</option>
        </select>
      </div>
      <div class="col-md-1">
        <button class="btn w-100" onclick="resetFilters('hospital')"
          style="background:linear-gradient(135deg,#0f4c81,#1a73e8);color:white;border-radius:10px;padding:10px;"
          title="Reset Filters"><i class="fas fa-redo"></i>
        </button>
      </div>
    </div>
  </div>
  <p class="text-white mb-3" style="font-weight:600;">
    Showing <span id="h_countNum">{h_total}</span> feedback(s)
  </p>
  <div id="h_feedbackContainer">
""")

if not hospital_feedbacks:
    print("""
    <div class="no-data">
      <i class="fas fa-hospital-slash"></i>
      <h5 class="text-muted">No Hospital Feedback Yet</h5>
      <p class="text-muted">Hospital feedback will appear here once submitted.</p>
    </div>""")
else:
    avatar_colors = ["#0f4c81","#1a73e8","#0097a7","#0d47a1","#00838f","#1565c0"]
    for idx, fb in enumerate(hospital_feedbacks):
        fid, hname, email, contact, rating, category, ftext, suggestion, *rest = fb
        created  = rest[0] if rest and rest[0] else ""
        rating   = int(rating) if rating else 0
        initials = (hname[:2] if hname else "??").upper()
        color    = avatar_colors[idx % len(avatar_colors)]
        rlabel   = rating_labels.get(rating, "")
        date_str = str(created)[:16] if created else "N/A"

        meta_parts = []
        if contact:  meta_parts.append(f'<span><i class="fas fa-user-md"></i> {contact}</span>')
        if category: meta_parts.append(f'<span><i class="fas fa-tags"></i> <span class="badge-category">{category}</span></span>')
        meta_parts.append(f'<span><i class="fas fa-clock"></i> {date_str}</span>')
        meta_parts.append(f'<span><i class="fas fa-hashtag"></i> {fid}</span>')

        suggestion_html = ""
        if suggestion:
            suggestion_html = f"""
      <div class="suggestion-box">
        <span class="sug-label"><i class="fas fa-lightbulb me-1"></i> Suggestion</span>
        {suggestion}
      </div>"""

        print(f"""
    <div class="feedback-card rating-{rating}"
         data-panel="hospital"
         data-name="{(hname or '').lower()}"
         data-email="{(email or '').lower()}"
         data-contact="{(contact or '').lower()}"
         data-text="{(ftext or '').lower()}"
         data-rating="{rating}"
         data-category="{category or ''}">
      <div class="feedback-header">
        <div class="d-flex align-items-center">
          <div class="user-avatar" style="background:{color}; border-radius:12px;">{initials}</div>
          <div class="user-info">
            <h6>{hname or 'N/A'}</h6>
            <small><i class="fas fa-envelope me-1"></i>{email or 'N/A'}</small>
          </div>
        </div>
        <div class="text-end">
          <div class="stars mb-1">{stars_html(rating)}</div>
          <small class="text-muted fw-bold">{rating}/5 &bull; {rlabel}</small>
        </div>
      </div>
      <div class="feedback-meta">{''.join(meta_parts)}</div>
      <div class="feedback-text">
        <i class="fas fa-quote-left text-muted me-2" style="font-size:0.8rem;"></i>
        {ftext or 'No feedback text provided.'}
      </div>
      {suggestion_html}
    </div>""")

print("  </div>")  # /h_feedbackContainer
print("</div>")    # /panel-hospital

print(f"""
    </div><!-- /content-area -->
  </div><!-- /row -->
</div><!-- /container-fluid -->

<script>
const TAB_ORDER = ['parent', 'hospital'];
const TAB_COLORS = {{ parent: 'active-parent', hospital: 'active-hospital' }};

function switchTab(tab) {{
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b =>
    b.classList.remove('active-parent', 'active-hospital')
  );
  document.getElementById('panel-' + tab).classList.add('active');
  document.querySelectorAll('.tab-btn')[TAB_ORDER.indexOf(tab)].classList.add(TAB_COLORS[tab]);
  const url = new URL(window.location.href);
  url.searchParams.set('tab', tab);
  history.replaceState(null, '', url.toString());
}}

function filterFeedback(panel) {{
  const prefix   = panel === 'parent' ? 'p_' : 'h_';
  const search   = document.getElementById(prefix + 'searchInput').value.toLowerCase();
  const rating   = document.getElementById(prefix + 'ratingFilter').value;
  const category = document.getElementById(prefix + 'categoryFilter').value;
  let visible = 0;
  const searchFields = panel === 'parent'
    ? ['data-name','data-email','data-hospital','data-text']
    : ['data-name','data-email','data-contact','data-text'];
  document.querySelectorAll('.feedback-card[data-panel="' + panel + '"]').forEach(card => {{
    const matchSearch   = !search   || searchFields.some(a => (card.getAttribute(a)||'').includes(search));
    const matchRating   = !rating   || card.getAttribute('data-rating') === rating;
    const matchCategory = !category || card.getAttribute('data-category') === category;
    if (matchSearch && matchRating && matchCategory) {{ card.style.display = ''; visible++; }}
    else {{ card.style.display = 'none'; }}
  }});
  document.getElementById(prefix + 'countNum').textContent = visible;
}}

function resetFilters(panel) {{
  const prefix = panel === 'parent' ? 'p_' : 'h_';
  document.getElementById(prefix + 'searchInput').value = '';
  document.getElementById(prefix + 'ratingFilter').value = '';
  document.getElementById(prefix + 'categoryFilter').value = '';
  filterFeedback(panel);
}}

function toggleSidebar() {{
  document.getElementById('sidebar').classList.toggle('show');
  document.getElementById('sidebarOverlay').classList.toggle('show');
}}

document.addEventListener('click', function(e) {{
  const sb = document.getElementById('sidebar');
  const mt = document.querySelector('.mobile-menu-toggle');
  if (window.innerWidth < 992 && sb && mt &&
      !sb.contains(e.target) && !mt.contains(e.target) &&
      sb.classList.contains('show')) {{
    sb.classList.remove('show');
    document.getElementById('sidebarOverlay').classList.remove('show');
  }}
}});

function logout() {{
  if (confirm('Are you sure you want to logout?')) window.location.href = 'main.py';
}}

document.addEventListener('DOMContentLoaded', () => switchTab(ACTIVE_TAB));
</script>
</body>
</html>
""")

con.close()