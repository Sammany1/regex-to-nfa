from AutomataTheory import *
import sys

def main():
    inp = "(01*1)*1"
    if len(sys.argv)>1:
        inp = sys.argv[1]
    print("Regular Expression: ", inp)
    nfaObj = NFAfromRegex(inp)
    nfa = nfaObj.getNFA()
    print("\nNFA: ")
    nfaObj.displayNFA()
    if isInstalled("dot"):        
        drawGraph(nfa, "nfa")
        print("\nGraphs have been created in the code directory")

if __name__  ==  '__main__':
    t = time.time()
    try:
        main()
    except BaseException as e:
        print("\nFailure:", e)
    print("\nExecution time: ", time.time() - t, "seconds")