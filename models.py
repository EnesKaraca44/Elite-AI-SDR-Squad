from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(250), nullable=False)
    operations = db.relationship('Operation', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Operation(db.Model):
    """Stores the results of an Elite AI Squad mission."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # True for now to handle legacy
    company_name = db.Column(db.String(200), nullable=False)
    company_url = db.Column(db.String(500), nullable=False)
    research_results = db.Column(db.Text, nullable=True)  # JSON string
    analysis_results = db.Column(db.Text, nullable=True)  # JSON string
    outreach_results = db.Column(db.Text, nullable=True)  # JSON string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "company_name": self.company_name,
            "company_url": self.company_url,
            "research": json.loads(self.research_results) if self.research_results else {},
            "analysis": json.loads(self.analysis_results) if self.analysis_results else {},
            "outreach": json.loads(self.outreach_results) if self.outreach_results else {},
            "timestamp": self.timestamp.isoformat()
        }

class SystemSettings(db.Model):
    """Stores user specific API keys, SMTP and Webhook settings."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    openai_api_key = db.Column(db.String(250), nullable=True)
    smtp_server = db.Column(db.String(200), nullable=True)
    smtp_port = db.Column(db.Integer, nullable=True)
    smtp_user = db.Column(db.String(200), nullable=True)
    smtp_pass = db.Column(db.String(250), nullable=True)
    webhook_url = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref=db.backref('settings', uselist=False))
