# radix-tree

[![PyPI - Version](https://img.shields.io/pypi/v/radix-tree.svg)](https://pypi.org/project/radix-tree)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/radix-tree.svg)](https://pypi.org/project/radix-tree)

-----

**Table of Contents**

- [Installation](#installation)
- [What is radix tree ?](#what_is_radix_tree)
- [Getting started](#Getting_started)
- [License](#license)

## Installation

```console
pip install radix-tree
```
## What_is_radix_tree
A radix tree is a specialized data structure used to store a 
set of data indexed by strings. These can be strings of 
characters, bits or any lexicographically ordered objects.

Radix tree are useful for building associative arrays with 
string keys. In particular, they are very efficient to store 
sets with hierarchical organization (such as IP addresses).

Insertion, deletion and searching have worst-case O(k) 
(where k is the size of the key) and are therefore extremely 
fast.

A set of strings of bits can be easily represented with a tree. 
For instance, a 3-bits string:

![radix-tree.png](radix-tree.png)

The string **ABB** is fully represented by a unique path in the 
tree. As a consequence, to associate some data to the string 
**ABB**, we just need to store this data (say a pointer to this 
data) in the last leaf of the path **ABB**.

Finding back the data associated to the string **ABB** is 
straightforward (and very fast) because we just need to follow 
the path (The algorithm to do this have O(3)).

This structure is then very efficient to build associative 
arrays. Unfortunately it is largely memory-in(radix-tree.png)efficient as the 
tree grows exponentially with the size of the key.

Here comes the radix tree. In a radix tree, we don’t branch for 
every bit, but only when the radixes of strings are different. 
In a way, when a node has only one child, we merge it with 
its root.

For instance, a 8-bits radix tree which stores the values 
**AAAABABA**, **AAABBBAA** and **AAABBBBA**:

![radix-tree-2.png](radix-tree-2.png)

Every intermediary node represents a radix of the string. 
The final leaf represents the complete strings and stores the 
associated data.

On this figure, you can see why the radix tree is useful to store
hierarchical organization of data. Imagine that **AAAABABA** is 
an IP address. **AAA/3** would be the network address. **AAAA/4** 
would be the subnetwork address, and **AAAABABA/8** the final 
address. This is why radix trees are commonly used for IP routing.

You can also see, that insertion, deletion and search in a radix
tree have worst-case O(k) where k is the size of the key 
(we branch on every bit). But it only happens when the tree is 
full (very unlikely for long strings and, for short strings, 
good-ol’ arrays are always your best shot).

>**Note that the current implementation of radix tree allows :**
>* keys of differents lengths,
>* data may be associated to every node (not only leaf of the 
tree)

## Getting_started
```python
from radix_tree import RadixTree

# Creation of empty radix tree
my_tree = RadixTree()

# Creation of first node
my_key = 'AAAABABA'
my_data = 'AAAABABA'
my_tree.insert_node(my_key , my_data )

# Creation of second node
my_key = 'AAABABAA'
my_data = 'AAABABAA'
my_tree.insert_node(my_key , my_data )

# Creation of third node
my_key = 'AAABBBBA'
my_data = 'AAABBBBA'
my_tree.insert_node(my_key , my_data )

# Display radix tree
my_tree.dump()

```

Result:

```console
□ key: AAA key_len: 3 next: 2
│└■ key: AAAABABA key_len: 8 next: 0 data: Container -> data: AAAABABA tag: 0
└□ key: AAAB key_len: 4 next: 2
 │└■ key: AAABABAA key_len: 8 next: 0 data: Container -> data: AAABABAA tag: 0
 └■ key: AAABBBBA key_len: 8 next: 0 data: Container -> data: AAABBBBA tag: 0
```

You can also delete or get node :

```python

# Get node
my_key = 'AAABBBBA'
print("Get node '%s'" % my_key)
print("Data associated to the node : %s" % my_tree.get_node(my_key))

# Deletion of second node
my_key = 'AAABABAA'
my_tree.delete_node(my_key)

# Deletion of third node
my_key = 'AAABBBBA'
my_tree.delete_node(my_key)

# Display radix tree
my_tree.dump()
```

Result:

```console
Get node 'AAABBBBA'
Data associated to the node : Container -> data: AAABBBBA tag: 0
■ key: AAAABABA key_len: 8 next: 0 data: Container -> data: AAAABABA tag: 0
```
## Debug
If you want to debug you can activate log in adding 
argument **level=debug** when you launch your script :
```console
$ python3 my_script.py level=debug
```
Log will be display on console and in file /tmp/radixTree.out.

## License

`radix-tree` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
