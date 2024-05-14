# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os
from urllib import parse

from scrapy import signals, http


# useful for handling different item types with a single interface


class PokedexSpiderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class PokedexSpiderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    __downloaded = set()

    def __new__(cls, *args, **kwargs):
        for filename in os.listdir("download"):
            cls.__downloaded.add(filename.split(".")[0])
        return super().__new__(cls, *args, **kwargs)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        # 查看是否已经下载过，已经下载过直接返回
        name = parse.unquote(request.url.split("/")[-1])

        if name not in self.__downloaded:
            return None
        else:
            spider.logger.info(f"已经下载: {name},无需再次下载")
            with open(f"download/{name}.html", "r", encoding="utf-8") as file:
                return http.HtmlResponse(url=request.url, body=file.read().encode("utf-8"), request=request)

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        pokemon_name = parse.unquote(request.url.split("/")[-1])
        if pokemon_name in self.__downloaded:
            spider.logger.info(f"已经保存过: {pokemon_name},无需再次保存")
            return response

        self.__downloaded.add(pokemon_name)
        with open(f"download/{pokemon_name}.html", "wb") as file:
            file.write(response.body)
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        spider.logger.info(f"下载异常: {exception}")

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
