from app.utils.text_cleaner import normalize_whitespace, truncate

class NewsSummarizeService:
    @staticmethod
    def summarize(title: str, content: str) -> str:
        """
        MVP 規則摘要：三段
        1) 發生什麼（用 title + 前 1~2 句）
        2) 為什麼重要（用關鍵字提示）
        3) 跟學生/一般人有何關係（簡單落地）
        """
        title = normalize_whitespace(title)
        content = normalize_whitespace(content)

        # 取內容前 240 字當作「事件描述」
        lead = truncate(content, 240) if content else ""

        # 極簡關鍵字判斷（你之後可換成 LLM）
        importance = "這則消息可能影響市場情緒與相關產業股價波動。"
        if any(k in (title + " " + content) for k in ["利率", "Fed", "央行", "通膨"]):
            importance = "利率與通膨消息會影響貸款成本、房租壓力與投資報酬，市場通常反應明顯。"
        elif any(k in (title + " " + content) for k in ["半導體", "AI", "晶片", "台積電"]):
            importance = "科技與半導體供需會牽動相關公司營收預期，也常帶動大盤走勢。"
        elif any(k in (title + " " + content) for k in ["匯率", "美元", "日圓"]):
            importance = "匯率變動會影響出國成本、進口物價與企業獲利，對生活與投資都相關。"

        relate = "如果你有定期定額或正在存第一筆投資金，重點是看：這則新聞影響的是「利率／景氣／某個產業」哪一塊，再決定要不要調整投入節奏。"

        parts = [
            f"發生什麼：{title}" + (f"（內容摘要：{lead}）" if lead else ""),
            f"為什麼重要：{importance}",
            f"跟你有什麼關係：{relate}"
        ]
        return "\n".join(parts)
