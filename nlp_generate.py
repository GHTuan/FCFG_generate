import nltk, copy, itertools, sys
from nltk.grammar import Nonterminal

# Go through all feature values of all nodes in a list of nodes.
# Return a mapping from distinct variable names to 'slots'.
# The slots are empty lists into which values can later be inserted.
def get_nodelist_variable_map(nodelist):
    varmap = {}
    for node in nodelist:
      if type(node)==str: continue
      for feature in node:
        if type(node[feature]) == nltk.sem.logic.Variable:
          varmap[node[feature].name] = []
    return varmap

## Copy nodelist and replace all variables with slots
## Instances of the same variable will get the same slot value.
def nodelist_replace_variables(nodelist):
    nodelist = copy.deepcopy(nodelist)
    varmap = get_nodelist_variable_map(nodelist)
    for node in nodelist:
      if type(node)==str: continue
      for feature in node:
          if type(node[feature]) == nltk.sem.logic.Variable:
              node[feature] = varmap[node[feature].name]
    return nodelist

## Copy a node, replacing Variable feature values with 'slots'
def replace_node_vars(node):
  if type(node)==str: return node  # quick return for terminals
  ## Otherwise just do it as a nodelist with one element
  return nodelist_replace_variables([node])[0]

## Copy a production rule, replacing Variable feature values with 'slots'
def replace_production_vars(prod):
  ## Turn the rule into a node list
  nodes = [prod.lhs()] + list(prod.rhs())
  nodes = nodelist_replace_variables(nodes)
  ## Turn the result back into a production rule
  return nltk.Production(nodes[0], nodes[1:])

## Unpack nested slots untill you get either empty list (variable slot)
## Or you get a value (the slot variable has been instantiated)
## If v is not a slot you just get back v.
def unslot(v):
  while type(v)== list:
    if v == []: return v # return the slot           
    v = v[0]             # unpack list
  return v               # return any non-list value

def unify_values(v1, v2):
      v1 = unslot(v1)
      v2 = unslot(v2)
      # Case of both str values
      if type(v1)==str and type(v2)==str:
        return v1 == v2
      # Cases of one str and one slot (variable) feature value
      # Insert the str into the slot.
      if  type(v1)==str:
            v2.insert(0,v1)
            return "Right"
      elif type(v2)==str:
            v1.insert(0,v2)
            return "Left"
      else:
          # Remaining case: both are slots
          slot = []   # Bind by adding new slot within each of them:
          v1.insert(0, slot)
          v2.insert(0, slot)
          return "Both"
      return True

def unify_nodes( n1, n2,checkOnly = True ):
    r = []
    for feature in n1:
        if feature in n2:
            uv = unify_values( n1[feature], n2[feature] )
            if not uv:
                # Un unify node that have been unify
                un_unify_nodes(n1,n2,r)
                return False
            else:
                r += [[{'node':n1,'feature':feature},{'node':n2,'feature':feature},uv]] 
    if checkOnly: 
      return True      
    else: 
      return r
  
def pop_last_slot(n , feature):
  temp = n[feature]
  while type(temp) == list:
    if type(temp[0]) == list:
      temp = temp[0]
      continue
    temp.pop()
    return

def pop_deepest_slot(n,feature):
  current = n[feature]
  while isinstance(current[0], list) and len(current[0]) > 0:
    if isinstance(current[0][0], list) and len(current[0][0]) == 0:
      current.pop()  # Remove the deepest empty list
      break
    current = current[0]
  return

def un_unify_nodes(n1,n2,feature_list):
    # item: left node, right node, unify_pos
    for item in feature_list:
      if item[2] == "Left":


        pop_last_slot(n1,item[0]['feature'])
      elif item[2] == "Right":

        pop_last_slot(n2,item[1]['feature'])
      elif item[2] == "Both":
        # print("Both",n1,n2)
        # pop_deepest_slot(n1,item[1]['feature'])
        # pop_deepest_slot(n2,item[1]['feature'])  
        pass
    return

def node_type(node):
  return list(node.items())[0][1] # is there an easier way??



def fcfg_generate(grammar, node=None, depth=None, debug=False, n = 1):
    def dbprint(*args):
      if debug: print(*args)

    if node == None:
      node = grammar.start()
      node = replace_node_vars(node)
    dbprint("***DEPTH:", depth)
    dbprint("* Generating from node:\n", node)
    dbprint("--- end of node ---")
    
    if depth is None:
            # Safe default, assuming the grammar may be recursive:
        depth = (sys.getrecursionlimit() // 3) - 3

    iter = _generate_all(grammar, [node], depth,debug=debug)
    dbprint("iter: ",iter)
    
    if n:
        iter = itertools.islice(iter, n)
    return iter
  
def _generate_all(grammar, items=None, depth=0, debug=False):
  def dbprint(*args):
    if debug: print(*args)
    
  # dbprint("generating items:", items)
  if items:
    try:
      for frag1 in _generate_one(grammar = grammar, item = items[0], depth=depth,debug = debug):
        for frag2 in _generate_all(grammar, items[1:], depth,debug = debug):
          yield frag1 + frag2
    except RecursionError as error:
      raise RuntimeError("The grammar has rule(s) that yield infinite recursion!\n\
Eventually use a lower 'depth', or a higher 'sys.setrecursionlimit()'."
            ) from error
  else:   
    yield []

  
def _generate_one(grammar, res=[], item=None,depth=0,debug=False):
    def dbprint(*args):
      if debug: print(*args)
    
    # dbprint(item)
    if depth > 0:
        if isinstance(item, Nonterminal):
            # dbprint("item is a nonterminal")
            rule_options = grammar.productions(lhs=item)
            if debug:
              print("Rule options:")
              for r in rule_options:
                print(r)
            for rule in rule_options:
              dbprint("Checking rule:",rule)
              rule = replace_production_vars(rule) # gives a copy with var slots added
              uv =True
              if uv:  # It's a Match!
                checkList = unify_nodes(item, rule.lhs(),checkOnly=False)
                if checkList == False:
                  dbprint("Fail CheckList:",checkList)
                  continue
                for i in _generate_all(grammar, rule.rhs(), depth - 1,debug=debug):
                    yield i
                dbprint("Checklist: ",checkList, item, rule)
                un_unify_nodes(item, rule.lhs() ,checkList)

                # un_unify_nodes(node_copy, rule_head, uv)
                # dbprint("After ChooseRule:",rule, "with", node_copy, rule_head)
              else:
                dbprint("Not choosing rule", rule, "with,", item)
        else:
            yield [item]
    

def fcfg_from_string( string ):
    return nltk.grammar.FeatureGrammar.fromstring(string)

def show_all_sentence(grammar,
                        node=None, # start node
                        n=1,       # number of sentences
                        debug=False):
    if type(grammar) == str:
      grammar = fcfg_from_string( grammar )
    structures = list(fcfg_generate(grammar, node=node, debug=debug,n = n))
    for structure in structures:
      print("structure:", structure)