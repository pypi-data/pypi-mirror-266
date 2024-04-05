import re


def proxy_parse_tuple(proxy: str | None) -> tuple | None:
    if proxy is None:
        return None
    else:
        try:
            rst = re.split('://|:', proxy)
            if len(rst) != 3:
                return None
            rst[-1] = int(rst[-1])
            return tuple(rst)
        except:
            return None
