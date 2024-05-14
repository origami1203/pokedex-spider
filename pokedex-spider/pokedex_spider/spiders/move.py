import scrapy

from pokedex_spider.items import MoveItem
from pokedex_spider.utils.effect_text import get_effect_text


class MoveSpider(scrapy.Spider):
    name = "move"
    allowed_domains = ["wiki.52poke.com"]
    start_urls = ["https://wiki.52poke.com/wiki/%E6%8B%9B%E5%BC%8F%E5%88%97%E8%A1%A8"]  # 招式列表

    custom_settings = {
        "ITEM_PIPELINES": {
            "pokedex_spider.pipelines.PokedexMovePipeline": 300,
        }
    }

    def parse(self, response):
        move_list = response.xpath("//table[contains(@class,'hvlist')]/tbody/tr[@data-type]")

        for move_line in move_list:
            move = MoveItem()
            move["move_no"] = move_line.xpath("./td[1]//text()").get().strip()
            move['move_cn_name'] = move_line.xpath("./td[2]//text()").get().strip()
            move['move_jp_name'] = move_line.xpath("./td[3]//text()").get().strip()
            move['move_en_name'] = move_line.xpath("./td[4]//text()").get().strip()
            move['move_type'] = move_line.xpath("./td[5]//text()").get().strip()
            move['move_category'] = move_line.xpath("./td[6]//text()").get().strip()
            move['move_power'] = move_line.xpath("./td[7]//text()").get().strip()
            move['move_accuracy'] = move_line.xpath("./td[8]//text()").get().strip()
            move['move_pp'] = move_line.xpath("./td[9]//text()").get().strip()
            move['move_description'] = move_line.xpath("./td[10]//text()").get().strip()

            detail_url = move_line.xpath("./td[2]/a/@href").get()

            yield response.follow(url=detail_url, callback=self._parse_detail, meta={'move': move})

    def _parse_detail(self, response):
        move: MoveItem = response.meta['move']

        priority_tag = response.xpath("//a[@title='优先度']/../parent::tr[not(contains(@class, 'hide'))]")
        if priority_tag:
            move['move_priority'] = priority_tag.xpath("./td[@class='at-l']/text()").get().strip()
        else:
            move['move_priority'] = '0'

        all_sibling_tags = response.xpath("//*[@id='招式附加效果']/../following-sibling::*")
        effect_text = get_effect_text(all_sibling_tags)

        move['move_effect'] = effect_text

        yield move
