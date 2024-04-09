from radix_tree import RadixTree

def test_radix_tree_00():
    # Radix Tree creation with string key
    # Creation of empty radix tree
    my_tree = RadixTree()
    # Get inexistent node
    print("*"*10)
    i = 1
    my_key = 'AB'
    print("%d. Get inexistent node '%s'" %(i,my_key))
    assert my_tree.get_node(my_key) == None
    # Delete inexistent node
    print("*"*10)
    i += 1
    my_key = 'ABBB'
    print("%d. Delete inexistent node '%s'" %(i,my_key))
    assert my_tree.delete_node(my_key) == False
    # Dump empty radix tree
    print("*"*10)
    i += 1
    print("%d. Dump empty radix tree" % i)
    my_tree.dump()

def test_radix_tree_01():
    # Radix Tree creation with string key
    # Creation of empty radix tree
    my_tree = RadixTree()
    # Insert first node
    print("*"*10)
    i = 1
    my_key = 'A'
    print("%d. Insert node '%s'" %(i,my_key))
    my_tree.insert_node(my_key,my_key)
    assert my_tree.get_node(my_key)._data == my_key
    my_tree.dump()
    # Insert first node
    print("*"*10)
    i += 1
    my_key = 'A'
    print("%d. Insert node '%s'" %(i,my_key))
    my_tree.insert_node(my_key,my_key)
    assert my_tree.get_node(my_key)._data == my_key
    my_tree.dump()
    # Insert second node
    print("*"*10)
    i += 1
    my_key = 'AB'
    print("%d. Insert node '%s'" %(i,my_key))
    my_tree.insert_node(my_key,my_key)
    assert my_tree.get_node(my_key)._data == my_key
    assert my_tree.get_node('A')._data == 'A'
    my_tree.dump()
    # Insert third node
    print("*"*10)
    i += 1
    my_key = 'X'
    print("%d. Insert node '%s'" %(i,my_key))
    my_tree.insert_node(my_key,my_key)
    assert my_tree.get_node(my_key)._data == my_key
    assert my_tree.get_node('A')._data == 'A'
    assert my_tree.get_node('AB')._data == 'AB'
    my_tree.dump()
    # Delete third node
    print("*"*10)
    i += 1
    my_key = 'X'
    print("%d. Delete node '%s'" %(i,my_key))
    assert my_tree.delete_node(my_key) == True
    assert my_tree.get_node(my_key) == None
    assert my_tree.get_node('A')._data == 'A'
    assert my_tree.get_node('AB')._data == 'AB'
    my_tree.dump()
    # Delete second node
    print("*"*10)
    i += 1
    my_key = 'AB'
    print("%d. Delete node '%s'" %(i,my_key))
    my_tree.delete_node(my_key)
    assert my_tree.get_node(my_key) == None
    assert my_tree.get_node('A')._data == 'A'
    my_tree.dump()
    # Delete First node
    print("*"*10)
    i += 1
    my_key = 'A'
    print("%d. Delete node '%s'" %(i,my_key))
    my_tree.delete_node(my_key)
    assert my_tree.get_node(my_key) == None
    my_tree.dump()

def test_radix_tree_02():
    # Radix Tree creation with string key
    # Creation of empty radix tree
    my_tree = RadixTree()
    # Insert first node
    print("*"*10)
    i = 1
    my_key = 'ABC'
    print("%d. Insert node '%s'" %(i,my_key))
    my_tree.insert_node(my_key,my_key)
    assert my_tree.get_node(my_key)._data == my_key
    my_tree.dump()
    # Insert second node
    print("*"*10)
    i += 1
    my_key = 'A'
    print("%d. Insert node '%s'" %(i,my_key))
    my_tree.insert_node(my_key,my_key)
    assert my_tree.get_node(my_key)._data == my_key
    assert my_tree.get_node('ABC')._data == 'ABC'
    my_tree.dump()
    # Insert third node
    print("*"*10)
    i += 1
    my_key = 'AB'
    print("%d. Insert node '%s'" %(i,my_key))
    my_tree.insert_node(my_key,my_key)
    assert my_tree.get_node(my_key)._data == my_key
    assert my_tree.get_node('A')._data == 'A'
    assert my_tree.get_node('ABC')._data == 'ABC'
    my_tree.dump()
    # Insert same node
    print("*"*10)
    i += 1
    my_key = 'ABC'
    print("%d. Insert node '%s'" %(i,my_key))
    my_tree.insert_node(my_key,my_key)
    assert my_tree.get_node(my_key)._data == my_key
    my_tree.dump()
    # Insert fourth node
    print("*"*10)
    i += 1
    my_key = 'ABD'
    print("%d. Insert node '%s'" %(i,my_key))
    my_tree.insert_node(my_key,my_key)
    assert my_tree.get_node(my_key)._data == my_key
    assert my_tree.get_node('A')._data == 'A'
    assert my_tree.get_node('AB')._data == 'AB'
    assert my_tree.get_node('ABC')._data == 'ABC'
    my_tree.dump()
    # Insert fifth node
    print("*"*10)
    i += 1
    my_key = 'ABCD'
    print("%d. Insert node '%s'" %(i,my_key))
    my_tree.insert_node(my_key,my_key)
    assert my_tree.get_node(my_key)._data == my_key
    assert my_tree.get_node('A')._data == 'A'
    assert my_tree.get_node('AB')._data == 'AB'
    assert my_tree.get_node('ABC')._data == 'ABC'
    assert my_tree.get_node('ABD')._data == 'ABD'
    my_tree.dump()
    # Insert sixth node
    print("*"*10)
    i += 1
    my_key = 'ACD'
    print("%d. Insert node '%s'" %(i,my_key))
    my_tree.insert_node(my_key,my_key)
    assert my_tree.get_node(my_key)._data == my_key
    assert my_tree.get_node('A')._data == 'A'
    assert my_tree.get_node('AB')._data == 'AB'
    assert my_tree.get_node('ABC')._data == 'ABC'
    assert my_tree.get_node('ABD')._data == 'ABD'
    assert my_tree.get_node('ABCD')._data == 'ABCD'
    my_tree.dump()
    # Insert seventh node
    print("*"*10)
    i += 1
    my_key = 'ACE'
    print("%d. Insert node '%s'" %(i,my_key))
    my_tree.insert_node(my_key,my_key)
    assert my_tree.get_node(my_key)._data == my_key
    assert my_tree.get_node('A')._data == 'A'
    assert my_tree.get_node('AB')._data == 'AB'
    assert my_tree.get_node('ABC')._data == 'ABC'
    assert my_tree.get_node('ABD')._data == 'ABD'
    assert my_tree.get_node('ABCD')._data == 'ABCD'
    assert my_tree.get_node('ACD')._data == 'ACD'
    my_tree.dump()
    # Delete seventh node
    print("*"*10)
    i += 1
    my_key = 'ACE'
    print("%d. Delete node '%s'" %(i,my_key))
    my_tree.delete_node(my_key)
    assert my_tree.get_node(my_key) == None
    assert my_tree.get_node('AC') == None
    assert my_tree.get_node('A')._data == 'A'
    assert my_tree.get_node('AB')._data == 'AB'
    assert my_tree.get_node('ABC')._data == 'ABC'
    assert my_tree.get_node('ABD')._data == 'ABD'
    assert my_tree.get_node('ABCD')._data == 'ABCD'
    assert my_tree.get_node('ACD')._data == 'ACD'
    my_tree.dump()
    # Insert seventh node
    print("*"*10)
    i += 1
    my_key = 'ACE'
    print("%d. Insert node '%s'" %(i,my_key))
    my_tree.insert_node(my_key,my_key)
    assert my_tree.get_node(my_key)._data == my_key
    assert my_tree.get_node('A')._data == 'A'
    assert my_tree.get_node('AB')._data == 'AB'
    assert my_tree.get_node('ABC')._data == 'ABC'
    assert my_tree.get_node('ABD')._data == 'ABD'
    assert my_tree.get_node('ABCD')._data == 'ABCD'
    assert my_tree.get_node('ACD')._data == 'ACD'
    my_tree.dump()
    # Insert eighth node
    print("*"*10)
    i += 1
    my_key = 'AC'
    print("%d. Insert node '%s'" %(i,my_key))
    my_tree.insert_node(my_key,my_key)
    assert my_tree.get_node(my_key)._data == my_key
    assert my_tree.get_node('A')._data == 'A'
    assert my_tree.get_node('AB')._data == 'AB'
    assert my_tree.get_node('ABC')._data == 'ABC'
    assert my_tree.get_node('ABD')._data == 'ABD'
    assert my_tree.get_node('ABCD')._data == 'ABCD'
    assert my_tree.get_node('ACD')._data == 'ACD'
    assert my_tree.get_node('ACE')._data == 'ACE'
    my_tree.dump()
    # Delete seventh node
    print("*"*10)
    i += 1
    my_key = 'ACE'
    print("%d. Delete node '%s'" %(i,my_key))
    my_tree.delete_node(my_key)
    assert my_tree.get_node(my_key) == None
    assert my_tree.get_node('AC')._data == 'AC'
    assert my_tree.get_node('A')._data == 'A'
    assert my_tree.get_node('AB')._data == 'AB'
    assert my_tree.get_node('ABC')._data == 'ABC'
    assert my_tree.get_node('ABD')._data == 'ABD'
    assert my_tree.get_node('ABCD')._data == 'ABCD'
    assert my_tree.get_node('ACD')._data == 'ACD'
    my_tree.dump()
    # Insert nineth node
    print("*"*10)
    i += 1
    my_key = 'ABE'
    print("%d. Insert node '%s'" %(i,my_key))
    my_tree.insert_node(my_key,my_key)
    assert my_tree.get_node(my_key)._data == my_key
    my_tree.dump()
    # Delete node
    print("*"*10)
    i += 1
    my_key = 'ABC'
    print("%d. Delete node '%s'" %(i,my_key))
    my_tree.delete_node(my_key)
    assert my_tree.get_node(my_key) == None
    assert my_tree.get_node('AC')._data == 'AC'
    assert my_tree.get_node('A')._data == 'A'
    assert my_tree.get_node('AB')._data == 'AB'
    assert my_tree.get_node('ABD')._data == 'ABD'
    assert my_tree.get_node('ABCD')._data == 'ABCD'
    assert my_tree.get_node('ACD')._data == 'ACD'
    my_tree.dump()
    # Delete node
    print("*"*10)
    i += 1
    my_key = 'AB'
    print("%d. Delete node '%s'" %(i,my_key))
    my_tree.delete_node(my_key)
    assert my_tree.get_node(my_key) == None
    assert my_tree.get_node('AC')._data == 'AC'
    assert my_tree.get_node('A')._data == 'A'
    assert my_tree.get_node('ABD')._data == 'ABD'
    assert my_tree.get_node('ABCD')._data == 'ABCD'
    assert my_tree.get_node('ACD')._data == 'ACD'
    my_tree.dump()

def test_radix_tree_03():
    # Radix Tree creation with numeric key
    # Creation of empty radix tree
    my_tree = RadixTree()
    # Insert first node
    print("*"*10)
    i = 1
    my_key = 0xC0A80101
    my_data = '192.168.1.1'
    print("%d. Insert node '%s'" %(i,my_key))
    my_tree.insert_node(my_key,my_data)
    assert my_tree.get_node(my_key)._data == my_data
    my_tree.dump()
    # Insert second node
    print("*" * 10)
    i = 1
    my_key = 0xC0A80102
    my_data = '192.168.1.2'
    print("%d. Insert node '%s'" % (i, my_key))
    my_tree.insert_node(my_key, my_data)
    assert my_tree.get_node(my_key)._data == my_data
    assert my_tree.get_node(0xC0A80101)._data == '192.168.1.1'
    my_tree.dump()
    # Delete first node
    print("*" * 10)
    i = 1
    my_key = 0xC0A80101
    print("%d. Delete node '%s'" % (i, my_key))
    my_tree.delete_node(my_key)
    assert my_tree.get_node(my_key) == None
    assert my_tree.get_node(0xC0A80102)._data == '192.168.1.2'
    my_tree.dump()

def test_radix_tree_04():
    # Radix Tree creation with string key
    # Creation of empty radix tree
    my_tree = RadixTree()
    # Insert first node
    print("*"*10)
    i = 1
    my_key = 'ABC'
    print("%d. Insert node '%s'" %(i,my_key))
    my_tree.insert_node(my_key,my_key)
    assert my_tree.get_node(my_key)._data == my_key
    my_tree.dump()
    # Delete inexistent node
    print("*"*10)
    i = 1
    my_key = 'A'
    print("%d. Delete node '%s'" %(i,my_key))
    my_tree.delete_node(my_key)
    assert my_tree.get_node(my_key) == None
    my_tree.dump()
    # Delete inexistent node
    print("*"*10)
    i = 1
    my_key = 'AB'
    print("%d. Delete node '%s'" %(i,my_key))
    my_tree.delete_node(my_key)
    assert my_tree.get_node(my_key) == None
    my_tree.dump()
    # Insert second node
    print("*"*10)
    i = 1
    my_key = 'ABD'
    print("%d. Insert node '%s'" %(i,my_key))
    my_tree.insert_node(my_key,my_key)
    assert my_tree.get_node(my_key)._data == my_key
    my_tree.dump()
    # Delete inexistent node
    print("*"*10)
    i = 1
    my_key = 'AC'
    print("%d. Delete node '%s'" %(i,my_key))
    my_tree.delete_node(my_key)
    assert my_tree.get_node(my_key) == None
    my_tree.dump()
    # Delete inexistent node
    print("*"*10)
    i = 1
    my_key = 'ABDE'
    print("%d. Delete node '%s'" %(i,my_key))
    my_tree.delete_node(my_key)
    assert my_tree.get_node(my_key) == None
    my_tree.dump()
    # Delete node
    print("*"*10)
    i = 1
    my_key = 'ABC'
    print("%d. Delete node '%s'" %(i,my_key))
    my_tree.delete_node(my_key)
    assert my_tree.get_node(my_key) == None
    my_tree.dump()
    # Delete node
    print("*"*10)
    i = 1
    my_key = 'ABD'
    print("%d. Delete node '%s'" %(i,my_key))
    my_tree.delete_node(my_key)
    assert my_tree.get_node(my_key) == None
    my_tree.dump()


if __name__ == "__main__":
    test_radix_tree_00()
    test_radix_tree_01()
    test_radix_tree_02()
    test_radix_tree_03()
    test_radix_tree_04()



