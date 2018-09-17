
# coding: utf-8

# In[1]:


import csv
import sys
import itertools


# In[2]:


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


# In[3]:


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


# In[4]:


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


# In[5]:


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
        print (' |'*ind, self.id, '-', self.counter)
#         print (' |'*ind, self.id, '-', self.counter,file=file)
        for child in self.children:
            child.disp(file,ind+1)


# In[6]:


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


# In[7]:


def sort_items_and_add_support_column(d):
    '''
    Sort a dictionary based on the value.
    input: d - A dictionary with item names as keys and items support as value.
    output: Sort d based on the support and return the same.
    '''
    d_sorted = []
    for key in sorted(d, key=d.get,reverse=True):  #Sorting based on support value.
        d_sorted.append([key,0,d[key]])
    return d_sorted


# In[8]:


def generate_patterns(root,prefix,prefix_sup):
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


# In[9]:


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


# In[22]:


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


# In[60]:


def FP_growth(fp_tree,prefix,prefix_sup,output_file,MIS,lms):
    '''
    Final FP Growth Alogrithm.
    Generates Patterns if Tree is a single prefix path.
    If tree is not a single prefix path then conditional pattern base is generated and key is added to the 
    Prefix. Again FP tree is build on the conditional Pattern Base. A recursive step.
    '''
    count = 0;
    no_of_nodes = 0;
    frequent_patterns = []
    if(check_for_single_prefix_path(fp_tree.root)):
        if(prefix_sup >= MIS[prefix[0]]):
            count,frequent_patterns = generate_patterns(fp_tree.root,prefix,prefix_sup)
        if frequent_patterns:
            pass
#             print(frequent_patterns)
        return count,fp_tree.nodeCount
    else:
        if prefix:
            minsupport = MIS[prefix[0]]
            count += 1
#             print({tuple(prefix):prefix_sup})      # Very Important do not delete. Print an important pattern
        else:
            minsupport = lms

        conditional_pattern_base = fp_tree.find_coditional_pattern_base();
        conditional_pattern_base = del_infrequent(conditional_pattern_base,minsupport)  # Very important step to enhance the code.
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
            a,b = FP_growth(new_fp_tree,pre,prefix_sup,output_file,MIS,lms)
            count += a
            no_of_nodes += b
            
    return count,no_of_nodes
    


# In[61]:


def get_MIS(item_support,beta,minSup):
    MIS = {}
    for item,value in item_support.items():
        MIS[item] = max(beta*value,minSup)
    return MIS
    


# In[62]:


class MIS_tree:
    def __init__(self,MIS):
        self.MIS_list = sort_items_and_add_support_column(MIS)    #Sorting MIS and obtaining a array in which row represent [item name, MIS, support]
        self.prefix_tree = FP_tree()
    def createTree(self,data):
        for transaction in data:
            itemset = []
            for i in range(0,len(self.MIS_list)):
                key = self.MIS_list[i][0]
                if key in transaction:
                    self.MIS_list[i][1] += 1
                    itemset.append(self.MIS_list[i][0])
                    transaction.remove(key)
            self.prefix_tree.insert(itemset,1)
#         print(self.prefix_tree.header_table)
#         self.prefix_tree.root.disp("")
        
    def misPruning(self,item):
        node = self.prefix_tree.header_table[item][1]
        del self.prefix_tree.header_table[item]
        while(node):
            if not node.children:
                parent = node.parent
                parent.children.remove(node)
            else:
                parent = node.parent
                parent.children.remove(node)
                for x in node.children:     # ******************Enhanced Version *******************
                    flag = 0
                    for y in parent.children:
                        if(y.id == x.id):
                            y.inc(x.counter)
                            flag = 1
                            break
                    if(flag == 0):
                        parent.children.append(x)
            node = node.nextLink
        
    def inFrequentLeafNodePruning(self):
        length = len(self.MIS_list)
        for index in range(length - 2,-1,-1):
            if(self.MIS_list[index][1] < self.MIS_list[index][2]):  #support less than MIS then inFrequent
                node = self.prefix_tree.header_table[self.MIS_list[index][0]][1]  # Get node link.
                if(node != None):
                    flag = 1  # First Node
                    while(node):
                        if not node.children:  # If node is a child node. i.e., No Children
                            self.prefix_tree.header_table[self.MIS_list[index][0]][0] -= node.counter # Decrease value in header table.
                            if(flag == 1):  # Indicate that the node is first node linked to header table.
                                self.prefix_tree.header_table[self.MIS_list[index][0]][1] = node.nextLink
                                node.parent.children.remove(node)
                            else:
                                prev.nextLink = node.nextLink
                                node.parent.children.remove(node)
                        else:
                            flag = 0
                        prev = node
                        node = node.nextLink
                else:
                    del self.prefix_tree.header_table[self.MIS_list[index][0]]
                    del self.MIS_list[index]


# In[63]:


def createCompactMISTree(data,MIS):
    mis_tree= MIS_tree(MIS)
    mis_tree.createTree(data)
    length = len(mis_tree.MIS_list)
    header_table = mis_tree.MIS_list
    for index in range(length - 1,-1,-1):
        if(header_table[index][1] < header_table[index][2]):    # Support less than MIS
            mis_tree.misPruning(mis_tree.MIS_list[index][0])
            del mis_tree.MIS_list[index]
        else:
            LMS = mis_tree.MIS_list[index][2]
            break
            
    length = len(mis_tree.MIS_list)
    for index in range(length - 1, -1 ,-1):
        if(header_table[index][1] < LMS):    # Support less than Least minimum support
            mis_tree.misPruning(mis_tree.MIS_list[index][0])
            del mis_tree.MIS_list[index]
    mis_tree.inFrequentLeafNodePruning()
#     mis_tree.prefix_tree.root.disp("")
    return mis_tree,LMS



def main(pathToDataSet,beta,minSup):
    '''
    Inputs: pathToDataSet - Absolute path to the data set.
            MIS - A dictionary of minimum support value for every item.
    '''
    data = []   # Carries list of data and transactions.
    header_table = {}  # Header Table keeps track of all the nodes of same type.
    total_trans = 0
    with open(pathToDataSet,'r') as csvfile:
        plots = csv.reader(csvfile, delimiter=' ')
        for row in plots:
            data.append(row)
            total_trans += 1
    print("No of Transactions:",total_trans)
    minSup = (minSup*total_trans/100)
    item_support = find_support_for_every_item(data)
    item_support = sort_items_on_Value(item_support)
    MIS = get_MIS(item_support,beta,minSup)
#     print(MIS)
    tree,lms = createCompactMISTree(data,MIS)
    print("No of Frequent Items:",len(tree.prefix_tree.header_table))
    total_patterns,nodeCount = FP_growth(tree.prefix_tree,[],0,'',MIS,lms)
    print("No of Frequent Patterns:",total_patterns)
    print("No of Nodes:",nodeCount)



if(__name__ == "__main__"):
    path = '/home/satya/Research/uday/'
    path += str(sys.argv[1])
    main(path,float(sys.argv[2]),float(sys.argv[3]))     #support in percentage
