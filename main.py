#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import sys
import os
from flask import Flask, request

app = Flask(__name__)

sys.stdout.reconfigure(encoding="utf-8")
print("Content-Type: text/html\r\n\r\n")

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
    print(f"<h2 style='color:red;'>Database Connection Failed!</h2><pre>{e}</pre>")
    sys.exit()

@app.route("/", methods=["GET", "POST"])
def home():
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
                print(
                    '<script>alert("Email already registered! Please use a different email address.");window.location.href="main.py";</script>')
                sys.exit()
            
            os.makedirs("image", exist_ok=True)
            
            
            def save_file(field):
              if field in form and form[field].filename:
                 f = form[field];
                 n = os.path.basename(f.filename)
                 open("image/" + n, "wb").write(f.file.read());
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
            print('<script>alert("Hospital Registered Successfully! \u2705");window.location.href="main.py";</script>')
            sys.exit()
                        
        except pymysql.IntegrityError as e:
            con.rollback()
            em = "Email already registered!" if "email_id" in str(
                e) else "Mobile already registered!" if "hospital_mobile" in str(
                e) else "License number already exists!" if "license_number" in str(e) else "This record already exists."
            print(f'<script>alert("{em}");window.location.href="main.py";</script>');
            sys.exit()
        except Exception as e:
            con.rollback()
            print(f'<script>alert("Registration Failed: {str(e)}");window.location.href="main.py";</script>');
            sys.exit()           

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
                    print(
                        '<script>alert("Email already registered! Please use a different email address.");window.location.href="main.py";</script>')
                    sys.exit()
                        
                os.makedirs("image", exist_ok=True)
                        
                        
                def save_file(field):
                   if field in form and form[field].filename:
                      f = form[field];
                      n = os.path.basename(f.filename)
                      open("image/" + n, "wb").write(f.file.read());
                      return n
                return ""
            
            
                pprofile_name = save_file('pprofile');
                pidproof_name = save_file('pidproof')
                        
                cur.execute("""INSERT INTO parent (parent_type,parent_name,parent_gender,parent_dob,parent_mobile,
                            email_id,parent_profile,alternate_mobile,state,district,city,pincode,street,area,id_type,
                            id_number,id_proof,child_order) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                                    (ptype, pname, pgender, pdob, pmobile, pemail, pprofile_name, palternum, pstate, pdistrict,
                                     pcity, ppin, pstreet, parea, pid, pidnum, pidproof_name, corder))
                con.commit()
                print('<script>alert("Parent Registered Successfully! \u2705");window.location.href="main.py";</script>')
                sys.exit()
                        
            except pymysql.IntegrityError as e:
                con.rollback()
                em = "Email already registered!" if "email_id" in str(
                    e) else "Mobile already registered!" if "parent_mobile" in str(e) else "This record already exists."
                print(f'<script>alert("{em}");window.location.href="main.py";</script>');
                sys.exit()
            except Exception as e:
                con.rollback()
                print(f'<script>alert("Registration Failed: {str(e)}");window.location.href="main.py";</script>');
                sys.exit()

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
                        print(
                            f'<script>alert("\\u2705 Account Found!\\n\\nHospital Name : {name}\\nUser ID : {forgot_user}\\nPassword : {pw}");window.location.href="main.py";</script>')
                   else:
                        print(
                            '<script>alert("\\u274C Invalid Hospital User ID or Email!");window.location.href="main.py";</script>')
                elif forgot_role == "parent":
                    cur.execute("SELECT password, parent_name FROM parent WHERE email_id=%s AND user_id=%s",
                        (forgot_email, forgot_user))
                    result = cur.fetchone()
                    if result:
                        pw, name = result
                        print(
                            f'<script>alert("\\u2705 Account Found!\\n\\nParent Name : {name}\\nUser ID : {forgot_user}\\nPassword : {pw}");window.location.href="main.py";</script>')
                    else:
                        print(
                            '<script>alert("\\u274C Invalid Parent User ID or Email!");window.location.href="main.py";</script>')
            except Exception as e:
                print(f'<script>alert("Error: {str(e)}");window.location.href="main.py";</script>')
                sys.exit()
                    
        # ========== LOGIN PROCESSING ==========
        admin_submit = form.get("admin_login")
        if admin_submit is not None:
            userid = form.get("admin_user_id");
            password = form.get("admin_password")
            if userid and password:
                cur.execute("SELECT id FROM admin WHERE user_id = %s AND password = %s", (userid, password))
                r = cur.fetchone()
                if r:
                    print(
                        f'<script>alert("Admin login successful!");location.href="admin_dashboard.py?admin_id={int(r[0])}";</script>');
                     sys.exit()
                else:
                    print('<script>alert("Invalid Admin credentials!");</script>')
                    
        hospital_submit = form.get("hospital_login")
        if hospital_submit is not None:
            userid = form.get("hospital_user_id");
            password = form.get("hospital_password")
            if userid and password:
                cur.execute("SELECT id FROM hospital WHERE user_id = %s AND password = %s", (userid, password))
                r = cur.fetchone()
                if r:
                    print(
                        f'<script>alert("Hospital login successful!");location.href="hospital_dashboard.py?hospital_id={int(r[0])}";</script>');
                    sys.exit()
                else:
                    print('<script>alert("Invalid Hospital credentials!");</script>')
                    
        parent_submit = form.get("parent_login")
        if parent_submit is not None:
            userid = form.get("parent_user_id");
            password = form.get("parent_password")
            if userid and password:
                cur.execute("SELECT id FROM parent WHERE user_id = %s AND password = %s", (userid, password))
                r = cur.fetchone()
                if r:
                    print(
                        f'<script>alert("Parent login successful!");location.href="parent_dashboard.py?parent_id={int(r[0])}";</script>');
                    sys.exit()
                else:
                    print('<script>alert("Invalid Parent credentials!");</script>')
                    
                    
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
        print(f"""<!DOCTYPE html>
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
              <li><a class="nav-link" href="main_help.py"><i class="fa-solid fa-handshake-angle me-1"></i> Help &amp; Support</a></li>
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
          <a class="nav-link" href="main_help.py"><i class="fa-solid fa-handshake-angle me-2"></i>Help &amp; Support</a>
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
                      <input type="text" name="hname" class="form-control" placeholder="Enter Hospital Name" required pattern="[A-Za-z0-9\s]{{3,}}"></div>
                    <div class="col-md-6"><label class="form-label">Hospital Type</label>
                      <select name="htype" class="form-select" required><option value="">Select Type</option>
                        <option>Government</option><option>Private</option><option>Trust</option><option>Clinic</option></select></div>
                    <div class="col-md-6"><label class="form-label">License Number</label>
                      <input type="text" name="hlic" class="form-control" placeholder="Enter License Number" required pattern="[A-Za-z0-9\-\/]{{5,}}"></div>
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
                      <input type="text" name="oname" class="form-control" placeholder="Enter full name" pattern="[A-Za-z\s]{{3,50}}" required></div>
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
                <form id="parentForm" name="prigister" method="post" enctype="multipart/form-data">
                  <div class="row g-3">
                    <div class="col-12"><div class="form-section-title"><i class="fa-solid fa-users"></i> 1. Parent / Guardian Information</div></div>
                    <div class="col-md-6"><label class="form-label">Relationship to Child</label>
                      <select name="ptype" class="form-select" required><option value="">Select relationship</option>
                        <option>Father</option><option>Mother</option><option>Guardian</option></select></div>
                    <div class="col-md-6"><label class="form-label">Parent / Guardian Name</label>
                      <input type="text" name="pname" class="form-control" placeholder="Enter full name" pattern="[A-Za-z\s]{{3,50}}" required></div>
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
                  <li><a href="main.py"><i class="fa-solid fa-chevron-right" style="font-size:0.7rem;"></i>Home</a></li>
                  <li><a href="main.py"><i class="fa-solid fa-chevron-right" style="font-size:0.7rem;"></i>Profile</a></li>
                  <li><a href="main.py"><i class="fa-solid fa-chevron-right" style="font-size:0.7rem;"></i>Login</a></li>
                  <li><a href="main_help.py"><i class="fa-solid fa-chevron-right" style="font-size:0.7rem;"></i>Help</a></li>
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
        """)
        
        cur.close()
        con.close()
        
        if __name__ == "__main__":
            import os
            port = int(os.environ.get("PORT", 5000))
            app.run(host="0.0.0.0", port=port)
