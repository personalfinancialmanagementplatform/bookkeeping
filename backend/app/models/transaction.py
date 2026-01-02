"""
Transaction 模型 - 交易記錄
對應資料庫的 transactions 表
"""
from app.database import db
from datetime import datetime, date as date_type

from sqlalchemy import String, Numeric, DateTime, Date, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    # 主鍵
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # 外鍵關聯
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey('accounts.id'), nullable=False)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), nullable=True)
    
    # 基本資訊
    date: Mapped[date_type] = mapped_column(Date, nullable=False, default=datetime.utcnow)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # income, expense
    
    # 選填資訊
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    # 時間戳記
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """
        將模型轉換成字典格式
        """
        return {
            'id': self.id,
            'account_id': self.account_id,
            'category_id': self.category_id,
            'date': self.date.isoformat() if self.date else None,
            'description': self.description,
            'amount': float(self.amount),
            'type': self.type,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Transaction {self.description}: ${self.amount} ({self.type})>'