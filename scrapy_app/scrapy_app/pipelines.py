# -*- coding: utf-8 -*-
from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem
from scrapy_app.models import Article, Issue, db_connect, create_table



class FullfillDataPipeline(object):

    def __init__(self):
        self.keys_to_check = ['article_authors', 'article_tags', 'section_name', 'article_content', 'article_intro', 'issue_cover_url']

    def process_item(self, item, spider):
        for key in self.keys_to_check:
            if key not in item.keys():
                item[key] = None
        return item

class ShortestPipeline(object):
    
    def process_item(self, item, spider):
        if item['article_content'] == None or len(item['article_content']) < 100:
            raise DropItem("Item shorter than 100: %s" % item)
        else:
            return item


class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['article_url'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['article_url'])
            return item

class Save2dbPipeline(object):

    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """Save articles and issues in the database
        This method is called for every item pipeline component
        """
        session = self.Session()
        issue = Issue()
        article = Article()
        
        # Issues data
        issue.name = item['issue_name']
        issue.number = item['issue_number']
        issue.cover_url = item['issue_cover_url']
        issue.issue_url = item['issue_url']
        exist_issue = session.query(Issue).filter_by(issue_url=issue.issue_url).first()
        if exist_issue:
            article.issue_id = exist_issue.id
        else:
            session.add(issue)
            session.commit()
            new_issue = session.query(Issue).filter_by(issue_url=issue.issue_url).first()
            article.issue_id = new_issue.id
        # Articles data
        article.section_name = item['section_name']
        article.title = item['article_title']
        article.authors = item['article_authors']
        try:
            article.intro = item['article_intro']
        except:
            article.intro = None
        article.content = item['article_content']
        article.tags = item['article_tags']
        article.url = item['article_url']
        
        try:
            session.add(article)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return item