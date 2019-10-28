def djb(s):
    # calculates DJB hash for string s
    # from https://gist.github.com/mengzhuo/180cd6be8ba9e2743753#file-hash_djb2-py
    hash = 5381
    for x in s:
        hash = ((hash << 5) + hash) + ord(x)
    return hash & 0xFFFFFFFF
