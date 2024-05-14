import scrapy
from scrapy.http import Response

from pokedex_spider.items import AbilityItem
from pokedex_spider.utils.effect_text import get_effect_text


class AbilitySpider(scrapy.Spider):
    name = "ability"
    allowed_domains = ["wiki.52poke.com"]
    start_urls = ["https://wiki.52poke.com/wiki/%E7%89%B9%E6%80%A7%E5%88%97%E8%A1%A8"]

    custom_settings = {
        "ITEM_PIPELINES": {
            "pokedex_spider.pipelines.PokedexAbilityPipeline": 300,
        }
    }

    def parse(self, response: Response):
        ability_list = response.xpath("//table[contains(@class,'eplist')]/tbody/tr[position() > 1]")

        for ability_line in ability_list:
            ability = AbilityItem()
            ability["ability_no"] = ability_line.xpath("./td[1]/text()").get().strip()
            ability["ability_cn_name"] = ability_line.xpath("./td[2]/a/text()").get().strip()
            ability["ability_jp_name"] = ability_line.xpath("./td[3]/text()").get().strip()
            ability["ability_en_name"] = ability_line.xpath("./td[4]/text()").get().strip()
            ability["ability_description"] = ability_line.xpath("./td[5]/text()").get().strip()

            detail_url = ability_line.xpath("./td[2]/a/@href").get()
            yield response.follow(url=detail_url, callback=self._parse_detail, meta={'ability': ability})

    def _parse_detail(self, response: Response):
        ability: AbilityItem = response.meta['ability']

        effect_tags = response.xpath("//*[@id='特性效果']/../following-sibling::*")
        effect_text = get_effect_text(effect_tags)

        ability['ability_effect'] = effect_text

        ability['ability_change_log'] = ""

        change_log_tags = response.xpath("//*[@id='特性变更']/../following-sibling::*")
        if change_log_tags:
            ability['ability_change_log'] = get_effect_text(change_log_tags)

        yield ability
