#!/usr/bin/env python
"""
 This is an implementation of a property graph, inspired by 
 pg.50, Chapter 2 of Designing Data-Intensive Applications.

 A Property Graph consists of 
   - Nodes (Vertices)
     - A unique identifier
     - A set of outgoing edges
     - A set of incoming edges
     - A collection of properties (k/v)
   - Edges
     - A unique identifier
     - The vertex at which the edge starts (Tail Vertex).
     - The vertex at which the edge ends (Head Vertex).
     - A label to describe the kind of relationship between the two vertices.
     - A collection of properties (k/v).
"""

from typing import List
from dataclasses import dataclass, field
import shortuuid

@dataclass
class Node:
    """ 
        Vertex in the property graph.
    """
    uid: str
    properties: dict = field(default_factory=dict)
    outgoing: dict = field(default_factory=dict)
    incoming: dict = field(default_factory=dict)

@dataclass
class Edge:
    """ 
        Edges in the property graph.
    """
    uid: str
    label: str
    tail: Node
    head: Node
    properties: dict = field(default_factory=dict)

class Graph:
    def __init__(self):
        """ 
            The property graph built on top of Nodes and Edges.
            Each node and edge is generated with a `shortuuid.uuid()` UID
            which can be used to uniquely identify and fetch them.

            @member dict{UID: Node} self.nodes: Nodes in the graph indexed by the UID
            @member dict{UID: Edge} self.edges: Edges in the graph indexed by the UID
        """
        self.nodes = dict()
        self.edges = dict()
    
    @staticmethod
    def _generate_uid():
        """ 
            Generate a short sized random UUID.
        """
        return shortuuid.uuid() 

    def add_node(self, properties: dict, **kwargs) -> Node:
        """ 
            Add a new node to the graph with `properties`.

            @kwargs str uid: Set the UID explicitly.
        """
        uid = kwargs.get('uid', self._generate_uid())
        self.nodes[uid] = Node(uid, properties)
        return self.nodes[uid]

    def node(self, uid: str) -> Node:
        """ 
            Fetch a node with uid=`uid`.
        """
        return self.nodes.get(uid, None)
    
    def add_edge(self, tail: Node, label: str, head: Node, properties: dict = {}, **kwargs) -> Edge:
        """ 
            - Add an edge to self.edges,
             also update the head and tail nodes associated with the edge. 
            
            @kwargs str uid: Set the UID explicitly.
        """
        uid = kwargs.get('uid', self._generate_uid())
        if self.node(tail.uid) is None and self.node(head.uid) is None:
            return None
        
        tail_uid = tail.uid
        head_uid = head.uid
        
        self.edges[uid] = Edge(uid, label, tail, head, properties)
        self.nodes[tail_uid].outgoing[self.edges[uid].uid] = self.edges[uid]
        self.nodes[head_uid].incoming[self.edges[uid].uid] = self.edges[uid]

        return self.edges.get(uid, None)

    def edge(self, uid: str) -> Edge:
        """ 
            Fetch an edge with uid=`uid`
        """
        return self.edges.get(uid, None)

    @staticmethod
    def _match_dict(d1: dict, d2: dict) -> int:
        """ 
            Match the keys and values of two dicitonaries
            Only one level of dictionaries, no recursive dictionary matching.

            @return: number of keys matched between the two dictionaries.
        """
        matches = 0
        for key, val in d2.items():
            if d1.get(key) == val:
                matches += 1        

        return matches

    def find_node(self, properties: dict) -> List[Node]:
        """
            Find a nodes with an exact or partial match of properties.
            
            @return List[Node]: List of nodes having more than zero keys matching with properties.
        """
        nodes_matching = list()

        for _, node in self.nodes.items():
            matches = self._match_dict(node.properties, properties)
            if matches:
                nodes_matching.append(node) 

        return nodes_matching

    def find_node_edges_label_outgoing(self, node: Node, label: str) -> List[Edge]:
        """ 
            Match a label on the node's outgoing edges.

            @return List[Edge]: List of all outgoing edges of Node with the label.
        """
        edge_matches = list()
        for _, edge in node.outgoing.items():
            if edge.label == label:
                edge_matches.append(edge)

        return edge_matches

    def find_node_edges_label_incoming(self, node: Node, label: str) -> List[Edge]:
        """ 
            Match a label on the node's incoming edges.

            @return List[Edge]: List of all incoming edges of Node with the label.
        """
        edge_matches = list()
        for _, edge in node.incoming.items():
            if edge.label == label:
                edge_matches.append(edge)

        return edge_matches
    
    def follow_edge_on_label(self, edge: Edge, label: str) -> Node:
        """
            Follow edge via head vertices on a specific label,
            return the last node which does not have an edge with `label`.
            
            If the passed edge's head does not have any edges with the label,
            None is returned
            
            If there is more than one edge on the head vertex matching the label, 
            only the first edge in the list followed, the order of this list is undetermined
            (uses find_node_edges_label_outgoing).

            @param Edge edge: Edge to start on.
            @param label str: Label to follow.
            @return Node|None: Last node without any edge to `label` or None if the current edge's head does not have any edge to `label`.
        """

        curr_head = edge.head

        curr_head_edges_with_label = self.find_node_edges_label_outgoing(curr_head, label)
        if len(curr_head_edges_with_label) == 0:
            return None

        while len(curr_head_edges_with_label) > 0:
            edge = curr_head_edges_with_label[0]
            curr_head = edge.head
            curr_head_edges_with_label = self.find_node_edges_label_outgoing(curr_head, label)

        return curr_head

if __name__ == "__main__":
    graph = Graph()
    
    # Add locations
    # North America
    n_namerica = graph.add_node({'type': 'Continent', 'name': 'North America'})
    n_usa = graph.add_node({'type': 'Country', 'name': 'United States'})
    n_idaho = graph.add_node({'type': 'State', 'name': 'Idaho'})
    
    # Add edges
    # Idaho is within United States, which is within North America 
    graph.add_edge(n_usa, 'WITHIN', n_namerica)
    graph.add_edge(n_idaho, 'WITHIN', n_usa)
    
    # Europe
    n_europe = graph.add_node({'type': 'Continent', 'name': 'Europe'})
    n_england = graph.add_node({'type': 'Country', 'name': 'England'})
    n_london = graph.add_node({'type': 'City', 'name': 'London'})

    # Add edges
    # London is within England, which is within Europe 
    graph.add_edge(n_england, 'WITHIN', n_europe)
    graph.add_edge(n_london, 'WITHIN', n_england)
    
    # Add Lucy
    n_lucy = graph.add_node({"type": "Person", "name": "Lucy"})

    # Add edges
    # Lucy was born in Idaho, United States but now lives in Londo, England.
    graph.add_edge(n_lucy, "BORN_IN", n_idaho)
    graph.add_edge(n_lucy, "LIVES_IN", n_london)

    # In the database of nodes, find a `Person` with the name: "Lucy"
    # who was `BORN_IN` "Idaho" `WITHIN` "United States" 
    # and now `LIVES_IN` "London" `WITHIN' "England".
    lucy_matches = graph.find_node({"type": "Person", "name": "Lucy"})
    for lucy in lucy_matches:
        
        # Check if lucy born in the State of Idaho.
        lucy_born_in_list = graph.find_node_edges_label_outgoing(lucy, 'BORN_IN')
        if len(lucy_born_in_list) > 0:
            lucy_born_in = lucy_born_in_list[0]
            if not lucy_born_in.head.properties['type'] == 'State' and not lucy_born_in.head.properties['name'] == 'Idaho':
                break
            
            # Check if this Idaho is within North America
            lucy_born_in_continent = graph.follow_edge_on_label(lucy_born_in, 'WITHIN')
            if lucy_born_in_continent:
                if not lucy_born_in_continent.properties['type'] == 'Continent' and not lucy_born_in_continent.properties['name'] == 'North America':
                    break
        
        print("This lucy is from Idaho, North America!")

        # Check if lucy born in the State of Idaho.
        lucy_lives_in_list = graph.find_node_edges_label_outgoing(lucy, 'LIVES_IN')
        if len(lucy_lives_in_list) > 0:
            lucy_lives_in = lucy_lives_in_list[0]
            if not lucy_lives_in.head.properties['type'] == 'State' and not lucy_lives_in.head.properties['name'] == 'London':
                break
            
            # Check if this Idaho is within North America
            lucy_lives_in_continent = graph.follow_edge_on_label(lucy_lives_in, 'WITHIN')
            if lucy_lives_in_continent:
                if not lucy_lives_in_continent.properties['type'] == 'Continent' and not lucy_lives_in_continent.properties['name'] == 'Europe':
                    break

        print("and she lives in London, the one in Europe!")




