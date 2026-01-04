from typing import Dict, List
from app.services.search_service import SearchService
from app.utils.text_cleaner import truncate, normalize_whitespace

TEMPLATES = {
    "ETF": {
        "explain": "ETF 可以想成「把一籃子股票/債券打包成一個商品」；你買 1 份 ETF，就等於用較低門檻分散投資。",
        "example": "例子：你每月拿 1000 元定期定額買追蹤大盤的 ETF，就像每月固定把錢分散買進很多家公司，而不是押單一股票。"
    },
    "定期定額": {
        "explain": "定期定額是「固定時間、固定金額」買同一個投資標的，用來降低一次買在高點的風險。",
        "example": "例子：每月 10 號投入 2000 元，不管漲跌都買，長期平均成本更平滑。"
    },
    "複利": {
        "explain": "複利是「利息再生利息」：你賺到的報酬不拿走，繼續投入，時間越久成長越快。",
        "example": "例子：如果每年 6% 報酬，10 萬放 1 年變 10.6 萬；下一年是用 10.6 萬再去長大。"
    }
}

class KnowledgeService:
    @staticmethod
    def query(q: str, top_k: int = 5) -> Dict:
        qn = normalize_whitespace(q)
        hits = SearchService.search_knowledge(qn, limit=top_k)

        # 找模板關鍵字（非常 MVP，但 demo 好用）
        chosen = None
        for key in TEMPLATES.keys():
            if key.lower() in qn.lower() or key in qn:
                chosen = key
                break

        if chosen:
            answer = TEMPLATES[chosen]["explain"]
            example = TEMPLATES[chosen]["example"]
        else:
            # 沒命中模板：用搜尋結果的內容拼「摘要式回答」
            if hits:
                snippet = truncate(hits[0]["content"], 220)
                answer = f"根據知識庫內容整理：{snippet}"
                example = "你可以告訴我你是學生、每月可投入金額、以及想投資多久，我可以用簡單例子幫你把概念套進生活情境。"
            else:
                answer = "我目前在知識庫中找不到直接對應的內容。你可以換個說法或補充關鍵字（例如 ETF、定期定額、複利、風險）。"
                example = ""

        sources: List[Dict] = []
        for h in hits:
            sources.append({
                "id": h["id"],
                "title": h["title"],
                "source": h.get("source"),
                "tags": h.get("tags"),
            })

        return {
            "query": qn,
            "answer": answer,
            "example": example,
            "sources": sources
        }
