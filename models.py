# --- models.py ---
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 初始化 SQLAlchemy（请确保在 app.py 中调用 db.init_app(app)）
db = SQLAlchemy()

class VisaApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    passport_number = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50))
    photo_filename = db.Column(db.String(200))
    document_filename = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')  # pending / approved / rejected
    rejection_reason = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<VisaApplication {self.passport_number}>"