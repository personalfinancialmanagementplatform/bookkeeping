"""
Account 模型 - 帳戶
對應資料庫的 accounts 表
"""

from app.database import db
from datetime import datetime
from sqlalchemy import String, Numeric, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

class Account(db.Model):
    __tablename__ = 'accounts'
    
    # 主鍵
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # 基本資訊
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # checking, savings, cash, credit_card
    balance: Mapped[float] = mapped_column(Numeric(15, 2), default=0.00)
    currency: Mapped[str] = mapped_column(String(3), default='TWD')
    
    # 選填資訊
    description: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 時間戳記
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """
        將模型轉換成字典格式，方便 API 回傳 JSON
        """
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'balance': float(self.balance),
            'currency': self.currency,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """
        方便在 debug 時看到帳戶資訊
        """
        return f'<Account {self.name} ({self.type}): ${self.balance}>'