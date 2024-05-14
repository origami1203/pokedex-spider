# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import difflib

import pymysql
import scrapy


class PokedexSpiderPipeline:

    def __init__(self):
        self.connection: pymysql.connections.Connection = None
        self.cache_items = []

    def open_spider(self, spider):
        database_config = spider.settings.get('DATABASE')
        self.connection = pymysql.connect(host=database_config['host'],
                                          port=database_config['port'],
                                          user=database_config['username'],
                                          password=database_config['password'],
                                          database=database_config['database'],
                                          charset=database_config['charset'],
                                          cursorclass=pymysql.cursors.DictCursor)

    def process_item(self, item, spider):
        spider.log("保存数据到数据库中,图鉴编号为：%s" % item['pokedex_index'])
        self.cache_items.append(item)
        if len(self.cache_items) >= 50:
            self.__insert()
        return item

    def close_spider(self, spider):
        self.__insert()
        if self.connection is not None and self.connection.open:
            self.connection.close()

    def __insert(self):

        if self.cache_items:
            with self.connection.cursor() as cursor:
                insert_sql = """INSERT INTO pokemon (id, pokedex_index, is_original, cn_name, jp_name, en_name, species, 
                              type1, type2, ability1, ability2,ability_hidden,height, weight, egg_group1, egg_group2, 
                              catch_rate, simple_description) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s , %s, %s,
                               %s, %s,%s,%s)"""

                cursor.executemany(
                    insert_sql,
                    [(None, item['pokedex_index'], item['original'], item['cn_name'], item['jp_name'], item['en_name'],
                      item['species'],
                      item['type1'], item['type2'], item['ability1'], item['ability2'], item['ability_hidden'],
                      item['height'], item['weight'],
                      item['egg_group1'], item['egg_group2'], item['catch_rate'], item['simple_description']) for item
                     in
                     self.cache_items])

            self.cache_items = []
            self.connection.commit()


class PokedexBaseStatsPipeline:
    """
    宝可梦的种族值数据
    """

    def __init__(self):
        self.connection: pymysql.connections.Connection = None

    def open_spider(self, spider):
        database_config = spider.settings.get('DATABASE')
        self.connection = pymysql.connect(host=database_config['host'],
                                          port=database_config['port'],
                                          user=database_config['username'],
                                          password=database_config['password'],
                                          database=database_config['database'],
                                          charset=database_config['charset'],
                                          cursorclass=pymysql.cursors.DictCursor)

    def process_item(self, item, spider):
        with self.connection.cursor() as cursor:
            self.__do_process(cursor, item)
            self.connection.commit()
        return item

    def close_spider(self, spider):
        self.__final_process_forme()
        if self.connection is not None and self.connection.open:
            self.connection.close()

    def __do_process(self, cursor, item):
        cursor.execute("SELECT pokedex_index,cn_name,hp,attack,defense,sp_attack,sp_defense,speed FROM pokemon "
                       "WHERE pokedex_index = %s AND is_original = %s AND hp IS NULL",
                       (item['pokedex_index'], item['original']))
        forme_pokemon = cursor.fetchall()

        if len(forme_pokemon) == 0:
            return

        if len(forme_pokemon) == 1:
            hp = forme_pokemon[0]['hp']
            if hp:
                return

            cursor.execute("UPDATE pokemon SET cn_name=%s, hp = %s, attack = %s, defense = %s, sp_attack = %s, "
                           "sp_defense = %s, speed = %s WHERE pokedex_index = %s AND is_original = %s",
                           (item['cn_name'], item['hp'], item['attack'], item['defense'], item['sp_attack'],
                            item['sp_defense'], item['speed'], item['pokedex_index'], item['original']))

        if len(forme_pokemon) > 1:
            pokemon_forme_name_list = map(lambda pokemon: pokemon['cn_name'], forme_pokemon)
            max_match_name = difflib.get_close_matches(item['cn_name'], list(pokemon_forme_name_list), n=1, cutoff=0.1)

            if len(max_match_name) == 0:
                return

            cursor.execute(
                "UPDATE pokemon SET cn_name = %s, hp = %s, attack = %s, defense = %s, sp_attack = %s, sp_defense = %s, "
                "speed = %s WHERE pokedex_index = %s AND cn_name = %s",
                (item['cn_name'], item['hp'], item['attack'], item['defense'], item['sp_attack'], item['sp_defense'],
                 item['speed'], item['pokedex_index'], max_match_name[0]))

    def __final_process_forme(self):
        """剩余部分的宝可梦只是形态的不同,种族值与原始数据是一样的,选择原始宝可梦的种族值进行覆盖"""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT id,pokedex_index,hp,attack,defense,sp_attack,sp_defense,speed FROM pokemon "
                           "WHERE hp IS NULL")
            empty_stat_pokemons = cursor.fetchall()

            if len(empty_stat_pokemons) == 0:
                return

            for empty_stat_pokemon in empty_stat_pokemons:
                cursor.execute("SELECT hp,attack,defense,sp_attack,sp_defense,speed FROM pokemon WHERE  pokedex_index "
                               "= %s AND is_original = 1", empty_stat_pokemon['pokedex_index'])

                original_pokemon = cursor.fetchone()

                if original_pokemon == 0:
                    continue

                cursor.execute("UPDATE pokemon SET hp = %s, attack = %s, defense = %s, sp_attack = %s, sp_defense = %s,"
                               "speed = %s WHERE id = %s",
                               (original_pokemon['hp'], original_pokemon['attack'],
                                original_pokemon['defense'], original_pokemon['sp_attack'],
                                original_pokemon['sp_defense'], original_pokemon['speed'], empty_stat_pokemon['id']))

            self.connection.commit()


class PokedexMovePipeline:

    def __init__(self):
        self.connection: pymysql.connections.Connection = None

    def open_spider(self, spider):
        self.connection = get_connection(spider)

    def close_spider(self, spider):
        if self.connection is not None and self.connection.open:
            self.connection.close()

    def process_item(self, item, spider):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO moves (move_no, move_cn_name, move_en_name, move_jp_name, move_type, "
                           "move_category, move_power, move_accuracy, move_pp, move_description, move_priority,"
                           "move_effect) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (item['move_no'], item['move_cn_name'], item['move_en_name'], item['move_jp_name'],
                            item['move_type'], item['move_category'], item['move_power'], item['move_accuracy'],
                            item['move_pp'], item['move_description'], item['move_priority'], item['move_effect']))

        self.connection.commit()


class PokedexAbilityPipeline:
    def __init__(self):
        self.connection: pymysql.connections.Connection = None
        self.cache_items = []

    def open_spider(self, spider):
        database_config = spider.settings.get('DATABASE')
        self.connection = pymysql.connect(host=database_config['host'],
                                          port=database_config['port'],
                                          user=database_config['username'],
                                          password=database_config['password'],
                                          database=database_config['database'],
                                          charset=database_config['charset'],
                                          cursorclass=pymysql.cursors.DictCursor)

    def process_item(self, item, spider):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO abilities (ability_no, ability_cn_name, ability_en_name, ability_jp_name, "
                           "ability_description, ability_effect, ability_change_log) VALUES (%s, %s, %s, %s, %s,%s,%s)",
                           (item['ability_no'], item['ability_cn_name'], item['ability_en_name'],
                            item['ability_jp_name'],
                            item['ability_description'], item['ability_effect'], item['ability_change_log']))

        self.connection.commit()
        return item

    def close_spider(self, spider):
        if self.connection is not None and self.connection.open:
            self.connection.close()


class PokedexItemPipeline:

    def __init__(self):
        self.connection: pymysql.connections.Connection = None

    def open_spider(self, spider):
        self.connection = get_connection(spider)

    def process_item(self, item, spider):
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO items (item_cn_name, item_en_name, item_jp_name, item_description, item_effect,"
                           " item_change_log,item_acquisition) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                           (item['item_cn_name'], item['item_en_name'], item['item_jp_name'], item['item_description'],
                            item['item_effect'], item['item_change_log'], item['item_acquisition']))

        self.connection.commit()

    def close_spider(self, spider):
        if self.connection is not None and self.connection.open:
            self.connection.close()


def get_connection(spider: scrapy.Spider):
    database_config = spider.settings.get('DATABASE', {})
    return pymysql.connect(host=database_config['host'],
                           port=database_config['port'],
                           user=database_config['username'],
                           password=database_config['password'],
                           database=database_config['database'],
                           charset=database_config['charset'],
                           cursorclass=pymysql.cursors.DictCursor)
