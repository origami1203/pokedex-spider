from itertools import takewhile
from urllib import parse

import scrapy
from scrapy.http import Response

from pokedex_spider.items import PokemonItem


class PokedexSpider(scrapy.Spider):
    name = "pokemon"
    allowed_domains = ["wiki.52poke.com"]
    start_urls = ["https://wiki.52poke.com/wiki/%E5%A6%99%E8%9B%99%E7%A7%8D%E5%AD%90"]  # 妙蛙种子
    stop_urls = "/wiki/%E5%A6%99%E8%9B%99%E7%A7%8D%E5%AD%90"

    custom_settings = {
        "ITEM_PIPELINES": {
            "pokedex_spider.pipelines.PokedexSpiderPipeline": 300,
        }
    }

    def parse(self, response: Response):
        next_page_url = response.xpath(
            "//div[@class='mw-parser-output']/table[1]//*[@title='宝可梦列表（按全国图鉴编号）/简单版']/../../td[last()]"
            "/descendant::a[1]/@href").get()

        single_pokemon_forme_list = PokedexSpider.__parse_pokemons(response)
        for pokemon_forme in single_pokemon_forme_list:
            yield pokemon_forme

        self.log("解析数据: %s" % parse.unquote(response.url))

        # 防止循环
        if next_page_url is not None and next_page_url != self.stop_urls:
            yield response.follow(url=next_page_url, callback=self.parse)

    @staticmethod
    def __parse_pokemons(response: Response):
        multi_pm_forme_list = PokedexSpider.__get_pm_info_forme(response)
        pokemon_list = []

        for pm_forme in multi_pm_forme_list:
            pokemon = PokedexSpider.__do_parse_pokemon(pm_forme)
            if pokemon is not None:
                if len(pokemon_list) == 0:
                    pokemon['original'] = 1
                else:
                    pokemon['original'] = 0
                pokemon_list.append(pokemon)

        return pokemon_list

    @staticmethod
    def __get_pm_info_forme(response: Response):
        result = []
        multi_forme_table = response.xpath("//*[@id='multi-pm-form-table']")
        pm_info_table = response.xpath("//*[@id='mw-content-text']/div[1]/table[2]")

        # 多种形态
        if multi_forme_table:
            pm_info_table_list = pm_info_table.xpath("./tbody/tr")
            actual_multi_forme_list = multi_forme_table.xpath("//tr[@class='md-hide']")
            for index, forme_table in enumerate(actual_multi_forme_list):
                multi_forme_cn_name = forme_table.xpath("./th/text()").get().strip()
                result.append((multi_forme_cn_name, pm_info_table_list[index]))

        # 单种形态
        else:
            single_forme_table = response.xpath("//*[@id='mw-content-text']/div[1]/table[2]")
            result.append((None, single_forme_table))

        return result

    @staticmethod
    def __do_parse_pokemon(forem_tuple):
        pokemon = PokemonItem()

        info_table = forem_tuple[1]
        pokemon['pokedex_index'] = info_table.xpath("//a[@title='宝可梦列表（按全国图鉴编号）']/text()").get()
        jp_span_location = info_table.xpath("//*[@lang='ja']")
        pokemon['jp_name'] = jp_span_location.xpath("./text()").get()
        pokemon['en_name'] = jp_span_location.xpath("./../following-sibling::b[1]/text()").get()
        pokemon['species'] = info_table.xpath("//a[@title='分类']/../../table//a/text()").get()

        cn_name = jp_span_location.xpath("./../preceding-sibling::span[1]/b/text()").get()
        pokemon['cn_name'] = cn_name
        multi_forme_cn_name = forem_tuple[0]
        if multi_forme_cn_name is not None:
            if cn_name in multi_forme_cn_name:
                pokemon['cn_name'] = multi_forme_cn_name
            else:
                pokemon['cn_name'] = cn_name + "-" + multi_forme_cn_name

        # 属性
        types = info_table.xpath(
            ".//b/a[@title='属性']/../../table//a//span[@class='type-box-9-text']/text()").getall()
        if len(types) == 1:
            pokemon['type1'] = types[0]
            pokemon['type2'] = ''
        else:
            pokemon['type1'] = types[0]
            pokemon['type2'] = types[1]

        # 蛋组
        egg_groups = info_table.xpath(
            ".//a[@title='宝可梦培育' and text() = '培育']/../../table//td[1]/*/text()").getall()

        # 猛擂鼓的培育html与其他不一致
        if len(egg_groups) == 0:
            pokemon['egg_group1'] = '未发现群'
            pokemon['egg_group2'] = ''
        elif len(egg_groups) == 1:
            pokemon['egg_group1'] = egg_groups[0]
            pokemon['egg_group2'] = ''
        else:
            pokemon['egg_group1'] = egg_groups[0]
            pokemon['egg_group2'] = egg_groups[1]

        pokemon['height'] = info_table.xpath(
            ".//a[@title='宝可梦列表（按身高和体重排序）' and text()='身高']/../../table//td/text()").get().strip()
        pokemon['weight'] = info_table.xpath(
            ".//a[@title='宝可梦列表（按身高和体重排序）'and text()='体重']/../../table//td/text()").get().strip()
        pokemon['catch_rate'] = info_table.xpath(".//span[@title='普通的精灵球在满体力下的捕获率']/text()").get()

        # 特性
        abilities = info_table.xpath(".//a[@title='特性']/../../table//td[1]/a/text()").getall()

        # 基格尔德的细胞和核心形态并不属于宝可梦对战  跳过
        if len(abilities) == 0:
            return None

        if len(abilities) == 1:
            pokemon['ability1'] = abilities[0]
            pokemon['ability2'] = ''
        else:
            pokemon['ability1'] = abilities[0]
            pokemon['ability2'] = abilities[1]

        hidden_ability = info_table.xpath(".//a[@title='特性']/../../table//td[2]/a/text()").get()
        if hidden_ability is None:
            pokemon['ability_hidden'] = ''
        else:
            pokemon['ability_hidden'] = hidden_ability

        all_siblings = info_table.xpath("//*[@id='概述']/../following-sibling::*")
        if len(all_siblings) == 0:
            all_siblings = info_table.xpath("//*[@id='基本介绍']/../following-sibling::*")
        p_tags = takewhile(lambda x: x.xpath("self::p"), all_siblings)
        pokemon['simple_description'] = "".join([p_tag.xpath("./text()").get() for p_tag in p_tags])

        return pokemon
