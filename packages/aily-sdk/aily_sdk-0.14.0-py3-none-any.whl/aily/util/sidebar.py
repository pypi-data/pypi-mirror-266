import urllib.parse


def get_sidebar_url(url):
    return 'https://applink.feishu.cn/client/web_url/open?mode=sidebar-semi&url=' + urllib.parse.quote(url)


if __name__ == '__main__':
    print(get_sidebar_url('https://www.feishu.cn'))
