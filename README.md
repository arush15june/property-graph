# property-graph

Implementation of a property graph, inspired by Designing Data-Intensive Applications (pg.50). The example included is of Lucy born in Idaho, United States, who now lives in London, England as described in Fig 2-5 (pg. 50, DDIA).

## Property Graph

- Nodes
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
