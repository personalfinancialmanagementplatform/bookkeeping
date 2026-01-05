from datetime import datetime, timezone
from typing import List, Dict, Optional
import feedparser
from dateutil import parser as date_parser

from app.database import db
from app.models.news_article import NewsArticle
from app.utils.text_cleaner import normalize_whitespace

DEFAULT_RSS = [
    # 先放一個範例，你可自行改成你們要的財經 RSS
    # 例如：Reuters、CNBC、Yahoo Finance、或台灣媒體的 RSS（若有提供）
    # 注意：不同來源可能有使用條款，demo 先用公開 RSS。
]

class NewsIngestService:
    @staticmethod
    def _to_utc_aware(dt: Optional[datetime]) -> Optional[datetime]:
        """
        統一轉成「UTC aware datetime」：
        - aware datetime -> 轉成 UTC aware
        - naive datetime -> 視為 UTC，補上 tzinfo=UTC
        """
        if dt is None:
            return None

        if dt.tzinfo is None:
            # RSS 沒有時區資訊：先當作 UTC（MVP 最安全）
            return dt.replace(tzinfo=timezone.utc)

        # 有時區：轉 UTC
        return dt.astimezone(timezone.utc)
    
    @staticmethod
    def fetch_from_rss(rss_urls: List[str]) -> List[Dict]:
        articles: List[Dict] = []

        for url in rss_urls:
            feed = feedparser.parse(url)

            # source（RSS feed title）
            source = None
            if hasattr(feed, "feed") and hasattr(feed.feed, "title"):
                source = normalize_whitespace(feed.feed.title or "")

            if source and "：" in source:
                source = source.split("：", 1)[0].strip()

            for e in getattr(feed, "entries", []) or []:
                title = normalize_whitespace(getattr(e, "title", "") or "")
                link = normalize_whitespace(getattr(e, "link", "") or "")

                # 常見時間欄位：published / updated / pubDate
                published_raw = (
                    getattr(e, "published", None)
                    or getattr(e, "updated", None)
                    or getattr(e, "pubDate", None)
                )

                published_at: Optional[datetime] = None
                if published_raw:
                    try:
                        dt = date_parser.parse(published_raw)
                        published_at = NewsIngestService._to_utc_aware(dt)
                    except Exception:
                        published_at = None

                summary = normalize_whitespace(getattr(e, "summary", "") or "")
                content = summary  # MVP: RSS 摘要當 content

                if not title or not link:
                    continue

                articles.append({
                    "title": title,
                    "url": link,
                    "source": source,
                    "published_at": published_at,  # ✅ UTC aware
                    "content": content
                })

        return articles


    @staticmethod
    def upsert_articles(items: List[Dict]) -> Dict:
        inserted = 0
        skipped = 0

        for it in items:
            exists = NewsArticle.query.filter_by(url=it["url"]).first()
            if exists:
                skipped += 1
                continue

            a = NewsArticle(
                title=it["title"],
                url=it["url"],
                source=it.get("source"),
                published_at=it.get("published_at"),
                content=it.get("content"),
            )
            db.session.add(a)
            inserted += 1

        db.session.commit()
        return {"inserted": inserted, "skipped": skipped}
