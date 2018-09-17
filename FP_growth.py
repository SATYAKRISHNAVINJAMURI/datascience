import csv
import itertools
import sys

def find_support_for_every_item(data):
    '''
    Calculate support count for every item in the dataset. Data Set is also preprocessed here.
    input: A List of transactions.
    Output: A Dictionary with item as key and support count as value.
    '''
    items_support = {}
    for transaction in data:
        for item in transaction:
            if(item == ''):      # Data Cleaning eliminate empty space.
                continue
            if item in items_support.keys():
                items_support[item] += 1
            else:
                items_support[item] = 1
    return items_support


# In[71]:


def remove_less_support_items(items_support,minSup):
    '''
    Preprocessing of items - Items with support less than given minimum Support are removed from itemset.
    Input:  1)items_support - A Dictionary of items with item name as key and support as value
            2)minSup - Minimum Support value.
    Output: A Dictionary of removed less minimum_support_items with item names as keys and support as values.
    '''
    after_deletion_support = items_support.copy()
    for key,value in items_support.items():
        if(value < minSup):
            del after_deletion_support[key]
    return after_deletion_support


# In[72]:


def sort_items_on_Value(d):
    '''
    Sort a dictionary based on the value.
    input: d - A dictionary with item names as keys and items support as value.
    output: Sort d based on the support and return the same.
    '''
    d_sorted = {}
    for key in sorted(d, key=d.get,reverse=True):  #Sorting based on support value.
        d_sorted[key] = d[key]
    return d_sorted


# In[73]:


def order_items(data,sorted_frequent_items):
    '''
    Order the items in the dataset such that items with more support appears first and items with support less than
    minimum support are deleted.
    input:  a) data - A list of transactions.
            b) sorted_frequent_items - Sorted Frequent itemset with item names key and support count as values.
    '''
    ordered_dataset = []
    for transaction in data:
        sorted_transaction = []
        for key in sorted_frequent_items.keys():
            if key in transaction:
                sorted_transaction.append(key)
                transaction.remove(key)
        ordered_dataset.append(sorted_transaction)
    return ordered_dataset


# In[74]:


class treeNode:
    def __init__(self, id, counter, parentNode):
        self.id = id
        self.counter = counter
        self.nextLink = None
        self.parent = parentNode
        self.children = []
    def inc(self, numOccur):
        '''
        Increments the counter attribute with a given value.  
        '''
        self.counter += numOccur
    #display tree in text. Useful for debugging        
    def disp(self,file,ind=1):
        '''
        Displays the node and it's children recursively.
        Outputs the tree to a file.
        '''
#         print (' |'*ind, self.id, '-', self.counter)
        print (' |'*ind, self.id, '-', self.counter,file=file)
        for child in self.children:
            child.disp(file,ind+1)


# In[75]:


class FP_tree:
    def __init__(self):
        '''
        header_table is a dictionary where keys are item names and values are a list of support value and nextNode LInk.
        Conventional Header_Table.
        '''
        self.header_table = {}
        self.root =  treeNode('root',0,None)
        self.nodeCount = 1
        
    def insert(self,itemset,counter):
        '''
        Insert the entire item set into FP Tree.
        Input : 1) itemset - List of items to be inserted.
                2) Counter - No of such itemsets. i,e., no of times the itemset to be inserted.
        
        '''
        parent = self.root
        itemset = list(itemset) # Just to make it list given in anyform
        for item in itemset:
            flag = 0
            for node in parent.children:
                if(node.id == item):
                    node.inc(counter)
                    self.header_table[node.id][0] += counter
                    parent = node
                    flag = 1
                    break
            if(flag != 1):
                node = treeNode(item,counter,parent)
                self.nodeCount += 1
                parent.children.append(node)
                self.update_header_table(node,counter)
                parent = node
        return
    
    
    def findPrefixPath(self,node):
        '''
        Returns all the id's of the nodes in the path from root to this node.
        Input: Node to which the path to be found.
        Output: A List of 2d tuples with path as 1st value and counter as second value.
        '''
        all_paths = []
        while(node):
            plist = []
            pnode = node.parent
            while(pnode.id != 'root'):
                plist.append(pnode.id)
                pnode = pnode.parent
            plist.reverse()
            all_paths.append((plist,node.counter))
            node = node.nextLink
        return all_paths
    
    
    def find_coditional_pattern_base(self):
        '''
        Output: Dictionary with item as key and tuple of list of paths returned by findPrefix Path method.
        This coditional_pattern_base is later used for generating frequent patterns.
        '''
        conditional_pattern_base = {}
        for values in self.header_table.values():
            conditional_pattern_base[values[1].id] = self.findPrefixPath(values[1])
        return conditional_pattern_base
    
    
    def update_header_table(self,node,counter):
        '''
        Updates the header_table with the given node. Just adds the node at the end of its linked list.
        header_table is a dictionary with item_id as key and list of support count and link to next node as values.
        '''
        if node.id not in self.header_table.keys():
            self.header_table[node.id] = [counter,None]
        else:
            self.header_table[node.id][0] += counter
        nextNode = self.header_table[node.id][1]
        if(nextNode == None):
            self.header_table[node.id][1] = node
        else:
            while(nextNode.nextLink):
                nextNode = nextNode.nextLink
            nextNode.nextLink = node
    def sum_of_nodes(self,item):
        '''
        function:sum_of_nodes(item)
        Calculates the sum of counter values in all nodes and returns the same. Usefull for debugging.
        '''
        sum = 0
        nextNode = self.header_table[item][1]
        while(nextNode):
            sum += nextNode.counter
            nextNode = nextNode.nextLink
        return sum


# In[76]:


def generate_patterns(root,prefix,prefix_sup,minsup):
    '''
    Generate all the Frequent Patterns.
    '''
    subsets = {}
    nodes_list = {}
    subsets[tuple(prefix)]= prefix_sup
    if not root.children:
        return len(subsets),subsets
    while(root.children):
        node = root.children[0]
        nodes_list[node.id] = node.counter
        root = node
    p_nodes = list(nodes_list.keys())
    for item in prefix:                     
        nodes_list[item] = prefix_sup
    for i in range(1,len(p_nodes) + 1):
        apex = list(itertools.combinations(p_nodes, i))
        after_list = [tuple([x for x in prefix] + list(tup)) for tup in apex]
        for fpattern in after_list:
            all_sup = []
            for item in fpattern:
                all_sup.append(nodes_list[item])
            sup = min(all_sup)
            subsets[fpattern] = sup
    return len(subsets),subsets


# In[77]:


def check_for_single_prefix_path(parent):
    '''
    Checks if FP Tree has only one single path like linked list.
    '''
    while(parent):
        if(len(parent.children) > 1):
            return False
        elif(len(parent.children) == 0):
            break
        else:
            parent = parent.children[0]
    return True


# In[78]:


def del_infrequent(conditional_pattern_base,minsup):
    '''
    From the conditional pattern base, support count of all items is calculated and items with less support are removed.
    This is an enhancing the conditional Pattern Base before building Tree.
    Because of this conditional patterns are modified such that node with high support appears first just to 
    satisfy the property of FP Tree.
    '''
    result = {}
    for key,values in conditional_pattern_base.items():
        item_support = {}
        for ttuple in values:
            itemset = ttuple[0]
            counter = ttuple[1]
            for item in itemset:
                if item in item_support.keys():
                    item_support[item] += counter
                else:
                    item_support[item] = counter
        item_support = sort_items_on_Value(item_support)
        itemslist = list(item_support.keys())
        for tkey ,tvalue in item_support.items():
            if(tvalue < minsup):
                itemslist.remove(tkey)
        patterns = []
        for qtuple in values:
            item_list = list(qtuple[0])
            counter = qtuple[1]
            new_list = []
            for k in itemslist:
                if k in item_list:
                    new_list.append(k)
            patterns.append((tuple(new_list),counter))
        result[key] = patterns
    return result


# In[79]:


def FP_growth(fp_tree,prefix,prefix_sup,output_file,minsup):
    '''
    Final FP Growth Alogrithm.
    Generates Patterns if Tree is a single prefix path.
    If tree is not a single prefix path then conditional pattern base is generated and key is added to the 
    Prefix. Again FP tree is build on the conditional Pattern Base. A recursive step.
    '''
    count = 0;
    no_of_nodes = 0;
    if(check_for_single_prefix_path(fp_tree.root)):
        count,frequent_patterns = generate_patterns(fp_tree.root,prefix,prefix_sup,minsup)
        if frequent_patterns:
            pass
#             print(frequent_patterns)
        return count,fp_tree.nodeCount
    else:
        if prefix:
            count += 1
#             print({tuple(prefix):prefix_sup})      # Very Important do not delete. Print an important pattern
        conditional_pattern_base = fp_tree.find_coditional_pattern_base();
        conditional_pattern_base = del_infrequent(conditional_pattern_base,minsup)  # Very important step to enhance the code.
        for key,values in conditional_pattern_base.items():
            prefix_sup = fp_tree.header_table[key][0]
            header_table_child = {}
            new_fp_tree = FP_tree()
            for qtuple in values:
                itemset = qtuple[0]
                counter = qtuple[1]
                new_fp_tree.insert(itemset,counter)
            prefix.append(key)
            pre = prefix.copy()
            prefix.remove(key)
            a,b = FP_growth(new_fp_tree,pre,prefix_sup,output_file,minsup)
            count += a
            no_of_nodes += b
            
    return count,no_of_nodes




def main(pathToDataSet,minSup):
    '''
    Inputs: pathToDataSet - Absolute path to the data set.
            minSup - min support value in percentage.
    '''
    data = []   # Carries list of data and transactions.
    header_table = {}  # Header Table keeps track of all the nodes of same type.
    total_trans = 0
    with open(pathToDataSet,'r') as csvfile:
        plots = csv.reader(csvfile, delimiter=' ')
        for row in plots:
            data.append(row)
            total_trans += 1
    minSup = (minSup*total_trans/100)      # Percentage => to normal.
    print("No of Transactions:",total_trans)
    items_support = find_support_for_every_item(data)  # Carries support count for each item.
    print("No of Items:",len(items_support))
    frequent_items = remove_less_support_items(items_support,minSup)  # After removing items with less support count.
    sorted_frequent_items = sort_items_on_Value(frequent_items)
    ordered_dataset = order_items(data,sorted_frequent_items)
    print("No of Frequent Items:",len(frequent_items))
    fp_tree = FP_tree()
    for itemset in ordered_dataset:
        fp_tree.insert(itemset,1)
    file = open("output.txt","w+")
    total_patterns,nodeCount = FP_growth(fp_tree,[],0,file,minSup)
    print("No of Frequent Patterns:",total_patterns)
    print("No of Nodes:",nodeCount)
    file.close()
    
    
    
if(__name__ == "__main__"):
    path = '/home/satya/Research/uday/'
    path += str(sys.argv[1])
    main(path,float(sys.argv[2]))         #upport in percentage
