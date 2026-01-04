from sqlalchemy import text
from app.database import db

class SearchService:
    @staticmethod
    def search_knowledge(q: str, limit: int = 5):
        sql = text("""
            SELECT id, title, content, source, tags,
                   ts_rank_cd(
                     to_tsvector('simple', coalesce(title,'') || ' ' || coalesce(content,'')),
                     plainto_tsquery('simple', :q)
                   ) AS rank
            FROM knowledge_docs
            WHERE to_tsvector('simple', coalesce(title,'') || ' ' || coalesce(content,''))
                  @@ plainto_tsquery('simple', :q)
            ORDER BY rank DESC
            LIMIT :limit
        """)
        rows = db.session.execute(sql, {"q": q, "limit": limit}).mappings().all()
        return list(rows)

    @staticmethod
    def search_news(q: str, limit: int = 20):
        sql = text("""
            SELECT id, title, source, url, published_at, summary, content,
                   ts_rank_cd(
                     to_tsvector('simple', coalesce(title,'') || ' ' || coalesce(content,'') || ' ' || coalesce(summary,'')),
                     plainto_tsquery('simple', :q)
                   ) AS rank
            FROM news_articles
            WHERE to_tsvector('simple', coalesce(title,'') || ' ' || coalesce(content,'') || ' ' || coalesce(summary,''))
                  @@ plainto_tsquery('simple', :q)
            ORDER BY rank DESC
            LIMIT :limit
        """)
        rows = db.session.execute(sql, {"q": q, "limit": limit}).mappings().all()
        return list(rows)
