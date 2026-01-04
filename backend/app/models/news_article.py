from datetime import datetime
from app.database import db

class NewsArticle(db.Model):
    __tablename__ = "news_articles"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.Text, nullable=False)
    source = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, unique=True, nullable=False)

    published_at = db.Column(db.DateTime, nullable=True)

    content = db.Column(db.Text, nullable=True)
    summary = db.Column(db.Text, nullable=True)
    topics = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "url": self.url,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "content": self.content,
            "summary": self.summary,
            "topics": self.topics,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
