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
parent_id = form.getvalue("parent_id", "")

# Handle form submission
if form.getvalue("submit_feedback"):
    parent_name   = form.getvalue("parent_name", "").strip()
    email         = form.getvalue("email", "").strip()
    child_name    = form.getvalue("child_name", "").strip()
    hospital_name = form.getvalue("hospital_name", "").strip()
    rating        = form.getvalue("rating", "").strip()
    category      = form.getvalue("category", "").strip()
    feedback_text = form.getvalue("feedback_text", "").strip()

    if not parent_name or not email or not rating or not feedback_text:
        error_msg = "Please fill in all required fields."
    else:
        try:
            con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
            cur = con.cursor()
            sql = """INSERT INTO parent_feedback
                     (parent_name, email, child_name, hospital_name, rating, category, feedback_text)
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cur.execute(sql, (parent_name, email, child_name, hospital_name, rating, category, feedback_text))
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
<title>Parent Feedback - Child Vaccination System</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  background: linear-gradient(135deg, #052e16, #22c55e, #dcfce7);
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow-x: hidden;
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
  font-weight: 600;
  color: white !important;
  letter-spacing: 2px;
  text-transform: uppercase;
}}
.navbar-brand i {{
  margin-right: 10px; color: #d1fae5; font-size: 1.5rem; animation: bounce 2s infinite;
}}
@keyframes bounce {{
  0%,100% {{ transform: translateY(0); }}
  50%      {{ transform: translateY(-5px); }}
}}

/* Hamburger — hidden on desktop, flex on mobile */
.navbar-toggler-custom {{
  display: none; flex-shrink: 0;
  background: rgba(255,255,255,0.15); border: 1.5px solid rgba(255,255,255,0.4);
  color: white; padding: 6px 11px; border-radius: 8px; font-size: 1.15rem;
  cursor: pointer; line-height: 1; transition: background 0.25s;
  order: -1;
}}
.navbar-toggler-custom:hover {{ background: rgba(255,255,255,0.28); }}

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
  background: linear-gradient(135deg, #052e16, #22c55e);
  box-shadow: 4px 0 20px rgba(0,0,0,0.3);
  padding: 20px 0;
}}
.sidebar-link {{
  display: block; padding: 14px 18px; color: #d1fae5; text-decoration: none;
  cursor: pointer; transition: all 0.3s ease; border-left: 4px solid transparent;
  font-weight: 500; margin: 6px 0;
}}

.sidebar-link:hover, .sidebar-link.active {{
  background: linear-gradient(90deg, #22c55e, transparent 100%);
  color: #fff; border-left: 4px solid #dcfce7; padding-left: 24px;
}}
.sidebar-link i {{ margin-right: 12px; width: 22px; text-align: center; }}

.sidebar-overlay {{
  display: none; position: fixed; top:0; left:0;
  width:100%; height:100%; background:rgba(0,0,0,0.6); z-index:998; backdrop-filter:blur(2px);
}}
.sidebar-overlay.show {{ display: block; }}

/* ===== CONTENT ===== */
.content-col {{ padding: 30px 20px; }}

.feedback-wrapper {{
  width: 100%; max-width: 750px; margin: 0 auto;
}}

.form-card {{
  background: white; border-radius: 20px;
  box-shadow: 0 15px 50px rgba(0,0,0,0.2); overflow: hidden;
}}

.card-header-bar {{
  background: linear-gradient(135deg, #047857 0%, #059669 100%);
  padding: 18px 25px; color: white; font-size: 1.1rem; font-weight: 600;
}}

.card-body {{ padding: 30px; }}

.form-label {{ font-weight:600; color:#333; margin-bottom:6px; font-size:0.92rem; }}
.required-star {{ color: #e53e3e; }}

.form-control, .form-select {{
  border: 2px solid #e2e8f0; border-radius: 10px;
  padding: 10px 14px; font-size: 0.92rem; transition: all 0.3s ease;
}}
.form-control:focus, .form-select:focus {{
  border-color: #059669; box-shadow: 0 0 0 3px rgba(5,150,105,0.2);
}}

/* STAR RATING */
.star-rating {{
  display: flex; flex-direction: row-reverse; justify-content: flex-end; gap: 6px; margin-top: 4px;
}}
.star-rating input {{ display: none; }}
.star-rating label {{
  font-size: 2rem; color: #d1d5db; cursor: pointer; transition: color 0.2s ease, transform 0.2s ease;
}}
.star-rating input:checked ~ label,
.star-rating label:hover,
.star-rating label:hover ~ label {{ color: #f59e0b; transform: scale(1.1); }}

/* CATEGORY PILLS */
.category-pills {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 6px; }}
.category-pills input {{ display: none; }}
.category-pills label {{
  padding: 7px 18px; border-radius: 25px; border: 2px solid #059669;
  color: #059669; font-weight: 600; font-size: 0.85rem;
  cursor: pointer; transition: all 0.2s ease; user-select: none;
}}
.category-pills input:checked + label {{
  background: linear-gradient(135deg, #047857 0%, #059669 100%);
  color: white; border-color: transparent; box-shadow: 0 4px 12px rgba(5,150,105,0.4);
}}
.category-pills label:hover {{ background: rgba(5,150,105,0.1); }}

/* CHARACTER COUNTER */
.char-counter {{ font-size: 0.78rem; color: #9ca3af; text-align: right; margin-top: 4px; }}

/* SUBMIT BUTTON */
.btn-submit {{
  background: linear-gradient(135deg, #052e16, #22c55e);
  border: none; padding: 13px 40px; border-radius: 30px;
  color: white; font-weight: 700; font-size: 1rem;
  transition: all 0.3s ease; box-shadow: 0 5px 20px rgba(5,150,105,0.4);
  width: 100%; cursor: pointer;
}}
.btn-submit:hover {{ transform: translateY(-2px); box-shadow: 0 8px 25px rgba(5,150,105,0.6); color: white; }}

/* SECTION DIVIDER */
.section-divider {{ display: flex; align-items: center; gap: 10px; margin: 20px 0 15px; }}
.section-divider span {{
  font-weight: 700; color: #4b5563; font-size: 0.88rem;
  text-transform: uppercase; letter-spacing: 0.5px; white-space: nowrap;
}}
.section-divider::before, .section-divider::after {{
  content: ''; flex: 1; height: 1px; background: #e5e7eb;
}}

.alert {{ border-radius: 12px; border: none; padding: 14px 20px; }}
.alert-success {{ background: #d1fae5; color: #065f46; }}
.alert-danger  {{ background: #fee2e2; color: #991b1b; }}

/* SUCCESS STATE */
.success-state {{ text-align: center; padding: 40px 20px; }}
.success-state .check-icon {{
  font-size: 4rem; color: #10b981; margin-bottom: 15px;
  display: block; animation: bounceIn 0.6s ease;
}}
@keyframes bounceIn {{
  0%   {{ transform: scale(0); }}
  60%  {{ transform: scale(1.2); }}
  100% {{ transform: scale(1); }}
}}
.success-state h4 {{ font-weight: 700; color: #065f46; margin-bottom: 10px; }}
.success-state p  {{ color: #6b7280; }}

.footer-note {{
  text-align: center; color: rgba(255,255,255,0.7);
  font-size: 0.82rem; margin-top: 20px; padding-bottom: 20px;
}}

/* ===== RESPONSIVE ===== */
@media (max-width: 991.98px) {{
  /* Show hamburger inside navbar */
  .navbar-toggler-custom {{ display: flex; align-items: center; justify-content: center; }}
  .sidebar {{
    position: fixed; left: -100%; top: 0;
    width: 280px; height: 100vh; z-index: 999; transition: left 0.3s ease; overflow-y: auto;
  }}
  .sidebar.show {{ left: 0; }}
  .content-col {{ padding: 15px 10px; }}
  /* Navbar text — tablet */
  .navbar-brand   {{ font-size: 1rem; letter-spacing: 1px; }}
  .navbar-brand i {{ font-size: 1.3rem; }}
}}
@media (max-width: 767.98px) {{
  .content-col {{ padding: 12px 8px; }}
  .btn-logout {{ padding: 6px 16px; font-size: 0.85rem; }}
}}
@media (max-width: 575.98px) {{
  /* Navbar text — small mobile */
  .navbar-brand   {{ font-size: 0.85rem; letter-spacing: 0.5px; }}
  .navbar-brand i {{ font-size: 1.1rem; margin-right: 6px; }}
  .btn-logout     {{ padding: 6px 12px; font-size: 0.8rem; }}
}}
@media (max-width: 400px) {{
  /* Navbar text — very small */
  .navbar-brand {{ font-size: 0.75rem; }}
}}
</style>
</head>
<body>

<!-- NAVBAR -->
<nav class="navbar navbar-dark">
  <div class="container-fluid">

    <!-- Hamburger: order:-1 keeps it leftmost, hidden on desktop -->
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

<div class="container-fluid p-0">
  <div class="row g-0">

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
      <a href="parent_reminder.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fas fa-bell"></i> My Reminders
      </a>
      <a href="parent_profile.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fas fa-user-circle"></i> My Profile
      </a>
      <a href="parent_feedback.py?parent_id={parent_id}" class="sidebar-link active" onclick="closeSidebarMobile()">
        <i class="fas fa-comment-dots"></i> Feedback
      </a>
      <a href="parent_help.py?parent_id={parent_id}" class="sidebar-link" onclick="closeSidebarMobile()">
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
            <i class="fas fa-comment-dots me-2"></i> Parent Feedback
          </div>
          <div class="card-body">
            <div class="success-state">
              <i class="fas fa-check-circle check-icon"></i>
              <h4>Feedback Submitted!</h4>
              <p>{success_msg}</p>
              <a href="parent_feedback.py?parent_id={parent_id}" class="btn-submit mt-3"
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
            <form method="POST" action="parent_feedback.py" id="feedbackForm">
              <input type="hidden" name="parent_id" value="{parent_id}">

              <div class="section-divider"><span><i class="fas fa-user me-1"></i> Parent Information</span></div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Parent Name <span class="required-star">*</span></label>
                  <input type="text" class="form-control" name="parent_name"
                         placeholder="Enter registered name" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Email Address <span class="required-star">*</span></label>
                  <input type="email" class="form-control" name="email"
                         placeholder="Enter registered email" required>
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Child's Name</label>
                  <input type="text" class="form-control" name="child_name" placeholder="Enter child's name">
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Hospital / Clinic Name</label>
                  <input type="text" class="form-control" name="hospital_name"
                         placeholder="Which hospital did you visit?">
                </div>
              </div>

              <div class="section-divider"><span><i class="fas fa-star me-1"></i> Overall Rating</span></div>

              <div class="mb-3">
                <label class="form-label">How would you rate your experience? <span class="required-star">*</span></label>
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
                  <input type="radio" name="category" id="cat1" value="Vaccination Service">
                  <label for="cat1"><i class="fas fa-syringe me-1"></i> Vaccination Service</label>
                  <input type="radio" name="category" id="cat2" value="Staff Behaviour">
                  <label for="cat2"><i class="fas fa-user-nurse me-1"></i> Staff Behaviour</label>
                  <input type="radio" name="category" id="cat3" value="Hospital Facility">
                  <label for="cat3"><i class="fas fa-hospital me-1"></i> Hospital Facility</label>
                  <input type="radio" name="category" id="cat4" value="App / Website">
                  <label for="cat4"><i class="fas fa-laptop me-1"></i> App / Website</label>
                  <input type="radio" name="category" id="cat5" value="Appointment Booking">
                  <label for="cat5"><i class="fas fa-calendar-check me-1"></i> Appointment Booking</label>
                  <input type="radio" name="category" id="cat6" value="General">
                  <label for="cat6"><i class="fas fa-comment me-1"></i> General</label>
                </div>
              </div>

              <div class="section-divider"><span><i class="fas fa-pen me-1"></i> Your Feedback</span></div>

              <div class="mb-4">
                <label class="form-label">Please describe your experience <span class="required-star">*</span></label>
                <textarea class="form-control" name="feedback_text" id="feedbackText" rows="5"
                          placeholder="Share your experience, suggestions, or any issues you faced..."
                          maxlength="1000" oninput="updateCounter()" required></textarea>
                <div class="char-counter"><span id="charCount">0</span> / 1000 characters</div>
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
/* RATING LABELS */
const ratingLabels = { '5':'⭐ Excellent', '4':'👍 Good', '3':'😐 Average', '2':'👎 Poor', '1':'😞 Very Poor' };
document.querySelectorAll('.star-rating input').forEach(input => {
  input.addEventListener('change', function() {
    document.getElementById('ratingLabel').textContent = ratingLabels[this.value] || 'Click a star to rate';
  });
});

/* CHARACTER COUNTER */
function updateCounter() {
  document.getElementById('charCount').textContent = document.getElementById('feedbackText').value.length;
}

/* FORM VALIDATION */
document.getElementById('feedbackForm').addEventListener('submit', function(e) {
  if (!document.querySelector('input[name="rating"]:checked')) {
    e.preventDefault();
    alert('Please select a star rating before submitting.');
  }
});

/* SIDEBAR TOGGLE */
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

/* Close sidebar when clicking outside on mobile */
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
</html>
""")