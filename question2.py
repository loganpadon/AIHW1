import operator
import sys
from aima3.utils import (
    is_in, memoize, PriorityQueue
)
infinity = float('inf')


class Problem(object):
    """The abstract class for a formal problem. You should subclass
    this and implement the methods actions and result, and possibly
    __init__, goal_test, and path_cost. Then you will create instances
    of your subclass and solve them with the various search functions."""

    def __init__(self, initial, goal=None):
        """The constructor specifies the initial state, and possibly a goal
        state, if there is a unique goal. Your subclass's constructor can add
        other arguments."""
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        raise NotImplementedError

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        raise NotImplementedError

    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""
        if isinstance(self.goal, list):
            return is_in(state, self.goal)
        else:
            return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        return c + 1

    def value(self, state):
        """For optimization problems, each state has a value. Hill-climbing
        and related algorithms try to maximize this value."""
        raise NotImplementedError

class MissionaryAndCannibals(Problem):
    """ Three missionaries and three cannibals are on one side of the river, along with a boat that can
     hold one or two people. A state is represented as a tuple of length 3 which describes number of missionaries
     on the wrong side, number of missionaries on the wrong side and the side boat is on."""

    def __init__(self, initial=(3,3,1), goal=(0,0,0)):
        """ Define goal state and initialize a problem """

        self.goal = goal
        self.initial = initial
        Problem.__init__(self, initial, goal)

    def find_direction(self, state):
        """Return the index of the blank square in a given state"""
        return state[2]

    def actions(self, state):
        """ Return the actions that can be executed in the given state.
        The result would be a list of tuples."""
        possible_actions = []

        positive_actions = [(1,0,1),(2,0,1),(0,1,1),(0,2,1),(1,1,1)]
        negative_actions = [(-1,0,-1),(-2,0,-1),(0,-1,-1),(0,-2,-1),(-1,-1,-1)]
        dir_to_go = self.find_direction(state)

        if dir_to_go == 1:
            possible_actions = negative_actions
            if state[0] == 0:
                possible_actions.remove((-1,0,-1))
                possible_actions.remove((-2,0,-1))
                possible_actions.remove((-1,-1,-1))
            if state[1] == 0:
                possible_actions.remove((0,-1,-1))
                possible_actions.remove((0,-2,-1))
                possible_actions.remove((-1,-1,-1))
            if state[0] == 1:
                possible_actions.remove((-2,0,-1))
            if state[1] == 1:
                possible_actions.remove((0,-2,-1))
        else:
            possible_actions = positive_actions
            if state[0] == 3:
                possible_actions.remove((1,0,1))
                possible_actions.remove((2,0,1))
                possible_actions.remove((1,1,1))
            if state[1] == 3:
                possible_actions.remove((0,1,1))
                possible_actions.remove((0,2,1))
                possible_actions.remove((1,1,1))
            if state[0] == 2:
                possible_actions.remove((2,0,1))
            if state[1] == 2:
                possible_actions.remove((0,2,1))
        p = possible_actions.copy()
        for i in p:
            new_state =tuple(map(operator.add, state, i))
            if (new_state[0] < new_state[1]):
                possible_actions.remove(i)
        return possible_actions

    def result(self, state, action):
        """ Given state and action, return a new state that is the result of the action.
        Action is assumed to be a valid action in the state """
        new_state =tuple(map(operator.add, state, action))
        return new_state

    def goal_test(self, state):
        """ Given a state, return True if state is a goal state or False, otherwise """
        return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        return c + 1

    def h(self, node):
        """ Return the heuristic value for a given state. Default heuristic function used is 
        h(n) = number of people on initital side -1 """
        return (node.state[0] + node.state[1])/2

class Node:
    """A node in a search tree. Contains a pointer to the parent (the node
    that this is a successor of) and to the actual state for this node. Note
    that if a state is arrived at by two paths, then there are two nodes with
    the same state.  Also includes the action that got us to this state, and
    the total path_cost (also known as g) to reach the node.  Other functions
    may add an f and h value; see best_first_graph_search and astar_search for
    an explanation of how the f and h values are handled. You will not need to
    subclass this class."""

    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Create a search tree Node, derived from a parent by an action."""
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, problem):
        """List the nodes reachable in one step from this node."""
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        """[Figure 3.10]"""
        next_state = problem.result(self.state, action)
        next_node = Node(next_state, self, action,
                         problem.path_cost(self.path_cost, self.state,
                                           action, next_state))
        return next_node

    def solution(self):
        """Return the sequence of actions to go from the root to this node."""
        return [node.action for node in self.path()[1:]]

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    # We want for a queue of nodes in breadth_first_graph_search or
    # astar_search to have no duplicated states, so we treat nodes
    # with the same state as equal. [Problem: this may not be what you
    # want in other contexts.]

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)

def best_first_graph_search(problem, f):
    """Search the nodes with the lowest f scores first.
    You specify the function f(node) that you want to minimize; for example,
    if f is a heuristic estimate to the goal, then we have greedy best
    first search; if f is node.depth then we have breadth-first search.
    There is a subtlety: the line "f = memoize(f, 'f')" means that the f
    values will be cached on the nodes as they are computed. So after doing
    a best first search you can examine the f values of the path returned."""
    f = memoize(f, 'f')
    node = Node(problem.initial)
    frontier = PriorityQueue('min', f)
    frontier.append(node)
    explored = set()

    while frontier:
        node = frontier.pop()
        print("Current Node")
        print(node.state)
        if problem.goal_test(node.state):
            return node
        explored.add(node.state)
        for child in node.expand(problem):
            if child.state not in explored and child not in frontier:
                frontier.append(child)
            elif child in frontier:
                if f(child) < f(frontier[child]):
                    del frontier[child]
                    frontier.append(child)
        print("Explored")
        print(explored)
        frontierS = set()
        for i in range(len(frontier)):
            frontierS.add(frontier.A[i][1])
        print("Frontier")
        print(frontierS)
    return None

def recursive_best_first_search(problem, h=None):
    """[Figure 3.26]"""
    h = memoize(h or problem.h, 'h')

    def RBFS(problem, node, flimit, path):
        print(node.state)
        if problem.goal_test(node.state):
            path.add(node)
            return node, 0  # (The second value is immaterial)
        successors = node.expand(problem)
        if len(successors) == 0:
            return None, infinity
        for s in successors:
            s.f = max(s.path_cost + h(s), node.f)
        while True:
            # Order by lowest f value
            successors.sort(key=lambda x: x.f)
            best = successors[0]
            if best.f > flimit:
                return None, best.f
            if len(successors) > 1:
                alternative = successors[1].f
            else:
                alternative = infinity
            path.add(node)
            result, best.f = RBFS(problem, best, min(flimit, alternative), path)
            if result is not None:
                return result, best.f

    node = Node(problem.initial)
    node.f = h(node)
    path = set()
    result, bestf = RBFS(problem, node, infinity, path)
    print("Path To Result")
    print(path)
    return result

def uniform_cost_search(problem):
    """[Figure 3.14]"""
    return best_first_graph_search(problem, lambda node: node.path_cost)

def depth_limited_search(problem, limit=50):
    """[Figure 3.17]"""

    def recursive_dls(node, problem, limit, explored):
        print("Current Node")
        print(node)

        if problem.goal_test(node.state):
            return node
        elif limit == 0:
            print("Explored")
            print(explored)
            explored.add(node)
            return 'cutoff'
        else:
            print("Explored")
            print(explored)
            explored.add(node)
            cutoff_occurred = False
            for child in node.expand(problem):
                result = recursive_dls(child, problem, limit - 1, explored)
                if result == 'cutoff':
                    cutoff_occurred = True
                elif result is not None:
                    return result
            return 'cutoff' if cutoff_occurred else None

    # Body of depth_limited_search:
    explored = set()
    return recursive_dls(Node(problem.initial), problem, limit, explored)

def iterative_deepening_search(problem):
    """[Figure 3.18]"""
    for depth in range(sys.maxsize):
        result = depth_limited_search(problem, depth)
        if result != 'cutoff':
            return result

def astar_search(problem, h=None):
    """A* search is best-first graph search with f(n) = g(n)+h(n).
    You need to specify the h function when you call astar_search, or
    else in your Problem subclass."""
    h = memoize(h or problem.h, 'h')
    return best_first_graph_search(problem, lambda n: n.path_cost + h(n))

missandcan = MissionaryAndCannibals((3,3,1),(0,0,0))

print("Uniform Cost Search")
uniform_cost_search(missandcan)
print("")
print("Iterative Deepening Search")
iterative_deepening_search(missandcan)
print("")
print("Greedy Best-First Search")
best_first_graph_search(missandcan, lambda node: (node.state[0] + node.state[1])/2)
print("")
print("A* Search")
astar_search(missandcan)
print("")
print("Recursive Best-First Search")
recursive_best_first_search(missandcan)