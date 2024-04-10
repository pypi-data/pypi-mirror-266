from urllib import parse

def http_build_query(data):
    '''http_build_query() emulates the PHP function of the same name.
    `data` can be list or dict containing nested lists or dicts of any depth.
    The output is an url encoded string that can be posted using the
    application/x-www-form-urlencoded format.
    '''
    parents = list()
    pairs = dict()

    def renderKey(parents):
        depth, out = 0, ''
        for x in parents:
            s = "[%s]" if depth > 0 or isinstance(x, int) else "%s"
            out += s % str(x)
            depth += 1
        return out

    def r_urlencode(data):
        if isinstance(data, list) or isinstance(data, tuple):
            for i in range(len(data)):
                parents.append(i)
                r_urlencode(data[i])
                parents.pop()
        elif isinstance(data, dict):
            for key, value in data.items():
                parents.append(key)
                r_urlencode(value)
                parents.pop()
        else:
            pairs[renderKey(parents)] = str(data)

        return pairs

    return parse.urlencode(r_urlencode(data))