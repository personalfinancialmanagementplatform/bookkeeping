"""
FinancialGoal 模型 - 財務目標
對應資料庫的 financial_goals 表
"""

from app.database import db
from datetime import datetime, date
from sqlalchemy import String, Numeric, DateTime, Date, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

class FinancialGoal(db.Model):
    __tablename__ = 'financial_goals'
    
    # 主鍵
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # 基本資訊
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    current_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.00)
    
    # 目標設定
    deadline: Mapped[date] = mapped_column(Date, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=1)  # 1-5
    status: Mapped[str] = mapped_column(String(50), default='in_progress')  # in_progress, completed, cancelled
    
    # 選填資訊
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    # 時間戳記
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """
        將模型轉換成字典格式
        """
        return {
            'id': self.id,
            'name': self.name,
            'target_amount': float(self.target_amount),
            'current_amount': float(self.current_amount),
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'priority': self.priority,
            'status': self.status,
            'description': self.description,
            'progress': self.get_progress(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_progress(self):
        """
        計算目標達成進度（百分比）
        """
        if self.target_amount == 0:
            return 0
        return round((float(self.current_amount) / float(self.target_amount)) * 100, 2)
    
    def __repr__(self):
        return f'<FinancialGoal {self.name}: {self.get_progress()}%>'