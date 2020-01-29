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


Command = str

def rg_del_all(*keys) -> Command:
    """
    # TODO pprint in advance??
    Assuming pretty printed output?
    """
    # TODO FIXME pipefail??
    # TODO or just multiple commands?
    return 'python3 -m json.tool'


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


@pytest.mark.parametrize('json, exp', [
    ('{}', '{}'),
    # (_JSON_EXAMPLE, {}),
])
def test_rg_del_all(json, exp):
    from subprocess import run, PIPE
    def dodo(s: str, *args):
       cmd = rg_del_all(*args)
       r = run(cmd, shell=True, input=s.encode('utf8'), stdout=PIPE)
       r.check_returncode()
       return r.stdout.decode('utf8').rstrip('\n')

    res = dodo(json, 'title')
    assert res == exp

