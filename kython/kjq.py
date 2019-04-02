def pipe(*queries):
    return ' | '.join(queries)

def jdel(q):
    return f'del({q})'

def jq_del_all(*keys):
    parts = []
    # TODO shit. looks like query might be too long for jq...
    for q in range(0, len(keys), 10):
        kk = keys[q: q + 10]
        parts.append(jdel('.. | ({})'.format(', '.join('.' + k + '?' for k in kk))))
    return pipe(*parts)
