import pymysql
import os
from flask import Flask, request, render_template_string

app = Flask(__name__)


db_error = None
try:
    con = pymysql.connect(
    host=os.environ.get("MYSQLHOST"),
    user=os.environ.get("MYSQLUSER"),
    password=os.environ.get("MYSQLPASSWORD"),
    database=os.environ.get("MYSQLDATABASE"),
    port=int(os.environ.get("MYSQLPORT"))
)
    cur = con.cursor()
except Exception as e:
    con = None
    cur = None
    db_error = str(e)

@app.route("/", methods=["GET", "POST"])
def home():
    if db_error:
        return f"<h2 style='color:red;'>Database Connection Failed!</h2><pre>{db_error}</pre>", 500
    form = request.form

    # ========== HOSPITAL REGISTRATION ==========
    hregister = form.get("hregister")
    if hregister is not None:
        try:
            hname = form.get("hname");
            htype = form.get("htype");
            hlic = form.get("hlic")
            hyear = form.get("hyear");
            hemail = form.get("hemail");
            hmobile = form.get("hmobile")
            hemcnum = form.get("hemcnum");
            hstate = form.get("hstate");
            hdistrict = form.get("hdistrict")
            hcity = form.get("hcity");
            hpin = form.get("hpin");
            hstreet = form.get("hstreet")
            harea = form.get("harea");
            hbed = form.get("hbed");
            hicu = form.get("hicu")
            hemc = form.get("hemc");
            hambulance = form.get("hambulance");
            hbbank = form.get("hbbank")
            hpharmacy = form.get("hpharmacy");
            hservice = form.get("hservice");
            hwtime = form.get("hwtime")
            hopdtime = form.get("hopdtime");
            oname = form.get("oname");
            odob = form.get("odob")
            ogender = form.get("ogender");
            oid = form.get("oid");
            oidnum = form.get("oidnum")
            otype = form.get("otype")
        
            cur.execute("SELECT email_id FROM hospital WHERE email_id = %s", (hemail,))
            if cur.fetchone():
                return '<script>alert("Email already registered! Please use a different email address.");window.location.href="/";</script>'
            os.makedirs("image", exist_ok=True)
            
            
            def save_file(field):
                if field in request.files:
                    f = request.files[field]
                       
                    if f.filename != "":
                        n = os.path.basename(f.filename)
                        with open("image/" + n, "wb") as file:
                            file.write(f.read())
                        return n
                return ""
                        
            licence_name = save_file('hlicproof');
            logo_name = save_file('hlogo')
            profile_name = save_file('oprofile');
            idproof_name = save_file('oidproof')
            ownership_name = save_file('oownership')
                        
            cur.execute("""INSERT INTO hospital (hospital_name,hospital_type,license_number,license_proof,
                        year_of_establishment,hospital_logo,email_id,hospital_mobile,hospital_mobile_emergency,state,
                        district,city,pincode,street,area,bed,icu,emergency,ambulence,blood_bank,pharmacy,service,
                        working_time,opd_time,owner_name,owner_dob,owner_gender,owner_profile,id_type,id_number,
                        id_proof,owner_type,ownership_proof) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (hname, htype, hlic, licence_name, hyear, logo_name, hemail, hmobile, hemcnum, hstate, hdistrict,
                            hcity, hpin, hstreet, harea, hbed, hicu, hemc, hambulance, hbbank, hpharmacy, hservice, hwtime,
                            hopdtime, oname, odob, ogender, profile_name, oid, oidnum, idproof_name, otype, ownership_name))
            con.commit()
            return '<script>alert("Hospital Registered Successfully! \u2705");window.location.href="/";</script>'
                        
        except pymysql.IntegrityError as e:
            con.rollback()
            em = "Email already registered!" if "email_id" in str(
                e) else "Mobile already registered!" if "hospital_mobile" in str(
                e) else "License number already exists!" if "license_number" in str(e) else "This record already exists."
            return f'<script>alert("{em}");window.location.href="/";</script>'
        except Exception as e:
            con.rollback()
            return f'<script>alert("Registration Failed: {str(e)}");window.location.href="/";</script>'           

    # ========== PARENT REGISTRATION ==========
    pregister = form.get("pregister")
    if pregister is not None:
        try:
            ptype = form.get("ptype");
            pname = form.get("pname");
            pgender = form.get("pgender")
            pdob = form.get("pdob");
            pmobile = form.get("pmobile");
            pemail = form.get("pemail")
            palternum = form.get("palternum") or "";
            pstate = form.get("pstate")
            pdistrict = form.get("pdistrict");
            pcity = form.get("pcity");
            ppin = form.get("ppin")
            pstreet = form.get("pstreet");
            parea = form.get("parea");
            pid = form.get("pid")
            pidnum = form.get("pidnum");
            corder = form.get("corder")
        
            cur.execute("SELECT email_id FROM parent WHERE email_id = %s", (pemail,))
            if cur.fetchone():
                return '<script>alert("Email already registered! Please use a different email address.");window.location.href="/";</script>'
            os.makedirs("image", exist_ok=True)
                    
                    

        except pymysql.IntegrityError as e:
            con.rollback()
            em = "Email already registered!" if "email_id" in str(
                e) else "Mobile already registered!" if "parent_mobile" in str(e) else "This record already exists."
            return f'<script>alert("{em}");window.location.href="/";</script>'
        except Exception as e:
            con.rollback()
            return f'<script>alert("Registration Failed: {str(e)}");window.location.href="/";</script>'

    # ========== FORGOT PASSWORD ==========
    forgot_password = form.get("forgot_password")
    if forgot_password is not None:
        forgot_email = form.get("forgot_email")
        forgot_user = form.get("forgot_user_id")
        forgot_role = form.get("forgot_role")
        try:
            if forgot_role == "hospital":
               cur.execute("SELECT password, hospital_name FROM hospital WHERE email_id=%s AND user_id=%s",
                    (forgot_email, forgot_user))
               result = cur.fetchone()
               if result:
                    pw, name = result
                    return f'<script>alert("\\u2705 Account Found!\\n\\nHospital Name : {name}\\nUser ID : {forgot_user}\\nPassword : {pw}");window.location.href="/";</script>'
               else:
                    return '<script>alert("\\u274C Invalid Hospital User ID or Email!");window.location.href="/";</script>'
            elif forgot_role == "parent":
                cur.execute("SELECT password, parent_name FROM parent WHERE email_id=%s AND user_id=%s",
                    (forgot_email, forgot_user))
                result = cur.fetchone()
                if result:
                    pw, name = result
                    return f'<script>alert("\\u2705 Account Found!\\n\\nParent Name : {name}\\nUser ID : {forgot_user}\\nPassword : {pw}");window.location.href="/";</script>'
                else:
                    return '<script>alert("\\u274C Invalid Parent User ID or Email!");window.location.href="/";</script>'
        except Exception as e:
            return f'<script>alert("Error: {str(e)}");window.location.href="/";</script>'
                
    # ========== LOGIN PROCESSING ==========
    admin_submit = form.get("admin_login")
    if admin_submit is not None:
        userid = form.get("admin_user_id");
        password = form.get("admin_password")
        if userid and password:
            cur.execute("SELECT id FROM admin WHERE user_id = %s AND password = %s", (userid, password))
            r = cur.fetchone()
            if r:
                return f'<script>alert("Admin login successful!");location.href="/admin_dashboard?admin_id={int(r[0])}";</script>'
            else:
                return '<script>alert("Invalid Admin credentials!");</script>'
                
    hospital_submit = form.get("hospital_login")
    if hospital_submit is not None:
        userid = form.get("hospital_user_id");
        password = form.get("hospital_password")
        if userid and password:
            cur.execute("SELECT id FROM hospital WHERE user_id = %s AND password = %s", (userid, password))
            r = cur.fetchone()
            if r:
                return f'<script>alert("Hospital login successful!");location.href="/hospital_dashboard?hospital_id={int(r[0])}";</script>'
            else:
                return '<script>alert("Invalid Hospital credentials!");</script>'
                
    parent_submit = form.get("parent_login")
    if parent_submit is not None:
        userid = form.get("parent_user_id");
        password = form.get("parent_password")
        if userid and password:
            cur.execute("SELECT id FROM parent WHERE user_id = %s AND password = %s", (userid, password))
            r = cur.fetchone()
            if r:
                return f'<script>alert("Parent login successful!");location.href="/parent_dashboard?parent_id={int(r[0])}";</script>'
            else:
                return '<script>alert("Invalid Parent credentials!");</script>'
                
                
    # ========== DB COUNTERS ==========
    def get_count(q):
        try:
            cur.execute(q); r = cur.fetchone(); return int(r[0]) if r else 0
        except:
            return 0
                
    cnt_children = get_count("SELECT COUNT(*) FROM manage_child")
    cnt_hospitals = get_count("SELECT COUNT(*) FROM hospital")
    cnt_vaccines = get_count("SELECT COUNT(*) FROM hospital_appointment WHERE status='completed'")
  

    # ========== HTML ==========
    return f"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home | Child Vaccination System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"/>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
      :root{{--primary:#0f6cbd;--primary-dark:#0a4d8c;--primary-light:#e8f4ff;--accent:#00c9a7;--accent2:#ff6b6b;--bg:#f0f5fc;--card-bg:#ffffff;--text:#1a2b42;--text-muted:#6b7a99;--border:#dde6f5;--shadow:0 4px 24px rgba(15,108,189,0.10);--shadow-lg:0 12px 40px rgba(15,108,189,0.16);--radius:18px;--radius-sm:10px;--navbar-h:72px;}}
    
      *{{box-sizing:border-box;margin:0;padding:0;}}
      body{{background:var(--bg);font-family:'Plus Jakarta Sans',sans-serif;color:var(--text);overflow-x:hidden;}}
      ::-webkit-scrollbar{{width:7px;}}::-webkit-scrollbar-track{{background:var(--bg);}}::-webkit-scrollbar-thumb{{background:var(--primary);border-radius:10px;}}
    
      /* NAVBAR */
      .cvs-navbar{{position:fixed;top:0;left:0;right:0;z-index:1050;height:var(--navbar-h);background:rgba(255,255,255,0.95);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border-bottom:1px solid var(--border);box-shadow:0 2px 20px rgba(15,108,189,0.08);display:flex;align-items:center;}}
      .cvs-navbar .container{{display:flex;align-items:center;justify-content:space-between;}}
      .nav-brand{{display:flex;align-items:center;gap:12px;text-decoration:none;}}
      .nav-brand img{{height:48px;width:48px;border-radius:14px;object-fit:cover;border:2px solid var(--primary-light);}}
      .nav-brand-text{{font-family:'Nunito',sans-serif;font-weight:800;font-size:1.1rem;color:var(--primary);line-height:1.2;}}
      .nav-brand-sub{{font-size:0.7rem;color:var(--text-muted);font-weight:500;letter-spacing:0.5px;}}
      .nav-links{{display:flex;align-items:center;gap:6px;list-style:none;}}
      .nav-links .nav-link{{color:var(--text-muted);font-weight:600;font-size:0.9rem;padding:8px 14px;border-radius:var(--radius-sm);transition:all 0.2s;}}
      .nav-links .nav-link:hover,.nav-links .nav-link.active{{color:var(--primary);background:var(--primary-light);}}
      .btn-login-nav{{background:var(--primary);color:white!important;border-radius:12px!important;padding:9px 20px!important;font-weight:700!important;font-size:0.88rem!important;border:none;transition:all 0.25s!important;box-shadow:0 3px 12px rgba(15,108,189,0.3);}}
      .btn-login-nav:hover{{background:var(--primary-dark)!important;transform:translateY(-1px);box-shadow:0 6px 18px rgba(15,108,189,0.4)!important;}}
      .navbar-toggler-btn{{background:var(--primary-light);border:none;border-radius:10px;width:42px;height:42px;display:none;align-items:center;justify-content:center;cursor:pointer;color:var(--primary);font-size:1.2rem;}}
      .mobile-menu{{display:none;position:fixed;top:var(--navbar-h);left:0;right:0;background:white;border-bottom:1px solid var(--border);padding:16px 20px;box-shadow:0 8px 24px rgba(0,0,0,0.1);z-index:1049;flex-direction:column;gap:6px;}}
      .mobile-menu.open{{display:flex;}}
      .mobile-menu .nav-link{{display:block;padding:12px 16px;border-radius:var(--radius-sm);color:var(--text);font-weight:600;text-decoration:none;}}
      .mobile-menu .nav-link:hover{{background:var(--primary-light);color:var(--primary);}}
      .mobile-submenu{{padding-left:16px;}}
      .mobile-submenu a{{display:block;padding:10px 16px;color:var(--text-muted);font-weight:500;border-radius:var(--radius-sm);text-decoration:none;transition:all 0.2s;}}
      .mobile-submenu a:hover{{background:var(--primary-light);color:var(--primary);}}
      @media(max-width:991px){{.navbar-toggler-btn{{display:flex;}}.nav-links{{display:none;}}}}
    
      /* HERO */
      .hero-section{{margin-top:var(--navbar-h);background:linear-gradient(135deg,#0f6cbd 0%,#1a8fe3 40%,#00c9a7 100%);position:relative;overflow:hidden;padding:80px 0 120px;}}
      .hero-section::before{{content:'';position:absolute;inset:0;background:url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.04'%3E%3Ccircle cx='30' cy='30' r='20'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");}}
      .hero-blob{{position:absolute;border-radius:50%;background:rgba(255,255,255,0.06);animation:floatBlob 8s ease-in-out infinite;}}
      .hero-blob-1{{width:500px;height:500px;top:-200px;right:-100px;animation-delay:0s;}}
      .hero-blob-2{{width:300px;height:300px;bottom:-100px;left:-80px;animation-delay:3s;animation-direction:reverse;}}
      @keyframes floatBlob{{0%,100%{{transform:translateY(0) scale(1);}}50%{{transform:translateY(-20px) scale(1.04);}}}}
      .hero-title{{font-family:'Nunito',sans-serif;font-weight:900;font-size:clamp(2rem,5vw,3.2rem);color:white;line-height:1.15;margin-bottom:20px;animation:slideUp 0.7s ease both;}}
      .hero-sub{{color:rgba(255,255,255,0.88);font-size:clamp(0.95rem,2vw,1.15rem);font-weight:500;margin-bottom:36px;line-height:1.7;animation:slideUp 0.7s 0.15s ease both;}}
      .hero-actions{{display:flex;flex-wrap:wrap;gap:14px;animation:slideUp 0.7s 0.3s ease both;}}
      .btn-hero-primary{{background:white;color:var(--primary);border:none;border-radius:14px;padding:14px 30px;font-weight:800;font-size:0.95rem;cursor:pointer;transition:all 0.25s;box-shadow:0 6px 20px rgba(0,0,0,0.15);}}
      .btn-hero-primary:hover{{transform:translateY(-2px);box-shadow:0 10px 28px rgba(0,0,0,0.2);}}
      .btn-hero-outline{{background:transparent;color:white;border:2px solid rgba(255,255,255,0.6);border-radius:14px;padding:14px 30px;font-weight:700;font-size:0.95rem;cursor:pointer;transition:all 0.25s;}}
      .btn-hero-outline:hover{{background:rgba(255,255,255,0.12);border-color:white;}}
      .hero-img-wrap{{text-align:center;animation:floatBlob 4s ease-in-out infinite;}}
      .hero-img-wrap img{{max-width:min(340px,85%);filter:drop-shadow(0 20px 40px rgba(0,0,0,0.2));}}
      .hero-badges{{display:flex;flex-wrap:wrap;gap:10px;margin-top:28px;animation:slideUp 0.7s 0.45s ease both;}}
      .hero-badge{{background:rgba(255,255,255,0.15);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.25);color:white;border-radius:50px;padding:6px 16px;font-size:0.82rem;font-weight:600;display:flex;align-items:center;gap:6px;}}
      .hero-wave{{position:absolute;bottom:-2px;left:0;width:100%;}}
      @keyframes slideUp{{from{{opacity:0;transform:translateY(30px);}}to{{opacity:1;transform:translateY(0);}}}}
    
      /* STAT CARDS */
      .stats-section{{padding:0 0 60px;position:relative;z-index:2;margin-top: 80px;}}
      .stat-card{{background:var(--card-bg);border-radius:var(--radius);padding:28px 24px;box-shadow:var(--shadow);border:1px solid var(--border);text-align:center;transition:all 0.3s;position:relative;overflow:hidden;}}
      .stat-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:4px;border-radius:var(--radius) var(--radius) 0 0;}}
      .stat-card.s1::before{{background:linear-gradient(90deg,#0f6cbd,#1a8fe3);}}
      .stat-card.s2::before{{background:linear-gradient(90deg,#00c9a7,#0ea5e9);}}
      .stat-card.s3::before{{background:linear-gradient(90deg,#ff6b6b,#ffa94d);}}
      .stat-card.s4::before{{background:linear-gradient(90deg,#845ef7,#cc5de8);}}
      .stat-card:hover{{transform:translateY(-6px);box-shadow:var(--shadow-lg);}}
      .stat-icon{{width:56px;height:56px;border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:1.4rem;margin:0 auto 14px;}}
      .stat-card.s1 .stat-icon{{background:#e8f4ff;color:var(--primary);}}
      .stat-card.s2 .stat-icon{{background:#e6fdf8;color:#00c9a7;}}
      .stat-card.s3 .stat-icon{{background:#fff0f0;color:var(--accent2);}}
      .stat-card.s4 .stat-icon{{background:#f3f0ff;color:#845ef7;}}
      .stat-number{{font-family:'Nunito',sans-serif;font-size:2.4rem;font-weight:900;line-height:1;margin-bottom:6px;}}
      .stat-card.s1 .stat-number{{color:var(--primary);}}
      .stat-card.s2 .stat-number{{color:#00c9a7;}}
      .stat-card.s3 .stat-number{{color:var(--accent2);}}
      .stat-card.s4 .stat-number{{color:#845ef7;}}
      .stat-label{{font-size:0.88rem;color:var(--text-muted);font-weight:600;}}
      .counter{{display:inline;}}
    
      /* SECTIONS */
      .section-label{{display:inline-block;background:var(--primary-light);color:var(--primary);border-radius:50px;padding:6px 18px;font-size:0.8rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:14px;}}
      .section-title{{font-family:'Nunito',sans-serif;font-weight:800;font-size:clamp(1.6rem,3.5vw,2.4rem);color:var(--text);margin-bottom:14px;line-height:1.2;}}
      .section-sub{{color:var(--text-muted);font-size:1rem;line-height:1.7;max-width:560px;}}
    
      /* ROLE CARDS */
      .highlights-section{{margin-top: 80px;}}
      .role-card{{background:rgb(249, 252, 255);border-radius:var(--radius);padding:36px 28px;border:1px solid var(--border);transition:all 0.3s;text-align:center;position:relative;overflow:hidden;}}
      .role-card::after{{content:'';position:absolute;bottom:0;left:0;right:0;height:0;transition:height 0.3s;border-radius:0 0 var(--radius) var(--radius);}}
      .role-card:hover{{transform:translateY(-8px);box-shadow:var(--shadow-lg);background:white;}}
      .role-card:hover::after{{height:5px;}}
      .role-card.rc-parent:hover::after{{background:var(--accent);}}
      .role-card.rc-hospital:hover::after{{background:var(--primary);}}
      .role-card.rc-admin:hover::after{{background:var(--accent2);}}
      .role-icon{{width:76px;height:76px;border-radius:22px;display:flex;align-items:center;justify-content:center;font-size:1.9rem;margin:0 auto 20px;transition:transform 0.3s;}}
      .role-card:hover .role-icon{{transform:scale(1.1) rotate(-5deg);}}
      .rc-parent .role-icon{{background:linear-gradient(135deg,#e6fdf8,#d0f5eb);color:var(--accent);}}
      .rc-hospital .role-icon{{background:linear-gradient(135deg,#e8f4ff,#d0e8ff);color:var(--primary);}}
      .rc-admin .role-icon{{background:linear-gradient(135deg,#fff0f0,#ffd6d6);color:var(--accent2);}}
      .role-card h5{{font-family:'Nunito',sans-serif;font-weight:800;font-size:1.2rem;margin-bottom:10px;}}
      .role-card p{{color:var(--text-muted);font-size:0.92rem;line-height:1.6;margin:0;}}
    
      /* STRIP */
      .strip-banner{{background:linear-gradient(135deg,#0f6cbd 0%,#0ea5e9 100%);padding:64px 0;position:relative;overflow:hidden;transform: skewY(-3deg);margin-top: 110px;}}
      .strip-banner .content{{transform: skewY(3deg);}}
      .strip-banner::before{{content:'';position:absolute;top:-60px;right:-60px;width:300px;height:300px;border-radius:50%;background:rgba(255,255,255,0.08);}}
      .strip-banner h2{{font-family:'Nunito',sans-serif;font-weight:900;font-size:clamp(1.5rem,3vw,2.2rem);color:white;margin-bottom:12px;}}
      .strip-banner p{{color:rgba(255,255,255,0.85);font-size:1.05rem;margin:0;}}
      .strip-dots{{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;margin-top:24px;}}
      .strip-dot{{background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.3);color:white;border-radius:50px;padding:8px 20px;font-size:0.88rem;font-weight:600;}}
    
      /* FEATURES */
      .features-section{{padding:80px 0;margin-top: 30px;}}
      .feature-card{{background:var(--card-bg);border:1px solid var(--border);border-radius:var(--radius);padding:32px 26px;box-shadow:var(--shadow);transition:all 0.3s;height:100%;display:flex;flex-direction:column;}}
      .feature-card:hover{{transform:translateY(-6px);box-shadow:var(--shadow-lg);border-color:var(--primary);}}
      .feature-icon{{width:60px;height:60px;border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:1.5rem;margin-bottom:20px;}}
      .fc1 .feature-icon{{background:#fff0f0;color:#e03131;}}.fc2 .feature-icon{{background:#e6fdf8;color:#00b37e;}}
      .fc3 .feature-icon{{background:#fff9e6;color:#e67700;}}.fc4 .feature-icon{{background:#f3f0ff;color:#845ef7;}}
      .fc5 .feature-icon{{background:#e8f4ff;color:var(--primary);}}.fc6 .feature-icon{{background:#fff0f5;color:#c2255c;}}
      .feature-card h5{{font-family:'Nunito',sans-serif;font-weight:800;font-size:1.05rem;margin-bottom:10px;}}
      .feature-card p{{color:var(--text-muted);font-size:0.88rem;line-height:1.6;margin:0;flex:1;}}
    
      /* METRICS */
      .metrics-section{{padding:60px 0;background:white;margin-top: 30px;}}
      .metric-item{{text-align:center;padding:20px;}}
      .metric-num{{font-family:'Nunito',sans-serif;font-size:2.8rem;font-weight:900;color:var(--primary);}}
      .metric-label{{color:var(--text-muted);font-weight:600;font-size:0.9rem;margin-top:4px;}}
      .metric-divider{{border-right:2px solid var(--border);}}
      @media(max-width:767px){{.metric-divider{{border-right:none;border-bottom:2px solid var(--border);}}.hero-section{{padding:60px 0 100px;}}.hero-img-wrap{{margin-top:40px;}}}}
    
      /* FOOTER */
      .cvs-footer{{background:#0f1b2d;color:#8ea0b8;padding:60px 0 24px;font-size:0.9rem;}}
      .footer-brand img{{height:52px;width:52px;border-radius:14px;margin-bottom:14px;}}
      .footer-brand-name{{font-family:'Nunito',sans-serif;font-weight:800;font-size:1rem;color:white;margin-bottom:10px;}}
      .footer-desc{{color:#8ea0b8;line-height:1.7;font-size:0.88rem;margin-bottom:20px;}}
      .footer-social{{display:flex;gap:10px;}}
      .social-btn{{width:38px;height:38px;border-radius:10px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;color:#8ea0b8;text-decoration:none;transition:all 0.2s;font-size:0.9rem;}}
      .social-btn:hover{{background:var(--primary);color:white;border-color:var(--primary);}}
      .footer-heading{{color:white;font-weight:700;font-size:0.92rem;margin-bottom:16px;letter-spacing:0.5px;}}
      .footer-links{{list-style:none;padding:0;margin:0;}}
      .footer-links li{{margin-bottom:10px;}}
      .footer-links a{{color:#8ea0b8;text-decoration:none;font-size:0.88rem;transition:all 0.2s;display:flex;align-items:center;gap:6px;}}
      .footer-links a:hover{{color:#00c9a7;padding-left:4px;}}
      .footer-contact-item{{display:flex;align-items:flex-start;gap:12px;margin-bottom:14px;}}
      .footer-contact-item i{{color:var(--primary);font-size:0.9rem;margin-top:3px;flex-shrink:0;}}
      .footer-contact-item span{{color:#8ea0b8;font-size:0.88rem;line-height:1.5;}}
      .footer-divider{{border-color:rgba(255,255,255,0.08);margin:32px 0 20px;}}
      .footer-copy{{color:#5a6e85;font-size:0.82rem;}}
    
      /* MODALS */
      .modal-content{{border-radius:22px!important;border:none!important;box-shadow:0 30px 80px rgba(0,0,0,0.18)!important;overflow:hidden;}}
      .modal-header{{padding:24px 28px!important;border:none!important;border-radius:22px 22px 0 0!important;}}
      .modal-header .modal-title{{font-family:'Nunito',sans-serif;font-weight:800;font-size:1.1rem;}}
      .modal-header.admin{{background:linear-gradient(135deg,#6c3be0 0%,#9b4de8 100%);color:white;}}
      .modal-header.hospital{{background:linear-gradient(135deg,#0f6cbd 0%,#1a8fe3 100%);color:white;}}
      .modal-header.parent{{background:linear-gradient(135deg,#00b37e 0%,#00c9a7 100%);color:white;}}
      .modal-header .btn-close{{filter:brightness(0) invert(1);opacity:0.8;}}
      .modal-body{{padding:28px 28px!important;}}
      .modal-footer{{padding:16px 28px!important;border-top:1px solid var(--border)!important;}}
      .form-label{{font-weight:600;font-size:0.88rem;color:var(--text);margin-bottom:7px;}}
      .form-control,.form-select{{border:1.5px solid var(--border);border-radius:12px!important;padding:10px 14px;font-size:0.92rem;color:var(--text);background:#fafbfc;transition:all 0.2s;}}
      .form-control:focus,.form-select:focus{{border-color:var(--primary)!important;box-shadow:0 0 0 3px rgba(15,108,189,0.12)!important;background:white;}}
      .form-control::placeholder{{color:#b0bac9;}}
      .btn-modal-primary{{width:100%;padding:12px;border:none;border-radius:12px;font-family:'Nunito',sans-serif;font-weight:800;font-size:0.95rem;cursor:pointer;transition:all 0.25s;display:flex;align-items:center;justify-content:center;gap:8px;}}
      .btn-modal-admin{{background:linear-gradient(135deg,#6c3be0,#9b4de8);color:white;}}
      .btn-modal-admin:hover{{transform:translateY(-1px);box-shadow:0 6px 20px rgba(108,59,224,0.35);}}
      .btn-modal-hospital{{background:linear-gradient(135deg,#0f6cbd,#1a8fe3);color:white;}}
      .btn-modal-hospital:hover{{transform:translateY(-1px);box-shadow:0 6px 20px rgba(15,108,189,0.35);}}
      .btn-modal-parent{{background:linear-gradient(135deg,#00b37e,#00c9a7);color:white;}}
      .btn-modal-parent:hover{{transform:translateY(-1px);box-shadow:0 6px 20px rgba(0,179,126,0.35);}}
      .btn-modal-forgot{{background:linear-gradient(135deg,#e67700,#ffa94d);color:white;}}
      .btn-modal-forgot:hover{{transform:translateY(-1px);box-shadow:0 6px 20px rgba(230,119,0,0.35);}}
      .forgot-link{{font-size:0.82rem;color:var(--text-muted);text-decoration:none;transition:color 0.2s;}}
      .forgot-link:hover{{color:var(--primary);text-decoration:underline;}}
      .register-divider{{text-align:center;margin:16px 0 12px;position:relative;}}
      .register-divider::before{{content:'';position:absolute;top:50%;left:0;right:0;height:1px;background:var(--border);}}
      .register-divider span{{background:white;padding:0 12px;color:var(--text-muted);font-size:0.82rem;position:relative;}}
      .btn-register-outline{{display:block;width:100%;padding:10px;border-radius:12px;font-weight:700;font-size:0.88rem;text-align:center;cursor:pointer;transition:all 0.2s;background:transparent;}}
      .btn-reg-hospital{{border:2px solid var(--primary);color:var(--primary);}}.btn-reg-hospital:hover{{background:var(--primary-light);}}
      .btn-reg-parent{{border:2px solid #00b37e;color:#00b37e;}}.btn-reg-parent:hover{{background:#e6fdf8;}}
      #hospitalForm,#parentForm{{display:none;}}
      .form-section-title{{font-family:'Nunito',sans-serif;font-weight:800;font-size:1rem;color:var(--primary);padding:10px 16px;border-radius:var(--radius-sm);background:var(--primary-light);margin-bottom:16px;margin-top:8px;display:flex;align-items:center;gap:8px;}}
      .radio-group{{display:flex;flex-wrap:wrap;gap:10px;}}
      .radio-pill{{display:flex;align-items:center;gap:6px;padding:7px 16px;border:1.5px solid var(--border);border-radius:50px;cursor:pointer;font-size:0.88rem;font-weight:600;transition:all 0.2s;color:var(--text-muted);background:#fafbfc;}}
      .radio-pill:has(input:checked){{border-color:var(--primary);background:var(--primary-light);color:var(--primary);}}
      .radio-pill input{{display:none;}}
      .modal-submit-btn{{background:linear-gradient(135deg,var(--primary),#1a8fe3);color:white;border:none;border-radius:14px;padding:13px 28px;width:100%;font-family:'Nunito',sans-serif;font-weight:800;font-size:1rem;cursor:pointer;transition:all 0.25s;box-shadow:0 4px 16px rgba(15,108,189,0.3);}}
      .modal-submit-btn:hover{{transform:translateY(-2px);box-shadow:0 8px 24px rgba(15,108,189,0.4);}}
      .modal-submit-btn.green{{background:linear-gradient(135deg,#00b37e,#00c9a7);box-shadow:0 4px 16px rgba(0,179,126,0.3);}}
      .modal-submit-btn.green:hover{{box-shadow:0 8px 24px rgba(0,179,126,0.4);}}
      @media(max-width:575px){{.modal-dialog{{margin:10px;}}.modal-body{{padding:20px 18px!important;}}.modal-header{{padding:18px 20px!important;}}}}
    </style>
    </head>
    <body>
    
    <!-- ===== NAVBAR ===== -->
    <nav class="cvs-navbar">
      <div class="container-fluid d-flex align-items-center justify-content-between">
        <a class="nav-brand" href="MP-CVS-logo.png">
          <img src="MP-CVS-logo.png" alt="CVS Logo">
          <div>
            <div class="nav-brand-text">Child Vaccination System</div>
            <div class="nav-brand-sub">Health Care...</div>
          </div>
        </a>
        <ul class="nav-links mb-0">
          <li><a class="nav-link active" href="#"><i class="fa-solid fa-house me-1"></i> Home</a></li>
          <li><a class="nav-link" href="/help"><i class="fa-solid fa-handshake-angle me-1"></i> Help &amp; Support</a></li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle btn-login-nav" href="#" id="loginDropdown" role="button"
               data-bs-toggle="dropdown" aria-expanded="false">
              <i class="fa-solid fa-right-to-bracket me-1"></i> Login
            </a>
            <ul class="dropdown-menu dropdown-menu-end shadow border-0"
                style="border-radius:14px;overflow:hidden;padding:6px;" aria-labelledby="loginDropdown">
              <li><button class="dropdown-item py-2 px-3 rounded-3 mb-1" style="font-weight:600;" onclick="openLoginModal('admin')">
                <i class="fa-solid fa-user-shield me-2" style="color:#6c3be0;"></i>Admin</button></li>
              <li><button class="dropdown-item py-2 px-3 rounded-3 mb-1" style="font-weight:600;" onclick="openLoginModal('hospital')">
                <i class="fa-solid fa-hospital me-2" style="color:#0f6cbd;"></i>Hospital</button></li>
              <li><button class="dropdown-item py-2 px-3 rounded-3" style="font-weight:600;" onclick="openLoginModal('parent')">
                <i class="fa-solid fa-hands-holding-child me-2" style="color:#00b37e;"></i>Parent</button></li>
            </ul>
          </li>
        </ul>
        <button class="navbar-toggler-btn" id="mobileMenuBtn" onclick="toggleMobileMenu()">
          <i class="fa-solid fa-bars" id="hamburgerIcon"></i>
        </button>
      </div>
    </nav>
    
    <!-- Mobile Menu -->
    <div class="mobile-menu" id="mobileMenu">
      <a class="nav-link" href="#"><i class="fa-solid fa-house me-2"></i>Home</a>
      <a class="nav-link" href="/help"><i class="fa-solid fa-handshake-angle me-2"></i>Help &amp; Support</a>
      <div class="mobile-submenu">
        <div style="font-size:0.78rem;font-weight:700;color:#b0bac9;text-transform:uppercase;letter-spacing:1px;padding:6px 16px 4px;">Login As</div>
        <a href="#" onclick="openLoginModal('admin');closeMobileMenu();return false;"><i class="fa-solid fa-user-shield me-2" style="color:#6c3be0;"></i>Admin</a>
        <a href="#" onclick="openLoginModal('hospital');closeMobileMenu();return false;"><i class="fa-solid fa-hospital me-2" style="color:#0f6cbd;"></i>Hospital</a>
        <a href="#" onclick="openLoginModal('parent');closeMobileMenu();return false;"><i class="fa-solid fa-hands-holding-child me-2" style="color:#00b37e;"></i>Parent</a>
      </div>
    </div>
    
    <!-- ===== ADMIN LOGIN MODAL ===== -->
    <div class="modal fade" id="adminLoginModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header admin">
            <h5 class="modal-title"><i class="fa-solid fa-user-shield me-2"></i>Admin Login</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form method="POST" action="">
              <div class="mb-3">
                <label class="form-label"><i class="fa-solid fa-user me-2" style="color:#6c3be0;"></i>Username</label>
                <input type="text" class="form-control" name="admin_user_id" placeholder="Enter admin username" required>
              </div>
              <div class="mb-4">
                <label class="form-label"><i class="fa-solid fa-lock me-2" style="color:#6c3be0;"></i>Password</label>
                <input type="password" class="form-control" name="admin_password" placeholder="Enter password" required>
              </div>
              <button type="submit" class="btn-modal-primary btn-modal-admin" name="admin_login" value="1">
                <i class="fa-solid fa-right-to-bracket"></i> Login as Admin
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- ===== HOSPITAL LOGIN MODAL ===== -->
    <div class="modal fade" id="hospitalLoginModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header hospital">
            <h5 class="modal-title"><i class="fa-solid fa-hospital me-2"></i>Hospital Login</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form method="POST" action="">
              <div class="mb-3">
                <label class="form-label"><i class="fa-solid fa-user me-2" style="color:#0f6cbd;"></i>Username</label>
                <input type="text" class="form-control" name="hospital_user_id" placeholder="Enter hospital username" required>
              </div>
              <div class="mb-2">
                <label class="form-label"><i class="fa-solid fa-lock me-2" style="color:#0f6cbd;"></i>Password</label>
                <input type="password" class="form-control" name="hospital_password" placeholder="Enter password" required>
              </div>
              <div class="text-end mb-4">
                <a href="#" class="forgot-link" onclick="openForgotPassword('hospital'); return false;">
                  <i class="fa-solid fa-key me-1"></i>Forgot User ID / Password?
                </a>
              </div>
              <button type="submit" class="btn-modal-primary btn-modal-hospital mb-3" name="hospital_login" value="1">
                <i class="fa-solid fa-right-to-bracket"></i> Login as Hospital
              </button>
              <div class="register-divider"><span>New here?</span></div>
              <button type="button" class="btn-register-outline btn-reg-hospital" onclick="openRegister('Hospital')">
                <i class="fa-solid fa-hospital me-2"></i>Register as Hospital
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- ===== PARENT LOGIN MODAL ===== -->
    <div class="modal fade" id="parentLoginModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header parent">
            <h5 class="modal-title"><i class="fa-solid fa-users me-2"></i>Parent Login</h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form method="POST" action="">
              <div class="mb-3">
                <label class="form-label"><i class="fa-solid fa-user me-2" style="color:#00b37e;"></i>Username</label>
                <input type="text" class="form-control" name="parent_user_id" placeholder="Enter parent username" required>
              </div>
              <div class="mb-2">
                <label class="form-label"><i class="fa-solid fa-lock me-2" style="color:#00b37e;"></i>Password</label>
                <input type="password" class="form-control" name="parent_password" placeholder="Enter password" required>
              </div>
              <div class="text-end mb-4">
                <a href="#" class="forgot-link" onclick="openForgotPassword('parent'); return false;">
                  <i class="fa-solid fa-key me-1"></i>Forgot User ID / Password?
                </a>
              </div>
              <button type="submit" class="btn-modal-primary btn-modal-parent mb-3" name="parent_login" value="1">
                <i class="fa-solid fa-right-to-bracket"></i> Login as Parent
              </button>
              <div class="register-divider"><span>New here?</span></div>
              <button type="button" class="btn-register-outline btn-reg-parent" onclick="openRegister('Parent')">
                <i class="fa-solid fa-users me-2"></i>Register as Parent
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- ===== FORGOT PASSWORD MODAL ===== -->
    <div class="modal fade" id="forgotPasswordModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header" style="background:linear-gradient(135deg,#e67700,#ffa94d);color:white;">
            <h5 class="modal-title" id="forgotModalTitle"><i class="fa-solid fa-key me-2"></i>Forgot User ID / Password</h5>
            <button class="btn-close" data-bs-dismiss="modal" style="filter:brightness(0) invert(1);"></button>
          </div>
          <div class="modal-body">
            <div class="alert d-flex align-items-start mb-4" role="alert"
              style="background:#fff9e6;border:1.5px solid #ffd43b;border-radius:12px;padding:14px 16px;">
              <i class="fa-solid fa-circle-info me-2 mt-1" style="color:#e67700;"></i>
              <div style="font-size:0.88rem;">Enter your <strong>registered email address</strong> to retrieve your <strong>User ID</strong> and <strong>Password</strong>.</div>
            </div>
            <form method="POST" action="">
              <input type="hidden" name="forgot_role" id="forgotRoleInput" value="">
              <div class="mb-3">
                <label class="form-label"><i class="fa-solid fa-user me-2" style="color:#e67700;"></i>User ID</label>
                <input type="text" class="form-control" name="forgot_user_id" placeholder="Enter your User ID" required>
              </div>
              <div class="mb-4">
                <label class="form-label"><i class="fa-solid fa-envelope me-2" style="color:#e67700;"></i>Registered Email Address</label>
                <input type="email" class="form-control" name="forgot_email" placeholder="Enter your registered email" required>
                <div class="form-text" style="color:#b0bac9;font-size:0.8rem;margin-top:5px;">We will verify your account using this email.</div>
              </div>
              <button type="submit" name="forgot_password" value="1" class="btn-modal-primary btn-modal-forgot">
                <i class="fa-solid fa-magnifying-glass"></i> Find My Account
              </button>
            </form>
            <div class="text-center mt-4">
              <a href="#" class="forgot-link" onclick="backToLogin(); return false;">
                <i class="fa-solid fa-arrow-left me-1"></i>Back to Login
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- ===== REGISTER MODAL ===== -->
    <div class="modal fade" id="registerModal" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header" id="registerModalHeader">
            <h5 class="modal-title" id="registerTitle"></h5>
            <button class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <!-- HOSPITAL FORM -->
            <form id="hospitalForm" name="hregister" method="post" enctype="multipart/form-data">
              <div class="row g-3">
                <div class="col-12"><div class="form-section-title"><i class="fa-solid fa-circle-info"></i> 1. Basic Hospital Information</div></div>
                <div class="col-12"><label class="form-label">Hospital Name</label>
                  <input type="text" name="hname" class="form-control" placeholder="Enter Hospital Name" required pattern="[A-Za-z0-9\\s]{{3,}}"></div>
                <div class="col-md-6"><label class="form-label">Hospital Type</label>
                  <select name="htype" class="form-select" required><option value="">Select Type</option>
                    <option>Government</option><option>Private</option><option>Trust</option><option>Clinic</option></select></div>
                <div class="col-md-6"><label class="form-label">License Number</label>
                  <input type="text" name="hlic" class="form-control" placeholder="Enter License Number" required pattern="[A-Za-z0-9\\-/]{{5,}}"></div>
                <div class="col-md-6"><label class="form-label">Upload License</label>
                  <input type="file" name="hlicproof" class="form-control" accept=".pdf,.jpg,.png" required></div>
                <div class="col-md-6"><label class="form-label">Year of Establishment</label>
                  <input type="number" name="hyear" class="form-control" placeholder="YYYY" min="1800" max="2026" required></div>
                <div class="col-md-6"><label class="form-label">Hospital Logo</label>
                  <input type="file" name="hlogo" class="form-control" accept="image/*" required></div>
    
                <div class="col-12 mt-2"><div class="form-section-title"><i class="fa-solid fa-location-dot"></i> 2. Contact / Address</div></div>
                <div class="col-md-6"><label class="form-label">Email</label>
                  <input type="email" name="hemail" class="form-control" placeholder="example@hospital.com" required></div>
                <div class="col-md-6"><label class="form-label">Hospital Mobile</label>
                  <input type="tel" name="hmobile" class="form-control" placeholder="10-digit mobile" pattern="[6-9]{{1}}[0-9]{{9}}" required></div>
                <div class="col-md-6"><label class="form-label">Emergency Mobile</label>
                  <input type="tel" name="hemcnum" class="form-control" placeholder="10-digit emergency" pattern="[6-9]{{1}}[0-9]{{9}}" required></div>
                <div class="col-md-6"><label class="form-label">State</label>
                  <select name="hstate" class="form-select" id="hospitalState" required onchange="loadDistricts('hospitalState','hospitalDistrict')">
                    <option value="">Select State</option>
                    <option>Andhra Pradesh</option><option>Arunachal Pradesh</option><option>Assam</option><option>Bihar</option>
                    <option>Chhattisgarh</option><option>Goa</option><option>Gujarat</option><option>Haryana</option>
                    <option>Himachal Pradesh</option><option>Jharkhand</option><option>Karnataka</option><option>Kerala</option>
                    <option>Madhya Pradesh</option><option>Maharashtra</option><option>Manipur</option><option>Meghalaya</option>
                    <option>Mizoram</option><option>Nagaland</option><option>Odisha</option><option>Punjab</option>
                    <option>Rajasthan</option><option>Sikkim</option><option>Tamil Nadu</option><option>Telangana</option>
                    <option>Tripura</option><option>Uttar Pradesh</option><option>Uttarakhand</option><option>West Bengal</option>
                  </select></div>
                <div class="col-md-6"><label class="form-label">District</label>
                  <select name="hdistrict" class="form-select" id="hospitalDistrict" required disabled><option value="">Select District</option></select></div>
                <div class="col-md-6"><label class="form-label">City</label><input name="hcity" type="text" class="form-control" placeholder="City" required></div>
                <div class="col-md-6"><label class="form-label">PIN Code</label>
                  <input name="hpin" type="text" class="form-control" placeholder="6-digit PIN" pattern="[0-9]{{6}}" required></div>
                <div class="col-12"><label class="form-label">Building / Street</label>
                  <input name="hstreet" type="text" class="form-control" placeholder="Building / Street Name" required></div>
                <div class="col-md-6"><label class="form-label">Area / Locality</label>
                  <input name="harea" type="text" class="form-control" placeholder="Area / Locality" required></div>
    
                <div class="col-12 mt-2"><div class="form-section-title"><i class="fa-solid fa-stethoscope"></i> 3. Medical &amp; Facility Details</div></div>
                <div class="col-md-6"><label class="form-label">Total Beds</label>
                  <input name="hbed" type="number" class="form-control" placeholder="Enter total beds" min="1" required></div>
                <div class="col-12"><label class="form-label d-block mb-2">ICU Availability</label>
                  <div class="radio-group"><label class="radio-pill"><input type="radio" name="hicu" value="yes" required> Available</label>
                    <label class="radio-pill"><input type="radio" name="hicu" value="no"> Not Available</label></div></div>
                <div class="col-12"><label class="form-label d-block mb-2">Emergency Services</label>
                  <div class="radio-group"><label class="radio-pill"><input type="radio" name="hemc" value="yes" required> Available</label>
                    <label class="radio-pill"><input type="radio" name="hemc" value="no"> Not Available</label></div></div>
                <div class="col-12"><label class="form-label d-block mb-2">Ambulance Facility</label>
                  <div class="radio-group"><label class="radio-pill"><input type="radio" name="hambulance" value="yes" required> Available</label>
                    <label class="radio-pill"><input type="radio" name="hambulance" value="no"> Not Available</label></div></div>
                <div class="col-12"><label class="form-label d-block mb-2">Blood Bank</label>
                  <div class="radio-group"><label class="radio-pill"><input type="radio" name="hbbank" value="yes" required> Available</label>
                    <label class="radio-pill"><input type="radio" name="hbbank" value="no"> Not Available</label></div></div>
                <div class="col-12"><label class="form-label d-block mb-2">Pharmacy</label>
                  <div class="radio-group"><label class="radio-pill"><input type="radio" name="hpharmacy" value="yes" required> Available</label>
                    <label class="radio-pill"><input type="radio" name="hpharmacy" value="no"> Not Available</label></div></div>
    
                <div class="col-12 mt-2"><div class="form-section-title"><i class="fa-solid fa-clock"></i> 4. Operating Details</div></div>
                <div class="col-12"><label class="form-label d-block mb-2">24/7 Service</label>
                  <div class="radio-group"><label class="radio-pill"><input type="radio" name="hservice" value="yes" required> Yes</label>
                    <label class="radio-pill"><input type="radio" name="hservice" value="no"> No</label></div></div>
                <div class="col-md-6"><label class="form-label">Working Hours</label>
                  <input type="text" name="hwtime" class="form-control" placeholder="e.g., 09:00 AM - 06:00 PM" required></div>
                <div class="col-md-6"><label class="form-label">OPD Timings</label>
                  <input type="text" name="hopdtime" class="form-control" placeholder="e.g., 10:00 AM - 04:00 PM" required></div>
    
                <div class="col-12 mt-2"><div class="form-section-title"><i class="fa-solid fa-user-tie"></i> 5. Administrator Registration</div></div>
                <div class="col-md-6"><label class="form-label">Owner Name</label>
                  <input type="text" name="oname" class="form-control" placeholder="Enter full name" pattern="[A-Za-z\\s]{{3,50}}" required></div>
                <div class="col-md-6"><label class="form-label">Date of Birth</label>
                  <input type="date" name="odob" class="form-control" required></div>
                <div class="col-md-6"><label class="form-label">Gender</label>
                  <select name="ogender" class="form-select" required><option value="">Select Gender</option>
                    <option>Male</option><option>Female</option><option>Other</option></select></div>
                <div class="col-md-6"><label class="form-label">Profile Photo</label>
                  <input type="file" name="oprofile" class="form-control" accept="image/*" required></div>
    
                <div class="col-12 mt-2"><div class="form-section-title"><i class="fa-solid fa-id-card"></i> 6. Identity &amp; Verification</div></div>
                <div class="col-md-6"><label class="form-label">ID Type</label>
                  <input type="text" name="oid" class="form-control" value="Adhaar card" readonly required></div>
                <div class="col-md-6"><label class="form-label">ID Number</label>
                  <input type="text" name="oidnum" class="form-control" placeholder="Enter your ID number" required></div>
                <div class="col-md-6"><label class="form-label">ID Proof Upload</label>
                  <input type="file" name="oidproof" class="form-control" accept="image/*,application/pdf" required></div>
    
                <div class="col-12 mt-2"><div class="form-section-title"><i class="fa-solid fa-building"></i> 7. Ownership Details</div></div>
                <div class="col-12"><label class="form-label d-block mb-2">Owner Type</label>
                  <div class="radio-group">
                    <label class="radio-pill"><input type="radio" name="otype" value="Individual" required> Individual</label>
                    <label class="radio-pill"><input type="radio" name="otype" value="Partnership"> Partnership</label>
                    <label class="radio-pill"><input type="radio" name="otype" value="Trust"> Trust</label>
                  </div></div>
                <div class="col-md-6"><label class="form-label">Ownership Proof</label>
                  <input type="file" name="oownership" class="form-control" accept="image/*,application/pdf" required></div>
                <div class="col-12">
                  <div class="form-check">
                    <input name="hterms" class="form-check-input" type="checkbox" id="hospitalTerms" required>
                    <label class="form-check-label" for="hospitalTerms" style="font-size:0.88rem;color:var(--text-muted);">I agree to the terms &amp; conditions</label>
                  </div></div>
                <div class="col-12">
                  <button type="submit" name="hregister" value="1" class="modal-submit-btn">
                    <i class="fa-solid fa-hospital me-2"></i>Register Hospital
                  </button></div>
              </div>
            </form>
    
            <!-- PARENT FORM -->
            <form id="parentForm" name="pregister" method="post" enctype="multipart/form-data">
              <div class="row g-3">
                <div class="col-12"><div class="form-section-title"><i class="fa-solid fa-users"></i> 1. Parent / Guardian Information</div></div>
                <div class="col-md-6"><label class="form-label">Relationship to Child</label>
                  <select name="ptype" class="form-select" required><option value="">Select relationship</option>
                    <option>Father</option><option>Mother</option><option>Guardian</option></select></div>
                <div class="col-md-6"><label class="form-label">Parent / Guardian Name</label>
                  <input type="text" name="pname" class="form-control" placeholder="Enter full name" pattern="[A-Za-z\\s]{{3,50}}" required></div>
                <div class="col-md-6"><label class="form-label">Gender</label>
                  <select name="pgender" class="form-select" required><option value="">Select gender</option>
                    <option>Male</option><option>Female</option><option>Other</option></select></div>
                <div class="col-md-6"><label class="form-label">Date of Birth</label>
                  <input type="date" name="pdob" class="form-control" required></div>
                <div class="col-md-6"><label class="form-label">Mobile Number</label>
                  <input type="tel" name="pmobile" class="form-control" placeholder="10-digit mobile" pattern="[6-9]{{1}}[0-9]{{9}}" required></div>
                <div class="col-md-6"><label class="form-label">Email Address</label>
                  <input type="email" name="pemail" class="form-control" placeholder="example@email.com" required></div>
                <div class="col-12"><label class="form-label d-block mb-2">Birth Order</label>
                  <div class="radio-group">
                    <label class="radio-pill"><input type="radio" name="corder" value="One Child" required> One Child</label>
                    <label class="radio-pill"><input type="radio" name="corder" value="Two Childs"> Two Childs</label>
                    <label class="radio-pill"><input type="radio" name="corder" value="Three Childs"> Three Childs</label>
                    <label class="radio-pill"><input type="radio" name="corder" value="Four Childs"> Four Childs</label>
                    <label class="radio-pill"><input type="radio" name="corder" value="Five Childs"> Five Childs</label>
                  </div></div>
                <div class="col-md-6"><label class="form-label">Profile Photo</label>
                  <input type="file" name="pprofile" class="form-control" accept="image/*" required></div>
    
                <div class="col-12 mt-2"><div class="form-section-title"><i class="fa-solid fa-address-book"></i> 2. Contact Details</div></div>
                <div class="col-md-6"><label class="form-label">Alternate Mobile</label>
                  <input type="tel" name="palternum" class="form-control" placeholder="10-digit alternate" pattern="[6-9]{{1}}[0-9]{{9}}"></div>
                <div class="col-md-6"><label class="form-label">State</label>
                  <select name="pstate" class="form-select" id="parentState" required onchange="loadDistricts('parentState','parentDistrict')">
                    <option value="">Select State</option>
                    <option>Andhra Pradesh</option><option>Arunachal Pradesh</option><option>Assam</option><option>Bihar</option>
                    <option>Chhattisgarh</option><option>Goa</option><option>Gujarat</option><option>Haryana</option>
                    <option>Himachal Pradesh</option><option>Jharkhand</option><option>Karnataka</option><option>Kerala</option>
                    <option>Madhya Pradesh</option><option>Maharashtra</option><option>Manipur</option><option>Meghalaya</option>
                    <option>Mizoram</option><option>Nagaland</option><option>Odisha</option><option>Punjab</option>
                    <option>Rajasthan</option><option>Sikkim</option><option>Tamil Nadu</option><option>Telangana</option>
                    <option>Tripura</option><option>Uttar Pradesh</option><option>Uttarakhand</option><option>West Bengal</option>
                  </select></div>
                <div class="col-md-6"><label class="form-label">District</label>
                  <select name="pdistrict" class="form-select" id="parentDistrict" required disabled><option value="">Select District</option></select></div>
                <div class="col-md-6"><label class="form-label">City</label>
                  <input type="text" name="pcity" class="form-control" placeholder="City" required></div>
                <div class="col-md-6"><label class="form-label">PIN Code</label>
                  <input type="text" name="ppin" class="form-control" placeholder="6-digit PIN" pattern="[0-9]{{6}}" required></div>
                <div class="col-md-6"><label class="form-label">Area / Locality</label>
                  <input type="text" name="parea" class="form-control" placeholder="Area / Locality" required></div>
                <div class="col-12"><label class="form-label">House No / Street</label>
                  <input type="text" name="pstreet" class="form-control" placeholder="House number / Street name" required></div>
    
                <div class="col-12 mt-2"><div class="form-section-title"><i class="fa-solid fa-id-card"></i> 3. Identity &amp; Verification</div></div>
                <div class="col-md-6"><label class="form-label">ID Type</label>
                  <input type="text" name="pid" class="form-control" value="Adhaar card" readonly required></div>
                <div class="col-md-6"><label class="form-label">ID Number</label>
                  <input type="text" name="pidnum" class="form-control" placeholder="Enter ID number" pattern="[A-Za-z0-9]{{6,20}}" required>
                  <small style="color:#b0bac9;font-size:0.78rem;">Aadhaar Number (12 digits)</small></div>
                <div class="col-md-6"><label class="form-label">ID Proof Upload</label>
                  <input type="file" name="pidproof" class="form-control" accept="image/*,application/pdf" required>
                  <small style="color:#b0bac9;font-size:0.78rem;">Accepted: JPG, PNG, PDF</small></div>
                <div class="col-12">
                  <div class="form-check">
                    <input name="pterm" class="form-check-input" type="checkbox" id="parentTerms" required>
                    <label class="form-check-label" for="parentTerms" style="font-size:0.88rem;color:var(--text-muted);">I agree to the terms &amp; conditions</label>
                  </div></div>
                <div class="col-12">
                  <button type="submit" name="pregister" value="1" class="modal-submit-btn green">
                    <i class="fa-solid fa-users me-2"></i>Register Parent
                  </button></div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" style="border-radius:10px;font-weight:600;">Cancel</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- ===== HERO ===== -->
    <section class="hero-section">
      <div class="hero-blob hero-blob-1"></div>
      <div class="hero-blob hero-blob-2"></div>
      <div class="container position-relative">
        <div class="row align-items-center">
          <div class="col-lg-6 col-md-7">
            <div class="hero-title">Child Vaccination<br><span style="color:#a8f0de;">Management System</span></div>
            <p class="hero-sub">Ensuring every child receives vaccines on time through a secure, modern digital healthcare platform trusted by hospitals and families across India.</p>
            <div class="hero-actions">
              <button class="btn-hero-primary" onclick="openLoginModal('parent')">
                <i class="fa-solid fa-right-to-bracket me-2"></i>Get Started
              </button>
              <button class="btn-hero-outline" onclick="openLoginModal('hospital')">
                <i class="fa-solid fa-hospital me-2"></i>Hospital Portal
              </button>
            </div>
            <div class="hero-badges">
              <div class="hero-badge"><i class="fa-solid fa-shield-heart"></i> Secure &amp; Safe</div>
              <div class="hero-badge"><i class="fa-solid fa-bell"></i> Smart Reminders</div>
              <div class="hero-badge"><i class="fa-solid fa-mobile-screen"></i> User Friendly</div>
            </div>
          </div>
          <div class="col-lg-6 col-md-5">
            <div class="hero-img-wrap">
              <img src="https://cdn-icons-png.flaticon.com/512/2966/2966486.png" alt="Vaccination Illustration">
            </div>
          </div>
        </div>
      </div>
      <svg class="hero-wave" viewBox="0 0 1440 100" preserveAspectRatio="none">
        <path fill="#f0f5fc" d="M0,40L60,50C120,60,240,80,360,80C480,80,600,60,720,50C840,40,960,40,1080,46.7C1200,53,1320,67,1380,73.3L1440,80L1440,100L0,100Z"></path>
      </svg>
    </section>
    
    <!-- ===== STAT CARDS (DB values) ===== -->
    <section class="stats-section">
      <div class="container">
        <div class="row g-4 mt-1">
          <div class="col-6 col-lg-3">
            <div class="stat-card s1">
              <div class="stat-icon"><i class="fa-solid fa-child"></i></div>
              <div class="stat-number"><span class="counter" data-target="{cnt_children}">0</span>+</div>
              <div class="stat-label">Children Protected</div>
            </div>
          </div>
          <div class="col-6 col-lg-3">
            <div class="stat-card s2">
              <div class="stat-icon"><i class="fa-solid fa-hospital"></i></div>
              <div class="stat-number"><span class="counter" data-target="{cnt_hospitals}">0</span>+</div>
              <div class="stat-label">Registered Hospitals</div>
            </div>
          </div>
          <div class="col-6 col-lg-3">
            <div class="stat-card s3">
              <div class="stat-icon"><i class="fa-solid fa-syringe"></i></div>
              <div class="stat-number"><span class="counter" data-target="{cnt_vaccines}">0</span>+</div>
              <div class="stat-label">Vaccines Tracked</div>
            </div>
          </div>
          <div class="col-6 col-lg-3">
            <div class="stat-card s4">
              <div class="stat-icon"><i class="fa-solid fa-percent"></i></div>
              <div class="stat-number"><span class="counter" data-target="99.9">0</span>%</div>
              <div class="stat-label">Accuracy Rate</div>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <!-- ===== SYSTEM HIGHLIGHTS ===== -->
    <section class="highlights-section">
      <div class="container">
        <div class="text-center mb-5">
          <div class="section-label">Who Uses This System</div>
          <h2 class="section-title">Built for Everyone in the <span style="color:var(--primary);">Healthcare Chain</span></h2>
          <p class="section-sub mx-auto">A unified platform connecting parents, hospitals, and administrators for seamless vaccination management.</p>
        </div>
        <div class="row g-4">
          <div class="col-md-4"><div class="role-card rc-parent">
            <div class="role-icon"><i class="fa-solid fa-user-shield"></i></div>
            <h5>Parents &amp; Guardians</h5>
            <p>Track your child's vaccination history, book appointments, and get timely reminders for upcoming vaccines.</p>
          </div></div>
          <div class="col-md-4"><div class="role-card rc-hospital">
            <div class="role-icon"><i class="fa-solid fa-hospital"></i></div>
            <h5>Hospitals &amp; Clinics</h5>
            <p>Update vaccination records, manage schedules, handle patient appointments, and provide digital vaccine certificates.</p>
          </div></div>
          <div class="col-md-4"><div class="role-card rc-admin">
            <div class="role-icon"><i class="fa-solid fa-chart-simple"></i></div>
            <h5>Administrators</h5>
            <p>Monitor vaccination coverage across regions, generate reports, and oversee the entire healthcare network.</p>
          </div></div>
        </div>
      </div>
    </section>
    
    <!-- ===== STRIP BANNER ===== -->
    <section class="strip-banner">
      <div class="container content text-center">
        <h2>A Smarter Way to Manage Vaccination</h2>
        <p>Modern tools for better child healthcare outcomes</p>
        <div class="strip-dots">
          <div class="strip-dot"><i class="fa-solid fa-calendar-check me-2"></i>Easy Appointment Booking</div>
          <div class="strip-dot"><i class="fa-solid fa-lock me-2"></i>Secure Records</div>
          <div class="strip-dot"><i class="fa-solid fa-heart-pulse me-2"></i>Better Healthcare</div>
          <div class="strip-dot"><i class="fa-solid fa-bell me-2"></i>Smart Alerts</div>
        </div>
      </div>
    </section>
    
    <!-- ===== FEATURES ===== -->
    <section class="features-section">
      <div class="container">
        <div class="text-center mb-5">
          <div class="section-label">Key Features</div>
          <h2 class="section-title">Everything You Need, <span style="color:var(--primary);">All in One Place</span></h2>
        </div>
        <div class="row g-4">
          <div class="col-sm-6 col-lg-4"><div class="feature-card fc1">
            <div class="feature-icon"><i class="fas fa-syringe"></i></div>
            <h5>Vaccination Scheduling</h5>
            <p>Automatic reminders and smart scheduling for upcoming vaccines, ensuring no dose is ever missed.</p>
          </div></div>
          <div class="col-sm-6 col-lg-4"><div class="feature-card fc2">
            <div class="feature-icon"><i class="fa-solid fa-shield-heart"></i></div>
            <h5>Secure Health Records</h5>
            <p>Safe, permanent, and tamper-proof digital records of your child's entire vaccination history.</p>
          </div></div>
          <div class="col-sm-6 col-lg-4"><div class="feature-card fc3">
            <div class="feature-icon"><i class="fa-solid fa-chart-pie"></i></div>
            <h5>Admin Dashboard</h5>
            <p>Comprehensive vaccination analytics, coverage monitoring, and insightful reports for administrators.</p>
          </div></div>
    
          <div class="col-sm-6 col-lg-4"><div class="feature-card fc4">
            <div class="feature-icon"><i class="fa-solid fa-calendar-check"></i></div>
            <h5>Appointment Tracking</h5>
            <p>Easily book, reschedule, and track vaccination appointments with real-time status updates...</p>
          </div></div>
    
          <div class="col-sm-6 col-lg-4"><div class="feature-card fc5">
            <div class="feature-icon"><i class="fa-solid fa-file-waveform"></i></div>
            <h5>Child Health Reports</h5>
            <p>Detailed health reports for each child including vaccination history, growth milestones, and upcoming dose summaries.</p>
          </div></div>
          <div class="col-sm-6 col-lg-4"><div class="feature-card fc6">
            <div class="feature-icon"><i class="fa-solid fa-bell"></i></div>
            <h5>Real-Time Alerts</h5>
            <p>Instant email notifications for upcoming doses, appointment confirmations, and health advisories.</p>
          </div></div>
        </div>
      </div>
    </section>
    
    <!-- ===== METRICS ===== -->
    <section class="metrics-section">
      <div class="container">
        <div class="row">
          <div class="col-6 col-md-3 metric-item metric-divider"><div class="metric-num">100%</div><div class="metric-label">Digital Records</div></div>
          <div class="col-6 col-md-3 metric-item metric-divider"><div class="metric-num">24&#xD7;7</div><div class="metric-label">System Availability</div></div>
          <div class="col-6 col-md-3 metric-item metric-divider"><div class="metric-num">27+</div><div class="metric-label">States Covered</div></div>
          <div class="col-6 col-md-3 metric-item"><div class="metric-num">5&#x2605;</div><div class="metric-label">User Satisfaction</div></div>
        </div>
      </div>
    </section>
    
    <!-- ===== FOOTER ===== -->
    <footer class="cvs-footer">
      <div class="container">
        <div class="row gy-5">
          <div class="col-lg-4 col-md-6">
            <div class="footer-brand">
              <img src="MP-CVS-logo.png" alt="Logo">
              <div class="footer-brand-name">Child Vaccination Management System</div>
            </div>
            <p class="footer-desc">A secure digital platform designed to manage child vaccination records, schedule appointments, and improve healthcare service delivery across India.</p>
            <div class="footer-social">
              <a href="#" class="social-btn"><i class="fa-brands fa-facebook-f"></i></a>
              <a href="#" class="social-btn"><i class="fa-brands fa-twitter"></i></a>
              <a href="#" class="social-btn"><i class="fa-brands fa-instagram"></i></a>
              <a href="#" class="social-btn"><i class="fa-brands fa-linkedin-in"></i></a>
            </div>
          </div>
          <div class="col-lg-2 col-md-6 col-6">
            <div class="footer-heading">Services</div>
            <ul class="footer-links">
              <li><a href="#"><i class="fa-solid fa-chevron-right" style="font-size:0.7rem;"></i>Vaccination Records</a></li>
              <li><a href="#"><i class="fa-solid fa-chevron-right" style="font-size:0.7rem;"></i>Appointments</a></li>
              <li><a href="#"><i class="fa-solid fa-chevron-right" style="font-size:0.7rem;"></i>Hospitals</a></li>
              <li><a href="#"><i class="fa-solid fa-chevron-right" style="font-size:0.7rem;"></i>Notifications</a></li>
            </ul>
          </div>
          <div class="col-lg-2 col-md-6 col-6">
            <div class="footer-heading">Quick Links</div>
            <ul class="footer-links">
              <li><a href="/"><i class="fa-solid fa-chevron-right" style="font-size:0.7rem;"></i>Home</a></li>
              <li><a href="/"><i class="fa-solid fa-chevron-right" style="font-size:0.7rem;"></i>Profile</a></li>
              <li><a href="/"><i class="fa-solid fa-chevron-right" style="font-size:0.7rem;"></i>Login</a></li>
              <li><a href="/help"><i class="fa-solid fa-chevron-right" style="font-size:0.7rem;"></i>Help</a></li>
            </ul>
          </div>
          <div class="col-lg-4 col-md-6">
            <div class="footer-heading">Contact Us</div>
            <div class="footer-contact-item"><i class="fa-solid fa-location-dot"></i><span>Health Department, Government of India</span></div>
            <div class="footer-contact-item"><i class="fa-solid fa-envelope"></i><span>support@cvs.gov.in</span></div>
            <div class="footer-contact-item"><i class="fa-solid fa-phone"></i><span>+91 93457 90381</span></div>
            <div class="footer-contact-item"><i class="fa-solid fa-clock"></i><span>Mon - Sat, 9:00 AM - 6:00 PM</span></div>
          </div>
        </div>
        <hr class="footer-divider">
        <div class="row align-items-center">
          <div class="col-md-6 text-center text-md-start">
            <div class="footer-copy">&#169; 2026 Child Vaccination Management System. All rights reserved.</div>
          </div>
          <div class="col-md-6 text-center text-md-end mt-2 mt-md-0">
            <div class="footer-copy">Made with <i class="fa-solid fa-heart" style="color:#e03131;font-size:0.75rem;"></i> for healthier children</div>
          </div>
        </div>
      </div>
    </footer>
    
    <script>
    // MOBILE MENU
    function toggleMobileMenu(){{const m=document.getElementById('mobileMenu'),i=document.getElementById('hamburgerIcon');m.classList.toggle('open');i.className=m.classList.contains('open')?'fa-solid fa-xmark':'fa-solid fa-bars';}}
    function closeMobileMenu(){{const m=document.getElementById('mobileMenu'),i=document.getElementById('hamburgerIcon');m.classList.remove('open');i.className='fa-solid fa-bars';}}
    document.addEventListener('click',function(e){{const m=document.getElementById('mobileMenu'),b=document.getElementById('mobileMenuBtn');if(!m.contains(e.target)&&!b.contains(e.target))closeMobileMenu();}});
    
    // STATE-DISTRICT
    const stateDistrictData={{"Andhra Pradesh":["Anantapur","Chittoor","East Godavari","Guntur","Krishna","Kurnool","Nellore","Prakasam","Srikakulam","Visakhapatnam","Vizianagaram","West Godavari","YSR Kadapa"],"Arunachal Pradesh":["Tawang","West Kameng","East Kameng","Papum Pare","Kurung Kumey","Kra Daadi","Lower Subansiri","Upper Subansiri","West Siang","East Siang","Siang","Upper Siang","Lower Siang","Lower Dibang Valley","Dibang Valley","Anjaw","Lohit","Namsai","Changlang","Tirap","Longding"],"Assam":["Baksa","Barpeta","Biswanath","Bongaigaon","Cachar","Charaideo","Chirang","Darrang","Dhemaji","Dhubri","Dibrugarh","Goalpara","Golaghat","Hailakandi","Hojai","Jorhat","Kamrup Metropolitan","Kamrup","Karbi Anglong","Karimganj","Kokrajhar","Lakhimpur","Majuli","Morigaon","Nagaon","Nalbari","Dima Hasao","Sivasagar","Sonitpur","South Salamara-Mankachar","Tinsukia","Udalguri","West Karbi Anglong"],"Bihar":["Araria","Arwal","Aurangabad","Banka","Begusarai","Bhagalpur","Bhojpur","Buxar","Darbhanga","East Champaran","Gaya","Gopalganj","Jamui","Jehanabad","Kaimur","Katihar","Khagaria","Kishanganj","Lakhisarai","Madhepura","Madhubani","Munger","Muzaffarpur","Nalanda","Nawada","Patna","Purnia","Rohtas","Saharsa","Samastipur","Saran","Sheikhpura","Sheohar","Sitamarhi","Siwan","Supaul","Vaishali","West Champaran"],"Chhattisgarh":["Balod","Baloda Bazar","Balrampur","Bastar","Bemetara","Bijapur","Bilaspur","Dantewada","Dhamtari","Durg","Gariaband","Janjgir-Champa","Jashpur","Kabirdham","Kanker","Kondagaon","Korba","Koriya","Mahasamund","Mungeli","Narayanpur","Raigarh","Raipur","Rajnandgaon","Sukma","Surajpur","Surguja"],"Goa":["North Goa","South Goa"],"Gujarat":["Ahmedabad","Amreli","Anand","Aravalli","Banaskantha","Bharuch","Bhavnagar","Botad","Chhota Udaipur","Dahod","Dang","Devbhoomi Dwarka","Gandhinagar","Gir Somnath","Jamnagar","Junagadh","Kheda","Kutch","Mahisagar","Mehsana","Morbi","Narmada","Navsari","Panchmahal","Patan","Porbandar","Rajkot","Sabarkantha","Surat","Surendranagar","Tapi","Vadodara","Valsad"],"Haryana":["Ambala","Bhiwani","Charkhi Dadri","Faridabad","Fatehabad","Gurugram","Hisar","Jhajjar","Jind","Kaithal","Karnal","Kurukshetra","Mahendragarh","Nuh","Palwal","Panchkula","Panipat","Rewari","Rohtak","Sirsa","Sonipat","Yamunanagar"],"Himachal Pradesh":["Bilaspur","Chamba","Hamirpur","Kangra","Kinnaur","Kullu","Lahaul and Spiti","Mandi","Shimla","Sirmaur","Solan","Una"],"Jharkhand":["Bokaro","Chatra","Deoghar","Dhanbad","Dumka","East Singhbhum","Garhwa","Giridih","Godda","Gumla","Hazaribagh","Jamtara","Khunti","Koderma","Latehar","Lohardaga","Pakur","Palamu","Ramgarh","Ranchi","Sahebganj","Seraikela-Kharsawan","Simdega","West Singhbhum"],"Karnataka":["Bagalkot","Ballari","Belagavi","Bengaluru Rural","Bengaluru Urban","Bidar","Chamarajanagar","Chikkaballapur","Chikkamagaluru","Chitradurga","Dakshina Kannada","Davanagere","Dharwad","Gadag","Hassan","Haveri","Kalaburagi","Kodagu","Kolar","Koppal","Mandya","Mysuru","Raichur","Ramanagara","Shivamogga","Tumakuru","Udupi","Uttara Kannada","Vijayanagara","Yadgir"],"Kerala":["Alappuzha","Ernakulam","Idukki","Kannur","Kasaragod","Kollam","Kottayam","Kozhikode","Malappuram","Palakkad","Pathanamthitta","Thiruvananthapuram","Thrissur","Wayanad"],"Madhya Pradesh":["Agar Malwa","Alirajpur","Anuppur","Ashoknagar","Balaghat","Barwani","Betul","Bhind","Bhopal","Burhanpur","Chhatarpur","Chhindwara","Damoh","Datia","Dewas","Dhar","Dindori","Guna","Gwalior","Harda","Hoshangabad","Indore","Jabalpur","Jhabua","Katni","Khandwa","Khargone","Mandla","Mandsaur","Morena","Narsinghpur","Neemuch","Panna","Raisen","Rajgarh","Ratlam","Rewa","Sagar","Satna","Sehore","Seoni","Shahdol","Shajapur","Sheopur","Shivpuri","Sidhi","Singrauli","Tikamgarh","Ujjain","Umaria","Vidisha"],"Maharashtra":["Ahmednagar","Akola","Amravati","Aurangabad","Beed","Bhandara","Buldhana","Chandrapur","Dhule","Gadchiroli","Gondia","Hingoli","Jalgaon","Jalna","Kolhapur","Latur","Mumbai City","Mumbai Suburban","Nagpur","Nanded","Nandurbar","Nashik","Osmanabad","Palghar","Parbhani","Pune","Raigad","Ratnagiri","Sangli","Satara","Sindhudurg","Solapur","Thane","Wardha","Washim","Yavatmal"],"Manipur":["Bishnupur","Chandel","Churachandpur","Imphal East","Imphal West","Jiribam","Kakching","Kamjong","Kangpokpi","Noney","Pherzawl","Senapati","Tamenglong","Tengnoupal","Thoubal","Ukhrul"],"Meghalaya":["East Garo Hills","East Jaintia Hills","East Khasi Hills","North Garo Hills","Ri-Bhoi","South Garo Hills","South West Garo Hills","South West Khasi Hills","West Garo Hills","West Jaintia Hills","West Khasi Hills"],"Mizoram":["Aizawl","Champhai","Hnahthial","Khawzawl","Kolasib","Lawngtlai","Lunglei","Mamit","Saiha","Saitual","Serchhip"],"Nagaland":["Chumoukedima","Dimapur","Kiphire","Kohima","Longleng","Mokokchung","Mon","Niuland","Noklak","Peren","Phek","Shamator","Tuensang","Wokha","Zunheboto"],"Odisha":["Angul","Balangir","Balasore","Bargarh","Bhadrak","Boudh","Cuttack","Deogarh","Dhenkanal","Gajapati","Ganjam","Jagatsinghpur","Jajpur","Jharsuguda","Kalahandi","Kandhamal","Kendrapara","Kendujhar","Khordha","Koraput","Malkangiri","Mayurbhanj","Nabarangpur","Nayagarh","Nuapada","Puri","Rayagada","Sambalpur","Subarnapur","Sundargarh"],"Punjab":["Amritsar","Barnala","Bathinda","Faridkot","Fatehgarh Sahib","Fazilka","Ferozepur","Gurdaspur","Hoshiarpur","Jalandhar","Kapurthala","Ludhiana","Malerkotla","Mansa","Moga","Mohali","Muktsar","Pathankot","Patiala","Rupnagar","Sangrur","Shaheed Bhagat Singh Nagar","Tarn Taran"],"Rajasthan":["Ajmer","Alwar","Banswara","Baran","Barmer","Bharatpur","Bhilwara","Bikaner","Bundi","Chittorgarh","Churu","Dausa","Dholpur","Dungarpur","Hanumangarh","Jaipur","Jaisalmer","Jalore","Jhalawar","Jhunjhunu","Jodhpur","Karauli","Kota","Nagaur","Pali","Pratapgarh","Rajsamand","Sawai Madhopur","Sikar","Sirohi","Sri Ganganagar","Tonk","Udaipur"],"Sikkim":["East Sikkim","North Sikkim","South Sikkim","West Sikkim","Pakyong","Soreng"],"Tamil Nadu":["Ariyalur","Chengalpattu","Chennai","Coimbatore","Cuddalore","Dharmapuri","Dindigul","Erode","Kallakurichi","Kanchipuram","Karur","Krishnagiri","Madurai","Mayiladuthurai","Nagapattinam","Namakkal","Nilgiris","Perambalur","Pudukkottai","Ramanathapuram","Ranipet","Salem","Sivaganga","Tenkasi","Thanjavur","Theni","Thoothukudi","Tiruchirappalli","Tirunelveli","Tirupattur","Tiruppur","Tiruvallur","Tiruvannamalai","Tiruvarur","Vellore","Viluppuram","Virudhunagar"],"Telangana":["Adilabad","Bhadradri Kothagudem","Hyderabad","Jagtial","Jangaon","Jayashankar Bhupalpally","Jogulamba Gadwal","Kamareddy","Karimnagar","Khammam","Kumuram Bheem","Mahabubabad","Mahbubnagar","Mancherial","Medak","MedchalMalkajgiri","Mulugu","Nagarkurnool","Nalgonda","Narayanpet","Nirmal","Nizamabad","Peddapalli","Rajanna Sircilla","Ranga Reddy","Sangareddy","Siddipet","Suryapet","Vikarabad","Wanaparthy","Warangal Rural","Warangal Urban","Yadadri Bhuvanagiri"],"Tripura":["Dhalai","Gomati","Khowai","North Tripura","Sepahijala","South Tripura","Unakoti","West Tripura"],"Uttar Pradesh":["Agra","Aligarh","Allahabad","Ambedkar Nagar","Amethi","Amroha","Auraiya","Azamgarh","Baghpat","Bahraich","Ballia","Balrampur","Banda","Barabanki","Bareilly","Basti","Bhadohi","Bijnor","Budaun","Bulandshahr","Chandauli","Chitrakoot","Deoria","Etah","Etawah","Faizabad","Farrukhabad","Fatehpur","Firozabad","Gautam Buddha Nagar","Ghaziabad","Ghazipur","Gonda","Gorakhpur","Hamirpur","Hapur","Hardoi","Hathras","Jalaun","Jaunpur","Jhansi","Kannauj","Kanpur Dehat","Kanpur Nagar","Kasganj","Kaushambi","Kheri","Kushinagar","Lalitpur","Lucknow","Maharajganj","Mahoba","Mainpuri","Mathura","Mau","Meerut","Mirzapur","Moradabad","Muzaffarnagar","Pilibhit","Pratapgarh","Raebareli","Rampur","Saharanpur","Sambhal","Sant Kabir Nagar","Shahjahanpur","Shamli","Shravasti","Siddharthnagar","Sitapur","Sonbhadra","Sultanpur","Unnao","Varanasi"],"Uttarakhand":["Almora","Bageshwar","Chamoli","Champawat","Dehradun","Haridwar","Nainital","Pauri Garhwal","Pithoragarh","Rudraprayag","Tehri Garhwal","Udham Singh Nagar","Uttarkashi"],"West Bengal":["Alipurduar","Bankura","Birbhum","Cooch Behar","Dakshin Dinajpur","Darjeeling","Hooghly","Howrah","Jalpaiguri","Jhargram","Kalimpong","Kolkata","Malda","Murshidabad","Nadia","North 24 Parganas","Paschim Bardhaman","Paschim Medinipur","Purba Bardhaman","Purba Medinipur","Purulia","South 24 Parganas","Uttar Dinajpur"]}};
    
    // COUNTER
    document.querySelectorAll('.counter').forEach(c=>{{const u=()=>{{const t=+c.getAttribute('data-target'),v=+c.innerText,i=t/200;if(v<t){{c.innerText=Math.ceil(v+i);setTimeout(u,20);}}else c.innerText=t;}};u();}});
    
    // MODALS
    function openLoginModal(t){{if(t==='admin')new bootstrap.Modal(document.getElementById("adminLoginModal")).show();if(t==='hospital')new bootstrap.Modal(document.getElementById("hospitalLoginModal")).show();if(t==='parent')new bootstrap.Modal(document.getElementById("parentLoginModal")).show();}}
    
    function openRegister(t){{
      document.getElementById("hospitalForm").style.display="none";
      document.getElementById("parentForm").style.display="none";
      const h=document.getElementById("registerModalHeader");
      h.classList.remove('hospital','parent');
      if(t==="Hospital"){{document.getElementById("registerTitle").innerHTML='<i class="fa-solid fa-hospital me-2"></i>Hospital Registration';h.classList.add('hospital');document.getElementById("hospitalForm").style.display="block";}}
      else if(t==="Parent"){{document.getElementById("registerTitle").innerHTML='<i class="fa-solid fa-users me-2"></i>Parent Registration';h.classList.add('parent');document.getElementById("parentForm").style.display="block";}}
      ['adminLoginModal','hospitalLoginModal','parentLoginModal'].forEach(id=>{{const i=bootstrap.Modal.getInstance(document.getElementById(id));if(i)i.hide();}});
      new bootstrap.Modal(document.getElementById("registerModal")).show();
    }}
    
    let forgotFromRole="";
    function openForgotPassword(role){{
      forgotFromRole=role;
      document.getElementById("forgotRoleInput").value=role;
      const t=document.getElementById("forgotModalTitle");
      t.innerHTML=role==="hospital"?'<i class="fa-solid fa-hospital me-2"></i>Hospital - Forgot User ID / Password':'<i class="fa-solid fa-users me-2"></i>Parent - Forgot User ID / Password';
      ['adminLoginModal','hospitalLoginModal','parentLoginModal'].forEach(id=>{{const i=bootstrap.Modal.getInstance(document.getElementById(id));if(i)i.hide();}});
      setTimeout(()=>{{new bootstrap.Modal(document.getElementById("forgotPasswordModal")).show();}},300);
    }}
    function backToLogin(){{
      const i=bootstrap.Modal.getInstance(document.getElementById("forgotPasswordModal"));
      if(i)i.hide();
      setTimeout(()=>{{if(forgotFromRole==="hospital")new bootstrap.Modal(document.getElementById("hospitalLoginModal")).show();else if(forgotFromRole==="parent")new bootstrap.Modal(document.getElementById("parentLoginModal")).show();}},400);
    }}
    
    function loadDistricts(sId,dId){{
      const s=document.getElementById(sId).value,d=document.getElementById(dId);
      d.innerHTML='<option value="">Select District</option>';d.disabled=true;
      if(!s||!stateDistrictData[s])return;
      stateDistrictData[s].forEach(v=>{{const o=document.createElement("option");o.value=v;o.textContent=v;d.appendChild(o);}});
      d.disabled=false;
    }}
    </script>
    </body>
    </html>
    """
        
@app.route("/help")
def help_page():
    return """<!DOCTYPE html>
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
    <a href="/" class="btn-back">
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

function submitTicket() {
  const fullName = document.getElementById('fullName').value.trim();
  const email = document.getElementById('contactEmail').value.trim();
  const role = document.getElementById('userRole').value;
  const category = document.getElementById('issueCategory').value;
  const priority = document.getElementById('priority').value;
  const description = document.getElementById('issueDescription').value.trim();

  if (!fullName) { alert('Please enter your full name.'); return; }
  if (!email || !email.includes('@')) { alert('Please enter a valid email address.'); return; }
  if (!role) { alert('Please select your role.'); return; }
  if (!category) { alert('Please select an issue category.'); return; }
  if (!description) { alert('Please describe your issue.'); return; }

  const form = new FormData();
  form.append('fullName', fullName);
  form.append('contactEmail', email);
  form.append('userRole', role);
  form.append('issueCategory', category);
  form.append('priority', priority);
  form.append('issueDescription', description);

  const btn = document.getElementById('submitBtn');
  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Submitting...';

  fetch('/submit_ticket', { method: 'POST', body: form })
    .then(r => r.text())
    .then(html => { document.open(); document.write(html); document.close(); })
    .catch(() => {
      alert('Submission failed. Please try again.');
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-paper-plane me-2"></i> Submit Ticket';
    });
}
</script>

</body>
</html>"""


@app.route("/submit_ticket", methods=["POST"])
def submit_ticket():
    try:
        full_name = request.form.get("fullName", "").strip()
        email = request.form.get("contactEmail", "").strip()
        role = request.form.get("userRole", "")
        category = request.form.get("issueCategory", "")
        priority = request.form.get("priority", "")
        description = request.form.get("issueDescription", "").strip()

        if not full_name or not email or not role or not category or not description:
            return "<script>alert('Please fill all required fields.');window.history.back();</script>"

        if con:
            cur.execute(
                """INSERT INTO support_tickets (full_name, email, role, category, priority, description)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (full_name, email, role, category, priority, description)
            )
            con.commit()

        return "<script>alert('\u2705 Support ticket submitted successfully! We will respond within 24 hours.');window.location.href='/help';</script>"
    except Exception as e:
        if con:
            con.rollback()
        return f"<script>alert('Ticket submission failed: {str(e)}');window.history.back();</script>"


@app.errorhandler(404)
def not_found(e):
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>404 Not Found | CVS</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"/>
</head>
<body style="background:#f0f5fc;font-family:'Plus Jakarta Sans',sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;">
<div style="text-align:center;padding:40px;">
  <div style="font-size:5rem;color:#0f6cbd;margin-bottom:16px;"><i class="fa-solid fa-triangle-exclamation"></i></div>
  <h1 style="font-size:4rem;font-weight:900;color:#0f6cbd;margin-bottom:8px;">404</h1>
  <h2 style="font-weight:700;color:#1a2b42;margin-bottom:12px;">Page Not Found</h2>
  <p style="color:#6b7a99;margin-bottom:32px;">The page you are looking for doesn't exist or has been moved.</p>
  <a href="/" style="background:#0f6cbd;color:white;padding:12px 28px;border-radius:12px;text-decoration:none;font-weight:700;">
    <i class="fa-solid fa-house me-2"></i>Back to Home
  </a>
</div>
</body>
</html>""", 404




@app.route("/admin_dashboard")
def admin_dashboard():
    return render_template_string(r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Admin Dashboard - CVS</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">

<!-- BOOTSTRAP CSS -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- FONT AWESOME -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: linear-gradient(135deg, #3b021f, #ec4899, #fdf2f8);
  min-height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  overflow-x: hidden;
}

/* NAVBAR STYLING */
.navbar {
  background: linear-gradient(135deg, #3b021f, #ec4899, #fdf2f8) !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  padding: 15px 20px;
}

.navbar .container-fluid {
  display: flex;
  flex-direction: row;
  align-items: center;
  flex-wrap: nowrap;
}

.navbar-brand {
  font-weight: 600;
  color: white !important;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.navbar-brand i {
  margin-right: 10px;
  color: #fda4af;
  font-size: 1.5rem;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

/* Center brand text on mobile when hamburger is visible */
@media (max-width: 991.98px) {
  .navbar-brand {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    margin: 0 !important;
    white-space: nowrap;
  }
}

/* MOBILE MENU TOGGLE */
.mobile-menu-toggle {
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
}

.mobile-menu-toggle:hover {
  background: rgba(255, 255, 255, 0.28);
  border-color: rgba(255, 255, 255, 0.6);
  color: white;
}

.btn-logout {
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
}

.btn-logout:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(238, 9, 121, 0.6);
  color: white;
}

/* SIDEBAR STYLING */
.sidebar {
  min-height: 100vh;
  background: linear-gradient(135deg, #3b021f, #ec4899);
  box-shadow: 4px 0 15px rgba(0, 0, 0, 0.2);
  padding: 20px 0;
}

.sidebar-link {
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
}

.sidebar-link:hover, .sidebar-link.active {
  background: linear-gradient(90deg, #ec4899, transparent);
  color: #fff;
  border-left: 4px solid #fdf2f8;
  padding-left: 20px;
}

.sidebar-link i {
  margin-right: 10px;
  width: 20px;
  text-align: center;
}

/* CONTENT AREA */
.content-area {
  padding: 20px;
  min-height: 100vh;
}

.section {
  display: none;
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  background: white;
  padding: 20px;
  border-radius: 15px;
  margin-bottom: 20px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  border-left: 5px solid #667eea;
}

.page-header h4 {
  margin: 0;
  color: #2c3e50;
  font-weight: 700;
  font-size: 1.5rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.page-header h4 i {
  margin-right: 10px;
  color: #667eea;
}

/* DASHBOARD CARDS */
.card-box {
  border-radius: 20px;
  padding: 35px;
  color: white;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
  cursor: pointer;
  min-height: 160px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin-bottom: 15px;
}

.card-box::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: rgba(255, 255, 255, 0.1);
  transform: rotate(45deg);
  transition: all 0.6s ease;
}

.card-box:hover::before {
  top: -100%;
  right: -100%;
}

.card-box:hover {
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
}

.card-box h3 {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 1;
}

.card-box p, .card-box a {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  color: white;
  text-decoration: none;
  text-transform: uppercase;
  letter-spacing: 1px;
  position: relative;
  z-index: 1;
}

.card-box a:hover {
  text-decoration: underline;
}

.card-icon {
  position: absolute;
  top: 15px;
  right: 15px;
  font-size: 2.5rem;
  opacity: 0.80;
  z-index: 0;
}

/* CARD COLORS */
.bg-registered    { background: linear-gradient(135deg, #00c6ff, #0072ff, #8e2de2); }
.bg-haccepted     { background: linear-gradient(135deg, #11998e, #38ef7d, #b7f8db); }
.bg-hrejected     { background: linear-gradient(135deg, #833ab4, #fd1d1d, #fcb045); }
.bg-parent        { background: linear-gradient(135deg, #f7971e, #ffd200, #fff6b7); }
.bg-child         { background: linear-gradient(135deg, #b76e79, #f7cac9, #fde2e4); }
.bg-paccepted     { background: linear-gradient(135deg, #5c7c2f 0%, #b2f2bb 100%); }
.bg-prejected     { background: linear-gradient(135deg, #ff512f, #dd2476, #24c6dc); }
.bg-vaccinated    { background: linear-gradient(135deg, #2b1055, #7597de, #b993d6); }
.bg-notvac        { background: linear-gradient(135deg, #fbc2eb, #a6c1ee, #fdfbfb); }
.bg-appointments  { background: linear-gradient(135deg, #ff512f, #f09819, #ffdd00); }

/* TABLE STYLING */
.table-container {
  background: white;
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.table {
  margin: 0;
  border-radius: 10px;
  overflow: hidden;
  width: 100%;
}

.table thead {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.table thead th {
  border: none;
  padding: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.85rem;
  white-space: nowrap;
}

.table tbody tr {
  transition: all 0.3s ease;
}

.table tbody tr:hover {
  background: #f8f9ff;
  transform: scale(1.01);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.table tbody td {
  padding: 12px;
  vertical-align: middle;
  border-bottom: 1px solid #e9ecef;
  font-size: 0.9rem;
}

/* BUTTONS */
.btn-action {
  padding: 6px 15px;
  border-radius: 20px;
  border: none;
  font-weight: 600;
  transition: all 0.3s ease;
  margin: 3px;
  font-size: 0.85rem;
  white-space: nowrap;
}

.btn-accept {
  background: linear-gradient(135deg, #198754 0%, #51cf66 100%);
  color: white;
  box-shadow: 0 4px 10px rgba(25, 135, 84, 0.3);
}

.btn-accept:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(25, 135, 84, 0.5);
  color: white;
}

.btn-reject-action {
  background: linear-gradient(135deg, #dc3545 0%, #ff6b6b 100%);
  color: white;
  box-shadow: 0 4px 10px rgba(220, 53, 69, 0.3);
}

.btn-reject-action:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(220, 53, 69, 0.5);
  color: white;
}

.btn-export {
  padding: 10px 25px;
  border-radius: 25px;
  font-weight: 600;
  margin: 8px 5px;
  transition: all 0.3s ease;
  border: none;
  font-size: 0.95rem;
}

.btn-primary {
  background: linear-gradient(135deg, #0d6efd 0%, #4dabf7 100%);
  box-shadow: 0 4px 15px rgba(13, 110, 253, 0.4);
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(13, 110, 253, 0.6);
}

.btn-secondary {
  background: linear-gradient(135deg, #6c757d 0%, #adb5bd 100%);
  box-shadow: 0 4px 15px rgba(108, 117, 125, 0.4);
}

.btn-secondary:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(108, 117, 125, 0.6);
}

/* STATS BADGE */
.stats-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(255, 255, 255, 0.3);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  backdrop-filter: blur(10px);
  z-index: 1;
}

/* SIDEBAR OVERLAY */
.sidebar-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 998;
}

.sidebar-overlay.show {
  display: block;
}

/* ===== RESPONSIVE MEDIA QUERIES ===== */

/* Tablets and below (992px) */
@media (max-width: 991.98px) {
  .mobile-menu-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .sidebar {
    position: fixed;
    left: -100%;
    top: 0;
    width: 280px;
    height: 100vh;
    z-index: 999;
    transition: left 0.3s ease;
    overflow-y: auto;
  }

  .sidebar.show {
    left: 0;
  }

  .content-area {
    padding: 15px;
    margin-left: 0 !important;
  }

  .navbar-brand {
    font-size: 1rem;
    letter-spacing: 1px;
  }

  .navbar-brand i {
    font-size: 1.3rem;
  }
}

/* Mobile devices (768px and below) */
@media (max-width: 767.98px) {
  .card-box h3 {
    font-size: 2.5rem;
  }

  .card-box p, .card-box a {
    font-size: 0.95rem;
  }

  .page-header h4 {
    font-size: 1.2rem;
  }

  .page-header {
    padding: 15px;
  }

  .content-area {
    padding: 10px;
  }

  .card-box {
    min-height: 140px;
    padding: 20px;
  }

  .table-container {
    padding: 15px;
  }

  .btn-export {
    padding: 8px 20px;
    font-size: 0.85rem;
    display: block;
    width: 100%;
    margin: 5px 0;
  }

  .btn-logout {
    padding: 6px 15px;
    font-size: 0.8rem;
  }
}

/* Small mobile devices (576px and below) */
@media (max-width: 575.98px) {
  .navbar-brand {
    font-size: 0.85rem;
    letter-spacing: 0.5px;
  }

  .navbar-brand i {
    font-size: 1.1rem;
    margin-right: 6px;
  }

  .card-box h3 {
    font-size: 2rem;
  }

  .card-box p, .card-box a {
    font-size: 0.85rem;
  }

  .card-box {
    min-height: 130px;
    padding: 15px;
  }

  .btn-action {
    padding: 5px 10px;
    font-size: 0.75rem;
    margin: 2px;
    display: inline-block;
  }

  .table thead th {
    font-size: 0.7rem;
    padding: 8px 5px;
  }

  .table tbody td {
    padding: 8px 5px;
    font-size: 0.8rem;
  }

  .page-header h4 {
    font-size: 1rem;
  }

  .page-header h4 i {
    display: block;
    margin-bottom: 5px;
  }

  .card-icon {
    font-size: 2rem;
    top: 10px;
    right: 10px;
  }

  .stats-badge {
    font-size: 0.65rem;
    padding: 3px 8px;
  }
}

/* Extra small devices (400px and below) */
@media (max-width: 400px) {
  .navbar-brand {
    font-size: 0.75rem;
  }

  .card-box h3 {
    font-size: 1.8rem;
  }

  .card-box p, .card-box a {
    font-size: 0.75rem;
  }
}
</style>

</head>

<body>

<!-- NAVBAR -->
<nav class="navbar navbar-expand-lg navbar-dark">
  <div class="container-fluid">

    <!-- Hamburger toggle (visible only on mobile/tablet) -->
    <button class="mobile-menu-toggle" onclick="toggleSidebar()">
      <i class="fas fa-bars"></i>
    </button>

    <span class="navbar-brand ms-2">
      <i class="fa-solid fa-hands-holding-child"></i> CVS - Admin
    </span>

    <button class="btn btn-logout ms-auto" onclick="logout()">
      <i class="fas fa-sign-out-alt"></i> Logout
    </button>

  </div>
</nav>

<!-- Sidebar Overlay for Mobile -->
<div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

<div class="container-fluid">
  <div class="row">

    <!-- SIDEBAR -->
    <div class="col-lg-2 col-md-3 sidebar p-0" id="sidebar">
      <a href="admin_dashboard.html" class="sidebar-link active">
        <i class="fas fa-home"></i> Home
      </a>
      <a href="admin_vaccination.html" class="sidebar-link">
        <i class="fa-solid fa-circle-info"></i> Add Vaccination Info
      </a>
      <a href="admin_hospital_registration.html" class="sidebar-link">
        <i class="fas fa-hospital"></i> Hospital Registration
      </a>
      <a href="admin_parent_registration.html" class="sidebar-link">
        <i class="fas fa-user"></i> Parent Registration
      </a>
      <a href="admin_view_child.html" class="sidebar-link">
        <i class="fas fa-baby"></i> View Children
      </a>
      <a href="admin_view_appointment.html" class="sidebar-link">
        <i class="fas fa-calendar-check"></i> View Appointments
      </a>
      <a href="admin_vaccination_schedule.html" class="sidebar-link">
        <i class="fa-solid fa-syringe"></i> Vaccination Schedule
      </a>
      <a href="admin_appointment_reminder.html" class="sidebar-link">
        <i class="fas fa-bell"></i> Appointment Reminders
      </a>
      <a href="admin_export_data.html" class="sidebar-link">
        <i class="fas fa-file-export"></i> Export Data
      </a>
      <a href="admin_view_feedback.html" class="sidebar-link">
        <i class="fas fa-comment-dots"></i> Feedback
      </a>
    </div>

    <!-- CONTENT -->
    <div class="col-lg-10 col-md-9 col-12 content-area">

      <!-- HOME DASHBOARD -->
      <div id="home" class="section">
        <div class="page-header">
          <h4><i class="fas fa-chart-line"></i> Dashboard Overview</h4>
        </div>

        <!-- Hospital Stats Row -->
        <div class="row">
          <div class="col-lg-4 col-md-6 col-sm-6 col-12">
            <div class="card-box bg-registered">
              <span class="stats-badge">PENDING</span>
              <i class="fas fa-hospital-alt card-icon"></i>
              <h3 id="stat-hospital">0</h3>
              <p>Hospitals Registered</p>
            </div>
          </div>
          <div class="col-lg-4 col-md-6 col-sm-6 col-12">
            <div class="card-box bg-haccepted">
              <span class="stats-badge">ACTIVE</span>
              <i class="fas fa-check-circle card-icon"></i>
              <h3 id="stat-hospital-approved">0</h3>
              <p>Hospitals Approved</p>
            </div>
          </div>
          <div class="col-lg-4 col-md-6 col-sm-6 col-12">
            <div class="card-box bg-hrejected">
              <span class="stats-badge">DECLINED</span>
              <i class="fas fa-times-circle card-icon"></i>
              <h3 id="stat-hospital-rejected">0</h3>
              <p>Hospitals Rejected</p>
            </div>
          </div>
        </div>

        <!-- Parent & Children Row -->
        <div class="row">
          <div class="col-lg-6 col-md-6 col-12">
            <div class="card-box bg-parent">
              <span class="stats-badge">PENDING</span>
              <i class="fas fa-user-friends card-icon"></i>
              <h3 id="stat-parent-pending">0</h3>
              <p>Parents Registered</p>
            </div>
          </div>
          <div class="col-lg-6 col-md-6 col-12">
            <div class="card-box bg-child">
              <span class="stats-badge">TOTAL</span>
              <i class="fas fa-baby card-icon"></i>
              <h3 id="stat-children-total">0</h3>
              <p>Children Registered</p>
            </div>
          </div>
        </div>

        <!-- Parent Approved / Rejected Row -->
        <div class="row">
          <div class="col-lg-6 col-md-6 col-12">
            <div class="card-box bg-paccepted">
              <span class="stats-badge">ACTIVE</span>
              <i class="fas fa-check-circle card-icon"></i>
              <h3 id="stat-parent-approved">0</h3>
              <p>Parents Approved</p>
            </div>
          </div>
          <div class="col-lg-6 col-md-6 col-12">
            <div class="card-box bg-prejected">
              <span class="stats-badge">DECLINED</span>
              <i class="fas fa-times-circle card-icon"></i>
              <h3 id="stat-parent-rejected">0</h3>
              <p>Parents Rejected</p>
            </div>
          </div>
        </div>

        <!-- Vaccination & Appointments Row -->
        <div class="row">
          <div class="col-lg-4 col-md-6 col-sm-6 col-12">
            <div class="card-box bg-vaccinated">
              <span class="stats-badge">COMPLETED</span>
              <i class="fas fa-syringe card-icon"></i>
              <h3 id="stat-vaccinated">0</h3>
              <p>Children Vaccinated</p>
            </div>
          </div>
          <div class="col-lg-4 col-md-6 col-sm-6 col-12">
            <div class="card-box bg-notvac">
              <span class="stats-badge">PENDING</span>
              <i class="fas fa-exclamation-triangle card-icon"></i>
              <h3 id="stat-not-vaccinated">0</h3>
              <p>Not Vaccinated</p>
            </div>
          </div>
          <div class="col-lg-4 col-md-6 col-sm-6 col-12">
            <div class="card-box bg-appointments">
              <span class="stats-badge">SCHEDULED</span>
              <i class="fas fa-calendar-alt card-icon"></i>
              <h3 id="stat-appointments">0</h3>
              <p>Appointments Upcoming</p>
            </div>
          </div>
        </div>

      </div><!-- /home section -->

    </div><!-- /content-area -->
  </div><!-- /row -->
</div><!-- /container-fluid -->

<!-- BOOTSTRAP JS -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

<script>
  // ── SAMPLE DATA (replace with your actual API/fetch call) ──────────────────
  const dashboardStats = {
    hospital:             12,
    hospital_approved:     8,
    hospital_rejected:     2,
    parent_pending:       35,
    parent_approved:      58,
    parent_rejected:       7,
    children_total:      104,
    children_vaccinated:  76,
    children_not_vac:     28,
    appointments_upcoming: 14
  };

  // ── POPULATE STATS ─────────────────────────────────────────────────────────
  function populateStats(stats) {
    document.getElementById('stat-hospital').textContent           = stats.hospital;
    document.getElementById('stat-hospital-approved').textContent  = stats.hospital_approved;
    document.getElementById('stat-hospital-rejected').textContent  = stats.hospital_rejected;
    document.getElementById('stat-parent-pending').textContent     = stats.parent_pending;
    document.getElementById('stat-parent-approved').textContent    = stats.parent_approved;
    document.getElementById('stat-parent-rejected').textContent    = stats.parent_rejected;
    document.getElementById('stat-children-total').textContent     = stats.children_total;
    document.getElementById('stat-vaccinated').textContent         = stats.children_vaccinated;
    document.getElementById('stat-not-vaccinated').textContent     = stats.children_not_vac;
    document.getElementById('stat-appointments').textContent       = stats.appointments_upcoming;
  }

  // ── LOGOUT ─────────────────────────────────────────────────────────────────
  function logout() {
    if (confirm("Are you sure you want to logout?")) {
      window.location.href = "Home_main.html";
    }
  }

  // ── SIDEBAR TOGGLE (mobile) ────────────────────────────────────────────────
  function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    sidebar.classList.toggle('show');
    overlay.classList.toggle('show');
  }

  // Close sidebar when clicking outside on mobile
  document.addEventListener('click', function(event) {
    const sidebar = document.getElementById('sidebar');
    const menuToggle = document.querySelector('.mobile-menu-toggle');

    if (!sidebar || !menuToggle) return;

    if (
        window.innerWidth < 992 &&
        !sidebar.contains(event.target) &&
        !menuToggle.contains(event.target) &&
        sidebar.classList.contains('show')
    ) {
        sidebar.classList.remove('show');
        document.getElementById('sidebarOverlay').classList.remove('show');
    }
});

document.querySelectorAll('.sidebar-link').forEach(link => {
    link.addEventListener('click', () => {
        if (window.innerWidth < 992) {
            document.getElementById('sidebar').classList.remove('show');
            document.getElementById('sidebarOverlay').classList.remove('show');
        }
    });
});

  // ── ON LOAD ────────────────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('home').style.display = 'block';
    populateStats(dashboardStats);
  });

  const currentPage = window.location.pathname.split('/').pop();

  document.querySelectorAll('.sidebar-link').forEach(link => {
      const href = link.getAttribute('href');

      if (href === currentPage) {
          document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
          link.classList.add('active');
      }
  });

</script>

</body>
</html>""")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
