import os
import warnings
import configparser

def set_environ(f='config.ini'):
    config = configparser.ConfigParser()
    config.read( f )
    for k in config['environ']:
        os.environ[k.upper()] = config['environ'][k]


def environment_checker():
    """
    检查环境变量是否设置。

    检查以下环境变量是否在系统环境变量中设置：
    - MONGODB_URL: MongoDB数据库的URL。
    - MONGODB_PUB_URI: 公共访问的MongoDB数据库的URL。
    - DINGTALK_WEBHOOK: 钉钉机器人的Webhook地址。
    - QYWECHAT_WEBHOOK: 企业微信机器人的Webhook地址。

    如果环境变量未设置，则发出警告提示。

    参数:
        无

    返回:
        无
    """
    for k in ['MONGODB_URL', 'MONGODB_PUB_URI', 'DINGTALK_WEBHOOK','QYWECHAT_WEBHOOK']:
        if k not in os.environ:
            if k == 'MONGODB_URL':
                print('see <Setting Up DBWorker> https://second-cloche-446.notion.site/ANBUtils-Wiki-f3ba5d99b6904a56a3335aff927492ee' )
            warnings.warn( '\nPlease set %s in environment variable' % k )



