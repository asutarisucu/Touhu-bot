import json
from collections import OrderedDict
import blocklist
import moblist
import staticslist
import sortlist

def convertjson(filename,f):
    js=json.load(f)
    f.close
    dump_js=sort(sortlist.sortlist,js)
    js_after=json.dumps(dump_js)
    js_after=convert(blocklist.blocklist,js_after)
    js_after=convert(staticslist.staticslist,js_after)
    js_after=convert(moblist.mobs,js_after)
    js_after=json.loads(js_after)
    json.dump(js_after, open(filename, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

def convert(wordlist,js_after):
   for list in wordlist:
      js_after=js_after.replace(list[0],list[1])
   return js_after

def sort(sortlist,js):
   dump_js=OrderedDict()
   for list in sortlist:
      dump_js[list[0]]= OrderedDict(sorted(js["stats"][list[1]].items(), key=lambda x: x[1],reverse=True))
   return dump_js
