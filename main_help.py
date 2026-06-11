from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

# ── DB ────────────────────────────────────────────────────────────────────────
def get_db():
    try:
        con = pymysql.connect(host="localhost", user="root", password="", database="cvsdp")
        return con, con.cursor()
    except Exception as e:
        return None, str(e)

# ── Ensure public_support_ticket table exists ─────────────────────────────────
def ensure_table():
    con, cur = get_db()
    if con is None:
        return
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS public_support_ticket (
                ticket_id      INT(11)      AUTO_INCREMENT PRIMARY KEY,
                full_name      VARCHAR(100) NOT NULL,
                contact_email  VARCHAR(100) NOT NULL,
                user_role      VARCHAR(50)  NOT NULL,
                issue_category VARCHAR(100) NOT NULL,
                priority       VARCHAR(50)  NOT NULL,
                description    TEXT         NOT NULL,
                status         VARCHAR(30)  DEFAULT 'open',
                created_at     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
            )
        """)
        con.commit()
    except Exception:
        pass
    finally:
        con.close()

def send_json(ok, msg="", ticket_id=None):
    payload = {"success": ok, "message": msg}
    if ticket_id:
        payload["ticket_id"] = ticket_id
    return jsonify(payload)


def handle_ticket_submission(form):
    full_name     = form.get('full_name',      '').strip()
    contact_email = form.get('contact_email',  '').strip()
    user_role     = form.get('user_role',       '').strip()
    issue_cat     = form.get('issue_category',  '').strip()
    priority      = form.get('priority',        '').strip()
    description   = form.get('description',     '').strip()

    if not full_name:
        return send_json(False, "Your name is required.")
    if not contact_email or "@" not in contact_email:
        return send_json(False, "A valid contact email is required.")
    if not user_role or user_role == "-- Select Role --":
        return send_json(False, "Please select your role.")
    if not issue_cat or issue_cat == "-- Select Category --":
        return send_json(False, "Please select an issue category.")
    if not priority:
        return send_json(False, "Priority is required.")
    if not description:
        return send_json(False, "Please describe your issue.")

    con, cur = get_db()
    if con is None:
        return send_json(False, f"Database connection failed: {cur}")

    try:
        cur.execute(
            """INSERT INTO public_support_ticket
               (full_name, contact_email, user_role, issue_category, priority, description, status)
               VALUES (%s, %s, %s, %s, %s, %s, 'open')""",
            (full_name, contact_email, user_role, issue_cat, priority, description)
        )
        con.commit()
        ticket_id = cur.lastrowid
        con.close()
        return send_json(
            True,
            f"Support ticket TKT-{ticket_id:05d} submitted successfully! "
            f"Our team will respond within 24 hours.",
            f"TKT-{ticket_id:05d}"
        )
    except Exception as e:
        try:
            con.rollback()
            con.close()
        except Exception:
            pass
        return send_json(False, f"Database error: {str(e)}")


# ============================================================
# PAGE LOAD — GET
# ============================================================
HELP_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Help & Support | Child Vaccination System</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<style>
* { margin:0; padding:0; box-sizing:border-box; }

body {
  background: #f4f6f9;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow-x: hidden;
}

/* ── NAVBAR ── */
.navbar {
  background: linear-gradient(135deg, #1e3a5f, #4585c6, #6fa8d8) !important;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
  padding: 13px 16px;
}
.navbar .container {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  justify-content: space-between !important;
  flex-wrap: nowrap !important;
  gap: 8px;
  width: 100%;
  max-width: 100%;
  padding-left: 0;
  padding-right: 0;
}
.navbar-brand {
  font-weight: 700; color: white !important;
  letter-spacing: 1.5px; text-transform: uppercase; font-size: 1rem;
  flex-shrink: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.btn-back {
  background: linear-gradient(135deg, #fff3, #ffffff22);
  border: 1.5px solid rgba(255,255,255,0.4);
  color: white; padding: 7px 20px; border-radius: 25px;
  font-weight: 600; font-size: 0.88rem; transition: all 0.3s;
  text-decoration: none; white-space: nowrap;
  flex-shrink: 0;
}
.btn-back:hover {
  background: rgba(255,255,255,0.25); color: white;
  transform: translateY(-2px);
}

@media (max-width: 576px) {
  .navbar { padding: 15px 14px; }
  .navbar-brand { font-size: 0.82rem; letter-spacing: 0.5px; }
  .btn-back { padding: 6px 14px; font-size: 0.82rem; }
}
@media (max-width: 400px) {
  .navbar { padding: 9px 10px; }
  .navbar-brand { font-size: 0.72rem; letter-spacing: 0.3px; }
  .btn-back { padding: 5px 11px; font-size: 0.75rem; }
}
@media (max-width: 320px) {
  .navbar-brand { font-size: 0.65rem; letter-spacing: 0; }
  .btn-back { padding: 5px 9px; font-size: 0.7rem; }
}

/* ── HERO BANNER ── */
.help-hero {
  background: linear-gradient(135deg, #1e3a5f 0%, #4585c6 50%, #8cdec4 100%);
  color: white; padding: 81px 0 60px;
  position: relative; overflow: hidden; text-align: center;
}
.help-hero::before {
  content: ''; position: absolute; top: -40%; right: -10%;
  width: 500px; height: 500px; background: rgba(255,255,255,0.07);
  border-radius: 50%; animation: float 8s ease-in-out infinite;
}
.help-hero::after {
  content: ''; position: absolute; bottom: -30%; left: -10%;
  width: 400px; height: 400px; background: rgba(255,255,255,0.06);
  border-radius: 50%; animation: float 10s ease-in-out infinite reverse;
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}
.help-hero h1 { font-size: 2.4rem; font-weight: 800; text-shadow: 2px 2px 10px rgba(0,0,0,0.2); }
.help-hero p { font-size: 1.1rem; opacity: 0.92; margin-top: 12px; }

/* ── SEARCH BAR ── */
.search-wrap {
  margin-top: -28px; position: relative; z-index: 10;
}
.search-box {
  background: white; border-radius: 50px; padding: 8px 8px 8px 25px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.15);
  display: flex; align-items: center; gap: 10px; max-width: 600px; margin: 0 auto;
}
.search-box input {
  border: none; outline: none; flex: 1; font-size: 1rem; color: #333;
  background: transparent;
}
.search-box button {
  background: linear-gradient(135deg, #4585c6, #6fa8d8);
  border: none; color: white; border-radius: 40px;
  padding: 10px 28px; font-weight: 700; font-size: 0.9rem; cursor: pointer;
  transition: all 0.3s; white-space: nowrap;
}
.search-box button:hover { opacity: 0.88; transform: scale(1.03); }

/* ── CONTACT CARDS ── */
.contact-card {
  background: white; border-radius: 18px; padding: 28px 22px;
  text-align: center; box-shadow: 0 8px 25px rgba(0,0,0,0.1);
  border-top: 4px solid; height: 100%; transition: transform 0.3s;
}
.contact-card:hover { transform: translateY(-5px); }
.contact-card.blue  { border-color: #4585c6; }
.contact-card.teal  { border-color: #0ea5e9; }
.contact-card.green { border-color: #22c55e; }
.contact-card.dark  { border-color: #1e3a5f; }
.icon-circle {
  width: 65px; height: 65px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 15px; font-size: 1.6rem;
}
.contact-card.blue  .icon-circle { background: #dbeafe; color: #4585c6; }
.contact-card.teal  .icon-circle { background: #e0f2fe; color: #0ea5e9; }
.contact-card.green .icon-circle { background: #dcfce7; color: #22c55e; }
.contact-card.dark  .icon-circle { background: #e0e7ff; color: #1e3a5f; }
.contact-card h5 { font-weight: 700; color: #1e3a5f; margin-bottom: 8px; }
.contact-card p  { color: #6b7280; font-size: 0.87rem; margin-bottom: 15px; }
.contact-card a {
  display: inline-block; padding: 8px 22px; border-radius: 20px;
  font-weight: 600; font-size: 0.85rem; text-decoration: none; color: white;
}
.contact-card.blue  a { background: linear-gradient(135deg, #4585c6, #6fa8d8); }
.contact-card.teal  a { background: linear-gradient(135deg, #0ea5e9, #22d3ee); }
.contact-card.green a { background: linear-gradient(135deg, #22c55e, #4ade80); }
.contact-card.dark  a { background: linear-gradient(135deg, #1e3a5f, #4585c6); }
.contact-card a:hover { opacity: 0.88; color: white; }

/* ── SECTION CARD ── */
.section-card {
  background: white; border-radius: 18px; padding: 28px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.08); margin-bottom: 28px;
}
.section-card h5 {
  font-weight: 700; color: #1e3a5f; margin-bottom: 22px;
  display: flex; align-items: center; gap: 10px; font-size: 1.1rem;
  border-bottom: 2px solid #e5e7eb; padding-bottom: 12px;
}
.section-card h5 i { color: #4585c6; font-size: 1.2rem; }

/* ── QUICK GUIDE ── */
.guide-card {
  background: linear-gradient(135deg, #eff6ff, #dbeafe);
  border-radius: 14px; padding: 20px;
  height: 100%; border-left: 4px solid #4585c6;
  transition: transform 0.3s;
}
.guide-card:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(69,133,198,0.15); }
.step-num {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, #1e3a5f, #4585c6); color: white;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.9rem; margin-bottom: 12px;
}
.guide-card h6 { font-weight: 700; color: #1e3a5f; margin-bottom: 8px; }
.guide-card p  { color: #555; font-size: 0.87rem; margin: 0; }

/* ── ROLE TABS ── */
.role-tab {
  padding: 9px 22px; border-radius: 25px; border: 2px solid #4585c6;
  color: #4585c6; font-weight: 600; cursor: pointer; font-size: 0.88rem;
  transition: all 0.3s; background: white; margin: 4px;
}
.role-tab.active, .role-tab:hover {
  background: linear-gradient(135deg, #4585c6, #6fa8d8);
  color: white; border-color: transparent;
}

/* ── FAQ ── */
.accordion-button { font-weight: 600; color: #1e3a5f; background: #eff6ff; }
.accordion-button:not(.collapsed) { background: #dbeafe; color: #1e40af; box-shadow: none; }
.accordion-button:focus { box-shadow: none; }
.accordion-body { color: #555; line-height: 1.75; font-size: 0.93rem; }
.accordion-item {
  border: 1px solid #bfdbfe; border-radius: 10px !important;
  margin-bottom: 8px; overflow: hidden;
}

/* ── TICKET FORM ── */
.form-label  { font-weight: 600; color: #1e3a5f; font-size: 0.9rem; }
.form-control, .form-select {
  border: 2px solid #bfdbfe; border-radius: 10px;
  padding: 10px 14px; font-size: 0.9rem;
}
.form-control:focus, .form-select:focus {
  border-color: #4585c6; box-shadow: 0 0 0 3px rgba(69,133,198,0.15);
}
.btn-submit {
  background: linear-gradient(135deg, #1e3a5f, #4585c6); color: white;
  border: none; padding: 12px 40px; border-radius: 25px; font-weight: 700;
  cursor: pointer; box-shadow: 0 4px 15px rgba(69,133,198,0.4);
  transition: all 0.3s; font-size: 0.95rem;
}
.btn-submit:hover { opacity: 0.9; transform: translateY(-2px); }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

/* ── INFO BOX ── */
.info-box {
  background: #eff6ff; border-radius: 12px; padding: 16px 18px;
  display: flex; align-items: center; gap: 14px;
}
.info-box i { font-size: 1.5rem; flex-shrink: 0; }

/* ── TOAST ── */
#toastContainer {
  position: fixed; top: 80px; right: 20px; z-index: 9999; width: 340px;
}
.custom-toast {
  padding: 14px 18px; border-radius: 12px; margin-bottom: 10px;
  display: flex; align-items: flex-start; gap: 12px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15); animation: slideIn 0.4s ease;
  font-size: 0.9rem; line-height: 1.4;
}
@keyframes slideIn {
  from { opacity: 0; transform: translateX(40px); }
  to   { opacity: 1; transform: translateX(0); }
}
.toast-success { background: #f0fdf4; border-left: 4px solid #22c55e; color: #166534; }
.toast-error   { background: #fef2f2; border-left: 4px solid #ef4444; color: #991b1b; }
.custom-toast i { font-size: 1.1rem; margin-top: 1px; flex-shrink: 0; }

/* ── FAQ TAB CONTENT ── */
.faq-pane { display: none; }
.faq-pane.active { display: block; }

/* ── RESPONSIVE ── */
@media (max-width: 768px) {
  .help-hero { padding: 55px 15px 50px; }
  .help-hero h1 { font-size: 1.7rem; }
  .help-hero p  { font-size: 0.92rem; }
  .help-hero .fa-headset { font-size: 2.6rem !important; }
  .search-wrap { margin-top: -22px; }
  .search-box  { margin: 0 12px; padding: 7px 7px 7px 18px; }
  .search-box input { font-size: 0.9rem; }
  .search-box button { padding: 8px 16px; font-size: 0.82rem; }
  .section-card { padding: 18px; }
  .btn-submit   { width: 100%; }
  .role-tab { padding: 7px 14px; font-size: 0.82rem; margin: 3px; }
}
@media (max-width: 480px) {
  .help-hero { padding: 50px 12px 45px; }
  .help-hero h1 { font-size: 1.45rem; }
  .help-hero p  { font-size: 0.87rem; }
  .search-box { flex-wrap: nowrap; }
  .search-box button { padding: 8px 12px; font-size: 0.78rem; }
  .section-card h5 { font-size: 1rem; }
  .guide-card { padding: 16px; }
  .role-tab { padding: 6px 10px; font-size: 0.78rem; margin: 2px; }
}

</style>
</head>
<body>

<!-- TOAST CONTAINER -->
<div id="toastContainer"></div>

<!-- NAVBAR -->
<nav class="navbar navbar-expand-lg navbar-dark fixed-top">
  <div class="container-fluid d-flex align-items-center justify-content-between">
    <span class="navbar-brand">
       Child Vaccination System
    </span>
    <a href="main.py" class="btn-back">
      <i class="fa-solid fa-arrow-left me-1"></i> Back to Home
    </a>
  </div>
</nav>

<!-- HERO BANNER -->
<section class="help-hero" style="margin-top:62px;">
  <div class="container position-relative" style="z-index:2;">
    <div class="mb-3">
      <i class="fa-solid fa-headset" style="font-size:3.5rem; opacity:0.92;"></i>
    </div>
    <h1>How Can We Help You?</h1>
    <p>Browse FAQs, quick guides, or submit a support ticket — we're here to help.</p>
  </div>
</section>

<!-- SEARCH BAR -->
<div class="container search-wrap mb-5">
  <div class="search-box">
    <i class="fa-solid fa-magnifying-glass text-secondary"></i>
    <input type="text" id="searchInput" placeholder="Search FAQs, topics, or keywords..." oninput="searchFAQ(this.value)">
    <button onclick="searchFAQ(document.getElementById('searchInput').value)">
      <i class="fa-solid fa-search me-1"></i> Search
    </button>
  </div>
  <div id="searchResults" class="mt-3" style="max-width:600px;margin:12px auto 0;display:none;">
    <div class="section-card p-3" id="searchResultsContent"></div>
  </div>
</div>

<!-- CONTACT CARDS -->
<section class="container mb-5">
  <div class="row g-4">
    <div class="col-lg-3 col-md-6">
      <div class="contact-card blue">
        <div class="icon-circle"><i class="fas fa-envelope"></i></div>
        <h5>Email Us</h5>
        <p>Send your query and get a response within 24 business hours.</p>
        <a href="mailto:childvaccinationsystem2026@gmail.com">
          <i class="fas fa-paper-plane me-1"></i> Send Email
        </a>
      </div>
    </div>
    <div class="col-lg-3 col-md-6">
      <div class="contact-card teal">
        <div class="icon-circle"><i class="fas fa-phone-alt"></i></div>
        <h5>Call Support</h5>
        <p>Mon–Sat, 9:00 AM – 6:00 PM IST. Immediate assistance available.</p>
        <a href="tel:+919345790381">
          <i class="fas fa-phone me-1"></i> +91 93457 90381
        </a>
      </div>
    </div>
    <div class="col-lg-3 col-md-6">
      <div class="contact-card green">
        <div class="icon-circle"><i class="fas fa-ticket-alt"></i></div>
        <h5>Submit Ticket</h5>
        <p>Raise a support ticket and track it. We respond within 24 hours.</p>
        <a href="#ticketSection" onclick="scrollToTicket()">
          <i class="fas fa-arrow-down me-1"></i> Raise Ticket
        </a>
      </div>
    </div>
    <div class="col-lg-3 col-md-6">
      <div class="contact-card dark">
        <div class="icon-circle"><i class="fas fa-map-marker-alt"></i></div>
        <h5>Head Office</h5>
        <p>Health Department, Government of India, New Delhi - 110001.</p>
        <a href="#">
          <i class="fas fa-directions me-1"></i> Get Directions
        </a>
      </div>
    </div>
  </div>
</section>

<!-- QUICK START GUIDES -->
<section class="container mb-5">
  <div class="section-card">
    <h5><i class="fas fa-rocket"></i> Quick Start Guides</h5>
    <div class="row g-3">
      <div class="col-lg-3 col-md-6">
        <div class="guide-card">
          <div class="step-num">1</div>
          <h6>Register as Hospital</h6>
          <p>Click Login → Hospital → Register as Hospital. Fill all sections and upload required documents. Admin will review and approve your application.</p>
        </div>
      </div>
      <div class="col-lg-3 col-md-6">
        <div class="guide-card">
          <div class="step-num">2</div>
          <h6>Register as Parent</h6>
          <p>Click Login → Parent → Register as Parent. Provide your details, child information, and ID proof. You'll receive login credentials after approval.</p>
        </div>
      </div>
      <div class="col-lg-3 col-md-6">
        <div class="guide-card">
          <div class="step-num">3</div>
          <h6>Book a Vaccination</h6>
          <p>Log in as Parent, go to View Hospital, select a hospital and fill the appointment form with your child's details and preferred date.</p>
        </div>
      </div>
      <div class="col-lg-3 col-md-6">
        <div class="guide-card">
          <div class="step-num">4</div>
          <h6>Track Vaccination</h6>
          <p>After login, visit Vaccination Info to view your child's completed and upcoming vaccines, schedule reminders, and download records.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- FAQs -->
<section class="container mb-5">
  <div class="section-card">
    <h5><i class="fas fa-circle-question"></i> Frequently Asked Questions</h5>

    <!-- Role Tabs -->
    <div class="mb-4 text-center">
      <button class="role-tab active" onclick="showFAQ('general', this)">
        <i class="fas fa-globe me-1"></i> General
      </button>
      <button class="role-tab" onclick="showFAQ('parent', this)">
        <i class="fas fa-users me-1"></i> Parents
      </button>
      <button class="role-tab" onclick="showFAQ('hospital', this)">
        <i class="fas fa-hospital me-1"></i> Hospitals
      </button>
    </div>

    <!-- General FAQ -->
    <div class="faq-pane active" id="faq-general">
      <div class="accordion" id="genFAQ">
        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#g1">
              <i class="fas fa-info-circle me-2 text-primary"></i> What is the Child Vaccination System?
            </button>
          </h2>
          <div id="g1" class="accordion-collapse collapse show" data-bs-parent="#genFAQ">
            <div class="accordion-body">
              The Child Vaccination System (CVS) is a digital healthcare platform that helps parents track vaccination records, book appointments at registered hospitals, and receive timely reminders for upcoming vaccines. Hospitals can manage vaccination schedules and records, while admins oversee the entire system.
            </div>
          </div>
        </div>
        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#g2">
              <i class="fas fa-user-plus me-2 text-success"></i> Who can register on this platform?
            </button>
          </h2>
          <div id="g2" class="accordion-collapse collapse" data-bs-parent="#genFAQ">
            <div class="accordion-body">
              Any <strong>parent or guardian</strong> with children requiring vaccination can register. <strong>Hospitals and clinics</strong> providing vaccination services can also register. All registrations are reviewed and approved by the system administrator before access is granted.
            </div>
          </div>
        </div>
        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#g3">
              <i class="fas fa-lock me-2 text-warning"></i> Is my data safe and secure?
            </button>
          </h2>
          <div id="g3" class="accordion-collapse collapse" data-bs-parent="#genFAQ">
            <div class="accordion-body">
              Yes. All personal information and health records are stored securely in our database. Your data is never shared with third parties. We follow strict data protection guidelines to ensure your privacy.
            </div>
          </div>
        </div>
        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#g4">
              <i class="fas fa-key me-2 text-danger"></i> I forgot my User ID or Password. What do I do?
            </button>
          </h2>
          <div id="g4" class="accordion-collapse collapse" data-bs-parent="#genFAQ">
            <div class="accordion-body">
              On the Login screen, click <strong>"Forgot User ID / Password?"</strong>. Enter your registered User ID and email address — your credentials will be displayed. If you still face issues, contact our support team at <strong>childvaccinationsystem2026@gmail.com</strong>.
            </div>
          </div>
        </div>
        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#g5">
              <i class="fas fa-mobile-alt me-2 text-info"></i> Can I use this system on my mobile?
            </button>
          </h2>
          <div id="g5" class="accordion-collapse collapse" data-bs-parent="#genFAQ">
            <div class="accordion-body">
              Yes! The Child Vaccination System is fully responsive and works on smartphones, tablets, and desktops. You can access it through any modern web browser without needing to install an app.
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Parent FAQ -->
    <div class="faq-pane" id="faq-parent">
      <div class="accordion" id="parFAQ">
        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#p1">
              <i class="fas fa-baby me-2 text-success"></i> How do I add my child to the system?
            </button>
          </h2>
          <div id="p1" class="accordion-collapse collapse show" data-bs-parent="#parFAQ">
            <div class="accordion-body">
              After logging in, go to <strong>Manage Child</strong> from the sidebar. Click <strong>Add Child</strong> and fill in your child's name, date of birth, gender, and vaccination details. You can manage multiple children from this section.
            </div>
          </div>
        </div>
        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#p2">
              <i class="fas fa-calendar-plus me-2 text-primary"></i> How do I book a vaccination appointment?
            </button>
          </h2>
          <div id="p2" class="accordion-collapse collapse" data-bs-parent="#parFAQ">
            <div class="accordion-body">
              Log in → Go to <strong>View Hospital</strong> → Find a hospital near you → Click <strong>Book Appointment</strong> → Fill in child details, select vaccine and preferred date → Submit. Your request will be reviewed and confirmed by the hospital.
            </div>
          </div>
        </div>
        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#p3">
              <i class="fas fa-syringe me-2 text-warning"></i> How do I view my child's vaccination history?
            </button>
          </h2>
          <div id="p3" class="accordion-collapse collapse" data-bs-parent="#parFAQ">
            <div class="accordion-body">
              Go to <strong>Vaccination Info</strong> in the sidebar. You will see a complete list of vaccines administered, dates, and the hospital where each vaccine was given. Upcoming vaccines are also shown with their schedules.
            </div>
          </div>
        </div>
        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#p4">
              <i class="fas fa-bell me-2 text-danger"></i> How do vaccination reminders work?
            </button>
          </h2>
          <div id="p4" class="accordion-collapse collapse" data-bs-parent="#parFAQ">
            <div class="accordion-body">
              The system automatically generates reminders for upcoming vaccinations based on your child's age and vaccination schedule. Visit <strong>My Reminders</strong> to view all upcoming alerts and ensure your contact details are updated in <strong>My Profile</strong>.
            </div>
          </div>
        </div>
        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#p5">
              <i class="fas fa-times-circle me-2 text-secondary"></i> Can I cancel or reschedule an appointment?
            </button>
          </h2>
          <div id="p5" class="accordion-collapse collapse" data-bs-parent="#parFAQ">
            <div class="accordion-body">
              Go to <strong>My Appointments</strong> in the sidebar to view all bookings. Contact the hospital directly using the contact details listed on their profile, or submit a support ticket requesting reschedule assistance.
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Hospital FAQ -->
    <div class="faq-pane" id="faq-hospital">
      <div class="accordion" id="hospFAQ">
        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#h1">
              <i class="fas fa-hospital-alt me-2 text-primary"></i> How do I register my hospital?
            </button>
          </h2>
          <div id="h1" class="accordion-collapse collapse show" data-bs-parent="#hospFAQ">
            <div class="accordion-body">
              On the homepage, click <strong>Login → Hospital → Register as Hospital</strong>. Complete all 7 sections including hospital info, contact details, facilities, operating hours, owner identity, and ownership proof. Upload required documents and submit. The admin will review and approve within 2–3 business days.
            </div>
          </div>
        </div>
        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#h2">
              <i class="fas fa-clipboard-check me-2 text-success"></i> How do I approve parent appointment requests?
            </button>
          </h2>
          <div id="h2" class="accordion-collapse collapse" data-bs-parent="#hospFAQ">
            <div class="accordion-body">
              Go to <strong>Parent Application</strong> in the sidebar. Review pending requests, click <strong>View</strong> to see child details, then <strong>Approve</strong> or <strong>Reject</strong>. Approved requests automatically create an appointment entry and notify the parent.
            </div>
          </div>
        </div>
        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#h3">
              <i class="fas fa-syringe me-2 text-warning"></i> How do I update vaccination records?
            </button>
          </h2>
          <div id="h3" class="accordion-collapse collapse" data-bs-parent="#hospFAQ">
            <div class="accordion-body">
              Go to <strong>Vaccination Info</strong> in the sidebar. Find the child's appointment and click <strong>Update</strong>. Enter the vaccine name, batch number, and administration date, then save. The parent's dashboard will reflect the update immediately.
            </div>
          </div>
        </div>
        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#h4">
              <i class="fas fa-edit me-2 text-info"></i> How do I update my hospital profile?
            </button>
          </h2>
          <div id="h4" class="accordion-collapse collapse" data-bs-parent="#hospFAQ">
            <div class="accordion-body">
              Go to <strong>My Profile</strong> from the sidebar and click <strong>Edit</strong> to update your hospital's name, address, contact number, email, or service availability. Save the changes to apply them.
            </div>
          </div>
        </div>
        <div class="accordion-item">
          <h2 class="accordion-header">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#h5">
              <i class="fas fa-comments me-2 text-secondary"></i> How do I communicate with parents?
            </button>
          </h2>
          <div id="h5" class="accordion-collapse collapse" data-bs-parent="#hospFAQ">
            <div class="accordion-body">
              Use the <strong>Chats</strong> section in the sidebar to send and receive messages from parents. You can discuss appointment details, vaccination queries, and health updates directly through the platform.
            </div>
          </div>
        </div>
      </div>
    </div>

  </div><!-- /section-card FAQs -->
</section>

<!-- SUPPORT TICKET FORM -->
<section class="container mb-5" id="ticketSection">
  <div class="section-card">
    <h5><i class="fas fa-headset"></i> Submit a Support Ticket</h5>
    <p class="text-muted mb-4" style="font-size:0.9rem;">
      Can't find what you need? Fill the form below and our team will respond within 24 business hours.
    </p>

    <div class="row g-3">
      <div class="col-md-6">
        <label class="form-label"><i class="fas fa-user me-1 text-primary"></i> Your Full Name</label>
        <input type="text" class="form-control" id="fullName" placeholder="Enter your full name" required>
      </div>
      <div class="col-md-6">
        <label class="form-label"><i class="fas fa-envelope me-1 text-primary"></i> Contact Email</label>
        <input type="email" class="form-control" id="contactEmail" placeholder="your@email.com" required>
      </div>
      <div class="col-md-6">
        <label class="form-label"><i class="fas fa-id-badge me-1 text-primary"></i> Your Role</label>
        <select class="form-select" id="userRole">
          <option value="">-- Select Role --</option>
          <option>Parent / Guardian</option>
          <option>Hospital Staff</option>
          <option>General Visitor</option>
          <option>Other</option>
        </select>
      </div>
      <div class="col-md-6">
        <label class="form-label"><i class="fas fa-tag me-1 text-primary"></i> Issue Category</label>
        <select class="form-select" id="issueCategory">
          <option value="">-- Select Category --</option>
          <option>Registration / Account</option>
          <option>Login / Access Issues</option>
          <option>Appointment Booking</option>
          <option>Vaccination Records</option>
          <option>Hospital Information</option>
          <option>Reminders & Notifications</option>
          <option>Technical Bug</option>
          <option>Other</option>
        </select>
      </div>
      <div class="col-md-6">
        <label class="form-label"><i class="fas fa-flag me-1 text-primary"></i> Priority</label>
        <select class="form-select" id="priority">
          <option>Low – General Question</option>
          <option>Medium – Need Help Soon</option>
          <option>High – Urgent Issue</option>
        </select>
      </div>
      <div class="col-12">
        <label class="form-label"><i class="fas fa-align-left me-1 text-primary"></i> Describe Your Issue</label>
        <textarea class="form-control" id="issueDescription" rows="5"
          placeholder="Please describe your issue in detail so we can assist you faster..."></textarea>
      </div>
      <div class="col-12">
        <button class="btn-submit" id="submitBtn" onclick="submitTicket()">
          <i class="fas fa-paper-plane me-2"></i> Submit Ticket
        </button>
      </div>
    </div>
  </div>
</section>

<!-- SYSTEM INFO -->
<section class="container mb-5">
  <div class="section-card">
    <h5><i class="fas fa-circle-info"></i> System Information</h5>
    <div class="row g-3">
      <div class="col-md-4">
        <div class="info-box">
          <i class="fas fa-clock text-primary"></i>
          <div>
            <div class="fw-bold text-dark" style="font-size:0.9rem;">Support Hours</div>
            <div class="text-muted" style="font-size:0.83rem;">Mon–Sat: 9:00 AM – 6:00 PM IST</div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="info-box">
          <i class="fas fa-reply text-success"></i>
          <div>
            <div class="fw-bold text-dark" style="font-size:0.9rem;">Response Time</div>
            <div class="text-muted" style="font-size:0.83rem;">Email: 24 hrs &nbsp;|&nbsp; Phone: Immediate</div>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="info-box">
          <i class="fas fa-shield-heart text-danger"></i>
          <div>
            <div class="fw-bold text-dark" style="font-size:0.9rem;">Your Data is Safe</div>
            <div class="text-muted" style="font-size:0.83rem;">All records are encrypted &amp; secure</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer style="background:#222;color:#cbd5e1;padding:35px 0 18px;text-align:center;margin-top:20px;">
  <p style="margin:0;font-size:0.9rem;">
    <i class="fas fa-hands-holding-child me-2" style="color:#4585c6;"></i>
    Child Vaccination Management System
  </p>
  <p style="margin:6px 0 0;font-size:0.8rem;color:#64748b;">
    &copy; 2026 CVS. All rights reserved.
    &nbsp;|&nbsp; <a href="mailto:childvaccinationsystem2026@gmail.com" style="color:#4585c6;text-decoration:none;">childvaccinationsystem2026@gmail.com</a>
    &nbsp;|&nbsp; +91 93457 90381
  </p>
</footer>

<!-- JAVASCRIPT -->
<script>

// ── FAQ TABS ──────────────────────────────────────────────
function showFAQ(role, btn) {
  document.querySelectorAll('.faq-pane').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.role-tab').forEach(b => b.classList.remove('active'));
  document.getElementById('faq-' + role).classList.add('active');
  btn.classList.add('active');
}

// ── SCROLL TO TICKET ──────────────────────────────────────
function scrollToTicket() {
  setTimeout(() => {
    document.getElementById('ticketSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 100);
}

// ── FAQ SEARCH ────────────────────────────────────────────
const faqData = [
  { q: "What is the Child Vaccination System?", a: "A digital platform to track vaccination records, book appointments, and receive reminders.", role: "General" },
  { q: "Who can register?", a: "Parents/guardians and hospitals/clinics can register. All registrations need admin approval.", role: "General" },
  { q: "Is my data safe?", a: "Yes. All data is stored securely and never shared with third parties.", role: "General" },
  { q: "I forgot my password", a: "Click 'Forgot User ID / Password?' on the login screen and enter your User ID and email.", role: "General" },
  { q: "Can I use on mobile?", a: "Yes, the system is fully responsive and works on any device.", role: "General" },
  { q: "How do I add my child?", a: "Login → Manage Child → Add Child. Fill in child details and save.", role: "Parent" },
  { q: "How do I book an appointment?", a: "Login → View Hospital → Select hospital → Book Appointment → Fill details.", role: "Parent" },
  { q: "How do I view vaccination history?", a: "Login → Vaccination Info in sidebar to see all completed and upcoming vaccines.", role: "Parent" },
  { q: "How do vaccination reminders work?", a: "Reminders are auto-generated based on your child's age and vaccination schedule.", role: "Parent" },
  { q: "How do I register my hospital?", a: "Login → Hospital → Register as Hospital. Complete all sections and submit for admin review.", role: "Hospital" },
  { q: "How do I approve appointments?", a: "Go to Parent Application in sidebar. Review and click Approve or Reject.", role: "Hospital" },
  { q: "How do I update vaccination records?", a: "Go to Vaccination Info → Find appointment → Update with vaccine details.", role: "Hospital" },
  { q: "How do I add a new vaccine?", a: "Admin → Add Vaccination Info → Enter vaccine name, age group, and description.", role: "Admin" },
  { q: "How do I export data?", a: "Admin → Export Data → Select type and date range → Download.", role: "Admin" },
];

function searchFAQ(val) {
  const q = val.trim().toLowerCase();
  const box = document.getElementById('searchResults');
  const content = document.getElementById('searchResultsContent');
  if (!q) { box.style.display = 'none'; return; }

  const matches = faqData.filter(f => f.q.toLowerCase().includes(q) || f.a.toLowerCase().includes(q));
  if (matches.length === 0) {
    content.innerHTML = '<p class="text-muted mb-0"><i class="fas fa-search me-2"></i>No results found. Try different keywords or submit a support ticket.</p>';
  } else {
    content.innerHTML = matches.map(f => `
      <div class="mb-3 pb-3 border-bottom">
        <div class="fw-bold text-primary mb-1">
          <span class="badge bg-secondary me-2" style="font-size:0.7rem;">${f.role}</span>${f.q}
        </div>
        <div class="text-muted" style="font-size:0.88rem;">${f.a}</div>
      </div>
    `).join('').replace(/<div class="mb-3 pb-3 border-bottom">((?:.|\n)*?)<\/div>\s*$/, '<div class="mb-0">$1</div>');
    // Clean last border
    content.innerHTML = content.innerHTML.replace(/border-bottom">\s*<div class="fw-bold[^"]*"[^>]*>\s*<span[^>]*>Admin/, 'border-bottom"><div class="fw-bold');
  }
  box.style.display = 'block';
}

// ── TOAST ─────────────────────────────────────────────────
function showToast(msg, type = 'success') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `custom-toast toast-${type}`;
  toast.innerHTML = `
    <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
    <span>${msg}</span>
  `;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.5s'; }, 4000);
  setTimeout(() => { if (toast.parentNode) toast.parentNode.removeChild(toast); }, 4500);
}

// ── SUBMIT TICKET ─────────────────────────────────────────
function submitTicket() {
  const fullName    = document.getElementById('fullName').value.trim();
  const email       = document.getElementById('contactEmail').value.trim();
  const role        = document.getElementById('userRole').value;
  const category    = document.getElementById('issueCategory').value;
  const priority    = document.getElementById('priority').value;
  const description = document.getElementById('issueDescription').value.trim();

  if (!fullName)    return showToast('Please enter your full name.', 'error');
  if (!email || !email.includes('@')) return showToast('Please enter a valid email address.', 'error');
  if (!role || role === '-- Select Role --')     return showToast('Please select your role.', 'error');
  if (!category || category === '-- Select Category --') return showToast('Please select an issue category.', 'error');
  if (!description) return showToast('Please describe your issue.', 'error');

  const btn = document.getElementById('submitBtn');
  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Submitting...';

  const formData = new FormData();
  formData.append('action', 'submit_ticket');
  formData.append('full_name', fullName);
  formData.append('contact_email', email);
  formData.append('user_role', role);
  formData.append('issue_category', category);
  formData.append('priority', priority);
  formData.append('description', description);

  fetch(window.location.pathname, { method: 'POST', body: formData })
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        showToast(`✅ ${data.message}`, 'success');
        // Clear form
        document.getElementById('fullName').value = '';
        document.getElementById('contactEmail').value = '';
        document.getElementById('userRole').value = '';
        document.getElementById('issueCategory').value = '';
        document.getElementById('priority').selectedIndex = 0;
        document.getElementById('issueDescription').value = '';
      } else {
        showToast(`❌ ${data.message}`, 'error');
      }
    })
    .catch(() => showToast('Network error. Please try again.', 'error'))
    .finally(() => {
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-paper-plane me-2"></i> Submit Ticket';
    });
}

</script>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def help_page():
    ensure_table()
    if request.method == "POST":
        action = request.form.get('action', '').strip()
        if action == 'submit_ticket':
            return handle_ticket_submission(request.form)
    return HELP_PAGE_HTML


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
