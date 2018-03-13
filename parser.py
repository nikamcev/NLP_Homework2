import nltk

from collections import defaultdict
from nltk.ccg.chart import printCCGDerivation
from nltk.ccg.lexicon import Token

from utils import *


class CCGParser:
    """ Parse CCG according to the CKY algorithm. """

    DEFAULT_START = AtomicCategory("S")
    DEFAULT_RULE_SET = []

    def __init__(self, lexicon, rules=DEFAULT_RULE_SET):
        self.lexicon = lexicon
        self.rules = rules

    @staticmethod
    @rule(DEFAULT_RULE_SET, 2, "A")
    def application(cat1, cat2):
        """
        Implements the combination rule for function application.
	   If cat1 and cat2 can be left or right-applied to each other (assuming cat1 is left of cat2),
	   return the resulting category. Otherwise, return None.
	   Hints:
		  * isinstance(cat, CombinedCategory) tells you whether a category is combined or atomic.
		  * For a combined category, cat.left and cat.right give the left and right subcategories.
		  * For a combined category, cat.direction is either "\\" or "/".
		  * You can use == to check whether categories are the same
	   """
	   #DETERMINE WHETHER "/" OR "\" THEN CHECK IF THINGS CAN BE COMBINED TO A RESULTANT CATEGORY BASED ON OPERATOR
	   #Do I do this recursively and see how far down categories can be simplified?
	
        #check to see if one or both are combined categories (cat1Sub/cat2Sub tell you if this is the case)
        cat1Sub = False
        cat2Sub = False
        if isinstance(cat1, CombinedCategory):
            cat1L = cat1.left
            cat1R = cat1.right
            cat1D = cat1.direction
            cat1Sub = True
        if isinstance(cat2, CombinedCategory):
            cat2L = cat2.left
            cat2R = cat2.right
            cat2D = cat2.direction
            cat2Sub = True

    #Currently written to handle cases where only one of the categories is a combined category (MIGHT HAVE TO CHANGE THIS)
        #if both are atomic
        if not cat1Sub and not cat2Sub:
            return None 
        else:
            if(cat1Sub and cat1D == "/") and (cat2 == cat1R):
                return(cat1L)
            #If the first category should precede the second
            elif(cat2Sub and cat2D == "\\") and (cat1 == cat2R):
                return(cat2L)
            else:                
                return None
       


    @staticmethod
    @rule(DEFAULT_RULE_SET, 2, "C")
    def composition(cat1, cat2):
        """
		Implements the combination rule for function composition.
		If cat1 and cat2 can be left or right-composed, return the resulting category.
		Otherwise, return None.
		"""
        cat1Sub = False
        cat2Sub = False
        if isinstance(cat1, CombinedCategory):
            cat1Sub = True
            cat1L = cat1.left
            cat1R = cat1.right
           
            cat1D = cat1.direction
        if isinstance(cat2, CombinedCategory):
            cat2Sub = True
            cat2L = cat2.left
          
            cat2R = cat2.right
            cat2D = cat2.direction
        if cat1Sub and cat2Sub:
            #If the first category is looking for a right-following category
            if cat1D == "/" and cat2D == "/" and cat1R == cat2L:
                cat3 = CombinedCategory(cat1L, "/", cat2R)
                return(cat3)
            #If the second category is looking for a preceding category
            elif(cat2D == "\\") and (cat1D == "\\") and cat2R == cat1L:
                cat3 = CombinedCategory(cat2L, "\\", cat1R)
                return(cat3)
            else:
                return None
        else:
            return None


    @staticmethod
    @rule(DEFAULT_RULE_SET, 1, "T")
    def typeRaising(cat1, cat2):
        """
		Implements the combination rule for type raising.
		If cat2 satisfies the type-raising constraints, type-raise cat1 (and vice-versa).
		Return value when successful should be the tuple (cat, dir):
			* cat is the resulting category of the type-raising
			* dir is "/" or "\\" and represents the direction of the raising
			* If no type-raising is possible, return None
		Hint: use cat.innermostFunction() to implement the conditional checks described in the
			specification.
		"""
        
       
        #If there are no atomic categories, return None; if there are only atomic categories, return None
        cat1Sub = False
        cat2Sub = False
        if isinstance(cat1, CombinedCategory):
            cat1Sub = True
            cat1L = cat1.left
            cat1R = cat1.right
            cat1D = cat1.direction
        if isinstance(cat2, CombinedCategory):
            cat2Sub = True
            cat2L = cat2.left
            cat2R = cat2.right
            cat2D = cat2.direction

        if cat1Sub and cat2Sub:
            return None
        elif(cat2Sub and isinstance(cat2.innermostFunction().right, AtomicCategory) and cat2.innermostFunction().direction == "\\" and cat1 == cat2.innermostFunction().right):
            cat3 = CombinedCategory(cat2.innermostFunction().left, "/", CombinedCategory(cat2.innermostFunction().left, "\\", cat1)) 
            return(cat3, cat3.direction)
        elif(cat1Sub and isinstance(cat1.innermostFunction().left, AtomicCategory) and cat1.innermostFunction().direction == "/"):
            cat3 = CombinedCategory(cat1.innermostFunction().left, "\\", CombinedCategory(cat1.innermostFunction().left, "/", cat2))
            return(cat3, cat3.direction)
        else:
            return None 



    class VocabException(Exception):
        pass

    def fillParseChart(self, tokens):
        """
		Builds and fills in a CKY parse chart for the sentence represented by tokens.
		The argument tokens is a list of words in the sentence.
		Each entry in the chart should be a list of Constituents:
			* Use AtomicConstituent(cat, word) to construct initialize Constituents of words.
			* Use CombinedConstituent(cat, leftPtr, rightPtr, rule) to construct Constituents
			  produced by rules. leftPtr and rightPtr are the Constituent objects that combined to
			  form the new Constituent, and rule should be the rule object itself.
		Should return (chart, parses), where parses is the final (top right) entry in the chart. 
		Each tuple in parses corresponds to a parse for the sentence.
		Hint: initialize the diagonal of the chart by looking up each token in the lexicon and then
			use self.rules to fill in the rest of the chart. Rules in self.rules are sorted by
			increasing arity (unary or binary), and you can use rule.arity to check the arity of a
			rule.
		"""
        # LAYOUT:
        #       Fill in the first diagonal in "for token in tokens:"
        #       Apply unary rules to this
        #       Apply unary/binary rules to combination of two by iterating from [0,2] --> [0,n] where n is the number 
        chart = defaultdict(list)
        # Go through tokens (each word in the sentence)
        pos = 0
        for token in tokens:
            #Get the categories for the word
            cats = self.lexicon.getCategories(token)
            #print cats
            #if there are none, print out error, exit
            if not cats:
                print "NO CATEGORIES FOR %s\n" % token
                exit(1)

          
            constituents = []
            #For each category, collect all atomic constituents for a word
            for cat in cats:
                constituents.append(AtomicConstituent(cat, token))
           
            #Add list of constituents to chart at index [word, 0] to fill diagonal
            
            """
            for item in constituents:
                print item.word
                print item.cat
            """
            
            chart[pos, pos+1] = constituents
            pos += 1 
        
        i = 2
        while i <= len(tokens):
            j = i-2
            while j >= 0:
                for rule in self.rules:
                    k = i - 1
                    while k > j:
                        constsR = chart[k, i]
                        constsL = chart[j, k]
                            
                        for constL in constsL:
                            for constR in constsR:
                                if rule(constL.cat, constR.cat) != None:
                                   
                                    if rule.arity == 2:
                                        
                
                                        chart[j, i].append(CombinedConstituent(rule(constL.cat, constR.cat), [constL, constR], rule))
                                    elif rule.arity == 1:
                                        #print rule(constL.cat, constR.cat)
                                        if rule(constL.cat, constR.cat)[1] == '/':     
                                            result_cat = rule(constL.cat, constR.cat)

                                            chart[j, k].append(CombinedConstituent(result_cat[0], [constL], rule))
                                            continue
                                        elif rule(constL.cat, constR.cat)[1] == '\\':
                                            result_cat = rule(constL.cat, constR.cat)

                                            chart[k, i].append(CombinedConstituent(result_cat[0], [constR], rule))
                                            continue
                        k -= 1                       
                j -= 1
            i += 1
 
       
        
        return(chart, chart[0, len(tokens)])

    @staticmethod
    def generateParseTree(cons, chart):
        """
		Helper function that returns an NLTK Tree object representing a parse.
		"""
        token = Token(None, cons.cat, None)
        if isinstance(cons, AtomicConstituent):
            return nltk.tree.Tree(
                (token, u"Leaf"),
                [nltk.tree.Tree(token, [cons.word])]
            )
        else:
            if cons.rule == CCGParser.typeRaising:
                return nltk.tree.Tree(
                    (token, cons.rule.name),
                    [CCGParser.generateParseTree(cons.ptrs[0], chart)]
                )
            else:
                return nltk.tree.Tree(
                    (token, cons.rule.name),
                    [CCGParser.generateParseTree(cons.ptrs[0], chart),
                     CCGParser.generateParseTree(cons.ptrs[1], chart)]
                )

    def getParseTrees(self, tokens):
        """
		Reconstructs parse trees for the sentences by following backpointers.
		"""
        chart, parses = self.fillParseChart(tokens)
        for cons in parses:
            yield CCGParser.generateParseTree(cons, chart)

    def accepts(self, tokens, sentCat=DEFAULT_START):
        """
		Return True iff the sentence represented by tokens is in this language (i.e. has at least
			one valid parse).
		"""
        _, parses = self.fillParseChart(tokens)
        for cons in parses:
            if cons.cat == sentCat: return True
        return False
