from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from flask import Blueprint, request, jsonify, current_app

from app.database import db
print("news_routes db id =", id(db))
from app.models.news_article import NewsArticle
from app.services.news_ingest_service import NewsIngestService
from app.services.news_summarize_service import NewsSummarizeService

news_bp = Blueprint("news", __name__, url_prefix="/api/news")

@news_bp.route("/ingest", methods=["POST"])
def ingest_news():
    data = request.get_json(silent=True) or {}
   # ① 前端傳的 rss_urls（可選）
    rss_urls = data.get("rss_urls")

    # ② 如果前端沒傳，用 run.py 的預設 RSS
    if not rss_urls:
        rss_urls = current_app.config.get("RSS_URLS", [])

    # ③ 兩邊都沒有才算錯
    if not rss_urls:
        return jsonify({
            "error": "No RSS_URLS provided",
            "hint": "Provide rss_urls in request body or set RSS_URLS in run.py"
        }), 400

    items = NewsIngestService.fetch_from_rss(rss_urls)
    stats = NewsIngestService.upsert_articles(items)

    return jsonify({
        "rss_count": len(rss_urls),
        "fetched": len(items),
        **stats
    })

@news_bp.route("/today", methods=["GET"])
def get_today_or_latest_news():
    limit = int(request.args.get("limit", 20))

    today = datetime.utcnow().date()

    items = (
        NewsArticle.query
        .filter(NewsArticle.published_at.isnot(None))
        .filter(db.func.date(NewsArticle.published_at) == today)
        .order_by(NewsArticle.published_at.desc())
        .limit(limit)
        .all()
    )

    if not items:
        # fallback：最新新聞
        items = (
            NewsArticle.query
            .filter(NewsArticle.published_at.isnot(None))
            .order_by(NewsArticle.published_at.desc())
            .limit(limit)
            .all()
        )

    return jsonify([a.to_dict() for a in items])

@news_bp.route("/query", methods=["GET"])
def query_news():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "q is required"}), 400

    limit = int(request.args.get("limit", 20))

    # 先用很簡單的 LIKE（保底可跑），之後再改成 SearchService.search_news
    items = (NewsArticle.query
             .filter(NewsArticle.title.ilike(f"%{q}%") | NewsArticle.content.ilike(f"%{q}%"))
             .order_by(NewsArticle.published_at.desc().nullslast())
             .limit(limit)
             .all())
    return jsonify([a.to_dict() for a in items])

@news_bp.route("/<int:article_id>/summarize", methods=["POST"])
def summarize_one(article_id: int):
    a = NewsArticle.query.get_or_404(article_id)
    a.summary = NewsSummarizeService.summarize(a.title, a.content or "")
    db.session.commit()
    return jsonify(a.to_dict())

@news_bp.route("/summarize_missing", methods=["POST"])
def summarize_missing():
    limit = int((request.get_json(silent=True) or {}).get("limit", 20))

    items = (NewsArticle.query
             .filter(NewsArticle.summary.is_(None))
             .order_by(NewsArticle.published_at.desc().nullslast())
             .limit(limit)
             .all())

    for a in items:
        a.summary = NewsSummarizeService.summarize(a.title, a.content or "")

    db.session.commit()
    return jsonify({"summarized": len(items)})
