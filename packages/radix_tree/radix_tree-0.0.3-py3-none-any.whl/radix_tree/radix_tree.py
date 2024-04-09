# -*- coding: utf-8 -*-

###################################################################
# run tests from Pycharms locally                                ##
#from radix_config import my_logger                              ##
#                                                                ##
# run tests from external Testpy as distributed package          ##
from radix_tree.radix_config import my_logger
#                                                                ##
###################################################################

class Container(object):
    """
    Container populated with data linked to a radic node
    """

    def __init__(self, data, tag=None):
        self._data = data
        self._tag = tag
        self._previous = None
        self._next = None

    def __str__(self):
        return ("Container -> data: %s tag: %s" % (self._data, self._tag))


class Node(object):
    """
     A radix node
     """

    def __init__(self, key, key_size, cont=None):
        self._next = {}
        self._key = key
        self._key_size = key_size
        self._data = cont

    def __str__(self):
        p = hex(id(self))
        if self._data:
            return ("Node %s -> key: %s (%s) key_size: %d _next: %s _data %s" % (
            p, self._key[0:self._key_size], self._key[self._key_size + 1:], self._key_size, self._next, self._data))
        else:
            return ("Node %s -> key: %s (%s) key_size: %d _next: %s" % (
            p, self._key[0:self._key_size], self._key[self._key_size + 1:], self._key_size, self._next))

class RadixTree(object):
    """
    A radix tree
    """

    #    max_key_len = 0

    def __init__(self):
        self._tree = None

    def insert_node(self, key, val, start_node=None):
        """
        Insert a node in radix tree with a string key
        :param key: string or int key
        :param val: data linked to the node
        :return: new node created
        """
        my_logger.debug(" RadixTree.insert_node() ".center(60, '-'))
        my_logger.debug(" key: %s " % key)

        if type(key) != str:
            key = bin(key).replace('0b', '')
            my_logger.debug("Key converted in string key: %s " % key)

        if start_node == None:
            current = self._tree
        else:
            current = start_node

        my_logger.info("Current node: %s " % current)

        if not current:
            """ the radix tree is empty """
            my_logger.debug("Radix tree empty")
            cont = Container(data=val, tag=0)
            node = Node(key, len(key), cont)
            self._tree = node
            my_logger.debug(node)
            return cont

        tested = 0
        while tested < current._key_size:
            if tested > len(key) - 1:
                #  Example
                #  key to insert AB
                #  tested = 2
                #  ┏━━━━━━━━━━━━┓B ┏━━━━━━━━━━━━┓
                #  ┃ current    ┃->┃ next node  ┃
                #  ┃ key=ABAB   ┃  ┃ key=ABABB  ┃
                #  ┃ len=4      ┃  ┃ len=5      ┃
                #  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛
                #  Result :
                #  ┏━━━━━━━━━━━━┓A ┏━━━━━━━━━━━━┓B ┏━━━━━━━━━━━━┓
                #  ┃ current    ┃->┃ node1      ┃->┃ next node  ┃
                #  ┃ key=AB     ┃  ┃ key=ABAB   ┃  ┃ key=ABABB  ┃
                #  ┃ len=2      ┃  ┃ len=4      ┃  ┃ len=5      ┃
                #  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛

                cont = Container(data=val, tag=0)
                node1 = Node(current._key, current._key_size, None)
                node1._next = current._next.copy()
                node1._data = current._data

                current._key_size = len(key)
                current._next[current._key[tested]] = node1
                current._key = key
                current._data = cont

                my_logger.debug(current)
                my_logger.debug(node1)

                return cont

            elif current._key[tested] != key[tested]:
                """
                Creation of two new nodes and one container for data
                """
                #  Example
                #  key to insert AC
                #  tested = 1
                #  ┏━━━━━━━━━━━━┓  ┏━━━━━━━━━━━━┓
                #  ┃ current    ┃->┃ next node  ┃
                #  ┃ key=ABAB   ┃  ┃ key=ABABB  ┃
                #  ┃ len=4      ┃  ┃ len=5      ┃
                #  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛
                #  Result :
                #  ┏━━━━━━━━━━━━┓B ┏━━━━━━━━━━━━┓  ┏━━━━━━━━━━━━┓
                #  ┃ current    ┃->┃ node1      ┃->┃ next node  ┃
                #  ┃ key=A      ┃  ┃ key=ABAB   ┃  ┃ key=ABABB  ┃
                #  ┃ len=1      ┃  ┃ len=4      ┃  ┃ len=5      ┃
                #  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛
                #        │ C       ┏━━━━━━━━━━━━┓
                #        +-------->┃ node2      ┃
                #                  ┃ key=AC     ┃
                #                  ┃ len=2      ┃
                #                  ┗━━━━━━━━━━━━┛
                cont = Container(data=val, tag=0)
                node1 = Node(current._key, current._key_size, None)
                node1._next = current._next.copy()
                node1._data = current._data
                node2 = Node(key, len(key), cont)

                current._key_size = tested
                # for k in current._next:
                #    del current._next[k]
                current._next = {}
                current._next[current._key[tested]] = node1
                current._next[key[tested]] = node2
                current._key = key[0:tested]
                current._data = None

                my_logger.debug(current)
                my_logger.debug(node1)
                my_logger.debug(node2)

                return cont
            tested += 1

        if tested == current._key_size:
            if tested < len(key):
                """Go to the next node"""
                if key[tested] in current._next:
                    current = current._next[key[tested]]
                    my_logger.debug("Go to the next node: %s" % current)
                    self.insert_node(key, val, current)
                else:
                    """Create the new node"""
                    #  Example
                    #  key to insert ABABA
                    #  tested = 4
                    #  ┏━━━━━━━━━━━━┓B ┏━━━━━━━━━━━━┓
                    #  ┃ current    ┃->┃            ┃
                    #  ┃ key=ABAB   ┃  ┃ key=ABABB  ┃
                    #  ┃ len=4      ┃  ┃ len=5      ┃
                    #  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛
                    #  Result :
                    #  ┏━━━━━━━━━━━━┓B ┏━━━━━━━━━━━━┓
                    #  ┃ current    ┃->┃            ┃
                    #  ┃ key=ABAB   ┃  ┃ key=ABABB  ┃
                    #  ┃ len=4      ┃  ┃ len=5      ┃
                    #  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛
                    #        │ A       ┏━━━━━━━━━━━━┓
                    #        +-------->┃ node       ┃
                    #                  ┃ key=ABABA  ┃
                    #                  ┃ len=5      ┃
                    #                  ┗━━━━━━━━━━━━┛

                    cont = Container(data=val, tag=0)
                    node = Node(key, len(key), cont)
                    current._next[key[tested]] = node
                    my_logger.debug("Create the next node: %s" % node)
                    my_logger.debug("Modify the current node: %s" % current)
                    return cont
            else:
                """The leaf already exists, we have to update container"""
                my_logger.debug("The leaf already exists, we have to update container node: %s" % current)
                current._key = key
                current._key_size = len(key)
                cont = current._data
                if cont:
                    """Update container"""
                    cont._data = val
                    my_logger.debug("Node already exist. Update container: %s" % current)
                else:
                    """Create container"""
                    my_logger.debug("Node already exist. Create container: %s" % current)
                    cont = Container(data=val, tag=0)
                    current._data = cont
                return cont

    def get_node(self, key, start_node=None):
        """
        Get node in the radix tree beginning to <start_node> indexed by <key>
        :param start_node: first node of the radix tree to explore
        :param key: key to search
        :return: data linked to the node, if any. None otherwise
        """

        my_logger.debug(" RadixTree.get_node() ".center(60, '-'))

        if type(key) != str:
            key = bin(key).replace('0b', '')
            my_logger.debug("Key converted in string key: %s " % key)

        my_logger.debug("key: %s" % key)

        if start_node == None:
            node = self._tree
        else:
            node = start_node

        if node:
            my_logger.info("Current node: %s" % node)
            if node._key == key and node._key_size == len(node._key):
                my_logger.info("Node found -> key: %s key_size: %d data: %s" % (node._key, node._key_size, node._data))
                return node._data
            else:
                tested = 0
                while tested < node._key_size:
                    if tested > len(key) - 1:
                        my_logger.warning("Node not found -> key: %s" % key)
                        return None
                    else:
                        my_logger.debug("Searching node... current node: %s " % node)
                        my_logger.debug(
                            "Searching node... index: %d tested: %s - %s" % (tested, node._key[tested], key[tested]))
                        if node._key[tested] != key[tested]:
                            my_logger.warning("Node not found -> key: %s" % key)
                            return None
                        else:
                            tested += 1

                if tested == node._key_size:
                    if key[tested] in node._next:
                        node = node._next[key[tested]]
                        my_logger.info("2 Go to the next node -> next: %s node: %s" % (node._key[tested], node))
                        return self.get_node(key, node)
                    else:
                        my_logger.warning("Node not found -> key: %s" % key)
                        return None
        else:
            my_logger.info("Radix tree empty")
            return None

    def delete_node(self, key, start_node=None, prev_node=None):
        """
        Delete node in radix tree
        :param key: key of the node to delete
        :param start_node: first node of the radix tree or None to start from the beginning of radix tree
        :param prev_node: previous node
        :return: True if deleted. False otherwise.
        """

        my_logger.debug(" RadixTree.delete_node() ".center(60, '-'))

        if type(key) != str:
            key = bin(key).replace('0b', '')
            my_logger.debug("Key converted in string key: %s " % key)

        my_logger.debug(" Key : %s" % key)

        if start_node == None:
            node = self._tree
        else:
            node = start_node

        my_logger.info("Current node -> %s" % node)

        if node:
            if node._key == key:
                # Node to delete found
                my_logger.debug("Node to delete found -> %s" % node)
                if len(node._next) == 0:
                    if prev_node == None:
                        my_logger.debug("First node of tree deleted -> Radix tree empty")
                        del self._tree
                        self._tree = None
                        return True
                    else:
                        # Example
                        # Delete 'ABA'
                        # ┏━━━━━━━━━━━━┓A ┏━━━━━━━━━┓
                        # ┃ prev_node  ┃->┃ node    ┃
                        # ┃ key=AB     ┃  ┃ key=ABA ┃
                        # ┃ len=2      ┃  ┃ len=3   ┃
                        # ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━┛
                        # Result :
                        # ┏━━━━━━━━━━━━┓
                        # ┃ prev_node  ┃
                        # ┃ key=AB     ┃
                        # ┃ len=2      ┃
                        # ┗━━━━━━━━━━━━┛

                        my_logger.debug("Node deleted %s " % node)
                        my_logger.debug("Previous link deleted %s " % prev_node)
                        del prev_node._next[node._key[prev_node._key_size]]
                        my_logger.debug("1. Previous node updated %s " % prev_node)

                        if len(prev_node._next) == 1 and prev_node._data == None:
                            # Example
                            # Delete 'ABB'
                            # ┏━━━━━━━━━━━━┓A ┏━━━━━━━━━┓
                            # ┃ prev_node  ┃->┃ node    ┃
                            # ┃ key=AB     ┃  ┃ key=ABA ┃
                            # ┃ len=2      ┃  ┃ len=3   ┃
                            # ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━┛
                            #        │ B       ┏━━━━━━━━━━━━┓
                            #        +-------->┃ other node ┃
                            #                  ┃ key=ABB    ┃
                            #                  ┃ len=3      ┃
                            #                  ┗━━━━━━━━━━━━┛
                            # Result :
                            # ┏━━━━━━━━━━━━┓
                            # ┃ prev_node  ┃
                            # ┃ key=ABA    ┃
                            # ┃ len=3      ┃
                            # ┗━━━━━━━━━━━━┛
                            for k in prev_node._next:
                                prev_node._key = prev_node._next[k]._key
                                prev_node._key_size = prev_node._next[k]._key_size
                                prev_node._data = prev_node._next[k]._data
                                prev_node._next = prev_node._next[k]._next
                                my_logger.debug("2. Previous node updated %s " % prev_node)

                        del node._data
                        del node
                        return True
                else:
                    if len(node._next) == 1:
                        # Example
                        # Delete 'ABA'
                        # ┏━━━━━━━━━━━━┓A ┏━━━━━━━━━━━━┓B ┏━━━━━━━━━━━━┓
                        # ┃ prev_node  ┃->┃ node       ┃->┃ next_node  ┃
                        # ┃ key=AB     ┃  ┃ key=ABA    ┃  ┃ key=ABAB   ┃
                        # ┃ len=2      ┃  ┃ len=3      ┃  ┃ len=4      ┃
                        # ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛
                        # Result :
                        # ┏━━━━━━━━━━━━┓A ┏━━━━━━━━━━━━┓
                        # ┃ prev_node  ┃->┃ node       ┃
                        # ┃ key=AB     ┃  ┃ key=ABAB   ┃
                        # ┃ len=2      ┃  ┃ len=4      ┃
                        # ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛
                        for ke in node._next:
                            next_node = node._next[ke]
                        my_logger.info("Node to update %s " % node)
                        node._key = next_node._key
                        node._key_size = next_node._key_size
                        node._data = next_node._data
                        node._next = next_node._next.copy()
                        my_logger.info("Node updated %s " % node)
                        my_logger.info("Node deleted %s " % next_node)
                        del next_node._data
                        del next_node
                        return True
                    else:
                        # Example
                        # Delete 'ABA'
                        # ┏━━━━━━━━━━━━┓A ┏━━━━━━━━━━━━┓B ┏━━━━━━━━━━━━┓
                        # ┃ prev_node  ┃->┃ node       ┃->┃ next_node1 ┃
                        # ┃ key=AB     ┃  ┃ key=ABA    ┃  ┃ key=ABAB   ┃
                        # ┃ len=2      ┃  ┃ len=3      ┃  ┃ len=4      ┃
                        # ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛
                        #                       │ C       ┏━━━━━━━━━━━━┓
                        #                       +-------->┃ next_nodei ┃
                        #                                 ┃ key=ABAC   ┃
                        #                                 ┃ len=4      ┃
                        #                                 ┗━━━━━━━━━━━━┛
                        # Result :
                        # ┏━━━━━━━━━━━━┓A ┏━━━━━━━━━━━━┓B ┏━━━━━━━━━━━━┓
                        # ┃ prev_node  ┃->┃ node       ┃->┃ next_node1 ┃
                        # ┃ key=AB     ┃  ┃ key=ABA    ┃  ┃ key=ABAB   ┃
                        # ┃ len=2      ┃  ┃ len=3      ┃  ┃ len=4      ┃
                        # ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━┛
                        #                       │ C       ┏━━━━━━━━━━━━┓
                        #                       +-------->┃ next_nodei ┃
                        #                                 ┃ key=ABAC   ┃
                        #                                 ┃ len=4      ┃
                        #                                 ┗━━━━━━━━━━━━┛
                        # In this case, just delete data linked to the node
                        del node._data
                        node._data = None
                        my_logger.info("Just delete data linked to the node %s " % node)
                        return True
            else:
                # Other node case
                tested = 0
                while tested < node._key_size:
                    if tested > len(key) - 1:
                        my_logger.warning("Node not found -> key: %s" % key)
                        return False
                    else:
                        my_logger.debug("Searching node... current node: %s " % node)
                        my_logger.debug(
                            "Searching node... index: %d tested: %s - %s" % (tested, node._key[tested], key[tested]))
                        if node._key[tested] != key[tested]:
                            my_logger.warning("Node not found -> key: %s" % key)
                            return False
                        else:
                            tested += 1

                if tested == node._key_size:
                    if key[tested] in node._next:
                        prev_node = node
                        node = node._next[key[tested]]
                        my_logger.info("Go to the next node -> next: %s node: %s" % (node._key[tested], node))
                        ret = self.delete_node(key, node, prev_node)
                        return ret
                    else:
                        my_logger.warning("Node not found -> key: %s" % key)
                        return False
        else:
            my_logger.info("Radix tree empty")
            return False

    def dump(self, node=None, st_next_line=''):
        """
        Display a radix node
        :param node: first node of the radix tree. If node = None dump the entire radix tree
        :param st_next_line: start of next line to display
        :return: None
        """

        my_logger.debug(" RadixTree.dump() ".center(60, '-'))

        if not node:
            """Dump the entire radix tree"""
            node = self._tree
            if not node:
                print("Radix tree empty")
                return
            if node._data:
                line = "■"
            else:
                line = "□"
            line += " key: %s key_len: %d next: %d" % (node._key, node._key_size, len(node._next))
            if node._data:
                line += " data: %s" % node._data
            print(line)
            cpt = len(node._next) - 1
            st_next_line = "│" * cpt
            for item in node._next:
                self.dump(node._next[item], st_next_line)
                cpt -= 1
                st_next_line = st_next_line[0:cpt]
        else:
            """Intermediate node"""
            line = st_next_line
            if node._data:
                line += "└■"
            else:
                line += "└□"
            line += " key: %s key_len: %d next: %d" % (node._key, node._key_size, len(node._next))
            if node._data:
                line += " data: %s" % node._data
            print(line)
            cpt = len(node._next) - 1
            if cpt > 1:
                st_next_line = st_next_line + " │" + "│" * (cpt - 1)
            if cpt == 1:
                my_logger.debug("node with only one son: %s" % node)
                st_next_line = st_next_line + " │"

            for item in node._next:
                self.dump(node._next[item], st_next_line)
                l = len(st_next_line) - 1
                st_next_line = st_next_line[0:l]
