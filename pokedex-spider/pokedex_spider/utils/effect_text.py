from itertools import takewhile
import parsel


def get_effect_text(xpath_node: parsel.SelectorList):
    desc_tags = takewhile(lambda x: not x.xpath("self::h2"), xpath_node)

    effect_text = ""

    for desc_tag in desc_tags:
        tags_text_list = desc_tag.xpath(".//text()").getall()
        tag_text = "".join(tags_text.strip() for tags_text in tags_text_list)
        effect_text += tag_text + "\n"

    return effect_text
