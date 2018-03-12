import sys
import subprocess
import pygraphviz as pgv

class Node:
    def __init__(self, ip='', time='', parent=''):
        self.ip = ip
        self.time = time
        self.parent = parent

    def __str__(self):
        if type(self.parent) == str:
            return 'ip: ' + str(self.ip) + '\ttime: ' + str(self.time) + '\tparent: root'
        else:
            return 'ip: ' + str(self.ip) + '\ttime: ' + str(self.time) + '\tparent: ' + str(self.parent.ip)


class VizRoute:
    def __init__(self):
        self.dump = ''
        self.nodes = []

    def getDump(self):
        if len(sys.argv) > 1:
            args = sys.argv[1:]
            self.dump = subprocess.check_output(["traceroute", *args])
        else:
            print('arguments have not been passed')

    def parseDump(self):
        self.dump = self.dump.decode('utf-8').split('\n')
        self.dump = [i.replace(' ms', 'ms') for i in self.dump if i.find('ms') != -1]
        for i, hop in enumerate(self.dump):
            self.dump[i] = [j for j in hop.split(' ') if j.find('ms') != -1 or j.find('(') != -1]

    def linkNodes(self):
        self.createNodes()
        for i, hop in enumerate(self.nodes):
            for j, node in enumerate(hop):
                if i != 0:
                    ind = 0
                    if j < len(self.nodes[i-1]):
                        ind = j
                    else:
                        ind = 0
                    hop[j].parent = self.nodes[i-1][ind]

    def createNodesFromLine(self, lst):
        nodes = []
        for i in range(len(lst)):
            if lst[i].find('(') != -1 and i == 0:
                node = Node(lst[i])
            elif lst[i].find('(') != -1 and i != 0:
                nodes.append(node)
                node = Node(lst[i])
            else:
                node.time += lst[i].replace('ms', '') + ', '
            if i == len(lst)-1:
                nodes.append(node)
        return nodes

    def createNodes(self):
        self.getDump()
        self.parseDump()
        for i in range(len(self.dump)):
            self.nodes.append(self.createNodesFromLine(self.dump[i]))

    def flatten(self, lst):
        return sum(([x] if not isinstance(x, list) else self.flatten(x)
                    for x in lst), [])

    def getLens(self):
        self.lens = []
        for n in self.nodes:
            length = float(n.time.split(' ')[0].replace(',', ''))
            self.lens.append(length)
        maxItem = max(self.lens)
        self.lens = [float(i)*4/maxItem + 1 for i in self.lens]

    def createNet(self):
        self.linkNodes()
        self.nodes = list(self.flatten(self.nodes))

    def buildGraph(self):
        self.createNet()
        self.getLens()
        g = pgv.AGraph()
        g.layout()
        g.add_node('root', label="You're here", color='red', style='filled', shape='polygon', sides=5, dir='back')
        for i, node in enumerate(self.nodes):
            if type(node.parent) != str:
                g.add_edge(node.ip, node.parent.ip, label=node.time+' ms', len=self.lens[i], dir='back',
                           color='blue', style='filled')
            else:
                g.add_edge(node.ip, 'root', label=node.time, len=self.lens[i], color='blue', style='filled')

        g.write('graph.dot')
        g.draw('graph_neato.png', prog='neato')
        g.draw('graph_dot.png', prog='dot')


