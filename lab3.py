# MIT 6.034 Lab 3: Constraint Satisfaction Problems
# Written by 6.034 staff

from constraint_api import *
from test_problems import get_pokemon_problem


#### Part 1: Warmup ############################################################

def has_empty_domains(csp) :
    """Returns True if the problem has one or more empty domains, otherwise False"""
    if len(csp.variables)==0: return False
    allDoms = [csp.get_domain(v) for v in csp.get_all_variables()]
    for v in allDoms:
        if len(v)==0:
            return True
    return False


def check_all_constraints(csp) :
    """Return False if the problem's assigned values violate some constraint,
    otherwise True"""
    #get list of all constraint objects and name it listOfConstraints
    listOfConstraints = csp.get_all_constraints()
    #get dict of assigned vars
    assigned = csp.assignments
    #for each constraint in listOfConstraints, if Constraint.var1 is in assignemntsDict,
    #then check if var2 is in the dictionary entry for the key con.var1
    for con in listOfConstraints:
        val1 = con.var1
        val2 = con.var2
        if val1 in assigned and val2 in assigned:
            if con.check(assigned[val1], assigned[val2]) == False:
                return False
    return True
#### Part 2: Depth-First Constraint Solver #####################################

def solve_constraint_dfs(problem) :
    """
    Solves the problem using depth-first search.  Returns a tuple containing:
    1. the solution (a dictionary mapping variables to assigned values)
    2. the number of extensions made (the number of problems popped off the agenda).
    If no solution was found, return None as the first element of the tuple.
    """
    #Initialize your agenda and the extension count.
    agenda = [problem]
    extensions=0
    #Until the agenda is empty, pop the first problem off the list and increment the extension count.
    while len(agenda)!=0:
        currentProb = agenda.pop(0)
        extensions+=1


#If any variable's domain is empty or if any constraints are violated,
#the problem is unsolvable with the current assignments.
        #(only enter this block if zero constraints are violated)
        if check_all_constraints(currentProb):
        #Take top unassigned variable off list using currentProb.pop_next_unassigned_var()
            unassigned = currentProb.unassigned_vars

            #if problem has no unassigned vars (as in all its vars are assigned) then youve found a solution!
            if len(unassigned)==0: return(currentProb.assignments, extensions)

            #only gets to this block if currentProb has unassigned variables
            nextUnassigned = currentProb.pop_next_unassigned_var()
            nextDomain = currentProb.get_domain(nextUnassigned)
            if nextDomain!=None:
                newProbs = []
                for val in nextDomain:
                    copyP = currentProb.copy()
                    newP = copyP.set_assignment(nextUnassigned, val)
                    newProbs.append(newP)
                agenda= newProbs+agenda
#if cannot find solution once agenda has run dry
    return (None, extensions)


# QUESTION 1: How many extensions does it take to solve the Pokemon problem
#    with DFS?

# Hint: Use get_pokemon_problem() to get a new copy of the Pokemon problem
#    each time you want to solve it with a different search method.

ANSWER_1 = 20


#### Part 3: Forward Checking ##################################################

def eliminate_from_neighbors(csp, var) :
    """
    Eliminates incompatible values from var's neighbors' domains, modifying
    the original csp.  Returns an alphabetically sorted list of the neighboring
    variables whose domains were reduced, with each variable appearing at most
    once.  If no domains were reduced, returns empty list.
    If a domain is reduced to size 0, quits immediately and returns None.
    """
    varsReduced = []
    domainOfVar = csp.get_domain(var)
    allVars = csp.get_all_variables()
    if len(domainOfVar) > 1:
        #var still has multiple options so we dont have to reduce the domain of any neibhors
        return varsReduced
    elif len(domainOfVar)==0:
        return None
    else:
        #for each other var in all the variables
        for otherVar in allVars:
            # examine what constrainst exist between the var and every otherVar
            for constraint in csp.constraints_between(var, otherVar):
                #for val in otherVar's domain
                otherDomains = csp.get_domain(otherVar)[:]
                for other in otherDomains:
                    #if theres a constraint between otherVar and our var, remove that val from the otherVal's domain.
                    if not constraint.check(domainOfVar[0], other):
                        csp.eliminate(otherVar, other)
                        #if the other var runs out of domain values, then no solution either
                        if len(csp.get_domain(otherVar)) == 0:
                            return None
                        #otherwise, add this otherVar to the list of reduced vars
                        varsReduced.append(otherVar)

    listToReturn = list(set(varsReduced))
    theListToReturn = sorted(listToReturn)
    return theListToReturn


# Because names give us power over things (you're free to use this alias)
forward_check = eliminate_from_neighbors

def solve_constraint_forward_checking(problem) :
    """
    Solves the problem using depth-first search with forward checking.
    Same return type as solve_constraint_dfs.
    """
    solution=None
    if has_empty_domains(problem):
        return (solution, 1)
    agenda = [problem]
    extensions = 0
    while len(agenda) > 0:
        currentProb = agenda.pop(0)
        extensions += 1
        if not has_empty_domains(currentProb) and check_all_constraints(currentProb):
            unassignedVars = currentProb.pop_next_unassigned_var()
            #if no more unassigned vars, then we found a solution
            if unassignedVars == None:
                return (currentProb.assignments,extensions)
            newProbs = []
            for val in currentProb.get_domain(unassignedVars):
                copyP = currentProb.copy()
                cp = copyP.set_assignment(unassignedVars,val)
                forward_check(cp,unassignedVars)
                newProbs.append(cp)
            newProbs = newProbs + agenda
            agenda = newProbs
    #if unsolveable
    return (None,extensions)




# QUESTION 2: How many extensions does it take to solve the Pokemon problem
#    with DFS and forward checking?

ANSWER_2 = 9


#### Part 4: Domain Reduction ##################################################

def domain_reduction(csp, queue=None) :
    """
    Uses constraints to reduce domains, propagating the domain reduction
    to all neighbors whose domains are reduced during the process.
    If queue is None, initializes propagation queue by adding all variables in
    their default order.
    Returns a list of all variables that were dequeued, in the order they
    were removed from the queue.  Variables may appear in the list multiple times.
    If a domain is reduced to size 0, quits immediately and returns None.
    This function modifies the original csp.
    """
    #Establish a queue.
    #before search (and when no queue is None), initialize propogation by adding
    #all the problem's variables to the queue using csp.get_all_variables()
    if queue == None:
        queue = csp.get_all_variables()[:]
    dequeued = []

    #while queue still has unassigned vars, pop the first variable off the queue
    while len(queue) > 0:
        # Pop off the first variabled
        currentVar = queue.pop(0)
        dequeued.append(currentVar)
        currentDomain = csp.get_domain(currentVar)

        #for each other node, check for constraints between current node and all others
        for otherVar in csp.get_all_variables():#does it matter that they're not sorted lexically as they would be in csp.variables?
            for constraint in csp.constraints_between(currentVar, otherVar):
                    # for loop through domain of other
        # go through all values in otherVar's domain
                otherDomain = csp.get_domain(otherVar)[:]
                lenOtherDomain= len(otherDomain)
                for otherVal in otherDomain:

                    lenOfCurrentDomain = len(currentDomain)
                    numOfConstraints = 0

                    for currentVal in csp.get_domain(currentVar):
                        if constraint.check(currentVal, otherVal):
                            pass
                        else:
                            numOfConstraints += 1
                    if numOfConstraints == lenOfCurrentDomain:
                        csp.eliminate(otherVar, otherVal)


                        if len(csp.get_domain(otherVar)) == 0:
                            #unsolvable if otherDomain is empty
                            return None

                        # Add to the queue if not there
                        if not otherVar in queue:
                            if len(csp.get_domain(otherVar)) == 1:
                                queue.append(otherVar)

    return dequeued








# QUESTION 3: How many extensions does it take to solve the Pokemon problem
#    with DFS (no forward checking) if you do domain reduction before solving it?

ANSWER_3 = 6


def solve_constraint_propagate_reduced_domains(problem) :
    """
    Solves the problem using depth-first search with forward checking and
    propagation through all reduced domains.  Same return type as
    solve_constraint_dfs.
    """
    #if the problem has empty domains, then it is unsolveable
    if has_empty_domains(problem):
        return (None, 1)
    extens = 0
    agenda = [problem]
    while len(agenda) != 0:
        prob = agenda.pop(0)
        extens += 1
        if not has_empty_domains(prob) and check_all_constraints(prob):
            unassigned = prob.pop_next_unassigned_var()
            if unassigned == None:
                return (prob.assignments,extens)
            copy = []
            for value in prob.get_domain(unassigned):
                copyProb = prob.copy().set_assignment(unassigned,value)
                domain_reduction(copyProb,[unassigned])
                copy.append(copyProb)
            copy = copy + agenda
            agenda = copy
    return (None,extens)


# QUESTION 4: How many extensions does it take to solve the Pokemon problem
#    with forward checking and propagation through reduced domains?

ANSWER_4 = 7


#### Part 5A: Generic Domain Reduction #########################################

def propagate(enqueue_condition_fn, csp, queue=None) :
    """
    Uses constraints to reduce domains, modifying the original csp.
    Uses enqueue_condition_fn to determine whether to enqueue a variable whose
    domain has been reduced. Same return type as domain_reduction.
    """
    if queue == None:
        queue = csp.get_all_variables()
    dequeued = []
    while len(queue) > 0:
        currentVar = queue.pop(0)
        checkAhead = forward_check(csp,currentVar)
        if checkAhead == None:
            return None
        for var in checkAhead:
            if enqueue_condition_fn(csp,var):
                queue.append(var)
        dequeued.append(currentVar)
    return dequeued

def condition_domain_reduction(csp, var) :
    """Returns True if var should be enqueued under the all-reduced-domains
    condition, otherwise False"""
    return True

def condition_singleton(csp, var) :
    """Returns True if var should be enqueued under the singleton-domains
    condition, otherwise False"""
    if len(csp.get_domain(var)) == 1:
        return True
    else:
        return False

def condition_forward_checking(csp, var) :
    """Returns True if var should be enqueued under the forward-checking
    condition, otherwise False"""
    return False


#### Part 5B: Generic Constraint Solver ########################################

def solve_constraint_generic(problem, enqueue_condition=None) :
    """
    Solves the problem, calling propagate with the specified enqueue
    condition (a function). If enqueue_condition is None, uses DFS only.
    Same return type as solve_constraint_dfs.
    """
    if has_empty_domains(problem):
        return (None, 1)
    extens = 0
    agenda = [problem]
    while len(agenda) > 0:
        prob = agenda.pop(0)
        extens += 1
        if not has_empty_domains(prob) and check_all_constraints(prob):
            unassigned = prob.pop_next_unassigned_var()
            if unassigned == None:
                return (prob.assignments,extens)
            copy = []
            for val in prob.get_domain(unassigned):
                csp = prob.copy().set_assignment(unassigned,val)
                if enqueue_condition != None:
                    propagate(enqueue_condition, csp,[unassigned])
                copy.append(csp)
            copy = copy + agenda
            agenda = copy
    return (None,extens)



# QUESTION 5: How many extensions does it take to solve the Pokemon problem
#    with forward checking and propagation through singleton domains? (Don't
#    use domain reduction before solving it.)

ANSWER_5 = 8


#### Part 6: Defining Custom Constraints #######################################

def constraint_adjacent(m, n) :
    """Returns True if m and n are adjacent, otherwise False.
    Assume m and n are ints."""
    if abs(m-n) == 1:
        return True
    else:
        return False

def constraint_not_adjacent(m, n) :
    """Returns True if m and n are NOT adjacent, otherwise False.
    Assume m and n are ints."""
    return not constraint_adjacent(m, n)

def all_different(variables) :
    """Returns a list of constraints, with one difference constraint between
    each pair of variables."""
    constraints = []
    numVars = len(variables)-1
    for i in range(numVars):
        for j in range(numVars-i):
            constraints.append(Constraint(variables[i],variables[i+j+1],constraint_different))
    return constraints


#### SURVEY ####################################################################

NAME = "Skylar Kolisko"
COLLABORATORS = None
HOW_MANY_HOURS_THIS_LAB_TOOK = 8
WHAT_I_FOUND_INTERESTING = "All"
WHAT_I_FOUND_BORING = "None"
SUGGESTIONS = None
