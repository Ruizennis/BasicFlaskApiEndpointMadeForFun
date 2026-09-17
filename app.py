from flask import Flask, jsonify, request, url_for, render_template, g, send_file
import sqlite3
import json
import datetime
import io
try:
    import qrcode
    import qrcode.image.svg
    NOT_QRCODE = False
except ImportError:
    NOT_QRCODE = True
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True # auto pretty print json data
app.url_map.strict_slashes = False
items = [
    {"id": 1, "Name": "Name1", "Cost": 10},
    {"id": 2, "Name": "Name2", "Cost": 15}
]

def initdbconnection():
    if 'db' not in g:
        g.db = sqlite3.connect("db.db")
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def makedbifnotexist():
    conn = initdbconnection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='items'")
    table_exists = cursor.fetchone() is not None

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Cost REAL NOT NULL
        )
    ''')
    
    if not table_exists:
        records_to_insert = [(item["id"], item["Name"], item["Cost"]) for item in items]
        
        cursor.executemany(
            "INSERT INTO items (id, Name, Cost) VALUES (?, ?, ?)", 
            records_to_insert
        )
        print("Database initialized and default items seeded!")
    conn.commit()

with app.app_context():
    makedbifnotexist()

@app.route("/")
def homepage():
    fetched_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn = initdbconnection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items")
        rows = cursor.fetchall()
        DICT = [dict(row) for row in rows]
        formatted_db = json.dumps(DICT, indent=4,sort_keys=False)
    except Exception as errormsg:
        formatted_db = f"Failed To Fetch Data :(\n Reason: {errormsg}, maybe try deleteing the DB and trying to run the app twice?"
    HTML = f'''
<head>
<title>Flask API Endpoint Coding Challange</title>
<style>
footer a, footer a:visited {{
    color: #0969da;            
    text-decoration: underline; 
    display: inline-block;   
    margin: 0 15px;           
}}

footer a:hover {{
    color: blue;               
}}

h1 {{
    color: blue;
}}
h5 {{
    color: blue;
}}
footer {{
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #d0d7de;
    grid: flex;
    text-align: center;
    /* Centering rules removed so everything left-aligns naturally */
}}
/* Container wrap */
pre {{
    background-color: #f6f8fa;
    border: 1px solid #d0d7de;
    border-radius: 6px;
    padding: 16px;
    overflow: auto;
    font-size: 85%;
    line-height: 1.45;
    max-width: 100%;
}}

/* Code content */
code {{
    font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace;
    color: #24292f;
}}
</style>
</head>
<h1>Avalilable API URls / Docs </h1>
<h2> All API Data Should Be Returned In JSON Format Unless Specified Manualy</h2>
<hr>
<h3> /api/items/ </h3>
<dl>
    <dt> /api/items/all </dt>
    <dd> Show All Items In The DB </dd>
    <dt> /api/items/&lt;ID&gt; </dt>
    <dd> Show Data For An Item Based On Entered ID </dd>
    <dt> /api/items/add </dt>
    <dd> Add A New Item To The DB (Params: name=...&cost=...) (Method: POST) </dd>
    <dt> /api/items/delete/&lt;ID&gt; </dt>
    <dd> Remove An Item From The DB (Method: DELETE) </dd>
    <dt> /api/items/update/&lt;ID&gt; </dt>
    <dd> Updates An Item On The DB (Params: Name=... OR Cost=... OR Name=...&Cost=...) (Method: PATCH)</dd>
<hr>
<h3> /api/ip/ </h3>
<dl>
    <dt> /api/ip/ (Method: GET) </dt>
    <dd> Get Your Devices Public IP (Params: ?format=...&callback=...) </dd>
        <dd>
        <strong>Optional Parameters:</strong>
        <ul>
            <li>format=text or plaintext: Returns raw text.</li>
            <li>callback=myCallbackFunc: Returns JSONP format wrapped in your custom function.</li>
            <li>Default (No parameters specified): Returns standard JSON.</li>
        </ul>
    </dd>
</dl>
<h3> /api/datetime/ </h3>
<dl>
    <dt>/api/datetime/</dt>
    <dd>Fetch Date And Time In The RFC 5322 date-time Format (Methods: GET)</dd>
    <dd>Example Response (JSON) {{"Date&Time":"Sun, 13 Sep 2026 10:53:14 GMT"}}</dd>
    <dd>
        <strong>Optional Parameters:</strong>
        <ul>
            <li>?data=text / ?data=plaintext: Returns raw text instead of JSON</li>
            <li>?format=YYYY-MM-DD: returns YYYY-MM-DD format (No Time)</li>
            <li>?format=ISO8601: Returns Time & Date In The ISO 8601 Format (YYYY-MM-DDTHH:mm:ssZ) </li>
        </ul>
       	<strong>Note:</strong> Invalid data or format parameters are ignored (defaults: json data and RFC 5322 date-time Format. )
    </dd>
</dl>
<h3> /api/all/ </h3>
<dl>
    <dt> /api/all </dt>
    <dd> Return All Api Urls And Their Methods (Methods: GET)</dd>
</dl>
<h3> /api/rebound/ </h3>
<dl>
    <dt> /api/rebound/rebound & /api/rebound </dt>
    <dd> Returns Client IP Headers And Other Data Sent To The Server, Data Is Not logged (Methods: GET, POST) </dd>
    <dt> /api/rebound/cookies </dt>
    <dd> Returns Client Cookies (Methods: GET)</dt>
</dl>
<h3> /api/qrcode </h3>
<dl>
    <dt> /api/qrcode (Method: GET) </dt>
    <dd> Returns a ascii / svg qrcode based on sent data </dd>
    <dd>
        <dd> The data parameter is required, this is the data embeded in the qrcode </dd>
        <strong>Optional Parameters:</strong>
        <ul>
            <li>?format=text or ?format=plaintext: Returns Qrcode in plain text </li>
        </ul>
       	<strong>Note:</strong> Invalid format parameters are ignored (default: SVG)
    </dd>
<hr>
    <h3>Database Contents <small style='Opacity: 0.5'> Last Fetched {fetched_time}</small></h3>


    <pre>
    <code>
    {formatted_db}
    </code>
    </pre>

    <footer>
    <h5> Users Are Never Logged When Using These Api Urls </h5>
    <a href="/sitemap.txt">SiteMap</a>    <a href="/api/all">All Apis </a> <a href="javascript:window.print()">Print API Docs</a> <a href="/robots.txt">Robots</a>
    </footer>
</dl>

    '''
    return HTML, 200
@app.route('/api')
def HTML():
    LOC = request.url
    html = f'''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<head>
<title>Flask Coding Challange API</title>
<h1>Whoops! You Seem To Be At The Wrong Location :(</h1>
<h2> Perhaps you were looking for the api list or documentation? If so use one of the links bellow :) </p>
<p><a href="/api/all">Get Api List</a></p>
<p><a href="/">Return to the Homepage</a></p>
    '''
    return html, 404
@app.route('/sitemap.txt', methods=['GET'])
def simple_sitemap():
    urls = []
    base_url = request.host_url.rstrip('/') 
    
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            methods = [m for m in rule.methods if m not in ('HEAD', 'OPTIONS')]
            methods_str = ",".join(methods)
            url_line = f"[{methods_str}] {base_url}{rule.rule}"
            urls.append(url_line)
            
    text_content = "\n".join(sorted(urls))
    return text_content, 200, {'Content-Type': 'text/plain'}

@app.route('/api/all', endpoint="api_all_root")
def returnall():
    routes = []
    for route in app.url_map.iter_rules():

        if route.endpoint in ['api_root', 'api_all_root', 'sitemap', 'static']:
            continue
        if not route.rule.startswith('/api'):
            continue

        routes.append({
            "Name": route.rule,
            "Methods": list(route.methods - {"HEAD", "OPTIONS"})
        })
    return jsonify({
            "AmountOfApiUrls": len(routes),
            "Urls": routes
        }), 200

@app.route('/api/items/all')
def returnalltwo():
    conn = initdbconnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    db_items = [dict(row) for row in rows]
    return jsonify(db_items)

@app.route("/api/items/<int:ItemId>")
def ItemLookup(ItemId):
    conn = initdbconnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (ItemId,))
    row = cursor.fetchone()
    if row:
        return jsonify(dict(row)), 200

    return jsonify({"Code": 404, "Message/reason": "Invalid Item ID!"}), 404
@app.route("/api/items/add", methods=["POST"])
def add_item():
    item_name = request.args.get('name')
    item_cost = request.args.get('cost')
    if item_name == None or item_cost == None:
        return jsonify({
            "Code": 400,
            "Message/Reason": "Invalid Parameters, Please Provide ?name=...&cost=...",
            "Params": request.args
        }), 400
    try:
        float(item_cost)
    except ValueError:
        return jsonify({
            "Code": 400,
            "Message/Reason": "Invalid Parameters, Please Ensure Cost Is INT or FLOAT type."
        }), 400
    conn = initdbconnection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO items (Name, Cost) VALUES (?, ?)", (item_name, item_cost))
    ID = cursor.lastrowid
    conn.commit()
    url = url_for('ItemLookup', ItemId=ID, _external=True)
    return jsonify({
        "Code": 201,
        "message": f"Successfully added '{item_name}' to the database with Id {ID}"
    }), 201, {"Location": url}
@app.route('/api/items/delete/<int:itemid>', methods=['DELETE'])
def removeitem(itemid):
    conn = initdbconnection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = ?", (itemid,))
    conn.commit()
    row_del = cursor.rowcount
    if row_del == 0:
        return jsonify({
            "Code": 404,
            "Message/Reason": f"Item id {itemid} Not Found!"
        }), 404
    return jsonify({
        "Code": 200,
        "Message/Reason": f"Item id {itemid} Removed Successfully."
    }), 200
@app.route('/api/items/update/<int:ItemId>', methods=['PATCH'])
def updateitem(ItemId):
    conn = initdbconnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (ItemId,))
    if not cursor.fetchone():
        return jsonify({"Code": 400, "Message/Reason": "ID Not Found On DB."}), 400
    item_name = request.args.get('name')
    item_cost = request.args.get('cost')
    if not item_cost and not item_name:
        return jsonify({"Code": 400, "Message/Reason": "Ensure One or more parameter is added to be updated. (name or cost)"}), 400
    if item_name and item_cost:
        cursor.execute("UPDATE items SET Name = ?, Cost = ? WHERE id = ?", (item_name, item_cost, ItemId))
    elif item_name:
        cursor.execute("UPDATE items SET Name = ? WHERE id = ?", (item_name, ItemId))
    else:
        cursor.execute("UPDATE items SET Cost = ? WHERE id = ?", (item_cost, ItemId))
    conn.commit()
    if item_name and item_cost:
        changes = f"Name to '{item_name}' and Cost to {item_cost}"
    elif item_name:
        changes = f"Name to '{item_name}'"
    else:
        changes = f"Cost to {item_cost}"
    return jsonify({
        "Code": 200,
        "Message/Reason": f"Successfully Updated {ItemId} with {changes}"
    }), 200



@app.route('/api/ip', methods=['GET'])
def returnpubip():
    header = request.headers.get('X-Forwarded-For')
    if header:
        IP = header.split(',')[0].strip()
    else:
        IP = request.remote_addr
    formatting = request.args.get('format')
    callback = request.args.get("callback")
    if formatting in ('text', 'plaintext'):
        return IP
    elif callback:
        data = {"ip": IP}
        response = f"{callback}({json.dumps(data)});"
        return response, 200, {'Content-Type': 'application/javascript'}
    else:
        return jsonify({"ip": IP}), 200

@app.route('/api/datetime', methods=['GET'])
def returntime():
    datatype = request.args.get("data")
    formatting = request.args.get("format")
    if formatting == 'YYYY-MM-DD':
        time = datetime.date.today().strftime('%Y-%m-%d')
    elif formatting == 'ISO8601':
        time = datetime.datetime.now().isoformat()
    else:
        time = datetime.datetime.now()
    if datatype == 'text' or datatype == 'plaintext':
        return str(time), 200
    else:
        return jsonify({"DateTime": time}), 200

@app.route('/api/rebound', methods=['GET', 'POST'])
@app.route('/api/rebound/rebound', methods=['GET', 'POST'])
def rebound():
    header = request.headers.get('X-Forwarded-For')
    if header:
        IP = header.split(',')[0].strip()
    else:
        IP = request.remote_addr
    if request.method == 'POST':
        return jsonify({
            "Type": "POST",
            "args": request.args,
            "data": request.data.decode('utf-8') if request.data else "",
            "ClientIp": IP,
            "headers": dict(request.headers),
            "formdata": request.form,
            "jsondata": request.get_json(silent=True),
            "url": request.url
        }), 200
    elif request.method == 'GET':
        return jsonify({
            "Type": "GET",
            "args": request.args,
            "headers": dict(request.headers),
            "ClientIp": IP,
            "url": request.url
        }), 200

@app.route("/api/rebound/cookies")
def returncookies():
    return jsonify({"Cookies": request.cookies}), 200
@app.route("/api/qrcode")
def returnQR():
    DATA = request.args.get("data")
    FORMAT = request.args.get("format")
    if NOT_QRCODE:
        return jsonify({"Code": 501, "Message/Reason": "This Server Does Not Have /api/qrcode Configured or qrcode is not installed"}), 501
    if not DATA:
        return jsonify({"Code": 400, "Message/Reason": "No Data was entered, please ensure your request contains ?data=..."}), 400
    if FORMAT:
        FORMAT = FORMAT.upper()
    if FORMAT in ["TEXT", "PLAINTEXT"]:
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=1
        )   
        qr.add_data(DATA)
        qr.make(fit=True)
        buffer = io.StringIO()
        qr.print_ascii(out=buffer)
        OUT = buffer.getvalue()
        return OUT, 200
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4,
        image_factory=qrcode.image.svg.SvgImage,
    )
    qr.add_data(DATA)
    qr.make(fit=True)
    img = qr.make_image()
    buffer = io.BytesIO()
    img.save(buffer)
    buffer.seek(0)
    return send_file(buffer, mimetype="image/svg+xml")
@app.route("/robots.txt", methods=["GET"])
def robots():
    fallback = "User-agent: *\nDisallow: /api*\nDisallow: /db.db\n\nSitemap: /sitemap.txt"
    try:
        with open("robots.txt") as F:
            return F.read(), 200, {'Content-Type': 'text/plain'}
    except:
        return fallback, 200, {'Content-Type': 'text/plain'}
@app.route("/404.html")
def fourOfour():
    return render_template('404.html'), 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"Code": 405, "Message/Reason": "Invalid Method!", "Method": request.method}), 405
@app.errorhandler(Exception)
def handleerr(error):
    app.logger.error(f"An unexpected Error occured. {error}")
    return jsonify({
        "Code": 500,
        "Message/Reason": "An internal server error occurred."
    }), 500