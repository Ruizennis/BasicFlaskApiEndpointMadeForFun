from flask import Flask, jsonify, request, url_for, render_template
import sqlite3
import json
import datetime
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True # pretty print
app.url_map.strict_slashes = False
items = [
    {"id": 1, "Name": "Name1", "Cost": 10},
    {"id": 2, "Name": "Name2", "Cost": 15}
]

def initdbconnection():
    conn = sqlite3.connect("db.db")
    conn.row_factory = sqlite3.Row
    return conn

def makedbifnotexist():
    conn = initdbconnection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='items'")
    table_exists = cursor.fetchone() is not None

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    conn.close()


makedbifnotexist()

@app.route("/")
def homepage():
    fetched_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn = initdbconnection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items")
        rows = cursor.fetchall()
        conn.close()
        DICT = [dict(row) for row in rows]
        formatted_db = json.dumps(DICT, indent=4,sort_keys=False)
    except Exception as errormsg:
        formatted_db = f"Failed To Fetch Data :(\n Reason: {errormsg}"
    HTML = f'''
<head>
<title>Flask API Endpoint Coding Challange</title>
<style>
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
<h3> /api/items/ </h3>
<hr>
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
<hr>
<dl>
    <dt>/api/datetime/</dt>
    <dd>Fetch Date And Time In The RFC 5322 date-time Format (Methods: GET)</dd>
    <dd>Example Response (JSON) {{"Date&Time":"Sun, 13 Sep 2026 10:53:14 GMT"}}</dd>
    <dd>
        <strong>Optional Parameters:</strong>
        <ul>
            <li>?data=text / ?data=plaintext: Returns raw text instead of JSON</li>
            <li>?format=YYYY-MM-DD: returns YYYY-MM-DD format (No Time)
            <li>?format=ISO8601: Returns Time & Date In The ISO 8601 Format (YYYY-MM-DDTHH:mm:ssZ)
        </ul>
    </dd>
</dl>
<h3> /api/all/ </h3>
<hr>
<dl>
    <dt> /api/all </dt>
    <dd> Return All Api Urls And Their Methods (Methods: GET)</dd>
</dl>
<h3> /api/rebound/ </h3>
<dl>
    <dt> /api/rebound/ </dt>
    <dd> Returns Client IP Headers And Other Data Sent To The Server, Data Is Not logged (Methods: GET, POST) </dd>
</dl>
<hr>
    <h3>Database Contents <small style='Opacity: 0.5'> Last Fetched {fetched_time}</small></h3>


    <pre>
    <code>
    {formatted_db}
    </code>
    </pre>

    <footer>
    <h5> Users Are Never Logged When Using These Api Urls </h5>
    <a href="/sitemap.txt">SiteMap</a>
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
def returnall():
    conn = initdbconnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    conn.close()
    db_items = [dict(row) for row in rows]
    return jsonify(db_items)

@app.route("/api/items/<int:ItemId>")
def ItemLookup(ItemId):
    conn = initdbconnection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (ItemId,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify(dict(row)), 200

    return jsonify({"Code": 404, "Message/reason": "Invalid Item ID!"}), 404
@app.route("/api/items/add", methods=["POST"])
def add_item():
    item_name = request.args.get('name')
    item_cost = request.args.get('cost')
    if not item_name or not item_cost:
        return jsonify({
            "Code": 400,
            "Message/Reason": "Invalid Parameters, Please Provide ?name=...&cost=..."
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
    conn.close()
    return jsonify({
        "Code": 200,
        "message": f"Successfully added '{item_name}' to the database with Id {ID}"
    }), 200
@app.route('/api/items/delete/<int:itemid>', methods=['DELETE'])
def removeitem(itemid):
    if not itemid:
        return jsonify({"Code": 400, "Message/Reason": "Malformed Request, Ensure /<ID>/ is included in your request"}), 400
    conn = initdbconnection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id = ?", (itemid,))
    conn.commit()
    row_del = cursor.rowcount
    conn.close()
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
        conn.close()
        return jsonify({"Code": 400, "Message/Reason": "ID Not Found On DB."}), 400
    item_name = request.args.get('name')
    item_cost = request.args.get('cost')
    if not item_cost and not item_name:
        conn.close()
        return jsonify({"Code": 400, "Message/Reason": "Ensure One or more parameter is added to be updated. (name or cost)"}), 400
    if item_name and item_cost:
        cursor.execute("UPDATE items SET Name = ?, Cost = ? WHERE id = ?", (item_name, item_cost, ItemId))
    elif item_name:
        cursor.execute("UPDATE items SET Name = ? WHERE id = ?", (item_name, ItemId))
    else:
        cursor.execute("UPDATE items SET Cost = ? WHERE id = ?", (item_cost, ItemId))
    conn.commit()
    conn.close()
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
        data = {"Ip": IP}
        response = f"{callback}({json.dumps(data)});"
        return response, 200, {'Content-Type': 'application/javascript'}
    else:
        return jsonify({"Ip": IP}), 200

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
    else:
        return jsonify({"Code": 405, "Message/Reason": f"Invalid Method \"{request.method}\""}), 405


@app.route("/404.html")
def fourOfour():
    return render_template('404.html'), 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404