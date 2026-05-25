from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json, csv, os, io
from datetime import datetime

import mimetypes
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')

base_dir = os.path.dirname(os.path.abspath(__file__))
web_app_dir = os.path.join(base_dir, "..", "web-app")
app = Flask(__name__, static_folder=web_app_dir, static_url_path="/static_assets_hidden")
CORS(app)

@app.route("/<path:filename>")
def serve_static(filename):
    file_path = os.path.join(web_app_dir, filename)
    if os.path.exists(file_path):
        mimetype = None
        if filename.endswith(".css"):
            mimetype = "text/css"
        elif filename.endswith(".js"):
            mimetype = "application/javascript"
        return send_file(file_path, mimetype=mimetype)
    return jsonify({"error": "Not found"}), 404

DATA_FILE = "leads.json"

def load_leads():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_leads(leads):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)

def is_duplicate(new_lead, existing_leads):
    for lead in existing_leads:
        if lead.get("email") and lead["email"].lower() == new_lead.get("email", "").lower():
            return True
        if lead.get("linkedin_url") and lead["linkedin_url"] == new_lead.get("linkedin_url"):
            return True
    return False

@app.route("/")
def index():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_app_dir = os.path.join(base_dir, "..", "web-app")
    return send_file(os.path.join(web_app_dir, "index.html"))

@app.route("/api/leads", methods=["GET"])
def get_leads():
    leads = load_leads()
    return jsonify({"leads": leads, "total": len(leads)})

@app.route("/api/leads", methods=["POST"])
def add_leads():
    data = request.json
    new_leads = data if isinstance(data, list) else [data]
    existing = load_leads()

    added, dupes = [], []
    for lead in new_leads:
        lead["created_at"] = datetime.now().isoformat()
        
        # Check for duplicates and update if necessary
        is_dupe = False
        for i, existing_lead in enumerate(existing):
            match_email = existing_lead.get("email") and lead.get("email") and existing_lead["email"].lower() == lead["email"].lower()
            match_url = existing_lead.get("linkedin_url") and lead.get("linkedin_url") and existing_lead["linkedin_url"] == lead["linkedin_url"]
            
            if match_email or match_url:
                is_dupe = True
                # Merge new data into existing lead
                for k, v in lead.items():
                    if v and v != "Chưa có":
                        existing[i][k] = v
                dupes.append(existing[i])
                break
                
        if is_dupe:
            pass # Already merged into existing
        else:
            lead["status"] = "new"
            existing.append(lead)
            added.append(lead)

    save_leads(existing)
    return jsonify({"added": len(added), "duplicates": len(dupes), "leads": added})

@app.route("/api/leads/<int:idx>", methods=["DELETE"])
def delete_lead(idx):
    leads = load_leads()
    if idx < 0 or idx >= len(leads):
        return jsonify({"error": "Not found"}), 404
    leads.pop(idx)
    save_leads(leads)
    return jsonify({"ok": True})

@app.route("/api/leads/bulk-delete", methods=["POST"])
def bulk_delete_leads():
    data = request.json
    indices = set(data.get("indices", []))
    leads = load_leads()
    leads = [lead for i, lead in enumerate(leads) if i not in indices]
    save_leads(leads)
    return jsonify({"ok": True, "deleted": len(indices)})

@app.route("/api/leads/clear", methods=["POST"])
def clear_leads():
    save_leads([])
    return jsonify({"ok": True})

@app.route("/api/export/csv", methods=["GET"])
def export_csv():
    leads = load_leads()
    if not leads:
        return jsonify({"error": "No leads"}), 400
    output = io.StringIO()
    fields = ["name", "title", "company", "email", "phone", "location", "linkedin_url", "status", "created_at"]
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(leads)
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

@app.route("/api/stats", methods=["GET"])
def stats():
    leads = load_leads()
    total = len(leads)
    verified = sum(1 for l in leads if l.get("status") == "verified")
    dupes = sum(1 for l in leads if l.get("status") == "duplicate")
    new = sum(1 for l in leads if l.get("status") == "new")
    return jsonify({"total": total, "verified": verified, "duplicates": dupes, "new": new})

@app.route("/api/leads/<int:idx>/verify", methods=["POST"])
def verify_lead(idx):
    leads = load_leads()
    if idx < 0 or idx >= len(leads):
        return jsonify({"error": "Not found"}), 404
    leads[idx]["status"] = "verified"
    save_leads(leads)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
