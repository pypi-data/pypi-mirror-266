from .base import BaseCracker

import warnings
warnings.filterwarnings('ignore')


class CloudFlareCracker(BaseCracker):
    
    cracker_name = "cloudflare"
    cracker_version = "universal"    

    """
    cloudflare cracker
    :param href: 触发 cloudfalre 验证的首页地址
    :param user_agent: 请求流程使用 ua, 不传
    :param headers: 触发验证必须的 headers, 默认 {} 
    :param cookies: 触发验证必须的 cookies, 默认 {} 
    :param html: 是否需要返回 html
    :param turnstile: 是否需要 cf_turnstile-response 参数
    :param timeout: 最大破解超时时间
    调用示例:
    cracker = CloudFlareCracker(
        href=href,
        user_token="xxx",
    )
    ret = cracker.crack()
    """
    
    # 必传参数
    must_check_params = ["href", "proxy"]
    # 默认可选参数
    option_params = {
        "branch": "Master",
        "user_agent": None,
        "headers": {},
        "cookies": {},
        "html": False,
        "sitekey": "",
        "alpha": False,
        "timeout": 30
    }
