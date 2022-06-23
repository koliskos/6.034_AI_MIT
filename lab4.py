# MIT 6.034 Lab 4: Rule-Based Systems
# Written by 6.034 staff

from production import IF, AND, OR, NOT, THEN, DELETE, forward_chain, pretty_goal_tree
from data import *
import pprint

pp = pprint.PrettyPrinter(indent=1)
pprint = pp.pprint

#### Part 1: Multiple Choice #########################################

ANSWER_1 = '2'

ANSWER_2 = '4'#in backward chaining, no new assertions are added

ANSWER_3 = '2' #to match means that ALL antecendents must match

ANSWER_4 = '0'

ANSWER_5 = '3'

ANSWER_6 = '1'

ANSWER_7 = '0'#since firing neither rules at this point will produce a new assertion

#### Part 2: Transitive Rule #########################################

# Fill this in with your rule
#ransitive_rule = IF( AND('(?2) beats (?1)', '(?3) beats (?2)'), THEN('(?3) beats (?1)'))
transitive_rule = IF( AND('(?x) beats (?y)', '(?z) beats (?x)'), THEN('(?z) beats (?y)'))

# You can test your rule by uncommenting these pretty print statements
#  and observing the results printed to your screen after executing lab1.py
# pprint(forward_chain([transitive_rule], abc_data))
# pprint(forward_chain([transitive_rule], poker_data))
# pprint(forward_chain([transitive_rule], minecraft_data))


#### Part 3: Family Relations #########################################

# Define your rules here. We've given you an example rule whose lead you can follow:
friend = IF( AND("person (?x)", "person (?y)"), THEN ("friend (?x) (?y)", "friend (?y) (?x)") )
same_person = IF ( 'parent (?y) (?x)', THEN ('same_person (?x) (?x)') )
sibling = IF ( AND('parent (?a) (?x)', 'parent (?a) (?y)', NOT('same_person (?x) (?y)')), THEN('sibling (?x) (?y)', 'sibling (?y) (?x)') )

child = IF('parent (?x) (?y)', THEN('child (?y) (?x)'))
cousin = IF( AND('parent (?p) (?x)', 'parent (?q) (?y)', 'sibling (?p) (?q)'), THEN('cousin (?x) (?y)', 'cousin (?y) (?x)'))
grandparent = IF( AND('parent (?x) (?y)', 'parent (?y) (?z)'), THEN( 'grandparent (?x) (?z)'))
grandchild = IF( AND('parent (?x) (?y)', 'parent (?y) (?z)'), THEN( 'grandchild (?z) (?x)'))


# Add your rules to this list:
family_rules = [ same_person, sibling, child, cousin, grandparent, grandchild ]


# Uncomment this to test your data on the Simpsons family:
# pprint(forward_chain(family_rules, simpsons_data, verbose=False))

# These smaller datasets might be helpful for debugging:
# pprint(forward_chain(family_rules, sibling_test_data, verbose=True))
# pprint(forward_chain(family_rules, grandparent_test_data, verbose=True))

# The following should generate 14 cousin relationships, representing 7 pairs
# of people who are cousins:
# harry_potter_family_cousins = [
#     relation for relation in
#     forward_chain(family_rules, harry_potter_family_data, verbose=False)
#     if "cousin" in relation ]

# To see if you found them all, uncomment this line:
# pprint(harry_potter_family_cousins)


#### Part 4: Backward Chaining #########################################

# Import additional methods for backchaining
from production import PASS, FAIL, match, populate, simplify, variables

def backchain_to_goal_tree(rules, hypothesis):
    """
    Takes a hypothesis (string) and a list of rules (list
    of IF objects), returning an AND/OR tree representing the
    backchain of possible statements we may need to test
    to determine if this hypothesis is reachable or not.

    This method should return an AND/OR tree, that is, an
    AND or OR object, whose constituents are the subgoals that
    need to be tested. The leaves of this tree should be strings
    (possibly with unbound variables), *not* AND or OR objects.
    Make sure to use simplify(...) to flatten trees where appropriate.
    """

    allPossibleStatements = [hypothesis]
    for rule in rules:
      setOfBindings = match(rule.consequent(), hypothesis)
      if setOfBindings != None:
        possibleStatements = []

        if isinstance(rule.antecedent(), AND) or isinstance(rule.antecedent(), OR):
          for statement in rule.antecedent():
            possibleStatements.append(backchain_to_goal_tree(rules, populate(statement, setOfBindings)))
        else:
          possibleStatements.append(backchain_to_goal_tree(rules, populate(rule.antecedent(), setOfBindings)))


        if isinstance(rule.antecedent(), AND):
          allPossibleStatements.append( AND(possibleStatements))
        else:
          allPossibleStatements.append( OR(possibleStatements))

    return simplify( OR(allPossibleStatements))


# Uncomment this to test out your backward chainer:
# pretty_goal_tree(backchain_to_goal_tree(zookeeper_rules, 'opus is a penguin'))


#### Survey #########################################

NAME = 'Skylar Kolisko'
COLLABORATORS = None
HOW_MANY_HOURS_THIS_LAB_TOOK = 5
WHAT_I_FOUND_INTERESTING = 'All'
WHAT_I_FOUND_BORING = 'None'
SUGGESTIONS = None


###########################################################
### Ignore everything below this line; for testing only ###
###########################################################

# The following lines are used in the tester. DO NOT CHANGE!
print("(Doing forward chaining. This may take a minute.)")
transitive_rule_poker = forward_chain([transitive_rule], poker_data)
transitive_rule_abc = forward_chain([transitive_rule], abc_data)
transitive_rule_minecraft = forward_chain([transitive_rule], minecraft_data)
family_rules_simpsons = forward_chain(family_rules, simpsons_data)
family_rules_harry_potter_family = forward_chain(family_rules, harry_potter_family_data)
family_rules_sibling = forward_chain(family_rules, sibling_test_data)
family_rules_grandparent = forward_chain(family_rules, grandparent_test_data)
family_rules_anonymous_family = forward_chain(family_rules, anonymous_family_test_data)
family_rules_black = forward_chain(family_rules, black_data)
