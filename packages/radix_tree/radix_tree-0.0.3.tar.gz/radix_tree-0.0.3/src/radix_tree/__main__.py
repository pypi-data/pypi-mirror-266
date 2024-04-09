# -*- coding: utf-8 -*-
from radix_tree import RadixTree

if __name__ == '__main__':
    # Radix Tree creation with string key
    # Creation of empty radix tree
    my_tree = RadixTree()
    i = 0
    # Insert first node
    i += 1
    my_key = 'AAAABABA'
    print("%d. Insert node '%s'" % (i, my_key))
    my_tree.insert_node(my_key, my_key)
    # Insert Second node
    i += 1
    my_key = 'AAABABAA'
    print("%d. Insert node '%s'" % (i, my_key))
    my_tree.insert_node(my_key, my_key)
    # Insert third node
    i += 1
    my_key = 'AAABBBBA'
    print("%d. Insert node '%s'" % (i, my_key))
    my_tree.insert_node(my_key, my_key)
    my_tree.dump()
    # Get node
    i += 1
    my_key = 'AAABBBBA'
    print("%d. Get node '%s'" % (i, my_key))
    print("Data associated to the node : %s" % my_tree.get_node(my_key))
    # Deletion of second node
    i += 1
    my_key = 'AAABABAA'
    print("%d. Delete node '%s'" % (i, my_key))
    my_tree.delete_node(my_key)
    # Deletion of third node
    i += 1
    my_key = 'AAABBBBA'
    print("%d. Delete node '%s'" % (i, my_key))
    my_tree.delete_node(my_key)
    # Display radix tree
    my_tree.dump()
