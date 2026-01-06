"""
休市日 API 路由
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

holiday_bp = Blueprint('holiday', __name__)


@holiday_bp.route('/api/holidays', methods=['GET'])
def get_holidays():
    """取得休市日清單"""
    try:
        from app.services.holiday_service import holiday_service
        
        year = request.args.get('year', type=int)
        if not year:
            year = datetime.now().year
        
        holidays = holiday_service.get_holidays_list(year)
        
        return jsonify({
            'year': year,
            'holidays': holidays,
            'count': len(holidays)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@holiday_bp.route('/api/holidays/check', methods=['GET'])
def check_holiday():
    """檢查某日是否為休市日"""
    try:
        from app.services.holiday_service import holiday_service
        
        date = request.args.get('date')
        if not date:
            return jsonify({'error': '請提供日期參數'}), 400
        
        is_holiday = holiday_service.is_holiday(date)
        
        return jsonify({
            'date': date,
            'is_holiday': is_holiday
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@holiday_bp.route('/api/settlement-date', methods=['GET'])
def get_settlement_date():
    """計算交割日"""
    try:
        from app.services.holiday_service import holiday_service
        
        sell_date = request.args.get('sell_date')
        if not sell_date:
            # 預設今天
            sell_date = datetime.now().strftime('%Y-%m-%d')
        
        result = holiday_service.calculate_settlement_date(sell_date)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@holiday_bp.route('/api/holidays/refresh', methods=['POST'])
def refresh_holidays():
    """強制重新抓取休市日"""
    try:
        from app.services.holiday_service import holiday_service
        
        # 清除快取
        holiday_service._last_fetch = None
        holidays = holiday_service.get_holidays()
        
        return jsonify({
            'success': True,
            'count': len(holidays),
            'message': '休市日資料已更新'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500