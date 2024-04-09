import random
import time

from scrapy.http import HtmlResponse


class DrissionPageMiddleware:
    """
    使用 Drission自动化操作页面需要在脚本开头
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.edge = ChromiumPage()  # 实例化浏览器
    """

    def process_request(self, request, spider):
        """
        使用 Drissonpage 请求
        :param request:
        :param spider:
        :return:
        """
        url = request.url
        spider.edge.get(url)  # 请求页面,和selemunim get方法一致
        spider.edge.wait.load_start(3)  # 等待加载
        html = spider.edge.html  # 获取页面 html，和selemunim的 source 属性一致
        return HtmlResponse(url=url, body=html, request=request, encoding='utf-8')

    def process_response(self, request, response, spider):
        """
        处理滑块验证码
        :param request:
        :param response:
        :param spider:
        :return:
        """
        url = request.url
        from DrissionPage.common import Actions
        # 出现滑块场景处理
        while spider.edge.s_ele('#nc_1_n1z'):  # 出现滑块验证码
            spider.edge.clear_cache()  # 清理缓存
            ac = Actions(spider.edge)
            for i in range(random.randint(10, 20)):
                ac.move(random.randint(-20, 20), random.randint(-10, 10))
            else:
                ac.move_to('#nc_1_n1z')
            ac.hold().move(300)
            time.sleep(2)
            spider.edge.get(url)
            time.sleep(2)
            html = spider.edge.html
            if not '滑动验证页面' in html:  # 验证成功
                return HtmlResponse(url=url, body=html, request=request, encoding='utf-8')
            else:  # 验证失败
                spider.edge.clear_cache()
                spider.edge.get(url)
        return response
