from os import popen
import time

class Automata:
    """Class representing a Non-deterministic Finite Automaton (NFA)
    
    This class implements the core data structure and operations for NFAs,
    including state management, transitions, and visualization capabilities.
    """

    def __init__(self, language = set(['0', '1'])):
        """Initialize an empty automaton with the specified language
        
        Args:
            language: Set of symbols in the automaton's alphabet (default: {0,1})
        """
        self.states = set()           # Set of all states in the automaton
        self.startstate = None        # The starting state
        self.finalstates = []         # List of accepting/final states
        self.transitions = dict()     # Dictionary mapping: from_state -> {to_state -> symbols}
        self.language = language      # The alphabet of the automaton

    @staticmethod
    def epsilon():
        """Return the symbol representing epsilon (empty string) transitions"""
        return ":e:"

    def setstartstate(self, state):
        """Set the start state of the automaton and add it to states set
        
        Args:
            state: The state to set as the start state
        """
        self.startstate = state
        self.states.add(state)

    def addfinalstates(self, state):
        """Add one or more states to the set of final (accepting) states
        
        Args:
            state: A single state or list of states to add as final states
        """
        if isinstance(state, int):
            state = [state]
        for s in state:
            if s not in self.finalstates:
                self.finalstates.append(s)

    def addtransition(self, fromstate, tostate, inp):
        """Add a transition between states on the specified input symbol(s)
        
        Args:
            fromstate: Source state
            tostate: Destination state
            inp: Input symbol or set of input symbols for this transition
        """
        if isinstance(inp, str):
            inp = set([inp])
        self.states.add(fromstate)
        self.states.add(tostate)
        if fromstate in self.transitions:
            if tostate in self.transitions[fromstate]:
                self.transitions[fromstate][tostate] = self.transitions[fromstate][tostate].union(inp)
            else:
                self.transitions[fromstate][tostate] = inp
        else:
            self.transitions[fromstate] = {tostate : inp}

    def addtransition_dict(self, transitions):
        """Add multiple transitions from a dictionary structure
        
        Args:
            transitions: Dictionary of transitions to add to the automaton
        """
        for fromstate, tostates in transitions.items():
            for state in tostates:
                self.addtransition(fromstate, state, tostates[state])

    def gettransitions(self, state, key):
        """Get all states reachable from the given state(s) on the specified input
        
        Args:
            state: A state or list of states
            key: Input symbol to check transitions for
            
        Returns:
            Set of states reachable from the given state(s) on the input
        """
        if isinstance(state, int):
            state = [state]
        trstates = set()
        for st in state:
            if st in self.transitions:
                for tns in self.transitions[st]:
                    if key in self.transitions[st][tns]:
                        trstates.add(tns)
        return trstates

    def getEClose(self, findstate):
        """Find the epsilon-closure of a state (all states reachable via epsilon transitions)
        
        Args:
            findstate: The state to find epsilon-closure for
            
        Returns:
            Set of states reachable from the given state via epsilon transitions
        """
        allstates = set()
        states = set([findstate])
        # Breadth-first search for all states reachable via epsilon
        while len(states)!= 0:
            state = states.pop()
            allstates.add(state)
            if state in self.transitions:
                for tns in self.transitions[state]:
                    if Automata.epsilon() in self.transitions[state][tns] and tns not in allstates:
                        states.add(tns)
        return allstates

    def display(self):
        """Print the automaton details to standard output"""
        print("states:", self.states)
        print("start state: ", self.startstate)
        print("final states:", self.finalstates)
        print("transitions:")
        for fromstate, tostates in self.transitions.items():
            for state in tostates:
                for char in tostates[state]:
                    print("  ", fromstate, "->", state, "on '" + char + "'", end="")
            print()

    def getPrintText(self):
        """Get a formatted text representation and line count for GUI display
        
        Returns:
            tuple: [formatted_text, line_count]
        """
        text = "language: {" + ", ".join(self.language) + "}\n"
        text += "states: {" + ", ".join(map(str,self.states)) + "}\n"
        text += "start state: " + str(self.startstate) + "\n"
        text += "final states: {" + ", ".join(map(str,self.finalstates)) + "}\n"
        text += "transitions:\n"
        linecount = 5
        for fromstate, tostates in self.transitions.items():
            for state in tostates:
                for char in tostates[state]:
                    text += "    " + str(fromstate) + " -> " + str(state) + " on '" + char + "'\n"
                    linecount +=1
        return [text, linecount]

    def newBuildFromNumber(self, startnum):
        """Create a new automaton with renumbered states starting from startnum
        
        Args:
            startnum: The starting state number for the new automaton
            
        Returns:
            tuple: [new_automaton, next_available_state_number]
        """
        translations = {}
        for i in list(self.states):
            translations[i] = startnum
            startnum += 1
        rebuild = Automata(self.language)
        rebuild.setstartstate(translations[self.startstate])
        rebuild.addfinalstates(translations[self.finalstates[0]])
        for fromstate, tostates in self.transitions.items():
            for state in tostates:
                rebuild.addtransition(translations[fromstate], translations[state], tostates[state])
        return [rebuild, startnum]

    def newBuildFromEquivalentStates(self, equivalent, pos):
        """Create a new automaton from equivalent states mapping
        
        Args:
            equivalent: List of equivalent states
            pos: Dictionary mapping original states to new positions
            
        Returns:
            New automaton with equivalent states combined
        """
        rebuild = Automata(self.language)
        for fromstate, tostates in self.transitions.items():
            for state in tostates:
                rebuild.addtransition(pos[fromstate], pos[state], tostates[state])
        rebuild.setstartstate(pos[self.startstate])
        for s in self.finalstates:
            rebuild.addfinalstates(pos[s])
        return rebuild

    def getDotFile(self):
        """Generate a DOT file representation for GraphViz visualization
        
        Returns:
            String containing DOT format representation of the automaton
        """
        dotFile = "digraph DFA {\nrankdir=LR\n"
        if len(self.states) != 0:
            dotFile += "root=s1\nstart [shape=point]\nstart->s%d\n" % self.startstate
            for state in self.states:
                if state in self.finalstates:
                    dotFile += "s%d [shape=doublecircle]\n" % state
                else:
                    dotFile += "s%d [shape=circle]\n" % state
            for fromstate, tostates in self.transitions.items():
                for state in tostates:
                    for char in tostates[state]:
                        dotFile += 's%d->s%d [label="%s"]\n' % (fromstate, state, char)
        dotFile += "}"
        return dotFile

class BuildAutomata:
    """Class for building elementary NFA structures using Thompson's Construction
    
    This class provides static methods to create basic NFA components
    and combine them into more complex structures according to
    Thompson's construction algorithm for converting regex to NFA.
    """

    @staticmethod
    def basicstruct(inp):
        """Create a basic NFA that accepts a single character
        
        Structure: state1 --(inp)--> state2
        
        Args:
            inp: The input symbol this NFA should accept
            
        Returns:
            Automata: A simple two-state NFA that accepts only the input symbol
        """
        state1 = 1
        state2 = 2
        basic = Automata()
        basic.setstartstate(state1)
        basic.addfinalstates(state2)
        basic.addtransition(1, 2, inp)
        return basic

    @staticmethod
    def ORstruct(a, b):
        """Combine two NFAs with an OR operation (union)
        
        Creates an NFA that accepts either pattern a OR pattern b
        
        Structure:
                  ε     
            ---> a ---->
           /           \
        1 -             -> 4
           \           /
            ---> b ---->
                  ε
        
        Args:
            a, b: The two automata to combine with OR
            
        Returns:
            Automata: Combined NFA accepting either a or b
        """
        [a, m1] = a.newBuildFromNumber(2)
        [b, m2] = b.newBuildFromNumber(m1)
        state1 = 1
        state2 = m2
        plus = Automata()
        plus.setstartstate(state1)
        plus.addfinalstates(state2)
        plus.addtransition(plus.startstate, a.startstate, Automata.epsilon())
        plus.addtransition(plus.startstate, b.startstate, Automata.epsilon())
        plus.addtransition(a.finalstates[0], plus.finalstates[0], Automata.epsilon())
        plus.addtransition(b.finalstates[0], plus.finalstates[0], Automata.epsilon())
        plus.addtransition_dict(a.transitions)
        plus.addtransition_dict(b.transitions)
        return plus

    @staticmethod
    def DOTstruct(a, b):
        """Combine two NFAs with concatenation (DOT operation)
        
        Creates an NFA that accepts pattern a followed by pattern b
        
        Structure:
        1 ---> a --ε--> b ---> last
        
        Args:
            a, b: The two automata to concatenate
            
        Returns:
            Automata: Combined NFA accepting a followed by b
        """
        [a, m1] = a.newBuildFromNumber(1)
        [b, m2] = b.newBuildFromNumber(m1)
        state1 = 1
        state2 = m2-1
        dot = Automata()
        dot.setstartstate(state1)
        dot.addfinalstates(state2)
        dot.addtransition(a.finalstates[0], b.startstate, Automata.epsilon())
        dot.addtransition_dict(a.transitions)
        dot.addtransition_dict(b.transitions)
        return dot

    @staticmethod
    def starstruct(a):
        """Apply the Kleene star operation to an NFA
        
        Creates an NFA that accepts zero or more repetitions of pattern a
        
        Structure:
                 ε
                 ┌─────┐
                 ▼     │
        1 --ε--> a --ε--+--ε--> 4
        │                       ▲
        └───────────ε───────────┘
        
        Args:
            a: The automaton to apply the star operation to
            
        Returns:
            Automata: NFA accepting zero or more repetitions of a
        """
        [a, m1] = a.newBuildFromNumber(2)
        state1 = 1
        state2 = m1
        star = Automata()
        star.setstartstate(state1)
        star.addfinalstates(state2)
        star.addtransition(star.startstate, a.startstate, Automata.epsilon())
        star.addtransition(star.startstate, star.finalstates[0], Automata.epsilon())
        star.addtransition(a.finalstates[0], star.finalstates[0], Automata.epsilon())
        star.addtransition(a.finalstates[0], a.startstate, Automata.epsilon())
        star.addtransition_dict(a.transitions)
        return star

class NFAfromRegex:
    """class for building e-nfa from regular expressions"""

    def __init__(self, regex):
        self.star = '*'
        self.OR = '|'
        self.dot = '.'
        self.openingBracket = '('
        self.closingBracket = ')'
        self.operators = [self.OR, self.dot]
        self.regex = regex
        self.alphabet = [chr(i) for i in range(65,91)]
        self.alphabet.extend([chr(i) for i in range(97,123)])
        self.alphabet.extend([chr(i) for i in range(48,58)])
        self.buildNFA()

    def getNFA(self):
        return self.nfa

    def displayNFA(self):
        self.nfa.display()

    def buildNFA(self): 
        language = set()
        self.stack = []
        self.automata = []
        previous = "::e::"
        for char in self.regex: # loop throw charchters
            if char in self.alphabet:
                language.add(char)
                if previous != self.dot and (previous in self.alphabet or previous in [self.closingBracket,self.star]):
                    self.addOperatorToStack(self.dot)
                self.automata.append(BuildAutomata.basicstruct(char))
            elif char  ==  self.openingBracket:
                if previous != self.dot and (previous in self.alphabet or previous in [self.closingBracket,self.star]):
                    self.addOperatorToStack(self.dot)
                self.stack.append(char)
            elif char  ==  self.closingBracket:
                if previous in self.operators:
                    raise BaseException("Error processing '%s' after '%s'" % (char, previous))
                while(1):
                    if len(self.stack) == 0:
                        raise BaseException("Error processing '%s'. Empty stack" % char)
                    o = self.stack.pop()
                    if o == self.openingBracket:
                        break
                    elif o in self.operators:
                        self.processOperator(o)
            elif char == self.star:
                if previous in self.operators or previous  == self.openingBracket or previous == self.star:
                    raise BaseException("Error processing '%s' after '%s'" % (char, previous))
                self.processOperator(char)
            elif char in self.operators:
                if previous in self.operators or previous  == self.openingBracket:
                    raise BaseException("Error processing '%s' after '%s'" % (char, previous))
                else:
                    self.addOperatorToStack(char)
            else:
                raise BaseException("Symbol '%s' is not allowed" % char)
            previous = char
        while len(self.stack) != 0:
            op = self.stack.pop()
            self.processOperator(op)
        if len(self.automata) > 1:
            print(self.automata)
            raise BaseException("Regex could not be parsed successfully")
        self.nfa = self.automata.pop()
        self.nfa.language = language

    def addOperatorToStack(self, char):
        while(1):
            if len(self.stack) == 0:
                break
            top = self.stack[len(self.stack)-1]
            if top == self.openingBracket:
                break
            if top == char or top == self.dot:
                op = self.stack.pop()
                self.processOperator(op)
            else:
                break
        self.stack.append(char)

    def processOperator(self, operator):
        if len(self.automata) == 0:
            raise BaseException("Error processing operator '%s'. Stack is empty" % operator)
        if operator == self.star:
            a = self.automata.pop()
            self.automata.append(BuildAutomata.starstruct(a))
        elif operator in self.operators:
            if len(self.automata) < 2:
                raise BaseException("Error processing operator '%s'. Inadequate operands" % operator)
            a = self.automata.pop()
            b = self.automata.pop()
            if operator == self.OR:
                self.automata.append(BuildAutomata.plusstruct(b,a))
            elif operator == self.dot:
                self.automata.append(BuildAutomata.dotstruct(b,a))

def drawGraph(automata, file = ""):
    """From https://github.com/max99x/automata-editor/blob/master/util.py"""
    f = popen(r"dot -Tpng -o graph%s.png" % file, 'w')
    try:
        f.write(automata.getDotFile())
    except:
        raise BaseException("Error creating graph")
    finally:
        f.close()

def isInstalled(program):
    """From http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python"""
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program) or is_exe(program+".exe"):
            return True
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file) or is_exe(exe_file+".exe"):
                return True
    return False