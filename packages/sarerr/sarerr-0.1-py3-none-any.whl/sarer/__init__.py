def sfb():
    print("""
from queue import PriorityQueue
def bestFirstSearch(source, target, n):
  visited = [False] * n 
  pq = PriorityQueue()
  pq.put((0, source))
  while pq.empty() == False:
    u = pq.get()[1]
    print(u, end=" ")
    if u == target:
      break
    for v, c in graph[u]:
      if visited[v] == False:
         visited[0] = True
         pq.put((c, v))
    print()
def addedge(x, y, cost):
 graph[x].append((y, cost))
 graph[y].append((x, cost))
v = 14
graph = [[] for i in range(v)]
addedge(0, 1, 3)
addedge(0, 2, 6)
addedge(0, 3, 5)
addedge(1, 4, 9)
addedge(1, 5, 8)
addedge(2, 6, 12)
addedge(2, 7, 14)
addedge(3, 8, 7)
addedge(8, 9, 5)
addedge(8, 10, 6)
addedge(9, 11, 1)
addedge(9, 12, 10)
addedge(9, 13, 2)
source = 0
target = 9
print("The Best First Serach Path from Node",source, "to",target,"is: ")
bestFirstSearch(source, target, v)
""")
def sa():
    print("""
class Graph:
  def __init__(self, graph_dict=None, directed=True):
    self.graph_dict = graph_dict or {}
    self.directed = directed
    if not directed:
      self.make_undirected()
  def make_undirected(self):
    for a in list(self.graph_dict.keys()):
      for (b, dist) in self.graph_dict[a].items():
        self.graph_dict.setdefault(b, {})[a] = dist
  def connect(self, A, B, distance=1):
    self.graph_dict.setdefault(A, {})[B] = distance
    if not self.directed:
      self.graph_dict.setdefault(B, {})[A] = distance
  def get(self, a, b=None):
    links = self.graph_dict.setdefault(a, {})
    if b is None:
      return links
    else:
      return links.get(b)
  def nodes(self):
    s1 = set([k for k in self.graph_dict.keys()])
    s2 = set([k2 for v in self.graph_dict.values() for k2, v2 in v.items()])
    nodes = s1.union(s2)
    return list(nodes)
class Node:
  def __init__(self, name:str, parent:str):
    self.name = name
    self.parent = parent
    self.g = 0
    self.h = 0
    self.f = 0
  def __eq__(self, other):
    return self.name == other.name
  def __lt__(self, other):
    return self.f < other.f
  def __repr__(self):
    return ('({0},{1})'.format(self.name, self.f))
def astar_search(graph, heuristics, start, end):
  open = []
  closed = []
  start_node = Node(start, None)
  goal_node = Node(end, None)
  open.append(start_node)
  while len(open) > 0:
    open.sort()
    current_node = open.pop(0)
    closed.append(current_node)
    if current_node == goal_node:
      path = []
      while current_node != start_node:
        path.append(current_node.name + ': ' + str(current_node.g))
        current_node = current_node.parent
        path.append(start_node.name + ': ' + str(start_node.g))
        return path[::-1]
    neighbors = graph.get(current_node.name)
    for key, value in neighbors.items():
      neighbor = Node(key, current_node)
      if(neighbor in closed):
        continue
      neighbor.g = current_node.g + graph.get(current_node.name, neighbor.name)
      neighbor.h = heuristics.get(neighbor.name)
      neighbor.f = neighbor.g + neighbor.h
      if(add_to_open(open, neighbor) == True):
        open.append(neighbor)
  return None
def add_to_open(open, neighbor):
  for node in open:
    if (neighbor == node and neighbor.f > node.f):
      return False
  return True
graph = Graph()
graph.connect('Frankfurt', 'Wurzburg', 111)
graph.connect('Frankfurt', 'Mannheim', 85)
graph.connect('Wurzburg', 'Nurnberg', 104)
graph.connect('Wurzburg', 'Stuttgart', 140)
graph.connect('Wurzburg', 'Ulm', 183)
graph.connect('Mannheim', 'Nurnberg', 230)
graph.connect('Mannheim', 'Karlsruhe', 67)
graph.connect('Karlsruhe', 'Basel', 191)
graph.connect('Karlsruhe', 'Stuttgart', 64)
graph.connect('Nurnberg', 'Ulm', 171)
graph.connect('Nurnberg', 'Munchen', 170)
graph.connect('Nurnberg', 'Passau', 220)
graph.connect('Stuttgart', 'Ulm', 107)
graph.connect('Basel', 'Bern', 91)
graph.connect('Basel', 'Zurich', 85)
graph.connect('Bern', 'Zurich', 120)
graph.connect('Zurich', 'Memmingen', 184)
graph.connect('Memmingen', 'Ulm', 55)
graph.connect('Memmingen', 'Munchen', 115)
graph.connect('Munchen', 'Ulm', 123)
graph.connect('Munchen', 'Passau', 189)
graph.connect('Munchen', 'Rosenheim', 59)
graph.connect('Rosenheim', 'Salzburg', 81)
graph.connect('Passau', 'Linz', 102)
graph.connect('Salzburg', 'Linz', 126)
graph.make_undirected()
heuristics = {}
heuristics['Basel'] = 204
heuristics['Bern'] = 247
heuristics['Frankfurt'] = 215
heuristics['Karlsruhe'] = 137
heuristics['Linz'] = 318
heuristics['Mannheim'] = 164
heuristics['Munchen'] = 120
heuristics['Memmingen'] = 47
heuristics['Nurnberg'] = 132
heuristics['Passau'] = 257
heuristics['Rosenheim'] = 168
heuristics['Stuttgart'] = 75
heuristics['Salzburg'] = 236
heuristics['Wurzburg'] = 153
heuristics['Zurich'] = 157
heuristics['Ulm'] = 0
path = astar_search(graph, heuristics, 'Frankfurt', 'Ulm')
print("Path:", path)
""")