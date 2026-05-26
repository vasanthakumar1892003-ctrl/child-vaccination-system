#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgi
import cgitb
import sys

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")
print("Content-Type: text/html\r\n\r\n")

form = cgi.FieldStorage()
success_msg = ""
error_msg = ""
hospital_id = form.getvalue("hospital_id", "")

# Handle form submission
if form.getvalue("submit_feedback"):
    hospital_name  = form.getvalue("hospital_name", "").strip()
    email          = form.getvalue("email", "").strip()
    contact_person = form.getvalue("contact_person", "").strip()
    rating         = form.getvalue("rating", "").strip()
    category       = form.getvalue("category", "").strip()
    feedback_text  = form.getvalue("feedback_text", "").strip()
    suggestion     = form.getvalue("suggestion", "").strip()

    if not hospital_name or not email or not rating or not feedback_text:
        error_msg = "Please fill in all required fields."
    else:
        try:
            con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
            cur = con.cursor()
            sql = """INSERT INTO hospital_feedback
                     (hospital_id, hospital_name, email, contact_person, rating, category, feedback_text, suggestion)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cur.execute(sql, (hospital_id or None, hospital_name, email, contact_person, rating, category, feedback_text, suggestion))
            con.commit()
            con.close()
            success_msg = "Thank you! Your feedback has been submitted successfully."
        except Exception as e:
            error_msg = f"Error submitting feedback: {str(e)}"

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<title>Hospital Feedback - Child Vaccination System</title>

<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  background: linear-gradient(135deg, #083344, #22d3ee, #cffafe);
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow-x: hidden;
}}

/* ===== NAVBAR ===== */
.navbar {{
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  padding: 15px 20px;
  background: linear-gradient(135deg, #083344, #22d3ee, #cffafe) !important;
}}
/* Force single-row flex, never wrap */
.navbar .container-fluid {{
  display: flex;
  flex-direction: row;
  align-items: center;
  flex-wrap: nowrap;
}}
.navbar-brand {{
  font-weight: 600;
  color: white !important;
  letter-spacing: 2px;
  text-transform: uppercase;
}}
.navbar-brand i {{
  margin-right: 10px;
  color: #e9d5ff;
  font-size: 1.5rem;
  animation: bounce 2s infinite;
}}

@keyframes bounce {{
  0%, 100% {{ transform: translateY(0); }}
  50% {{ transform: translateY(-5px); }}
}}

/* MOBILE MENU TOGGLE — inside navbar, hidden on desktop */
.mobile-menu-toggle {{
  display: none;
  flex-shrink: 0;
  align-self: center;
  background: rgba(255, 255, 255, 0.15);
  border: 1.5px solid rgba(255, 255, 255, 0.35);
  color: white;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(6px);
  line-height: 1;
  margin-right: 12px;
}}
.mobile-menu-toggle:hover {{
  background: rgba(255, 255, 255, 0.28);
  border-color: rgba(255, 255, 255, 0.6);
  color: white;
}}

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
  background: linear-gradient(135deg, #083344, #22d3ee);
  box-shadow: 4px 0 20px rgba(0,0,0,0.3);
  padding: 20px 0;
}}

.sidebar-link {{
 display: block; padding: 14px 18px; color: #e9d5ff;
  text-decoration: none; transition: all 0.3s ease;
  border-left: 4px solid transparent; font-weight: 500; margin: 6px 0;
}}

.sidebar-link:hover,
.sidebar-link.active {{
  background: linear-gradient(90deg, #22d3ee, transparent 100%);
  color: #fff;
  border-left: 4px solid #cffafe;
  padding-left: 24px;
  transform: translateX(5px);
}}

.sidebar-link i {{
  margin-right: 12px;
  width: 22px;
  text-align: center;
}}

.sidebar .dropdown-toggle {{
  background: transparent;
  border: none;
  color: #e9d5ff;
  font-weight: 500;
  padding: 14px 18px;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
  font-size: 0.95rem;
  width: 100%;
  text-align: left;
}}

.sidebar .dropdown-toggle:hover {{
  background: linear-gradient(90deg, rgba(124,58,237,0.3) 0%, transparent 100%);
  color: #fff;
  border-left: 4px solid #a78bfa;
}}

.sidebar .dropdown-toggle i {{ margin-right: 10px; }}

.sidebar .dropdown-menu {{
  background: #1e1b4b;
  border: none;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
  margin-left: 10px;
  width: 90%;
}}

.sidebar .dropdown-item {{
  color: #e9d5ff;
  padding: 10px 15px;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
  font-size: 0.9rem;
}}

.sidebar .dropdown-item:hover {{
  background: rgba(124,58,237,0.4);
  color: white;
  border-left: 3px solid #a78bfa;
  padding-left: 20px;
}}

/* SIDEBAR OVERLAY */
.sidebar-overlay {{
  display: none;
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.6);
  z-index: 998;
  backdrop-filter: blur(2px);
}}
.sidebar-overlay.show {{ display: block; }}

/* ===== CONTENT AREA ===== */
.content-col {{ padding: 25px 20px; min-height: 100vh; }}

.feedback-wrapper {{
  width: 100%;
  max-width: 780px;
  margin: 0 auto;
}}

/* FORM CARD */
.form-card {{
  background: white;
  border-radius: 20px;
  box-shadow: 0 15px 50px rgba(0,0,0,0.2);
  overflow: hidden;
}}

.card-header-bar {{
  background: linear-gradient(135deg, #5b21b6 0%, #7c3aed 100%);
  padding: 18px 25px;
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
}}

.card-body {{ padding: 30px; }}

.form-label {{
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
  font-size: 0.92rem;
}}

.required-star {{ color: #e53e3e; }}

.form-control, .form-select {{
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 0.92rem;
  transition: all 0.3s ease;
}}

.form-control:focus, .form-select:focus {{
  border-color: #7c3aed;
  box-shadow: 0 0 0 3px rgba(124,58,237,0.18);
}}

/* STAR RATING */
.star-rating {{
  display: flex;
  flex-direction: row-reverse;
  justify-content: flex-end;
  gap: 6px;
  margin-top: 4px;
}}

.star-rating input {{ display: none; }}

.star-rating label {{
  font-size: 2rem;
  color: #d1d5db;
  cursor: pointer;
  transition: color 0.2s ease, transform 0.2s ease;
}}

.star-rating input:checked ~ label,
.star-rating label:hover,
.star-rating label:hover ~ label {{
  color: #f59e0b;
  transform: scale(1.1);
}}

/* CATEGORY PILLS */
.category-pills {{
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 6px;
}}

.category-pills input {{ display: none; }}

.category-pills label {{
  padding: 7px 18px;
  border-radius: 25px;
  border: 2px solid #7c3aed;
  color: #7c3aed;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}}

.category-pills input:checked + label {{
  background: linear-gradient(135deg, #5b21b6 0%, #7c3aed 100%);
  color: white;
  border-color: transparent;
  box-shadow: 0 4px 12px rgba(124,58,237,0.4);
}}

.category-pills label:hover {{ background: rgba(124,58,237,0.08); }}

/* CHARACTER COUNTER */
.char-counter {{
  font-size: 0.78rem;
  color: #9ca3af;
  text-align: right;
  margin-top: 4px;
}}

/* SUBMIT BUTTON */
.btn-submit {{
  background: linear-gradient(135deg, #083344, #22d3ee);
  border: none;
  padding: 13px 40px;
  border-radius: 30px;
  color: white;
  font-weight: 700;
  font-size: 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 5px 20px rgba(124,58,237,0.4);
  width: 100%;
  cursor: pointer;
}}

.btn-submit:hover {{
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(124,58,237,0.6);
  color: white;
}}

/* SECTION DIVIDER */
.section-divider {{
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 20px 0 15px;
}}

.section-divider span {{
  font-weight: 700;
  color: #4b5563;
  font-size: 0.88rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}}

.section-divider::before, .section-divider::after {{
  content: '';
  flex: 1;
  height: 1px;
  background: #e5e7eb;
}}

.alert {{ border-radius: 12px; border: none; padding: 14px 20px; }}
.alert-success {{ background: #ede9fe; color: #4c1d95; }}
.alert-danger  {{ background: #fee2e2; color: #991b1b; }}

/* SUCCESS STATE */
.success-state {{ text-align: center; padding: 40px 20px; }}

.success-state .check-icon {{
  font-size: 4rem;
  color: #7c3aed;
  margin-bottom: 15px;
  display: block;
  animation: bounceIn 0.6s ease;
}}

@keyframes bounceIn {{
  0%   {{ transform: scale(0); }}
  60%  {{ transform: scale(1.2); }}
  100% {{ transform: scale(1); }}
}}

.success-state h4 {{ font-weight: 700; color: #4c1d95; margin-bottom: 10px; }}
.success-state p  {{ color: #6b7280; }}

.footer-note {{
  text-align: center;
  color: rgba(255,255,255,0.7);
  font-size: 0.82rem;
  margin-top: 20px;
  padding-bottom: 30px;
}}

/* ===== RESPONSIVE ===== */
@media (max-width: 991.98px) {{
  .mobile-menu-toggle {{
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .sidebar {{
    position: fixed;
    left: -100%; top: 0;
    width: 280px; height: 100vh;
    z-index: 999;
    transition: left 0.3s ease;
    overflow-y: auto;
  }}
  .sidebar.show {{ left: 0; }}
  .content-col {{ padding: 15px 10px; }}
  .navbar-brand {{ font-size: 1rem; letter-spacing: 1px; }}
  .navbar-brand i {{ font-size: 1.3rem; }}
}}

@media (max-width: 767.98px) {{
  .card-body {{ padding: 20px; }}
}}

@media (max-width: 575.98px) {{
  .navbar-brand {{ font-size: 0.85rem; letter-spacing: 0.5px; }}
  .navbar-brand i {{ font-size: 1.1rem; margin-right: 6px; }}
  .btn-logout {{ padding: 6px 14px; font-size: 0.8rem; }}
}}

@media (max-width: 400px) {{
  .navbar-brand {{ font-size: 0.75rem; }}
}}
</style>
</head>
<body>

<!-- NAVBAR -->
<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container-fluid">

    <!-- Hamburger — hidden on desktop, shown on tablet/mobile -->
    <button class="mobile-menu-toggle" onclick="toggleSidebar()">
      <i class="fas fa-bars"></i>
    </button>

    <!-- Brand — margin-right:auto pushes logout to the right -->
    <span class="navbar-brand ms-2">
      <i class="fa-solid fa-hospital"></i> CVS - Hospital
    </span>

    <!-- Logout — always far right -->
    <button class="btn btn-logout" onclick="logout()">
      <i class="fas fa-sign-out-alt"></i> Logout
    </button>

  </div>
</nav>

<!-- Sidebar Overlay -->
<div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

<div class="container-fluid p-0">
  <div class="row g-0">

    <!-- SIDEBAR -->
    <div class="col-lg-2 col-md-3 sidebar p-0" id="sidebar">
      <a href="hospital_dashboard.py?hospital_id={hospital_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fas fa-home"></i> Home
      </a>
      <a href="hospital_vaccination.py?hospital_id={hospital_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fa-solid fa-circle-info"></i> Vaccination Info
      </a>
      
      <a href="hospital_view_application.py?hospital_id={hospital_id}" class="sidebar-link">
        <i class="fa-solid fa-user-pen"></i> Parent Application
      </a>

      <a href="hospital_view_appointment.py?hospital_id={hospital_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fas fa-calendar-alt"></i> View Appointments
      </a>
      <a href="hospital_profile.py?hospital_id={hospital_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fas fa-user-circle"></i> My Profile
      </a>
      <a href="hospital_feedback.py?hospital_id={hospital_id}" class="sidebar-link active" onclick="closeSidebarMobile()">
        <i class="fas fa-comment-dots"></i> Feedback
      </a>
      <a href="hospital_chat.py?hospital_id={hospital_id}" class="sidebar-link">
        <i class="fas fa-notes-medical"></i> Chats
      </a>
      <a href="hospital_help.py?hospital_id={hospital_id}" class="sidebar-link">
        <i class="fas fa-circle-question"></i> Help & Support
      </a>
    </div>

    <!-- MAIN CONTENT -->
    <div class="col-lg-10 col-md-9 content-col">
      <div class="feedback-wrapper">

""")

if success_msg:
    print(f"""
        <div class="form-card">
          <div class="card-header-bar">
            <i class="fas fa-comment-dots me-2"></i> Hospital Feedback
          </div>
          <div class="card-body">
            <div class="success-state">
              <i class="fas fa-check-circle check-icon"></i>
              <h4>Feedback Submitted!</h4>
              <p>{success_msg}</p>
              <a href="hospital_feedback.py?hospital_id={hospital_id}" class="btn-submit mt-3"
                 style="display:inline-block;width:auto;padding:10px 30px;text-decoration:none;">
                <i class="fas fa-plus me-2"></i> Submit Another Feedback
              </a>
            </div>
          </div>
        </div>
""")
else:
    if error_msg:
        print(f'<div class="alert alert-danger mb-3"><i class="fas fa-exclamation-circle me-2"></i>{error_msg}</div>')

    print(f"""
        <div class="form-card">
          <div class="card-header-bar">
            <i class="fas fa-comment-dots me-2"></i> Share Your Feedback
          </div>
          <div class="card-body">
            <form method="POST" action="hospital_feedback.py" id="feedbackForm">
              <input type="hidden" name="hospital_id" value="{hospital_id}">

              <div class="section-divider"><span><i class="fas fa-hospital me-1"></i> Hospital Information</span></div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Hospital Name <span class="required-star">*</span></label>
                  <input type="text" class="form-control" name="hospital_name"
                         placeholder="Enter your hospital name" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Email Address <span class="required-star">*</span></label>
                  <input type="email" class="form-control" name="email"
                         placeholder="Enter registered email" required>
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Contact Person Name</label>
                  <input type="text" class="form-control" name="contact_person"
                         placeholder="Doctor / Manager name">
                </div>
              </div>

              <div class="section-divider"><span><i class="fas fa-star me-1"></i> Overall Rating</span></div>

              <div class="mb-3">
                <label class="form-label">How would you rate the system? <span class="required-star">*</span></label>
                <div class="star-rating">
                  <input type="radio" name="rating" id="star5" value="5">
                  <label for="star5" title="Excellent"><i class="fas fa-star"></i></label>
                  <input type="radio" name="rating" id="star4" value="4">
                  <label for="star4" title="Good"><i class="fas fa-star"></i></label>
                  <input type="radio" name="rating" id="star3" value="3">
                  <label for="star3" title="Average"><i class="fas fa-star"></i></label>
                  <input type="radio" name="rating" id="star2" value="2">
                  <label for="star2" title="Poor"><i class="fas fa-star"></i></label>
                  <input type="radio" name="rating" id="star1" value="1">
                  <label for="star1" title="Very Poor"><i class="fas fa-star"></i></label>
                </div>
                <small class="text-muted mt-2 d-block" id="ratingLabel">Click a star to rate</small>
              </div>

              <div class="section-divider"><span><i class="fas fa-tags me-1"></i> Feedback Category</span></div>

              <div class="mb-3">
                <label class="form-label">What is your feedback about?</label>
                <div class="category-pills">
                  <input type="radio" name="category" id="cat1" value="Appointment System">
                  <label for="cat1"><i class="fas fa-calendar-check me-1"></i> Appointment System</label>

                  <input type="radio" name="category" id="cat2" value="Vaccine Management">
                  <label for="cat2"><i class="fas fa-syringe me-1"></i> Vaccine Management</label>

                  <input type="radio" name="category" id="cat3" value="Parent Communication">
                  <label for="cat3"><i class="fas fa-comments me-1"></i> Parent Communication</label>

                  <input type="radio" name="category" id="cat4" value="App / Website">
                  <label for="cat4"><i class="fas fa-laptop me-1"></i> App / Website</label>

                  <input type="radio" name="category" id="cat5" value="Reports & Data">
                  <label for="cat5"><i class="fas fa-chart-bar me-1"></i> Reports & Data</label>

                  <input type="radio" name="category" id="cat6" value="General">
                  <label for="cat6"><i class="fas fa-comment me-1"></i> General</label>
                </div>
              </div>

              <div class="section-divider"><span><i class="fas fa-pen me-1"></i> Your Feedback</span></div>

              <div class="mb-3">
                <label class="form-label">Describe your experience <span class="required-star">*</span></label>
                <textarea class="form-control" name="feedback_text" id="feedbackText" rows="4"
                          placeholder="Share your experience, issues faced, or what you liked..."
                          maxlength="1000" oninput="updateCounter()" required></textarea>
                <div class="char-counter"><span id="charCount">0</span> / 1000 characters</div>
              </div>

              <div class="mb-4">
                <label class="form-label">Suggestions for Improvement</label>
                <textarea class="form-control" name="suggestion" rows="3"
                          placeholder="Any suggestions to improve the system for hospitals?"
                          maxlength="500"></textarea>
              </div>

              <button type="submit" name="submit_feedback" value="1" class="btn-submit">
                <i class="fas fa-paper-plane me-2"></i> Submit Feedback
              </button>

            </form>
          </div>
        </div>
""")

print("""
        <div class="footer-note">
          <i class="fas fa-lock me-1"></i> Your feedback is confidential and helps us improve our services.
        </div>

      </div><!-- /feedback-wrapper -->
    </div><!-- /content-col -->
  </div><!-- /row -->
</div><!-- /container-fluid -->

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
  /* ===== STAR RATING ===== */
  const ratingLabels = { '5':'⭐ Excellent', '4':'👍 Good', '3':'😐 Average', '2':'👎 Poor', '1':'😞 Very Poor' };

  document.querySelectorAll('.star-rating input').forEach(input => {
    input.addEventListener('change', function() {
      document.getElementById('ratingLabel').textContent = ratingLabels[this.value] || 'Click a star to rate';
    });
  });

  /* ===== CHARACTER COUNTER ===== */
  function updateCounter() {
    document.getElementById('charCount').textContent = document.getElementById('feedbackText').value.length;
  }

  /* ===== FORM VALIDATION ===== */
  document.getElementById('feedbackForm').addEventListener('submit', function(e) {
    if (!document.querySelector('input[name="rating"]:checked')) {
      e.preventDefault();
      alert('Please select a star rating before submitting.');
    }
  });

  /* ===== SIDEBAR TOGGLE ===== */
  function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    sidebar.classList.toggle('show');
    overlay.classList.toggle('show');
  }

  function closeSidebarMobile() {
    if (window.innerWidth < 992) {
      document.getElementById('sidebar').classList.remove('show');
      document.getElementById('sidebarOverlay').classList.remove('show');
    }
  }

  /* ===== LOGOUT ===== */
  function logout() {
    if (confirm('Are you sure you want to logout?')) {
      window.location.href = 'main.py';
    }
  }

  /* Close sidebar when clicking outside on mobile */
  document.addEventListener('click', function(event) {
    const sidebar    = document.getElementById('sidebar');
    const menuToggle = document.querySelector('.mobile-menu-toggle');
    if (window.innerWidth < 992 &&
        !sidebar.contains(event.target) &&
        !menuToggle.contains(event.target) &&
        sidebar.classList.contains('show')) {
      closeSidebarMobile();
    }
  });
</script>
</body>
</html>
""")