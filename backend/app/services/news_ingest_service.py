from datetime import datetime
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
    def fetch_from_rss(rss_urls: List[str]) -> List[Dict]:
        articles = []
        for url in rss_urls:
            feed = feedparser.parse(url)
            for e in feed.entries:
                title = normalize_whitespace(getattr(e, "title", "") or "")
                link = normalize_whitespace(getattr(e, "link", "") or "")
                published = getattr(e, "published", None) or getattr(e, "updated", None)

                published_at: Optional[datetime] = None
                if published:
                    try:
                        published_at = date_parser.parse(published)
                    except Exception:
                        published_at = None

                # RSS 通常只有摘要，當 content 用（MVP 夠）
                summary = normalize_whitespace(getattr(e, "summary", "") or "")
                content = summary

                source = None
                if hasattr(feed, "feed") and hasattr(feed.feed, "title"):
                    source = normalize_whitespace(feed.feed.title or "")

                if not title or not link:
                    continue

                articles.append({
                    "title": title,
                    "url": link,
                    "source": source,
                    "published_at": published_at,
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
