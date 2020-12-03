# -*- coding: utf-8 -*-
from scrapy.item import Item, Field
from itemloaders.processors import MapCompose, TakeFirst, Join
from w3lib.html import remove_tags
import re

def remove_empty_lines(content):
    return '\n'.join([line.strip() for line in content.split('\n') if line.strip() != '' and line != '\n' and not line.strip().startswith('Fot.') and not line.strip().startswith('fot.') and not line.strip().startswith('FOT.')])

def remove_xml_tags(content):
    return '\n'.join([line for line in content.split('\n') if '/* Style Definitions */' not in line.strip()])


class WeekliesScraperItem(Item):
    issue_name = Field(
        input_processor = MapCompose(),
        output_processor = TakeFirst()
    )
    issue_number = Field(
        input_processor = MapCompose(str.strip),
        output_processor = TakeFirst()
    )
    issue_cover_url = Field(
        input_processor = MapCompose(),
        output_processor = TakeFirst()
    )
    issue_url = Field(
        input_processor = MapCompose(),
        output_processor = TakeFirst()
    )
    section_name = Field(
        input_processor = MapCompose(remove_tags, str.strip, str.lower), 
        output_processor = TakeFirst()
    )
    article_url = Field(
        input_processor = MapCompose(),
        output_processor = TakeFirst()
    )
    article_title = Field(
        input_processor = MapCompose(remove_tags, str.strip),
        output_processor = TakeFirst()
    )
    article_authors = Field(
        input_processor = MapCompose(remove_tags, str.strip),
        output_processor = Join(', ')
    )
    article_intro = Field(
        input_processor = MapCompose(remove_tags, str.strip, remove_empty_lines), 
        output_processor = Join()
    )
    article_content = Field(
        input_processor = MapCompose(remove_tags, str.strip, remove_empty_lines, remove_xml_tags),
        output_processor = Join('\n')
    )
    article_tags = Field(
        input_processor = MapCompose(str.strip, str.lower),
        output_processor = Join(', ')
    )