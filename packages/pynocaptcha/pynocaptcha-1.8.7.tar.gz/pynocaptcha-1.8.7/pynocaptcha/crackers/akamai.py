
from .base import BaseCracker


class AkamaiV2Cracker(BaseCracker):
    
    cracker_name = "akamai"
    cracker_version = "v2"    

    """
    akamai v2 cracker
    :param href: 触发验证的页面地址
    :param api: akamai 提交 sensor_data 的地址
    :param telemetry: 是否 headers 中的 telemetry 参数验证形式, 默认 false
    :param cookies: 请求 href 首页返回的 cookie _abck, bm_sz 值, 传了 api 参数必须传该值, 示例: { "value": "_abck=xxx; bm_sz=xxx", "uri": "https://example.com" }
    :param device: 请求流程使用的设备类型, 可选 pc/mobile, 默认 mobile
    调用示例:
    cracker = AkamaiV2Cracker(
        user_token="xxx",
        href="xxx",
        api="xxx",
        
        # debug=True,
        # proxy=proxy,
    )
    ret = cracker.crack()
    """
    
    # 必传参数
    must_check_params = ["href"]
    # 默认可选参数
    option_params = {
        "api": "",
        "telemetry": False,
        "uncheck": True,
        "http2": True,
        "device": "mobile"
    }