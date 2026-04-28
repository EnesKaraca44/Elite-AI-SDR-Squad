from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
import json
import io
import csv
import threading
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.outreach_agent import OutreachAgent
from agents.contact_agent import ContactAgent
from models import db, Operation
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'elite_super_secret_key_123')
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///elite_saas_v2.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'

from models import User, SystemSettings

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

def process_bulk_jobs(app_instance, rows, user_id):
    with app_instance.app_context():
        import time
        for row in rows:
            vals = list(row.values())
            company_name = row.get('company_name') or (vals[0] if len(vals) > 0 else None)
            company_url = row.get('company_url') or (vals[1] if len(vals) > 1 else None)
            
            if not company_name or not company_url:
                continue

            try:
                research_agent = ResearchAgent()
                research_data = research_agent.execute(company_name, company_url)
                time.sleep(2)
                
                analysis_agent = AnalysisAgent()
                analysis_data = analysis_agent.analyze(research_data)
                time.sleep(2)
                
                contact_agent = ContactAgent()
                contacts_data = contact_agent.find_contacts(company_name, company_url)
                
                outreach_agent = OutreachAgent()
                outreach_data = outreach_agent.generate(analysis_data, contacts_data)
                outreach_data['contacts'] = contacts_data
                
                operation = Operation(
                    user_id=user_id,
                    company_name=company_name,
                    company_url=company_url,
                    research_results=json.dumps(research_data),
                    analysis_results=json.dumps(analysis_data),
                    outreach_results=json.dumps(outreach_data)
                )
                db.session.add(operation)
                db.session.commit()
                
                settings = SystemSettings.query.filter_by(user_id=user_id).first()
                if settings and settings.webhook_url:
                    import requests
                    try:
                        requests.post(settings.webhook_url, json=operation.to_dict(), timeout=5)
                    except Exception as e:
                        print(f"Bulk webhook error for {company_name}: {e}")
            except Exception as e:
                print(f"Bulk processing error for {company_name}: {e}")

@app.route('/')
def index():
    """Serve the Elite Dashboard UI."""
    return render_template('index.html')

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"error": "User already exists"}), 400
    user = User(username=data.get('username'))
    user.set_password(data.get('password'))
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return jsonify({"status": "success"})

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password')):
        login_user(user)
        return jsonify({"status": "success"})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/auth/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/api/settings', methods=['GET'])
@login_required
def get_settings():
    settings = SystemSettings.query.filter_by(user_id=current_user.id).first()
    if not settings:
        return jsonify({})
    return jsonify({
        "openai_api_key": settings.openai_api_key or "",
        "smtp_server": settings.smtp_server or "",
        "smtp_port": settings.smtp_port or "",
        "smtp_user": settings.smtp_user or "",
        "smtp_pass": settings.smtp_pass or "",
        "webhook_url": settings.webhook_url or ""
    })

@app.route('/api/settings', methods=['POST'])
@login_required
def update_settings():
    data = request.json
    settings = SystemSettings.query.filter_by(user_id=current_user.id).first()
    if not settings:
        settings = SystemSettings(user_id=current_user.id)
        db.session.add(settings)
    
    settings.openai_api_key = data.get('openai_api_key', settings.openai_api_key)
    settings.smtp_server = data.get('smtp_server', settings.smtp_server)
    if data.get('smtp_port'):
        settings.smtp_port = int(data.get('smtp_port'))
    settings.smtp_user = data.get('smtp_user', settings.smtp_user)
    settings.smtp_pass = data.get('smtp_pass', settings.smtp_pass)
    settings.webhook_url = data.get('webhook_url', settings.webhook_url)
    
    db.session.commit()
    return jsonify({"status": "success"})

@app.route('/api/analyze', methods=['POST'])
@login_required
def analyze():
    """Trigger the Multi-Agent Squad with Real-time Streaming and DB Persistence."""
    data = request.json
    company_name = data.get('company_name')
    company_url = data.get('company_url')
    
    current_uid = current_user.id

    if not company_name or not company_url:
        return jsonify({"error": "Missing company_name or company_url"}), 400

    def generate():
        with app.app_context():
            try:
                yield f"data: {json.dumps({'log': 'Initializing Elite AI Multi-Agent Squad...'})}\n\n"
                
                import time
                # 1. Research phase
                yield f"data: {json.dumps({'log': 'ResearchAgent: Scanning global indices and 24h news...'})}\n\n"
                research_agent = ResearchAgent()
                research_data = research_agent.execute(company_name, company_url)
                time.sleep(2) # Prevent 429 Rate Limit
                
                # 2. Analysis phase
                yield f"data: {json.dumps({'log': 'AnalysisAgent: Quantifying strategic ROI vectors...'})}\n\n"
                analysis_agent = AnalysisAgent()
                analysis_data = analysis_agent.analyze(research_data)
                time.sleep(2) # Prevent 429 Rate Limit
                
                # Contact phase
                yield f"data: {json.dumps({'log': 'ContactAgent: Finding Decision Maker profiles...'})}\n\n"
                contact_agent = ContactAgent()
                contacts_data = contact_agent.find_contacts(company_name, company_url)

                # 3. Outreach phase
                yield f"data: {json.dumps({'log': 'OutreachAgent: Synthesizing un-ignorable copy...'})}\n\n"
                outreach_agent = OutreachAgent()
                outreach_data = outreach_agent.generate(analysis_data, contacts_data)
                outreach_data['contacts'] = contacts_data
                
                # Save to Database
                operation = Operation(
                    user_id=current_uid,
                    company_name=company_name,
                    company_url=company_url,
                    research_results=json.dumps(research_data),
                    analysis_results=json.dumps(analysis_data),
                    outreach_results=json.dumps(outreach_data)
                )
                db.session.add(operation)
                db.session.commit()

                settings = SystemSettings.query.filter_by(user_id=current_uid).first()
                if settings and settings.webhook_url:
                    import requests
                    try:
                        requests.post(settings.webhook_url, json=operation.to_dict(), timeout=3)
                    except Exception as e:
                        print(f"Webhook error: {e}")

                yield f"data: {json.dumps({'status': 'success', 'data': operation.to_dict()})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return app.response_class(generate(), mimetype='text/event-stream')

@app.route('/api/bulk_analyze', methods=['POST'])
@login_required
def bulk_analyze():
    """Trigger bulk agent processing from a CSV file."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
        
    if file and file.filename.endswith('.csv'):
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        rows = list(csv_input)
        
        if not rows:
            return jsonify({"error": "CSV file is empty"}), 400
            
        thread = threading.Thread(target=process_bulk_jobs, args=(app, rows, current_user.id))
        thread.start()
        
        return jsonify({"status": "queued", "count": len(rows), "message": "Background squad deployed."})
    
    return jsonify({"error": "Invalid format. Valid: .csv"}), 400

@app.route('/api/webhook/<int:op_id>', methods=['POST'])
@login_required
def trigger_webhook(op_id):
    """Manually push intelligence data to the configured Webhook/CRM."""
    op = Operation.query.get_or_404(op_id)
    settings = SystemSettings.query.filter_by(user_id=current_user.id).first()
    if not settings or not settings.webhook_url:
        return jsonify({"error": "No Webhook URL configured in Settings."}), 400
        
    import requests
    try:
        response = requests.post(settings.webhook_url, json=op.to_dict(), timeout=10)
        return jsonify({"status": "success", "message": f"Data sent to CRM. Status: {response.status_code}"})
    except Exception as e:
        return jsonify({"error": f"Webhook Failed: {str(e)}"}), 500

@app.route('/api/send_email/<int:op_id>', methods=['POST'])
@login_required
def send_email(op_id):
    """Sends the edited cold email via SMTP (or simulates if no SMTP config)."""
    data = request.json
    target_email = data.get('target_email')
    email_body = data.get('email_body')
    
    if not target_email or not email_body:
        return jsonify({"error": "Missing email or body parameters."}), 400
        
    op = Operation.query.get_or_404(op_id)
    outreach = json.loads(op.outreach_results) if op.outreach_results else {}
    
    # Simple check for duplicates
    if outreach.get('email_status') == 'Sent':
        return jsonify({"error": "Email already dispatched for this module."}), 400
    
    settings = SystemSettings.query.filter_by(user_id=current_user.id).first()
    
    smtp_server = (settings and settings.smtp_server) or os.getenv('SMTP_SERVER')
    smtp_port = (settings and settings.smtp_port) or os.getenv('SMTP_PORT', 587)
    smtp_user = (settings and settings.smtp_user) or os.getenv('SMTP_USER')
    smtp_pass = (settings and settings.smtp_pass) or os.getenv('SMTP_PASS')
    
    if not smtp_server or not smtp_user:
        # Simulate Email Send for Demo Operations (Mock)
        outreach['email_status'] = 'Sent'
        op.outreach_results = json.dumps(outreach)
        db.session.commit()
        return jsonify({"status": "success", "message": f"SIMULATED: Email dispatched to {target_email}. Add SMTP config in .env for real sending."})
        
    import smtplib
    from email.message import EmailMessage
    
    msg = EmailMessage()
    msg['Subject'] = f"Strategic Collaboration Request - {op.company_name}"
    msg['From'] = smtp_user
    msg['To'] = target_email
    msg.set_content(email_body)
    
    try:
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            
        outreach['email_status'] = 'Sent'
        op.outreach_results = json.dumps(outreach)
        db.session.commit()
        return jsonify({"status": "success", "message": f"Email successfully sent to {target_email} via strict SMTP protocol."})
    except Exception as e:
        return jsonify({"error": f"SMTP Error: {str(e)}"}), 500

@app.route('/api/operations', methods=['GET'])
@login_required
def get_operations():
    """Retrieve history of operations."""
    ops = Operation.query.filter_by(user_id=current_user.id).order_by(Operation.timestamp.desc()).all()
    return jsonify([op.to_dict() for op in ops])

@app.route('/api/export/<int:op_id>', methods=['GET'])
def export_pdf(op_id):
    """Generate a professional PDF report for an operation."""
    op = Operation.query.get_or_404(op_id)
    op_data = op.to_dict()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], textColor=colors.hexColor("#00f2ea"), spaceAfter=12)
    sub_title_style = ParagraphStyle('SubTitleStyle', parent=styles['Heading2'], spaceAfter=10)
    body_style = styles['BodyText']

    elements = []
    
    # Content
    elements.append(Paragraph(f"Elite Intelligence Report: {op_data['company_name']}", title_style))
    elements.append(Paragraph(f"Source: {op_data['company_url']}", body_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Market Position", sub_title_style))
    elements.append(Paragraph(op_data['analysis'].get('market_position', 'N/A'), body_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Strategic Gaps", sub_title_style))
    for gap in op_data['analysis'].get('strategic_gaps', []):
        elements.append(Paragraph(f"• {gap}", body_style))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Outreach Draft", sub_title_style))
    # Basic sanitization for PDF characters
    draft = op_data['outreach'].get('outreach_drafts', 'N/A').replace('\n', '<br/>')
    elements.append(Paragraph(draft, body_style))

    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Elite_Report_{op_data['company_name']}.pdf",
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    # Use a port that is usually open (e.g., 5000 or 8080)
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
