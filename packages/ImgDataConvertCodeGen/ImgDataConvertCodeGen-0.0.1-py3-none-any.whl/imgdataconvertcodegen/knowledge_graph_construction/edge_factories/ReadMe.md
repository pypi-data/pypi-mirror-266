# Edge Factories for Knowledge Graph Construction

This directory houses edge factories crucial for constructing knowledge graphs. Each factory function takes source and target metadata as inputs and outputs the conversion code needed for their transformation. Notably, the source and target metadata are identical except for a **single differing attribute**.


To create an edge in the graph,  it's essential to ensure that:

* Each attribute adheres to the valid values specified by the libraries.
* The combination of attribute values forms a valid metadata entity.
* There is a feasible conversion code between the source and target metadata.
