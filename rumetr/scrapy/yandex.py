import hashlib

from rumetr.scrapy.item import ApptItem as Item
from scrapy.spiders import XMLFeedSpider


class YandexFeedSpider(XMLFeedSpider):
    """Base Spider to parse yandex-realty feed"""
    name = 'spider'
    namespaces = [('yandex', 'http://webmaster.yandex.ru/schemas/feed/realty/2010-06')]
    itertag = 'yandex:offer'
    iterator = 'xml'

    def parse_node(self, response, node):
        item = dict()

        item.update(dict(
            id=node.xpath('@internal-id')[0].extract(),
            room_count=node.xpath('yandex:rooms/text()')[0].extract(),
            square=node.xpath('yandex:area/yandex:value/text()')[0].extract(),
            price=node.xpath('yandex:price/yandex:value/text()')[0].extract(),
            house_id=node.xpath('yandex:building-section/text()')[0].extract(),
            house_name=node.xpath('yandex:building-section/text()')[0].extract(),
            complex_id=node.xpath('yandex:yandex-building-id/text()')[0].extract(),
            complex_name=node.xpath('yandex:building-name/text()')[0].extract(),
            complex_url=node.xpath('yandex:url/text()')[0].extract(),
            floor=node.xpath('yandex:floor/text()')[0].extract(),
            addr=self.build_address(node),
            is_studio=self.is_studio(node),
        ))

        item = self.append_feed_data(node, item)

        yield Item(**item)

    def append_feed_data(self, node, item):
        return item

    def is_studio(self, node):
        try:
            return bool(node.xpath('yandex:studio/text()')[0].extract())
        except IndexError:
            return False

    def build_address(self, node):
        location = node.xpath('yandex:location/yandex:region/text()')[0].extract()
        city = node.xpath('yandex:location/yandex:locality-name/text()')[0].extract()
        addr = node.xpath('yandex:location/yandex:address/text()')[0].extract()

        return ', '.join(x for x in [location, city, addr] if x is not None and len(x))

    def _hash(self, input):
        return hashlib.md5(input.encode('utf-8')).hexdigest()
