# PyTree
A fast implementation of trees from the mathematical theory of graphs

Inspired and applied in condensed matter physics, 
cellular biology and the World Wide Web.

## Mathematical Introduction
### Graphs
Mathematical objects of the theory of *graphs* have one-to-one matrix 
representations, as described by the theory of linear algebra.
In general, a graph is a network structure, whose off-diagonal terms 
in the matrix representation are known to Condensed Matter Physicists 
as hopping or interaction terms.

### Trees
A particular graph, known as a tree, is a network with a 
hierarchical structure, which we use to index 
objects in their matrix representation.

## Python implementation
The Tree is a Python subclass of a List, which adds the following *attributes* and *methods*: 

### Attributes
- parent : Tree or none (default)
children : Tree or none (default)
- ancestors : list of Trees lineage upwards 
- root: root of the tree (parent without parent)
- descendants : lists lineage downwards (list of list of Trees) 
- buds : lists descendants without descendants

### Methods
- set_ids : add an index (id) to the buds of this Tree
- get_ids : get the indices (ids) of the buds of this Tree
.attribute : attributes are inherited down the linage

## Summary
A *graph structure defines a matrix*; a *tree structure
indexes the matrix*. 

The tree structure adds parents, 
children, ancestors, descendants and inheritance of attributes.

## Installation
### Development environment
```sh
pip install --editable . --break-system-packages
```

## Build and upload
```sh
python3 -m build
twine upload dist/*
```
