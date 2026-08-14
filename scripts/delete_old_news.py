import logging
from datetime import datetime, timedelta
from api.database import SessionLocal
from api.models.article import Article
from api.models.story import Story, story_articles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    db = SessionLocal()
    cutoff_date = datetime.now() - timedelta(days=7)
    
    try:
        # Find IDs of old articles (server-side subquery)
        old_article_ids_query = db.query(Article.id).filter(Article.published_at < cutoff_date)
        
        # 1. Delete links in story_articles for these articles
        db.execute(story_articles.delete().where(story_articles.c.article_id.in_(old_article_ids_query)))
        
        # 2. Delete the articles
        deleted_articles_count = db.query(Article).filter(Article.published_at < cutoff_date).delete(synchronize_session=False)
        logger.info(f"Deleted {deleted_articles_count} articles published before {cutoff_date.date()}")
            
        # Find IDs of old stories (server-side subquery)
        old_story_ids_query = db.query(Story.id).filter(Story.created_at < cutoff_date)
        
        # 1. Delete links in story_articles for these stories
        db.execute(story_articles.delete().where(story_articles.c.story_id.in_(old_story_ids_query)))
        
        # 2. Delete the stories
        deleted_stories_count = db.query(Story).filter(Story.created_at < cutoff_date).delete(synchronize_session=False)
        logger.info(f"Deleted {deleted_stories_count} stories created before {cutoff_date.date()}")

        db.commit()
        logger.info("Cleanup successful.")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error during cleanup: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
