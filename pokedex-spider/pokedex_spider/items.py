# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PokemonItem(scrapy.Item):
    # 全国图鉴编号
    pokedex_index = scrapy.Field()
    # 是否是原始宝可梦（即不属于地区形态和极巨化 mage）
    original = scrapy.Field()
    cn_name = scrapy.Field()
    jp_name = scrapy.Field()
    en_name = scrapy.Field()
    # 分类
    species = scrapy.Field()
    # 属性
    type1 = scrapy.Field()
    type2 = scrapy.Field()
    # 特性
    ability1 = scrapy.Field()
    ability2 = scrapy.Field()
    ability_hidden = scrapy.Field()

    height = scrapy.Field()
    weight = scrapy.Field()

    egg_group_num = scrapy.Field()
    egg_group1 = scrapy.Field()
    egg_group2 = scrapy.Field()
    # 捕获率
    catch_rate = scrapy.Field()
    simple_description = scrapy.Field()

    # 种族值
    hp = scrapy.Field()
    attack = scrapy.Field()
    defense = scrapy.Field()
    sp_attack = scrapy.Field()
    sp_defense = scrapy.Field()
    speed = scrapy.Field()

    learn_set = scrapy.Field()

    evolution = scrapy.Field()


class MoveItem(scrapy.Item):
    move_no = scrapy.Field()
    move_cn_name = scrapy.Field()
    move_en_name = scrapy.Field()
    move_jp_name = scrapy.Field()

    # 招式属性（18种属性）
    move_type = scrapy.Field()
    # 招式分类（物理、特殊、变化）
    move_category = scrapy.Field()
    # 威力
    move_power = scrapy.Field()
    # 命中
    move_accuracy = scrapy.Field()
    move_pp = scrapy.Field()
    # 先制度
    move_priority = scrapy.Field()
    # 效果
    move_effect = scrapy.Field()

    move_description = scrapy.Field()


class AbilityItem(scrapy.Item):
    ability_no = scrapy.Field()
    ability_cn_name = scrapy.Field()
    ability_en_name = scrapy.Field()
    ability_jp_name = scrapy.Field()
    ability_description = scrapy.Field()
    ability_effect = scrapy.Field()
    ability_change_log = scrapy.Field()


class PokedexItem(scrapy.Item):
    item_cn_name = scrapy.Field()
    item_jp_name = scrapy.Field()
    item_en_name = scrapy.Field()
    item_description = scrapy.Field()
    item_effect = scrapy.Field()
    item_change_log = scrapy.Field()
    # 获取方式
    acquisition = scrapy.Field()
