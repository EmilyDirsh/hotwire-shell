import os,sys

from hotwire.cmdalias import AliasRegistry

default_aliases = {'sudo': 'term -w sudo',
                   'su': 'term -w su',                   
                   'vi': 'term vi',
                   'vim': 'term vim',
                   'gdb': 'term -w gdb',                   
                   'ssh': 'term -w ssh',
                   'man': 'term man',
                   'info': 'term info',
                   'less': 'term less',
                   'more': 'term more',  
                   'top': 'term top',
                   'powertop': 'term powertop',                   
                   'nano': 'term nano',
                   'pico': 'term pico',
                   'irssi': 'term -w irssi',
                   'mutt': 'term -w mutt',
                  }
aliases = AliasRegistry.getInstance()
for name,value in default_aliases.iteritems():
    aliases.insert(name, value)

import hotwire.sysdep.unix_completers