from scrapy import cmdline

if __name__ == '__main__':
    cmdline.execute("scrapy crawl pokemon -O pokemon.jsonl".split())
    # cmdline.execute("scrapy crawl base_stats".split())
    # cmdline.execute("scrapy crawl move".split())
    # cmdline.execute("scrapy crawl ability -O ability.jsonl".split())
    # cmdline.execute("scrapy crawl item -O item.jsonl".split())
