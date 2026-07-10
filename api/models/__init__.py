# Importing all models here registers them on Base.metadata so that
# Base.metadata.create_all() creates every table — omitting any model here
# will silently skip its table.
from api.models.article import Article
from api.models.interaction import Interaction
from api.models.source import Source
from api.models.story import Story, story_articles
from api.models.summary import Summary
from api.models.user import User

__all__ = ["User", "Source", "Article", "Story", "story_articles", "Summary", "Interaction"]
