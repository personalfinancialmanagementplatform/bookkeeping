"""
Category 模型 - 分類
對應資料庫的 categories 表
"""

from app.database import db
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

class Category(db.Model):
    __tablename__ = 'categories'
    
    # 主鍵
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # 基本資訊
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # income, expense
    
    # 階層結構（可選）
    parent_id: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # 視覺化
    color: Mapped[str] = mapped_column(String(7), nullable=True)  # HEX color
    icon: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # 選填資訊
    description: Mapped[str] = mapped_column(String, nullable=True)
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
            'name': self.name,
            'type': self.type,
            'parent_id': self.parent_id,
            'color': self.color,
            'icon': self.icon,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Category {self.name} ({self.type})>'