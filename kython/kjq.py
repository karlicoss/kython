"""
Some combinators for jq
"""

def pipe(*queries):
    return ' | '.join(queries)

def jdel(q):
    return f'del({q})'

def jq_del_all(*keys, split_by=10):
    parts = []
    # TODO shit. looks like query might be too long for jq...
    # TODO wow, split_by almost doesn't make any difference. actually _not splitting_ slows it down!
    for q in range(0, len(keys), split_by):
        kk = keys[q: q + split_by]
        parts.append(jdel('.. | ({})'.format(', '.join('.' + k + '?' for k in kk))))
    return pipe(*parts)


# https://stackoverflow.com/a/39420551/706389
# TODO this jq_del_all should be in kython and tested...
# TODO might be used by smth else??
# TODO not sure if walk is available by default?
def jq_del_all_faster(*keys, split_by=None):
    # ok, this is fucking unbearably slow...
    # pred = 'any(index({keyss}); . != null)'.format(keyss=', '.join(f'"{k}"' for k in keys))

    # regex is quite bit faster! jeez.
    # like a 3x speedup over jdel(.. | ) thing
    # TODO FIXME careful; might need escaping..
    pred = 'test("^({keyss})$")'.format(keyss='|'.join(keys))
    return '''walk(
      if type == "object"
        then with_entries(select( .key | {pred} | not))
        else .
      end)
    '''.format(pred=pred)


from typing import Dict, Any, Callable
Json = Dict[str, Any]
JsonFilter = Callable[[Json], Json]

def del_all_kjson(*keys) -> JsonFilter:
    from kython.kjson import JsonProcessor
    class DeleteKeys(JsonProcessor):
        def __init__(self, *delk: str) -> None:
            super().__init__()
            self.delk = set(delk)

        # TODO huh, ok, this is clearly very powerful. need to publish somwhere..
        def handle_dict(self, js, jp) -> None:
            todel = self.delk.intersection(js.keys())
            for k in todel:
                del js[k]


    def run(json: Json, keys=keys) -> Json:
        dk = DeleteKeys(*keys)
        dk.run(json)
        # TODO eh. it's inplace; might be a bit unexpected...
        return json

    return run


_JSON_EXAMPLE = '''
{"glossary": {"title": "example glossary",
  "GlossDiv": {
"title": "S", "GlossList": {"GlossEntry": {
   "ID": "SGML", "SortAs": "SGML", "GlossTerm": "Standard Generalized Markup Language", "Acronym": "SGML", "Abbrev": "ISO 8879:1986",
"GlossDef": {
  "para": "A meta-markup language, used to create markup languages such as DocBook.",
"GlossSeeAlso": ["GML", "XML"]
                    },
    "GlossSee": "markup"
}
            }
        }
    }
}
'''

import pytest # type: ignore




_EXAMPLE = '{"key1": "whatever...", "key2": {"key1": "hello", "alala": "oops key1 "}}'

@pytest.mark.parametrize('json, delk, exp', [
    ('{}'      , (), '{}'),
    ('["test"]', ("test"), '''
[
  "test"
]
'''),
    (
        _EXAMPLE,
        ('key1',),
'''
{
  "key2": {
    "alala": "oops key1 "
  }
}

'''
    ),
    (
        _EXAMPLE,
        ('key2',),
'''
{
  "key1": "whatever..."
}
'''
    ),
    # (_JSON_EXAMPLE, {}),
])
def test_rg_del_all(json, delk, exp):
    from subprocess import run, PIPE

    # syntax check
    run('python3 -m json.tool', shell=True, input=exp.encode('utf8')).check_returncode()

    def dodo(s: str, *args):
        import json
        j = json.loads(s)
        filt = del_all_kjson(*args)
        j = filt(j)
        js = json.dumps(j)
        # pretty print
        r = run('jq .', shell=True, input=js.encode('utf8'), stdout=PIPE)
        r.check_returncode()
        return r.stdout.decode('utf8')

    res = dodo(json, *delk)
    assert res.strip('\n') == exp.strip('\n')




