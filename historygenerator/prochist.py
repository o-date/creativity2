#!/usr/bin/env python
# source: https://gamedev.stackexchange.com/questions/23659/is-there-a-way-to-procedurally-generate-the-history-of-a-world
# to create a visualisation, run like this:
#    ./historygen.py --dot | dot -Tpng > filename.png
# brew install graphviz to get the dot files rendering
# to have the story, run like this:
# ./historygen.py
# have your state names in the names.txt file
# now, all of this *could* be done with tracery i suppose, but you can see the bones of the
# history system could be expanded to model other aspects, keep track of things, calculate new things. 

import sys
import random
import tracery #pip install tracery, to get python version https://github.com/aparrish/pytracery

from tracery.modifiers import base_english
from pprint import pprint

#set up the grammar. this is just to build story around the 
#history. The 'history' generated is more like a chronicle
#so the tracery bit is to flesh that all out a bit.
#maybe

rules = {
    'time': ['a few years later', 'as it came to pass','within a generation'],
    'connector': ['But','Then','Years passed - ','And then','The seasons cycled - but'],
    'dissolved': ['dissolved', 'slowly fell', 'quickly shattered', 'collapsed'],
    'strength': ['fragile', 'weakening', 'uncertain', 'weak'],
    'island': ['island.','peninsula, shielded from the rest of the world by tall mountains.','continent that should have been large enough for us all.','archipelago of islands and islets in an azure sea.'],
    'climatedisaster': ['flooding ruined the crops; the famine','the clouds grew dark, and hunger stalked the land. Sickness','pestilence and plague killed thousands, and'],
    'problem': ['hunger','patience','good will','strength'],
    'ruler': ['King','Patrician','Satrap','Consul','Princess','Queen','President','Dictator','Elders','Council'],
    'beginning': 'These people shared a single #island#',
    'originpartition': '#connector# #partition# and so,',
    'originconfederation': '#connector# #confed# and so, ',
    'originrevolution': ['#violent#','#peaceful#'],
    'originconquest': ['The thirst for new lands, new glory, and the desire to distract the people, led to new conquests','Sometimes, a people covet the wealth of their neighbours. And so','For honour, or for shame, I know not which - but the #ruler# sent the warriors to work. Thus'],
    'violent': ['#time#, the #problem# of the people could bear it no longer, and they rose up in violent revolution','Mistakes, blunders, and craven foolishness combined, and the whole edifice collapsed.','Whispers and rumors did the work of assassins, and the #ruler# could not control the people.'],
    'peaceful': ['#time#, the #ruler# gave up power and fled into exile'],
    'partition': ['#time#, class struggle tore the #strength# consensus apart','low cunning and high treachery divided them','#climatedisaster# weakened them all'],
    'confed': ['with a common enemy in view, they joined in alliance','#climatedisaster# weakened them all']
}

grammar = tracery.Grammar(rules)
grammar.add_modifiers(base_english)

# Names is a newline separated list of nation names.
file = "names.txt"
names = open(file, "r").read().split("\n") 
history = []
dot = False
if len(sys.argv) > 1 and sys.argv[1] == "--dot":
  dot = True

def wrap(str, wrap='"'):
  return wrap+str+wrap

def merge(states, names):
  number = random.randint(2,3)
  mergers = [] 
  if number < len(states):
    mergers = random.sample(states, number)
    new_name = random.choice(names)
    states = list(set(states).difference(set(mergers)))
    states.append(new_name)
    names.remove(new_name)
    if dot:
      for state in mergers:
        print '"%s" -> "%s" [label="confederation "]'%(state, new_name)
      print '{rank=same; %s }'%wrap(new_name)
    else:
      print grammar.flatten("#originconfederation#")
      print " %s became '%s'"%( " and ".join(map(wrap,mergers)), new_name)
  return states, names 


def split(states, names):
  number = random.randint(2,3)
  if number < len(names):
    splitter = random.choice(states)
    states.remove(splitter)
    new_states = random.sample(names, number)
    names = list(set(names).difference(set(new_states)))
    states = list(set(states).union(set(new_states)))
    if dot:
      for state in new_states:
        print '"%s" -> "%s" [label="partition "]'%(splitter, state)
      print '{rank=same; %s }'%("; ".join(map(wrap, new_states)))
    else:
      print grammar.flatten("#originpartition#")
      print " '%s' dissolved in fragments, eventually becoming %s"%(splitter, " and ".join(map(wrap,new_states)))
  return states, names

def revolt(states, names):
  old = random.choice(states)
  new = random.choice(names)
  names.remove(new)
  states.remove(old)
  states.append(new)
  if dot:
    print '"%s" -> "%s" [label="revolution "]'%(old, new)
    print '{rank=same; "%s"}'%new
  else:
    print grammar.flatten("#originrevolution#")
    print "The old '%s' was no more; a new dawn broke on '%s'"%(old, new)
  return states, names

def conquest(states, names):
  if len(states) > 1:
    loser = random.choice(states)
    states.remove(loser)
    winner = random.choice(states)
    if dot:
      print '"%s" -> "%s" [label="conquered by"]'%(loser, winner)
    else:
      print grammar.flatten("#originconquest#")
      print " '%s' conquered '%s'"%(winner, loser)
  return states, names


#ignore empty names
names = [name for name in names if name] #yes, really.

origin = random.sample(names, random.randint(1,3))
names = list(set(names).difference(set(origin)))
history.append(origin) #random starting states

if dot:
  print "digraph g {"
  print "{rank=same; %s}"%("; ".join(map(wrap,origin)))
else:
  print("Gather by, young ones, and let me tell you of our nations and peoples. \n In the beginning there was %s"%(" and ".join(map(wrap,history[0]))))
  print grammar.flatten("#beginning#")

while names:
  func = random.choice([merge, split, revolt, conquest, merge, split, revolt, revolt, conquest])
  states, names = func(history[-1], names)
  history.append(states)

if dot:
  print '{rank=same; %s}'%("; ".join(map(wrap,history[-1])))
  print "}"
else:
  print "Standing proud upon the ruins there are only now %s"%("and ".join(map(wrap,history[-1])))
