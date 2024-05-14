import scrapy

from pokedex_spider.items import PokedexItem
from pokedex_spider.utils.effect_text import get_effect_text


class PokedexItemSpider(scrapy.Spider):
    name = "item"
    allowed_domains = ["wiki.52poke.com"]
    start_urls = ["https://wiki.52poke.com/wiki/%E9%81%93%E5%85%B7%E5%88%97%E8%A1%A8"]

    custom_settings = {
        # 按照顺序爬取
        "CONCURRENT_REQUESTS": 1,
    }

    def parse(self, response):
        item_list = response.xpath("//table[contains(@class,'hvlist')]/tbody/tr[position() > 1]")

        # 生成器，顺序执行
        gen_priority = get_generator(len(item_list))
        prev_description = ""

        for item_line in item_list:
            item = PokedexItem()
            item["item_cn_name"] = item_line.xpath("./td[2]/a/text()").get().strip()
            item["item_jp_name"] = item_line.xpath("./td[3]/text()").get().strip()
            item["item_en_name"] = item_line.xpath("./td[4]/text()").get().strip()

            description_tag = item_line.xpath("./td[5]/text()")
            if description_tag:
                prev_description = description = description_tag.get().strip()
                item["item_description"] = description
            else:
                item["item_description"] = prev_description

            detail_url = item_line.xpath("./td[2]/a/@href").get()

            # dont_filter即使已经爬取过，也会再次爬取
            yield response.follow(url=detail_url, callback=self.__parse_detail, priority=next(gen_priority),
                                  dont_filter=True, meta={'item': item})

    def __parse_detail(self, response):
        item: PokedexItem = response.meta['item']

        response.xpath("//*[@id='特性']/../following-sibling::*")

        effect_tags = response.xpath("//*[@id='效果']/../following-sibling::*")
        if not effect_tags:
            effect_tags = response.xpath("//*[@id='使用效果']/../following-sibling::h2")
        effect_text = get_effect_text(effect_tags)

        item['item_effect'] = effect_text

        item['item_change_log'] = ""

        change_log_tags = response.xpath("//*[@id='效果变更']/../following-sibling::*")
        if change_log_tags:
            item['item_change_log'] = get_effect_text(change_log_tags)

        response.xpath("//*[@id='获得方式']/../following-sibling::*")

        item['acquisition'] = ""

        yield item


def get_generator(start, end=0, step=-1):
    current = start
    while current >= end:
        yield current
        current += step
