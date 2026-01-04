from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app

from app.services.news_ingest_service import NewsIngestService
from app.services.news_summarize_service import NewsSummarizeService
from app.models.news_article import NewsArticle
from app.database import db

def init_scheduler(app, rss_urls):
    """
    在 app 啟動後呼叫：
      init_scheduler(app, rss_urls=[...])
    """
    scheduler = BackgroundScheduler(timezone="Asia/Taipei")

    def job_ingest_and_summarize():
        with app.app_context():
            items = NewsIngestService.fetch_from_rss(rss_urls)
            stats = NewsIngestService.upsert_articles(items)

            # 補摘要（只補新增或缺摘要的前 20）
            targets = (NewsArticle.query
                       .filter(NewsArticle.summary.is_(None))
                       .order_by(NewsArticle.published_at.desc().nullslast())
                       .limit(20)
                       .all())
            for a in targets:
                a.summary = NewsSummarizeService.summarize(a.title, a.content or "")
            db.session.commit()

            current_app.logger.info(f"[scheduler] ingest stats={stats}, summarized={len(targets)}")

    # 每天 07:30 跑一次（你可改）
    scheduler.add_job(job_ingest_and_summarize, "cron", hour=7, minute=30)
    scheduler.start()
    return scheduler
