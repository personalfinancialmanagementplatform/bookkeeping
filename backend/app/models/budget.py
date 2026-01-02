"""
Budget 模型 - 預算
對應資料庫的 budgets 表
"""

from app.database import db
from datetime import datetime, date
from sqlalchemy import String, Numeric, Boolean, DateTime, Date, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

class Budget(db.Model):
    __tablename__ = 'budgets'
    
    # 主鍵
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # 外鍵關聯
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), nullable=False)
    
    # 基本資訊
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    period: Mapped[str] = mapped_column(String(50), nullable=False)  # daily, weekly, monthly, yearly
    
    # 日期範圍
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=True)
    
    # 狀態
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 時間戳記
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """
        將模型轉換成字典格式
        """
        return {
            'id': self.id,
            'category_id': self.category_id,
            'name': self.name,
            'amount': float(self.amount),
            'period': self.period,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Budget {self.name}: ${self.amount}/{self.period}>'