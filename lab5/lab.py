# NO ADDITIONAL IMPORTS!
from text_tokenize import tokenize_sentences


class Trie:
    def __init__(self):
        self.value = None
        self.children = {} #maps a string or tuple to a new Trie object
        self.type = None #will be changed to string or tuple


    def set(self, key, value):
        """
        Add a key with the given value to the trie, or reassign the associated
        value if it is already present in the trie.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is of
        the wrong type.
        """
        if self.type == None:
            self.type = type(key)
        elif self.type != type(key):
            raise TypeError
        
        #base case (when bottom of trie has been reached)
        if len(key) == 0:
            self.value = value
        
        else:
            letter = key[0:1]       
            if letter not in self.children: #create a new Trie for each new letter
                child = Trie()
                self.children[letter] = child
            self.children[letter].set(key[1:], value) #recursively call set for each letter    

    def get(self, key):
        """
        Return the value for the specified prefix.  If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        """
        if self.type != type(key):
            raise TypeError
        
        #base case (when bottom of trie has been reached)
        if len(key) == 0:
            return self.value
        
        else:
            letter = key[0:1]
            if letter not in self.children: #if letter doesn't exist in Trie
                raise KeyError
            return self.children[letter].get(key[1:]) #recusively traverse down the Trie

    def delete(self, key):
        """
        Delete the given key from the trie if it exists.
        """
        self.set(key, None)

    def contains(self, key):
        """
        Is key a key in the trie? return True or False.
        """
        #only returns True if the key has a value!
        if len(key) == 0:
            if self.value == None:
                return False
            return True
        else:
            letter = key[0:1]
            if letter in self.children:
                return self.children[letter].contains(key[1:]) #recusively traverse down the Trie
            return False

    def items(self, path=None):
        """
        Returns a list of (key, value) pairs for all keys/values in this trie and
        its children.
        """            
        result = []
        #add a node to the result if the node has a value
        if self.value != None:
            result.append((path, self.value))
        
        #recursively get the items for a node's children and add them to result
        #path stores the edges of the trie as you traverse down the graph
        if self.children != {}:
            for key, trie in self.children.items():
                if path == None:
                    subResult = trie.items(key) 
                else:
                    subResult = trie.items(path+key)
                #if a child trie has nodes with values, add them to result
                if subResult != []:
                    for tup in subResult:
                        result.append(tup)                     
        return result
    

def make_word_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text
    """
    #split text into a list of words
    text = tokenize_sentences(text)
    words = []
    for sentence in text:
        sentence = sentence.split()
        words = words+sentence
    
    root = Trie()
    for w in words:
        #if word isn't in trie, add it
        if not root.contains(w):
            root.set(w, 1)
        #if word is in trie, add 1 to it's value (frequency)
        else:
            value = root.get(w)
            root.set(w, value+1)
    return root

def make_phrase_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    sentences in the text (as tuples of individual words) and whose values are
    the number of times the associated sentence appears in the text.
    """
    #split text into tuples each containing a sentence
    text = tokenize_sentences(text)
    sentences = []
    for sent in text:
        sent = sent.split()
        sentences.append(tuple([x for x in sent]))
        
    root = Trie()
    for s in sentences:
        #if phrase isn't in trie, add it
        if not root.contains(s):
            root.set(s, 1)
        #if phrase is in trie, add 1 to it's value (frequency)
        else:
            value = root.get(s)
            root.set(s, value+1)
    return root                    

def autocomplete(trie, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is of an inappropriate type for the
    trie.
    """
    if trie.type != type(prefix):
        raise TypeError
    
    #sort trie's items by decreasing value    
    elems = trie.items()
    elems = sorted(elems, key=lambda x : x[1], reverse=True)
    
    result = []
    #return all valid items 
    if max_count == None:
        for tup in elems:
            if prefix == tup[0][:len(prefix)]:
                result.append(tup[0])
    #return max_count valid items
    else:
        for tup in elems:
            if prefix == tup[0][:len(prefix)] and len(result) < max_count:
                result.append(tup[0])
    return result

def autocorrect(trie, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    completions = autocomplete(trie, prefix, max_count)
    #if autocomplete already has least max_count items
    if max_count != None and len(completions) >= max_count:
        result = []
        for elem in completions:
            if len(result) < max_count:
                result.append(elem)
        return result
    
    edits = set([])
    for i in range(len(prefix)):
        
        #deleting a letter
        deletion = prefix[:i] + prefix[i+1:]
        if trie.contains(deletion):
            edits.add((deletion, trie.get(deletion)))
            
        for char in range(97,123):
            l = chr(char) #l will be a letter from a to z
            
            #inserting a letter
            insertion = prefix[:i] + l + prefix[i:]
            if trie.contains(insertion):
                edits.add((insertion, trie.get(insertion)))
            
            #replacing a letter
            replacement = prefix[:i] + l + prefix[i+1:]
            if trie.contains(replacement):
                edits.add((replacement, trie.get(replacement)))
                
            #swapping adjacent letters
            if i < len(prefix)-1:
                swap = prefix[:i] + prefix[i+1] + prefix[i] + prefix[i+2:]
                if trie.contains(swap):
                    edits.add((swap, trie.get(swap)))
    
    #get the most frequently occuring edits   
    if max_count != None:         
        numEdits = max_count - len(completions)
    edits = sorted(list(edits), key=lambda x : x[1], reverse=True)
    result = []
    for tup in edits:
        if max_count != None and len(result) < numEdits:
            result.append(tup[0])
        elif max_count == None:
            result.append(tup[0])
    return list(set(completions+result))


def word_filter(trie, pattern, path=''):
    """
    Return list of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    result = []
    if len(pattern) == 0:
        if trie.value != None:
            result.append((path, trie.value))
    else:    
        if pattern[0] == '*':
            result = result + word_filter(trie, pattern[1:], path)
        for l in trie.children:
            if pattern[0] == '?' or pattern[0] == l:
                 result = result + word_filter(trie.children[l], pattern[1:], path+l)
            elif pattern[0] == '*':
                 result = result + word_filter(trie.children[l], pattern, path+l)
    return list(set(result))


# you can include test cases of your own in the block below.
if __name__ == '__main__':
    with open("Pride and Prejudice.txt", encoding="utf-8") as f:
        text = f.read()
        
#    phrase = make_phrase_trie(text)
#    elems = phrase.items()
#    elems = sorted(list(elems), key=lambda x : x[1], reverse=True)
#    result = []
#    for i in range(4):
#        result.append(elems[i][0])
#    print(result)
    
    word = make_word_trie(text)
#    print(autocomplete(word, 'gre', 6))
#    print(autocorrect(word, 'tear', 9))
    result = []
    for i in word_filter(word, 'r?c*t'):
        result.append(i[0])
    print(result)
    
    pass
