from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import sqlite3
import datetime
import json
import base64
import time
import secrets
import hashlib
from pathlib import Path
from fastapi import Request, HTTPException, status, Response, Depends
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

app = FastAPI(title="Ryvo Electrix Server")

BASE_DIR = Path(__file__).parent
DB_PATH = str(BASE_DIR / "admin.db")
SECRET_KEY = "RYVO_SUPER_SECRET_2026"

def create_token(username):
    return f"{username}---" + hashlib.sha256(f"{username}{SECRET_KEY}".encode()).hexdigest()

def verify_token(req: Request):
    t = req.cookies.get("admin_auth")
    if not t: return None
    pts = t.split("---")
    if len(pts) == 2 and pts[1] == hashlib.sha256(f"{pts[0]}{SECRET_KEY}".encode()).hexdigest(): return pts[0]
    return None

def is_super(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT is_superuser FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    return row and row[0] == 1

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS queries (id INTEGER PRIMARY KEY, type TEXT, data TEXT, timestamp TEXT)''')
    try:
        c.execute("ALTER TABLE queries ADD COLUMN status TEXT DEFAULT 'Pending'")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE queries ADD COLUMN remarks TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
        
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, is_superuser INTEGER, is_active INTEGER DEFAULT 1)")
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password, is_superuser, is_active) VALUES (?, ?, 1, 1)", ('admin', 'ryvo123'))

    c.execute("CREATE TABLE IF NOT EXISTS slides (id INTEGER PRIMARY KEY, title TEXT, subtitle TEXT, image_url TEXT, link_text TEXT, link_url TEXT, is_active INTEGER DEFAULT 1)")
    c.execute("CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, range TEXT, speed TEXT, extra TEXT, price TEXT, image_url TEXT, badge TEXT, is_active INTEGER DEFAULT 1)")
    
    c.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    c.execute("SELECT COUNT(*) FROM settings")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO settings (key, value) VALUES (?, ?)", [
            ("contact_phone", "+91 8553417904"),
            ("contact_email", "info@ryvoelectrix.com"),
            ("address_footer", "Eco Tech-11, Plot No - 345,<br>Maincha, Greater Noida,<br>Uttar Pradesh 203202"),
            ("address_contact", "123 Green Mobility Hub, Industrial Area, Phase II, New Delhi, India 110020")
        ])
    
    c.execute("SELECT COUNT(*) FROM slides")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO slides (title, subtitle, image_url, link_text, link_url, is_active) VALUES (?,?,?,?,?,?)", [
            ("Electrify Your <br><span class='accent-text-gradient'>Journey</span>", "Experience the pinnacle of eco-mobility. No License.", "assets/slider1.jpg", "Explore Now", "products", 1),
            ("Unleash <br><span class='accent-text-gradient'>Performance</span>", "Up to 125km range on a single charge.", "assets/slider2.jpg", "Book Test Ride", "#", 1),
            ("Green <br><span class='accent-text-gradient'>Mobility</span>", "Zero emissions. Smart charging.", "assets/slider3.jpg", "Learn More", "about", 1)
        ])
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO products (name, range, speed, extra, price, image_url, badge, is_active) VALUES (?,?,?,?,?,?,?,?)", [
            ("Ryvo ATOM", "100km", "25 km/h", "No License", "₹65,000", "assets/atom.png", "Best Seller", 1),
            ("Ryvo NEUTRON", "125km", "40 km/h", "Rapid Charge", "₹82,000", "assets/neutron.png", "", 1)
        ])
        
    conn.commit()
    conn.close()
init_db()

def render_dynamic_content(content: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT title, subtitle, image_url, link_text, link_url FROM slides WHERE is_active=1")
    slides = c.fetchall()
    slides_html = ""
    for i, s in enumerate(slides):
        active_class = "active" if i == 0 else ""
        btn_action = f'onclick="openTestRideModal()"' if s[4]=='#' else f'onclick="window.location.href=\'{s[4]}\'"'
        slides_html += f"""
            <div class="slide {active_class}" style="background-image: url('{s[2]}');">
                <div class="slide-content">
                    <h1>{s[0]}</h1>
                    <p>{s[1]}</p>
                    <button {btn_action} class="btn-primary" style="display:inline-block;">{s[3]}</button>
                </div>
            </div>"""
    content = content.replace("<!-- DYNAMIC_SLIDES -->", slides_html)
    
    c.execute("SELECT name, range, speed, extra, price, image_url, badge FROM products WHERE is_active=1")
    products = c.fetchall()
    prods_html = ""
    for p in products:
        badge_html = f'<div class="badge">{p[6]}</div>' if p[6] else ""
        prods_html += f"""
            <div class="model-card glass-card fade-up">
                <div class="card-img-wrapper" style="background: rgba(0,0,0,0.2); display:flex; align-items:center; justify-content:center; padding:15px;">
                    <img src="{p[5]}" alt="{p[0]}" style="max-height:100%; object-fit:contain;">
                    {badge_html}
                </div>
                <div class="card-content">
                    <h3 style="margin-bottom: 0.5rem;">{p[0]}</h3>
                    <ul class="specs" style="margin-bottom: 1.2rem;">
                        <li><i data-lucide="battery-charging"></i> Range: {p[1]}</li>
                        <li><i data-lucide="zap"></i> Top Speed: {p[2]}</li>
                        <li><i data-lucide="shield-check"></i> {p[3]}</li>
                    </ul>
                    <div class="price-action">
                        <span class="price">{p[4]}</span>
                        <button onclick="openTestRideModal('{p[0]}')" class="btn-primary" style="padding: 10px 18px; font-size: 0.85rem;">Book Test Ride</button>
                    </div>
                </div>
            </div>"""
    content = content.replace("<!-- DYNAMIC_PRODUCTS -->", prods_html)
    
    c.execute("SELECT key, value FROM settings")
    settings_dict = dict(c.fetchall())
    content = content.replace("{{contact_phone}}", settings_dict.get("contact_phone", ""))
    content = content.replace("{{contact_email}}", settings_dict.get("contact_email", ""))
    content = content.replace("{{address_footer}}", settings_dict.get("address_footer", ""))
    content = content.replace("{{address_contact}}", settings_dict.get("address_contact", ""))
    
    conn.close()
    return content

# Mount assets directory for images
app.mount("/assets", StaticFiles(directory=str(BASE_DIR / "assets")), name="assets")

@app.get("/styles.css")
def get_css():
    return FileResponse(str(BASE_DIR / "styles.css"))

@app.get("/script.js")
def get_js():
    return FileResponse(str(BASE_DIR / "script.js"))

@app.post("/api/submit-query")
async def submit_query(request: Request):
    data = await request.json()
    query_type = data.get("type", "unknown")
    payload = json.dumps(data.get("payload", {}))
    
    # Simulate Notifications
    print(f"\n📧 [EMAIL SENT] New {query_type} query received! Details: {payload}")
    print(f"📱 [WHATSAPP API] Alert triggered to Admin (+91 8553417904): 'New customer inquiry waiting in Admin panel!'\n")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO queries (type, data, timestamp) VALUES (?, ?, ?)", 
              (query_type, payload, str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/admin-login")
async def process_admin_login(request: Request, response: Response):
    data = await request.json()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password, is_active FROM users WHERE username=?", (data.get("username"),))
    row = c.fetchone()
    conn.close()
    if row and row[0] == data.get("password"):
        if row[1] == 1:
            response.set_cookie(key="admin_auth", value=create_token(data.get("username")), httponly=True)
            return {"status": "success"}
        else: return Response(status_code=403, content="Account Disabled")
    return Response(status_code=401)

@app.post("/api/admin-logout")
async def process_admin_logout(response: Response):
    response.delete_cookie("admin_auth")
    return {"status": "success"}

@app.post("/api/update-status")
async def update_status_api(request: Request):
    if not verify_token(request): return Response(status_code=401)
    data = await request.json()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE queries SET status=? WHERE id=?", (data.get("status"), data.get("id")))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/update-remarks")
async def update_remarks_api(request: Request):
    if request.cookies.get("admin_auth") != "authorized":
        return Response(status_code=401)
    data = await request.json()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE queries SET remarks=? WHERE id=?", (data.get("remarks"), data.get("id")))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/admin/slides/add")
async def add_slide_api(request: Request):
    if not verify_token(request): return Response(status_code=401)
    data = await request.json()
    b64 = data["image_b64"].split(",")[1]
    filename = f"assets/slide_{int(time.time())}.jpg"
    with open(str(BASE_DIR / filename), "wb") as f:
        f.write(base64.b64decode(b64))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO slides (title, subtitle, image_url, link_text, link_url, is_active) VALUES (?,?,?,?,?,1)",
              (data["title"], data["subtitle"], filename, data["link_text"], data["link_url"]))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/admin/slides/toggle")
async def toggle_slide_api(request: Request):
    if not verify_token(request): return Response(status_code=401)
    data = await request.json()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE slides SET is_active = ? WHERE id = ?", (data["is_active"], data["id"]))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/admin/settings/update")
async def update_settings_api(request: Request):
    if not verify_token(request): return Response(status_code=401)
    data = await request.json()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE settings SET value=? WHERE key=?", (data.get("contact_phone"), "contact_phone"))
    c.execute("UPDATE settings SET value=? WHERE key=?", (data.get("contact_email"), "contact_email"))
    c.execute("UPDATE settings SET value=? WHERE key=?", (data.get("address_footer"), "address_footer"))
    c.execute("UPDATE settings SET value=? WHERE key=?", (data.get("address_contact"), "address_contact"))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/admin/slides/delete")
async def delete_slide_api(request: Request):
    if not verify_token(request): return Response(status_code=401)
    data = await request.json()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM slides WHERE id = ?", (data["id"],))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/admin/products/add")
async def add_prod_api(request: Request):
    if not verify_token(request): return Response(status_code=401)
    data = await request.json()
    b64 = data["image_b64"].split(",")[1]
    filename = f"assets/prod_{int(time.time())}.png"
    with open(str(BASE_DIR / filename), "wb") as f:
        f.write(base64.b64decode(b64))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO products (name, range, speed, extra, price, image_url, badge, is_active) VALUES (?,?,?,?,?,?,?,1)",
              (data["name"], data["range"], data["speed"], data["extra"], data["price"], filename, data["badge"]))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/admin/products/toggle")
async def toggle_prod_api(request: Request):
    if not verify_token(request): return Response(status_code=401)
    data = await request.json()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE products SET is_active = ? WHERE id = ?", (data["is_active"], data["id"]))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/admin/products/delete")
async def delete_prod_api(request: Request):
    if request.cookies.get("admin_auth") != "authorized": return Response(status_code=401)
    data = await request.json()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id = ?", (data["id"],))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/admin/users/add")
async def api_add_user(request: Request):
    user = verify_token(request)
    if not user or not is_super(user): return Response(status_code=403)
    data = await request.json()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, is_superuser, is_active) VALUES (?, ?, 0, 1)", (data["username"], data["password"]))
        conn.commit()
    except: pass
    conn.close()
    return {"status": "success"}

@app.post("/api/admin/users/toggle")
async def api_toggle_user(request: Request):
    user = verify_token(request)
    if not user or not is_super(user): return Response(status_code=403)
    data = await request.json()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET is_active=? WHERE id=? AND is_superuser=0", (data["is_active"], data["id"]))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.post("/api/admin/users/delete")
async def api_delete_user(request: Request):
    user = verify_token(request)
    if not user or not is_super(user): return Response(status_code=403)
    data = await request.json()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=? AND is_superuser=0", (data["id"],))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request):
    user = verify_token(request)
    if not user:
        with open(str(BASE_DIR / "login.html")) as f:
            return HTMLResponse(f.read())

    is_superuser = is_super(user)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. QUERIES
    c.execute("SELECT id, timestamp, type, data, status, remarks FROM queries ORDER BY id DESC")
    records = c.fetchall()
    rows_html = ""
    for r in records:
        try:
            data_dict = json.loads(r[3])
            data_str = "<br>".join([f"<b>{k}</b>: {v}" for k, v in data_dict.items()])
        except: data_str = r[3]
        status_dropdown = f'''<select onchange="updateStatus({r[0]}, this.value)" style="padding:6px; background:rgba(0,0,0,0.5); color:white; border:1px solid #00f0ff; border-radius:4px; font-family:'Outfit'; outline:none; cursor:pointer;">
            <option value="Pending" {'selected' if r[4]=='Pending' else ''}>🕒 Pending</option>
            <option value="Resolved" {'selected' if r[4]=='Resolved' else ''}>✅ Resolved</option>
            <option value="Discarded" {'selected' if r[4]=='Discarded' else ''}>🗑 Discarded</option>
        </select>'''
        rem_str = r[5] if r[5] else ''
        remarks_input = f"<textarea onchange='updateRemarks({r[0]}, this.value)' style='width:100%; min-width:150px; padding:8px; background:rgba(0,0,0,0.5); color:white; border:1px solid rgba(255,255,255,0.1); border-radius:4px; font-family:\"Outfit\"; display:block; box-sizing:border-box;' placeholder='Add notes...'>{rem_str}</textarea>"
        rows_html += f"<tr><td>{r[1]}</td><td><span class='tag'>{r[2]}</span></td><td>{data_str}</td><td>{status_dropdown}</td><td>{remarks_input}</td></tr>"

    # 2. SLIDES
    c.execute("SELECT id, title, subtitle, image_url, link_text, link_url, is_active FROM slides ORDER BY id DESC")
    slides_db = c.fetchall()
    slides_html = ""
    for s in slides_db:
        checked = "checked" if s[6] else ""
        slides_html += f'''<div class="glass-card" style="padding:15px; margin-bottom:10px; display:flex; align-items:center; gap:20px;">
            <img src="{s[3]}" style="width:100px; height:60px; object-fit:cover; border-radius:4px;">
            <div style="flex:1;"><b>{s[1]}</b><br><span style="color:var(--text-muted); font-size:0.9rem;">{s[2]} ({s[4]} -> {s[5]})</span></div>
            <div>
                <label>Active: <input type="checkbox" {checked} onchange="toggleSlide({s[0]}, this.checked)"></label>
                <button onclick="deleteSlide({s[0]})" style="background:#ff4757; color:white; border:none; padding:5px 10px; border-radius:4px; margin-left:10px; cursor:pointer;">Delete</button>
            </div>
        </div>'''

    # 3. PRODUCTS
    c.execute("SELECT id, name, range, speed, price, image_url, badge, is_active FROM products ORDER BY id DESC")
    prods_db = c.fetchall()
    prods_html = ""
    for p in prods_db:
        checked = "checked" if p[7] else ""
        prods_html += f'''<div class="glass-card" style="padding:15px; margin-bottom:10px; display:flex; align-items:center; gap:20px;">
            <img src="{p[5]}" style="width:80px; height:80px; object-fit:contain; border-radius:4px; background:rgba(0,0,0,0.5);">
            <div style="flex:1;"><b>{p[1]}</b> <span class="badge" style="font-size:0.8rem; padding:2px 6px;">{p[6]}</span><br><span style="color:var(--text-muted); font-size:0.9rem;">Range: {p[2]} | Speed: {p[3]} | Price: {p[4]}</span></div>
            <div>
                <label>Active: <input type="checkbox" {checked} onchange="toggleProd({p[0]}, this.checked)"></label>
                <button onclick="deleteProd({p[0]})" style="background:#ff4757; color:white; border:none; padding:5px 10px; border-radius:4px; margin-left:10px; cursor:pointer;">Delete</button>
            </div>
        </div>'''
        
    # 4. SUB-USERS
    team_tab_btn = ""
    team_tab_content = ""
    if is_superuser:
        team_tab_btn = '<button onclick="showTab(\'team\')" class="tab-btn">Manage Team Access</button>'
        users_html = ""
        c.execute("SELECT id, username, is_active FROM users WHERE is_superuser=0 ORDER BY id DESC")
        for u in c.fetchall():
            checked = "checked" if u[2] else ""
            users_html += f'''<div class="glass-card" style="padding:15px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
                <div><b>@{u[1]}</b> <span class="badge" style="padding:2px 8px;">Sub-User</span></div>
                <div>
                    <label>Active Access: <input type="checkbox" {checked} onchange="toggleTeam({u[0]}, this.checked)"></label>
                    <button onclick="deleteTeam({u[0]})" style="background:#ff4757; color:white; border:none; padding:5px 10px; border-radius:4px; margin-left:10px; cursor:pointer;">Revoke</button>
                </div>
            </div>'''
            
        team_tab_content = f'''<div id="team" class="tab-content"><div style="display:flex; gap:30px;"><div style="flex:1;">
            <h3>Create Sub-User</h3>
            <form onsubmit="addTeamObj(event)" class="glass-card" style="padding:20px;">
                <label>Username</label><input type="text" id="subUser" placeholder="demo.user" required autocomplete="off">
                <label>Password Setup</label><input type="password" id="subPass" required autocomplete="off">
                <button type="submit" style="background:#00f0ff; color:black; font-weight:bold; padding:10px; border:none; border-radius:4px; width:100%; cursor:pointer;">Create Access</button>
            </form>
        </div>
        <div style="flex:1;"><h3>Managed Staff</h3>{users_html}</div></div></div>'''

    # 5. SETTINGS
    c.execute("SELECT key, value FROM settings")
    settings_dict = dict(c.fetchall())
    settings_html = f'''<div id="settings" class="tab-content">
        <h3>Website Configurations</h3>
        <form onsubmit="updateSettings(event)" class="glass-card" style="padding:20px; max-width:600px;">
            <label>Contact Phone</label>
            <input type="text" id="setPhone" value="{settings_dict.get('contact_phone', '')}" required class="form-control" style="margin-bottom:15px; width:100%; border:1px solid rgba(255,255,255,0.2); background:rgba(0,0,0,0.5); padding:8px; color:white;">
            <label>Contact Email</label>
            <input type="email" id="setEmail" value="{settings_dict.get('contact_email', '')}" required class="form-control" style="margin-bottom:15px; width:100%; border:1px solid rgba(255,255,255,0.2); background:rgba(0,0,0,0.5); padding:8px; color:white;">
            <label>Address (Footer)</label>
            <textarea id="setAddrFooter" class="form-control" style="margin-bottom:15px; width:100%; border:1px solid rgba(255,255,255,0.2); background:rgba(0,0,0,0.5); padding:8px; color:white;" rows="3">{settings_dict.get('address_footer', '')}</textarea>
            <label>Address (Contact Page)</label>
            <textarea id="setAddrContact" class="form-control" style="margin-bottom:15px; width:100%; border:1px solid rgba(255,255,255,0.2); background:rgba(0,0,0,0.5); padding:8px; color:white;" rows="3">{settings_dict.get('address_contact', '')}</textarea>
            <button type="submit" style="background:#00f0ff; color:black; font-weight:bold; padding:10px; border:none; border-radius:4px; width:100%; cursor:pointer;">Save Settings</button>
        </form>
    </div>'''

    conn.close()
    
    with open(str(BASE_DIR / "admin.html")) as f:
        html = f.read()
    
    html = html.replace("{team_tab_btn}", team_tab_btn).replace("{team_tab_content}", team_tab_content).replace("{settings_txt}", settings_html)
    html = html.replace("{rows_html}", rows_html).replace("{slides_html}", slides_html).replace("{prods_html}", prods_html)
    return HTMLResponse(html)

@app.get("/", response_class=HTMLResponse)
@app.get("/home", response_class=HTMLResponse)
def home():
    """Returns index.html but magically strips all .html references for clean URLs"""
    with open(str(BASE_DIR / "index.html")) as f: 
        content = f.read()
        content = render_dynamic_content(content)
        content = content.replace('href="index.html"', 'href="/"')
        return content.replace(".html", "")

@app.get("/{page}", response_class=HTMLResponse)
def read_page(page: str):
    """Dynamically serves any .html file as a clean URL"""
    file_path = str(BASE_DIR / f"{page}.html")
    
    if os.path.exists(file_path):
        with open(file_path) as f:
            content = f.read()
            content = render_dynamic_content(content)
            # Rewrite all links on-the-fly dynamically
            content = content.replace('href="index.html"', 'href="/"')
            return content.replace(".html", "")
            
    return HTMLResponse("Page not found.", status_code=404)
