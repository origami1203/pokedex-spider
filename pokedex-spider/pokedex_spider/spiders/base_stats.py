import scrapy

from pokedex_spider.items import PokemonItem


class BaseStatsSpider(scrapy.Spider):
    name = "base_stats"
    allowed_domains = ["wiki.52poke.com"]

    custom_settings = {
        "ITEM_PIPELINES": {
            "pokedex_spider.pipelines.PokedexBaseStatsPipeline": 300,
        }
    }

    def start_requests(self):
        urls = [
            # "https://wiki.52poke.com/wiki/%E6%9C%80%E7%BB%88%E5%BD%A2%E6%80%81%E7%A7%8D%E6%97%8F%E5%80%BC%E5%88%97%E8%A1%A8",
            "https://wiki.52poke.com/wiki/%E7%A7%8D%E6%97%8F%E5%80%BC%E5%88%97%E8%A1%A8%EF%BC%88%E7%AC%AC%E4%B9%9D%E4%B8%96%E4%BB%A3%EF%BC%89",
            "https://wiki.52poke.com/wiki/%E7%A7%8D%E6%97%8F%E5%80%BC%E5%88%97%E8%A1%A8%EF%BC%88%E7%AC%AC%E5%85%AB%E4%B8%96%E4%BB%A3%EF%BC%89",
            "https://wiki.52poke.com/wiki/%E7%A7%8D%E6%97%8F%E5%80%BC%E5%88%97%E8%A1%A8%EF%BC%88%E7%AC%AC%E4%B8%83%E4%B8%96%E4%BB%A3%EF%BC%89",
            "https://wiki.52poke.com/wiki/%E7%A7%8D%E6%97%8F%E5%80%BC%E5%88%97%E8%A1%A8%EF%BC%88%E7%AC%AC%E4%B8%83%E4%B8%96%E4%BB%A3%EF%BC%89",
            "https://wiki.52poke.com/wiki/%E7%A7%8D%E6%97%8F%E5%80%BC%E5%88%97%E8%A1%A8%EF%BC%88%E7%AC%AC%E4%BA%94%E4%B8%96%E4%BB%A3%EF%BC%89"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        pokemon = PokemonItem()
        stat_table = response.xpath("//*[@id='mw-content-text']/div[1]/table[1]")

        for stat in stat_table.xpath("./tbody/tr[position() > 1 and position() < last()]"):
            pokemon["pokedex_index"] = '#' + stat.xpath("./td[1]/text()").get().strip()
            cn_name = stat.xpath("./td[3]/a/text()").get().strip()
            pokemon["cn_name"] = cn_name
            pokemon['original'] = 1
            forme = stat.xpath("./td[3]/small//text()")
            if forme:
                forme_cn_name = forme.get().strip()
                pokemon['original'] = 0
                if forme_cn_name.startswith("超级"):
                    pokemon["cn_name"] = forme_cn_name
                else:
                    pokemon["cn_name"] = cn_name + "-" + forme.get().strip()

            pokemon['hp'] = stat.xpath("./td[4]/text()").get().strip()
            pokemon['attack'] = stat.xpath("./td[5]/text()").get().strip()
            pokemon['defense'] = stat.xpath("./td[6]/text()").get().strip()
            pokemon['sp_attack'] = stat.xpath("./td[7]/text()").get().strip()
            pokemon['sp_defense'] = stat.xpath("./td[8]/text()").get().strip()
            pokemon['speed'] = stat.xpath("./td[9]/text()").get().strip()

            yield pokemon
