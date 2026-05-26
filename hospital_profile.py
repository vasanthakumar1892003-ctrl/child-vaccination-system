#!C:/Users/Vasan/AppData/Local/Programs/Python/Python311/python.exe

import pymysql
import cgi
import cgitb
import sys
import os

cgitb.enable()
sys.stdout.reconfigure(encoding="utf-8")
print("Content-Type: text/html\r\n\r\n")

# ============ DATABASE CONNECTION ============
try:
    con = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="cvsdp",
        cursorclass=pymysql.cursors.DictCursor
    )
    cur = con.cursor()
except Exception as e:
    print(f'<h2 style="color:red;">Database Connection Failed!</h2><pre>{e}</pre>')
    sys.exit()

# ============ GET & VALIDATE hospital_id ============
form = cgi.FieldStorage()
hospital_id = form.getvalue("hospital_id")

if not hospital_id or not str(hospital_id).isdigit():
    print("<h3>Invalid hospital</h3>")
    sys.exit()

# ============ UPDATE HANDLERS ============

logosubmit = form.getvalue("logoupdate")
if logosubmit is not None:
    if 'new_logo' in form:
        logo = form['new_logo']
        new_logo_name = os.path.basename(logo.filename)
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        file_ext = os.path.splitext(new_logo_name)[1].lower()
        if file_ext not in allowed_extensions:
            print(f"""<script>alert("Invalid file type. Only JPG, PNG, GIF, and WEBP are allowed.");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
            sys.exit()
        else:
            if not os.path.exists("image"):
                os.makedirs("image")
            open("image/" + new_logo_name, "wb").write(logo.file.read())
            cur.execute("UPDATE hospital SET hospital_logo = %s WHERE id = %s", (new_logo_name, hospital_id))
            con.commit()
            print(f"""<script>alert("Hospital logo updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
            sys.exit()

ownerprofilesubmit = form.getvalue("ownerprofileupdate")
if ownerprofilesubmit is not None:
    if 'new_owner_profile' in form:
        profile = form['new_owner_profile']
        new_profile_name = os.path.basename(profile.filename)
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        file_ext = os.path.splitext(new_profile_name)[1].lower()
        if file_ext not in allowed_extensions:
            print(f"""<script>alert("Invalid file type. Only JPG, PNG, GIF, and WEBP are allowed.");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
            sys.exit()
        else:
            if not os.path.exists("image"):
                os.makedirs("image")
            open("image/" + new_profile_name, "wb").write(profile.file.read())
            cur.execute("UPDATE hospital SET owner_profile = %s WHERE id = %s", (new_profile_name, hospital_id))
            con.commit()
            print(f"""<script>alert("Owner profile photo updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
            sys.exit()

hospitalnamesubmit = form.getvalue("hospitalnameupdate")
new_hospital_name = form.getvalue("up_hospital_name")
if hospitalnamesubmit is not None and new_hospital_name:
    cur.execute("UPDATE hospital SET hospital_name = %s WHERE id = %s", (new_hospital_name, hospital_id))
    con.commit()
    print(f"""<script>alert("Hospital name updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

hospitaltypesubmit = form.getvalue("hospitaltypeupdate")
new_hospital_type = form.getvalue("up_hospital_type")
if hospitaltypesubmit is not None and new_hospital_type:
    cur.execute("UPDATE hospital SET hospital_type = %s WHERE id = %s", (new_hospital_type, hospital_id))
    con.commit()
    print(f"""<script>alert("Hospital type updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

licensenumbersubmit = form.getvalue("licensenumberupdate")
new_license_number = form.getvalue("up_license_number")
if licensenumbersubmit is not None and new_license_number:
    cur.execute("UPDATE hospital SET license_number = %s WHERE id = %s", (new_license_number, hospital_id))
    con.commit()
    print(f"""<script>alert("License number updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

licenseproofsubmit = form.getvalue("licenseproofupdate")
if licenseproofsubmit is not None:
    if 'new_license_proof' in form:
        proof = form['new_license_proof']
        new_proof_name = os.path.basename(proof.filename)
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        file_ext = os.path.splitext(new_proof_name)[1].lower()
        if file_ext not in allowed_extensions:
            print(f"""<script>alert("Invalid file type. Only PDF and images are allowed.");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
            sys.exit()
        else:
            if not os.path.exists("documents"):
                os.makedirs("documents")
            open("documents/" + new_proof_name, "wb").write(proof.file.read())
            cur.execute("UPDATE hospital SET license_proof = %s WHERE id = %s", (new_proof_name, hospital_id))
            con.commit()
            print(f"""<script>alert("License proof updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
            sys.exit()

yearsubmit = form.getvalue("yearupdate")
new_year = form.getvalue("up_year_of_establishment")
if yearsubmit is not None and new_year:
    cur.execute("UPDATE hospital SET year_of_establishment = %s WHERE id = %s", (new_year, hospital_id))
    con.commit()
    print(f"""<script>alert("Year of establishment updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

emailsubmit = form.getvalue("emailupdate")
new_email = form.getvalue("up_email_id")
if emailsubmit is not None and new_email:
    cur.execute("UPDATE hospital SET email_id = %s WHERE id = %s", (new_email, hospital_id))
    con.commit()
    print(f"""<script>alert("Email updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

mobilesubmit = form.getvalue("mobileupdate")
new_mobile = form.getvalue("up_hospital_mobile")
if mobilesubmit is not None and new_mobile:
    cur.execute("UPDATE hospital SET hospital_mobile = %s WHERE id = %s", (new_mobile, hospital_id))
    con.commit()
    print(f"""<script>alert("Mobile number updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

emergencymobilesubmit = form.getvalue("emergencymobileupdate")
new_emergency_mobile = form.getvalue("up_hospital_mobile_emergency")
if emergencymobilesubmit is not None and new_emergency_mobile:
    cur.execute("UPDATE hospital SET hospital_mobile_emergency = %s WHERE id = %s", (new_emergency_mobile, hospital_id))
    con.commit()
    print(f"""<script>alert("Emergency mobile updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

streetsubmit = form.getvalue("streetupdate")
new_street = form.getvalue("up_street")
if streetsubmit is not None and new_street:
    cur.execute("UPDATE hospital SET street = %s WHERE id = %s", (new_street, hospital_id))
    con.commit()
    print(f"""<script>alert("Street updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

areasubmit = form.getvalue("areaupdate")
new_area = form.getvalue("up_area")
if areasubmit is not None and new_area:
    cur.execute("UPDATE hospital SET area = %s WHERE id = %s", (new_area, hospital_id))
    con.commit()
    print(f"""<script>alert("Area updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

citysubmit = form.getvalue("cityupdate")
new_city = form.getvalue("up_city")
if citysubmit is not None and new_city:
    cur.execute("UPDATE hospital SET city = %s WHERE id = %s", (new_city, hospital_id))
    con.commit()
    print(f"""<script>alert("City updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

districtsubmit = form.getvalue("districtupdate")
new_district = form.getvalue("up_district")
if districtsubmit is not None and new_district:
    cur.execute("UPDATE hospital SET district = %s WHERE id = %s", (new_district, hospital_id))
    con.commit()
    print(f"""<script>alert("District updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

statesubmit = form.getvalue("stateupdate")
new_state = form.getvalue("up_state")
if statesubmit is not None and new_state:
    cur.execute("UPDATE hospital SET state = %s WHERE id = %s", (new_state, hospital_id))
    con.commit()
    print(f"""<script>alert("State updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

pincodesubmit = form.getvalue("pincodeupdate")
new_pincode = form.getvalue("up_pincode")
if pincodesubmit is not None and new_pincode:
    cur.execute("UPDATE hospital SET pincode = %s WHERE id = %s", (new_pincode, hospital_id))
    con.commit()
    print(f"""<script>alert("Pincode updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

bedsubmit = form.getvalue("bedupdate")
new_bed = form.getvalue("up_bed")
if bedsubmit is not None and new_bed:
    cur.execute("UPDATE hospital SET bed = %s WHERE id = %s", (new_bed, hospital_id))
    con.commit()
    print(f"""<script>alert("Bed count updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

icusubmit = form.getvalue("icuupdate")
new_icu = form.getvalue("up_icu")
if icusubmit is not None and new_icu:
    cur.execute("UPDATE hospital SET icu = %s WHERE id = %s", (new_icu, hospital_id))
    con.commit()
    print(f"""<script>alert("ICU count updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

emergencysubmit = form.getvalue("emergencyupdate")
new_emergency = form.getvalue("up_emergency")
if emergencysubmit is not None and new_emergency:
    cur.execute("UPDATE hospital SET emergency = %s WHERE id = %s", (new_emergency, hospital_id))
    con.commit()
    print(f"""<script>alert("Emergency info updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

ambulancesubmit = form.getvalue("ambulanceupdate")
new_ambulance = form.getvalue("up_ambulance")
if ambulancesubmit is not None and new_ambulance:
    cur.execute("UPDATE hospital SET ambulance = %s WHERE id = %s", (new_ambulance, hospital_id))
    con.commit()
    print(f"""<script>alert("Ambulance info updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

bloodbanksubmit = form.getvalue("bloodbankupdate")
new_blood_bank = form.getvalue("up_blood_bank")
if bloodbanksubmit is not None and new_blood_bank:
    cur.execute("UPDATE hospital SET blood_bank = %s WHERE id = %s", (new_blood_bank, hospital_id))
    con.commit()
    print(f"""<script>alert("Blood bank info updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

pharmacysubmit = form.getvalue("pharmacyupdate")
new_pharmacy = form.getvalue("up_pharmacy")
if pharmacysubmit is not None and new_pharmacy:
    cur.execute("UPDATE hospital SET pharmacy = %s WHERE id = %s", (new_pharmacy, hospital_id))
    con.commit()
    print(f"""<script>alert("Pharmacy info updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

servicesubmit = form.getvalue("serviceupdate")
new_service = form.getvalue("up_service")
if servicesubmit is not None and new_service:
    cur.execute("UPDATE hospital SET service = %s WHERE id = %s", (new_service, hospital_id))
    con.commit()
    print(f"""<script>alert("Service updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

workingtimesubmit = form.getvalue("workingtimeupdate")
new_working_time = form.getvalue("up_working_time")
if workingtimesubmit is not None and new_working_time:
    cur.execute("UPDATE hospital SET working_time = %s WHERE id = %s", (new_working_time, hospital_id))
    con.commit()
    print(f"""<script>alert("Working time updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

opdtimesubmit = form.getvalue("opdtimeupdate")
new_opd_time = form.getvalue("up_opd_time")
if opdtimesubmit is not None and new_opd_time:
    cur.execute("UPDATE hospital SET opd_time = %s WHERE id = %s", (new_opd_time, hospital_id))
    con.commit()
    print(f"""<script>alert("OPD time updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

ownernamesubmit = form.getvalue("ownernameupdate")
new_owner_name = form.getvalue("up_owner_name")
if ownernamesubmit is not None and new_owner_name:
    cur.execute("UPDATE hospital SET owner_name = %s WHERE id = %s", (new_owner_name, hospital_id))
    con.commit()
    print(f"""<script>alert("Owner name updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

ownerdobsubmit = form.getvalue("ownerdobupdate")
new_owner_dob = form.getvalue("up_owner_dob")
if ownerdobsubmit is not None and new_owner_dob:
    cur.execute("UPDATE hospital SET owner_dob = %s WHERE id = %s", (new_owner_dob, hospital_id))
    con.commit()
    print(f"""<script>alert("Owner DOB updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

ownergendersubmit = form.getvalue("ownergenderupdate")
new_owner_gender = form.getvalue("up_owner_gender")
if ownergendersubmit is not None and new_owner_gender:
    cur.execute("UPDATE hospital SET owner_gender = %s WHERE id = %s", (new_owner_gender, hospital_id))
    con.commit()
    print(f"""<script>alert("Owner gender updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

ownertypesubmit = form.getvalue("ownertypeupdate")
new_owner_type = form.getvalue("up_owner_type")
if ownertypesubmit is not None and new_owner_type:
    cur.execute("UPDATE hospital SET owner_type = %s WHERE id = %s", (new_owner_type, hospital_id))
    con.commit()
    print(f"""<script>alert("Owner type updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

ownershipproofsubmit = form.getvalue("ownershipproofupdate")
if ownershipproofsubmit is not None:
    if 'new_ownership_proof' in form:
        proof = form['new_ownership_proof']
        new_proof_name = os.path.basename(proof.filename)
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        file_ext = os.path.splitext(new_proof_name)[1].lower()
        if file_ext not in allowed_extensions:
            print(f"""<script>alert("Invalid file type. Only PDF and images are allowed.");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
            sys.exit()
        else:
            if not os.path.exists("documents"):
                os.makedirs("documents")
            open("documents/" + new_proof_name, "wb").write(proof.file.read())
            cur.execute("UPDATE hospital SET ownership_proof = %s WHERE id = %s", (new_proof_name, hospital_id))
            con.commit()
            print(f"""<script>alert("Ownership proof updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
            sys.exit()

idtypesubmit = form.getvalue("idtypeupdate")
new_id_type = form.getvalue("up_id_type")
if idtypesubmit is not None and new_id_type:
    cur.execute("UPDATE hospital SET id_type = %s WHERE id = %s", (new_id_type, hospital_id))
    con.commit()
    print(f"""<script>alert("ID type updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

idnumbersubmit = form.getvalue("idnumberupdate")
new_id_number = form.getvalue("up_id_number")
if idnumbersubmit is not None and new_id_number:
    cur.execute("UPDATE hospital SET id_number = %s WHERE id = %s", (new_id_number, hospital_id))
    con.commit()
    print(f"""<script>alert("ID number updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

idproofsubmit = form.getvalue("idproofupdate")
if idproofsubmit is not None:
    if 'new_id_proof' in form:
        proof = form['new_id_proof']
        new_proof_name = os.path.basename(proof.filename)
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        file_ext = os.path.splitext(new_proof_name)[1].lower()
        if file_ext not in allowed_extensions:
            print(f"""<script>alert("Invalid file type. Only PDF and images are allowed.");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
            sys.exit()
        else:
            if not os.path.exists("documents"):
                os.makedirs("documents")
            open("documents/" + new_proof_name, "wb").write(proof.file.read())
            cur.execute("UPDATE hospital SET id_proof = %s WHERE id = %s", (new_proof_name, hospital_id))
            con.commit()
            print(f"""<script>alert("ID proof updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
            sys.exit()

passwordsubmit = form.getvalue("passwordupdate")
new_password = form.getvalue("up_password")
if passwordsubmit is not None and new_password:
    cur.execute("UPDATE hospital SET password = %s WHERE id = %s", (new_password, hospital_id))
    con.commit()
    print(f"""<script>alert("Password updated successfully");location.href="hospital_profile.py?hospital_id={hospital_id}";</script>""")
    sys.exit()

# ============ FETCH HOSPITAL DATA ============
cur.execute("SELECT * FROM hospital WHERE id = %s", (hospital_id,))
hospital = cur.fetchone()

if not hospital:
    print("<h3>Hospital not found</h3>")
    sys.exit()

hospital_name           = hospital["hospital_name"]
hospital_type           = hospital["hospital_type"]
license_number          = hospital["license_number"]
license_proof           = hospital["license_proof"]
year_of_establishment   = hospital["year_of_establishment"]
hospital_logo           = hospital["hospital_logo"]
email_id                = hospital["email_id"]
hospital_mobile         = hospital["hospital_mobile"]
hospital_mobile_emergency = hospital["hospital_mobile_emergency"]
state                   = hospital["state"]
district                = hospital["district"]
city                    = hospital["city"]
pincode                 = hospital["pincode"]
street                  = hospital["street"]
area                    = hospital["area"]
bed                     = hospital["bed"]
icu                     = hospital["icu"]
emergency               = hospital["emergency"]
ambulance               = hospital["ambulance"]
blood_bank              = hospital["blood_bank"]
pharmacy                = hospital["pharmacy"]
service                 = hospital["service"]
working_time            = hospital["working_time"]
opd_time                = hospital["opd_time"]
owner_name              = hospital["owner_name"]
owner_dob               = hospital["owner_dob"]
owner_gender            = hospital["owner_gender"]
owner_profile           = hospital["owner_profile"]
owner_type              = hospital["owner_type"]
ownership_proof         = hospital["ownership_proof"]
id_type                 = hospital["id_type"]
id_number               = hospital["id_number"]
id_proof                = hospital["id_proof"]
status                  = hospital["status"]
created_at              = hospital["Created_at"]
user_id                 = hospital["user_id"]

con.close()

print(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
<title>Hospital Profile - CVS</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
:root {{
  --primary-gradient: linear-gradient(135deg, #b76e79, #f7cac9, #fde2e4);
  --rose-gradient:    linear-gradient(135deg, #b76e79, #f7cac9, #fde2e4);
  --rose-dark:        #b76e79;
  --rose-text:        #5a1f2b;
  --text-dark:        #1f2937;
  --border-color:     #e5e7eb;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
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
.navbar .container-fluid {{
  display: flex; flex-direction: row; align-items: center; flex-wrap: nowrap; gap: 10px;
}}
.navbar-brand {{
  font-weight: 600; color: white !important; letter-spacing: 2px;
  text-transform: uppercase;
}}
.navbar-brand i {{ margin-right: 10px; color: #e9d5ff; font-size: 1.5rem; animation: bounce 2s infinite; }}
@keyframes bounce {{
  0%,100% {{ transform: translateY(0); }}
  50%      {{ transform: translateY(-5px); }}
}}
.navbar-toggler-custom {{
  display: none; flex-shrink: 0;
  background: rgba(255,255,255,0.15); border: 1.5px solid rgba(255,255,255,0.4);
  color: white; padding: 6px 11px; border-radius: 8px; font-size: 1.15rem;
  cursor: pointer; line-height: 1; transition: background 0.25s; order: -1;
}}
./* MOBILE MENU TOGGLE — inside navbar, hidden on desktop */
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
  box-shadow: 4px 0 20px rgba(0,0,0,0.3); padding: 20px 0;
}}
.sidebar-link {{
  display: block; padding: 14px 18px; color: #e9d5ff;
  text-decoration: none; transition: all 0.3s ease;
  border-left: 4px solid transparent; font-weight: 500; margin: 6px 0;
}}
.sidebar-link:hover, .sidebar-link.active {{
  background: linear-gradient(90deg, #22d3ee, transparent 100%);
  color: #fff; border-left: 4px solid #cffafe; padding-left: 24px; transform: translateX(5px);
}}
.sidebar-link i {{ margin-right: 12px; width: 22px; text-align: center; }}

.sidebar-overlay {{
  display: none; position: fixed; top:0; left:0;
  width:100%; height:100%; background:rgba(0,0,0,0.6); z-index:998; backdrop-filter:blur(2px);
}}
.sidebar-overlay.show {{ display: block; }}

/* ===== CONTENT ===== */
.main-content {{ padding: 30px 20px; min-height: 100vh; }}

/* ===== PROFILE CARD ===== */
.profile-card {{
  border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  overflow: hidden; background: white;
}}
.card-header {{
  background: var(--primary-gradient) !important;
  padding: 25px; border: none;
}}
.card-header h5 {{ margin:0; font-size:1.5rem; font-weight:600; }}

/* ===== PROFILE IMAGE SECTION — rose tint bg ===== */
.profile-image-section {{
  text-align: center; padding: 30px 0 20px;
  background: linear-gradient(to bottom, #fde2e4 0%, #fff8f9 100%);
}}
.profile-img {{
  width: 150px; height: 150px; object-fit: cover;
  border: 5px solid white; box-shadow: 0 10px 30px rgba(183,110,121,0.3);
  transition: transform 0.3s ease;
}}
.profile-img:hover {{ transform: scale(1.05); }}

/* ===== CHANGE PHOTO BUTTON — rose gold ===== */
.btn-change-photo {{
  background: var(--rose-gradient);
  border: none; padding: 8px 20px; border-radius: 25px;
  color: var(--rose-text); font-weight: 700;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(183,110,121,0.35);
}}
.btn-change-photo:hover {{ transform: translateY(-2px); color: var(--rose-text); }}

/* ===== SECTION HEADERS — rose gold ===== */
.section-header {{
  background: var(--rose-gradient);
  padding: 15px 20px; border-radius: 12px; margin: 30px 0 20px;
  box-shadow: 0 4px 15px rgba(183,110,121,0.3);
}}
.section-header h6 {{ margin:0; font-size:1.1rem; font-weight:700; color: var(--rose-text); }}

.form-label {{ font-weight:600; color:var(--text-dark); margin-bottom:8px; font-size:0.9rem; }}
.form-control {{
  border: 2px solid var(--border-color); border-radius: 10px;
  padding: 10px 15px; transition: all 0.3s ease; background-color: #f9fafb;
}}
.form-control:focus {{
  border-color: #b76e79; box-shadow: 0 0 0 3px rgba(183,110,121,0.15); background-color: white;
}}
.input-group-text {{
  background: white; border: 2px solid var(--border-color);
  border-left: none; border-radius: 0 10px 10px 0; cursor: pointer; transition: all 0.3s ease;
}}
.input-group-text:hover {{ background: #fdf0f2; }}
.input-group-text i {{ transition: transform 0.3s ease; }}
.input-group-text:hover i {{ transform: scale(1.2); }}
.input-group .form-control {{ border-right: none; border-radius: 10px 0 0 10px; }}

/* ===== MODALS — rose gold header + soft body ===== */
.modal-content {{
  border-radius: 20px; border: none;
  box-shadow: 0 20px 60px rgba(183,110,121,0.25);
}}
.modal-header {{
  background: var(--rose-gradient);
  border-radius: 20px 20px 0 0; padding: 20px 25px; border: none;
}}
.modal-title {{ font-weight:700; font-size:1.2rem; color: var(--rose-text); }}
.modal-title i {{ color: #8b3a47; }}
.btn-close {{
  filter: none;
  background: rgba(90,31,43,0.18) url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%235a1f2b'%3e%3cpath d='M.293.293a1 1 0 0 1 1.414 0L8 6.586 14.293.293a1 1 0 1 1 1.414 1.414L9.414 8l6.293 6.293a1 1 0 0 1-1.414 1.414L8 9.414l-6.293 6.293a1 1 0 0 1-1.414-1.414L6.586 8 .293 1.707a1 1 0 0 1 0-1.414z'/%3e%3c/svg%3e") center/0.8em auto no-repeat;
  border-radius: 50%; opacity: 1;
}}
.btn-close:hover {{ background-color: rgba(90,31,43,0.3); opacity: 1; }}
.modal-body {{ padding: 30px; background: #fffbfc; }}
.modal-body .form-label {{ color:var(--text-dark); font-weight:600; }}
.modal-body .form-control,
.modal-body .form-select {{
  border: 2px solid #f0d0d5; border-radius: 10px; padding: 12px 15px; background: white;
}}
.modal-body .form-control:focus,
.modal-body .form-select:focus {{
  border-color: #b76e79; box-shadow: 0 0 0 3px rgba(183,110,121,0.15);
}}

/* ===== BUTTONS — rose gold primary ===== */
.btn-primary {{
  background: var(--rose-gradient);
  border: none; padding: 10px 28px; border-radius: 10px;
  font-weight: 700; color: var(--rose-text);
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(183,110,121,0.35);
}}
.btn-primary:hover {{
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(183,110,121,0.45);
  color: #3d1019;
}}
.btn-secondary {{
  background: #e5e7eb; border: none; padding: 10px 25px;
  border-radius: 10px; font-weight: 600; color: #374151;
  transition: all 0.3s ease;
}}
.btn-secondary:hover {{ background: #d1d5db; transform: translateY(-2px); color: #1f2937; }}

.card-body {{ padding: 30px; }}
.row.g-3 {{ margin-bottom: 15px; }}

/* ===== RESPONSIVE ===== */
@media (max-width: 991.98px) {{
  .navbar-toggler-custom {{ display: flex; align-items: center; justify-content: center; }}
  .sidebar {{
    position: fixed; left: -100%; top: 0;
    width: 280px; height: 100vh; z-index: 999; transition: left 0.3s ease; overflow-y: auto;
  }}
  .sidebar.show {{ left: 0; }}
  .main-content {{ padding: 15px; }}
  .navbar-brand {{ font-size: 1rem; letter-spacing: 1px; }}
  .navbar-brand i {{ font-size: 1.3rem; }}
}}
@media (max-width: 767.98px) {{
  .main-content {{ padding: 12px; }}
  .btn-logout {{ padding: 6px 16px; font-size: 0.85rem; }}
}}
@media (max-width: 575.98px) {{
  .navbar-brand {{ font-size: 0.85rem; letter-spacing: 0.5px; }}
  .navbar-brand i {{ font-size: 1.1rem; margin-right: 6px; }}
  .btn-logout {{ padding: 6px 12px; font-size: 0.8rem; }}
}}
@media (max-width: 400px) {{
  .navbar-brand {{ font-size: 0.75rem; }}
}}
</style>
</head>
<body>

<!-- NAVBAR -->
<nav class="navbar navbar-dark">
  <div class="container-fluid">
    <button class="navbar-toggler-custom" id="sidebarToggleBtn" onclick="toggleSidebar()">
      <i class="fas fa-bars"></i>
    </button>
    <span class="navbar-brand">
      <i class="fa-solid fa-hospital"></i> CVS - Hospital
    </span>
    <button class="btn-logout" onclick="logout()">
      <i class="fas fa-sign-out-alt"></i> Logout
    </button>
  </div>
</nav>

<div class="sidebar-overlay" id="sidebarOverlay" onclick="toggleSidebar()"></div>

<div class="container-fluid">
  <div class="row">

    <!-- SIDEBAR -->
    <div class="col-lg-2 col-md-3 sidebar p-0" id="sidebar">
      <a href="hospital_dashboard.py?hospital_id={hospital_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fas fa-home"></i> Home
      </a>
      <a href="hospital_vaccination.py?hospital_id={hospital_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fa-solid fa-circle-info"></i> Vaccination Info
      </a>
      <a href="hospital_view_application.py?hospital_id={hospital_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fa-solid fa-user-pen"></i> Parent Application
      </a>
      <a href="hospital_view_appointment.py?hospital_id={hospital_id}" class="sidebar-link" onclick="closeSidebarMobile()">
        <i class="fas fa-calendar-alt"></i> View Appointments
      </a>
      <a href="hospital_profile.py?hospital_id={hospital_id}" class="sidebar-link active" onclick="closeSidebarMobile()">
        <i class="fas fa-user-circle"></i> My Profile
      </a>
      <a href="hospital_feedback.py?hospital_id={hospital_id}" class="sidebar-link" onclick="closeSidebarMobile()">
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
    <div class="col-lg-10 col-md-9 main-content">
      <div class="card profile-card">
        <div class="card-header">
          <h5 class="mb-0 text-white"><i class="fas fa-hospital me-2"></i>Hospital Profile</h5>
        </div>
        <div class="card-body">

          <!-- Hospital Logo -->
          <div class="profile-image-section">
            <img src="image/{hospital_logo}" class="rounded-circle profile-img" alt="Hospital Logo">
            <div></div>
            <button class="btn btn-change-photo mt-3" data-bs-toggle="modal" data-bs-target="#logomodal">
              <i class="fa fa-camera me-2"></i>Change Logo
            </button>
          </div>

          <!-- Hospital Information -->
          <div class="section-header">
            <h6 class="mb-0"><i class="fa fa-hospital me-2"></i>Hospital Information</h6>
          </div>
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Hospital Name</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{hospital_name}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#hospitalnamemodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Hospital Type</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{hospital_type}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#hospitaltypemodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">License Number</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{license_number}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#licensenumbermodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">License Proof</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{license_proof}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#licenseproofmodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Year of Establishment</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{year_of_establishment}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#yearmodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Mobile Number</label>
              <div class="input-group">
                <input type="tel" class="form-control" value="{hospital_mobile}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#mobilemodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Emergency Mobile</label>
              <div class="input-group">
                <input type="tel" class="form-control" value="{hospital_mobile_emergency}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#emergencymobilemodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Working Time</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{working_time}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#workingtimemodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">OPD Time</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{opd_time}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#opdtimemodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Password</label>
              <div class="input-group">
                <input type="password" class="form-control" placeholder="&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#passwordmodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-12">
              <label class="form-label">Email ID</label>
              <div class="input-group">
                <input type="email" class="form-control" value="{email_id}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#emailmodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
          </div>

          <!-- Address Information -->
          <div class="section-header">
            <h6 class="mb-0"><i class="fa fa-map-marker-alt me-2"></i>Address Information</h6>
          </div>
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Street</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{street}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#streetmodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Area</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{area}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#areamodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">City</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{city}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#citymodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">District</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{district}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#districtmodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">State</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{state}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#statemodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Pincode</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{pincode}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#pincodemodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
          </div>

          <!-- Facilities -->
          <div class="section-header">
            <h6 class="mb-0"><i class="fa fa-bed me-2"></i>Facilities</h6>
          </div>
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Beds</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{bed}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#bedmodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">ICU</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{icu}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#icumodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Emergency</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{emergency}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#emergencymodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Ambulance</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{ambulance}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#ambulancemodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Blood Bank</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{blood_bank}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#bloodbankmodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Pharmacy</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{pharmacy}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#pharmacymodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-12">
              <label class="form-label">Services 24&#xD7;7</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{service}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#servicemodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
          </div>

          <!-- Owner Information -->
          <div class="section-header">
            <h6 class="mb-0"><i class="fa fa-user-tie me-2"></i>Owner Information</h6>
          </div>
          <div class="profile-image-section" style="padding:20px 0 10px;">
            <img src="image/{owner_profile}" class="rounded-circle profile-img" alt="Owner Profile">
            <div></div>
            <button class="btn btn-change-photo mt-3" data-bs-toggle="modal" data-bs-target="#ownerprofilemodal">
              <i class="fa fa-camera me-2"></i>Change Owner Photo
            </button>
          </div>
          <div class="row g-3 mt-1">
            <div class="col-md-6">
              <label class="form-label">Owner Name</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{owner_name}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#ownernamemodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Owner Date of Birth</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{owner_dob}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#ownerdobmodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Owner Gender</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{owner_gender}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#ownergendermodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Owner Type</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{owner_type}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#ownertypemodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-12">
              <label class="form-label">Ownership Proof</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{ownership_proof}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#ownershipproofmodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
          </div>

          <!-- ID Proof Information -->
          <div class="section-header">
            <h6 class="mb-0"><i class="fa fa-id-card me-2"></i>ID Proof Information</h6>
          </div>
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">ID Type</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{id_type}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#idtypemodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">ID Number</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{id_number}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#idnumbermodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
            <div class="col-md-12">
              <label class="form-label">ID Proof Document</label>
              <div class="input-group">
                <input type="text" class="form-control" value="{id_proof}" readonly>
                <span class="input-group-text" role="button" data-bs-toggle="modal" data-bs-target="#idproofmodal">
                  <i class="fa fa-pen text-primary"></i></span>
              </div>
            </div>
          </div>

        </div><!-- /card-body -->
      </div><!-- /profile-card -->
    </div><!-- /main-content -->
  </div>
</div>

<!-- ==================== MODALS ==================== -->

<!-- Hospital Logo Modal -->
<div class="modal fade" id="logomodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-camera me-2"></i>Change Hospital Logo</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py" enctype="multipart/form-data">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Upload New Logo</label>
        <input type="file" name="new_logo" class="form-control" accept="image/*" required>
        <small class="text-muted">Accepted: JPG, PNG, GIF, WEBP</small>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="logoupdate" value="1">Update Logo</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Owner Profile Photo Modal -->
<div class="modal fade" id="ownerprofilemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-camera me-2"></i>Change Owner Photo</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py" enctype="multipart/form-data">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Upload Owner Profile Photo</label>
        <input type="file" name="new_owner_profile" class="form-control" accept="image/*" required>
        <small class="text-muted">Accepted: JPG, PNG, GIF, WEBP</small>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="ownerprofileupdate" value="1">Update Photo</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Hospital Name Modal -->
<div class="modal fade" id="hospitalnamemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-hospital me-2"></i>Change Hospital Name</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Hospital Name</label>
        <input type="text" class="form-control" name="up_hospital_name" value="{hospital_name}" required>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="hospitalnameupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Hospital Type Modal -->
<div class="modal fade" id="hospitaltypemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-tag me-2"></i>Change Hospital Type</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Hospital Type</label>
        <select class="form-select" name="up_hospital_type" required>
          <option value="">Select Type</option>
          <option value="Government"  {"selected" if hospital_type=="Government"  else ""}>Government</option>
          <option value="Private"     {"selected" if hospital_type=="Private"     else ""}>Private</option>
          <option value="Trust"       {"selected" if hospital_type=="Trust"       else ""}>Trust</option>
          <option value="Clinic"      {"selected" if hospital_type=="Clinic"      else ""}>Clinic</option>
        </select>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="hospitaltypeupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- License Number Modal -->
<div class="modal fade" id="licensenumbermodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-file-contract me-2"></i>Change License Number</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">License Number</label>
        <input type="text" class="form-control" name="up_license_number" value="{license_number}" required>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="licensenumberupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- License Proof Modal -->
<div class="modal fade" id="licenseproofmodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-file-upload me-2"></i>Upload License Proof</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py" enctype="multipart/form-data">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Upload License Proof</label>
        <input type="file" name="new_license_proof" class="form-control" accept=".pdf,.jpg,.jpeg,.png" required>
        <small class="text-muted">Accepted: PDF, JPG, PNG</small>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="licenseproofupdate" value="1">Upload</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Year of Establishment Modal -->
<div class="modal fade" id="yearmodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-calendar me-2"></i>Change Year of Establishment</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Year of Establishment</label>
        <input type="number" class="form-control" name="up_year_of_establishment" value="{year_of_establishment}" min="1800" max="2100" required>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="yearupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Email Modal -->
<div class="modal fade" id="emailmodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-envelope me-2"></i>Change Email</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Email Address</label>
        <input type="email" class="form-control" name="up_email_id" value="{email_id}" required>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="emailupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Mobile Modal -->
<div class="modal fade" id="mobilemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-phone me-2"></i>Change Mobile Number</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Mobile Number</label>
        <input type="tel" class="form-control" name="up_hospital_mobile" value="{hospital_mobile}" pattern="[0-9]{{10}}" maxlength="10" required>
        <small class="text-muted">Enter 10-digit mobile number</small>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="mobileupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Emergency Mobile Modal -->
<div class="modal fade" id="emergencymobilemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-phone-alt me-2"></i>Change Emergency Mobile</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Emergency Mobile Number</label>
        <input type="tel" class="form-control" name="up_hospital_mobile_emergency" value="{hospital_mobile_emergency}" pattern="[0-9]{{10}}" maxlength="10" required>
        <small class="text-muted">Enter 10-digit mobile number</small>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="emergencymobileupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Street Modal -->
<div class="modal fade" id="streetmodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-road me-2"></i>Change Street</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Street</label>
        <input type="text" class="form-control" name="up_street" value="{street}" required>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="streetupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Area Modal -->
<div class="modal fade" id="areamodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-map-signs me-2"></i>Change Area</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Area</label>
        <input type="text" class="form-control" name="up_area" value="{area}" required>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="areaupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- City Modal -->
<div class="modal fade" id="citymodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-city me-2"></i>Change City</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">City</label>
        <input type="text" class="form-control" name="up_city" value="{city}" required>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="cityupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- District Modal -->
<div class="modal fade" id="districtmodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-map me-2"></i>Change District</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">District</label>
        <input type="text" class="form-control" name="up_district" value="{district}" required>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="districtupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- State Modal -->
<div class="modal fade" id="statemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-flag me-2"></i>Change State</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">State</label>
        <input type="text" class="form-control" name="up_state" value="{state}" required>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="stateupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Pincode Modal -->
<div class="modal fade" id="pincodemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-map-pin me-2"></i>Change Pincode</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Pincode</label>
        <input type="text" class="form-control" name="up_pincode" value="{pincode}" pattern="[0-9]{{6}}" maxlength="6">
        <small class="text-muted">Enter 6-digit pincode</small>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="pincodeupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Bed Modal -->
<div class="modal fade" id="bedmodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-bed me-2"></i>Change Bed Count</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Number of Beds</label>
        <input type="number" class="form-control" name="up_bed" value="{bed}" min="0" required>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="bedupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- ICU Modal -->
<div class="modal fade" id="icumodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-procedures me-2"></i>Change ICU</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">ICU</label>
        <select class="form-select" name="up_icu" required>
          <option value="">Select</option>
          <option value="Available"     {"selected" if icu=="Available"     else ""}>Available</option>
          <option value="Not Available" {"selected" if icu=="Not Available" else ""}>Not Available</option>
        </select>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="icuupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Emergency Modal -->
<div class="modal fade" id="emergencymodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-ambulance me-2"></i>Change Emergency</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Emergency</label>
        <select class="form-select" name="up_emergency" required>
          <option value="">Select</option>
          <option value="Available"     {"selected" if emergency=="Available"     else ""}>Available</option>
          <option value="Not Available" {"selected" if emergency=="Not Available" else ""}>Not Available</option>
        </select>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="emergencyupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Ambulance Modal -->
<div class="modal fade" id="ambulancemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-truck-medical me-2"></i>Change Ambulance</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Ambulance</label>
        <select class="form-select" name="up_ambulance" required>
          <option value="">Select</option>
          <option value="Available"     {"selected" if ambulance=="Available"     else ""}>Available</option>
          <option value="Not Available" {"selected" if ambulance=="Not Available" else ""}>Not Available</option>
        </select>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="ambulanceupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Blood Bank Modal -->
<div class="modal fade" id="bloodbankmodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-tint me-2"></i>Change Blood Bank</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Blood Bank</label>
        <select class="form-select" name="up_blood_bank" required>
          <option value="">Select</option>
          <option value="Available"     {"selected" if blood_bank=="Available"     else ""}>Available</option>
          <option value="Not Available" {"selected" if blood_bank=="Not Available" else ""}>Not Available</option>
        </select>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="bloodbankupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Pharmacy Modal -->
<div class="modal fade" id="pharmacymodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-pills me-2"></i>Change Pharmacy</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Pharmacy</label>
        <select class="form-select" name="up_pharmacy" required>
          <option value="">Select</option>
          <option value="Available"     {"selected" if pharmacy=="Available"     else ""}>Available</option>
          <option value="Not Available" {"selected" if pharmacy=="Not Available" else ""}>Not Available</option>
        </select>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="pharmacyupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Service Modal -->
<div class="modal fade" id="servicemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-stethoscope me-2"></i>Change Service 24&#xD7;7</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Services</label>
        <input type="text" class="form-control" name="up_service" value="{service}" required>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="serviceupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Working Time Modal -->
<div class="modal fade" id="workingtimemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-clock me-2"></i>Change Working Time</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Working Time</label>
        <input type="text" class="form-control" name="up_working_time" value="{working_time}" placeholder="e.g. 8:00 AM - 8:00 PM" required>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="workingtimeupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- OPD Time Modal -->
<div class="modal fade" id="opdtimemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-clock me-2"></i>Change OPD Time</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">OPD Time</label>
        <input type="text" class="form-control" name="up_opd_time" value="{opd_time}" placeholder="e.g. 9:00 AM - 1:00 PM" required>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="opdtimeupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Owner Name Modal -->
<div class="modal fade" id="ownernamemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-user-tie me-2"></i>Change Owner Name</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Owner Name</label>
        <input type="text" class="form-control" name="up_owner_name" value="{owner_name}" required>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="ownernameupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Owner DOB Modal -->
<div class="modal fade" id="ownerdobmodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-calendar me-2"></i>Change Owner Date of Birth</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Date of Birth</label>
        <input type="date" class="form-control" name="up_owner_dob" required>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="ownerdobupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Owner Gender Modal -->
<div class="modal fade" id="ownergendermodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-venus-mars me-2"></i>Change Owner Gender</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Gender</label>
        <select class="form-select" name="up_owner_gender" required>
          <option value="">Select Gender</option>
          <option value="Male"   {"selected" if owner_gender=="Male"   else ""}>Male</option>
          <option value="Female" {"selected" if owner_gender=="Female" else ""}>Female</option>
          <option value="Other"  {"selected" if owner_gender=="Other"  else ""}>Other</option>
        </select>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="ownergenderupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Owner Type Modal -->
<div class="modal fade" id="ownertypemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-user-tag me-2"></i>Change Owner Type</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Owner Type</label>
        <select class="form-select" name="up_owner_type" required>
          <option value="">Select Type</option>
          <option value="Individual"  {"selected" if owner_type=="Individual"  else ""}>Individual</option>
          <option value="Partnership" {"selected" if owner_type=="Partnership" else ""}>Partnership</option>
          <option value="Trust"       {"selected" if owner_type=="Trust"       else ""}>Trust</option>
          <option value="Government"  {"selected" if owner_type=="Government"  else ""}>Government</option>
        </select>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="ownertypeupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Ownership Proof Modal -->
<div class="modal fade" id="ownershipproofmodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-file-upload me-2"></i>Upload Ownership Proof</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py" enctype="multipart/form-data">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Upload Ownership Proof</label>
        <input type="file" name="new_ownership_proof" class="form-control" accept=".pdf,.jpg,.jpeg,.png" required>
        <small class="text-muted">Accepted: PDF, JPG, PNG</small>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="ownershipproofupdate" value="1">Upload</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- ID Type Modal -->
<div class="modal fade" id="idtypemodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-id-card me-2"></i>Change ID Type</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">ID Type</label>
        <select class="form-select" name="up_id_type">
          <option value="">Select ID Type</option>
          <option value="Aadhaar Card" {"selected" if id_type=="Aadhaar Card" else ""}>Aadhaar Card</option>
        </select>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="idtypeupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- ID Number Modal -->
<div class="modal fade" id="idnumbermodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-hashtag me-2"></i>Change ID Number</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">ID Number</label>
        <input type="text" class="form-control" name="up_id_number" value="{id_number}">
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="idnumberupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- ID Proof Modal -->
<div class="modal fade" id="idproofmodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-file-upload me-2"></i>Upload ID Proof</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py" enctype="multipart/form-data">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">Upload ID Proof Document</label>
        <input type="file" name="new_id_proof" class="form-control" accept=".pdf,.jpg,.jpeg,.png" required>
        <small class="text-muted">Accepted: PDF, JPG, PNG</small>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="idproofupdate" value="1">Upload</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<!-- Password Modal -->
<div class="modal fade" id="passwordmodal" data-bs-backdrop="static" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered"><div class="modal-content">
    <div class="modal-header"><h5 class="modal-title"><i class="fas fa-lock me-2"></i>Change Password</h5>
      <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body">
      <form method="post" action="hospital_profile.py">
        <input type="hidden" name="hospital_id" value="{hospital_id}">
        <label class="form-label">New Password</label>
        <input type="password" class="form-control" name="up_password" minlength="6" required>
        <small class="text-muted">Password must be at least 6 characters</small>
        <div class="mt-4 d-flex justify-content-end gap-2">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-primary" name="passwordupdate" value="1">Update</button>
        </div>
      </form>
    </div>
  </div></div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
<script>
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
  var sidebar = document.getElementById('sidebar');
  var btn     = document.getElementById('sidebarToggleBtn');
  if (window.innerWidth < 992 &&
      sidebar.classList.contains('show') &&
      !sidebar.contains(e.target) &&
      !btn.contains(e.target)) {{
    closeSidebarMobile();
  }}
}});
</script>
</body>
</html>""")