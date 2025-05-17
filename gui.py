import sys
import time

try:
    from tkinter import *
    from tkinter import font as tkFont
    from tkinter import ttk
except ImportError:
    print("Error: Tkinter library is required for using the GUI.")
    sys.exit(1)

from AutomataTheory import *


def simulate_nfa(nfa, input_string):
    def dfs(states, index):
        if index == len(input_string):
            return any(s in nfa.finalstates for state in states for s in nfa.getEClose(state))

        symbol = input_string[index]
        next_states = set()

        for state in states:
            for s in nfa.getEClose(state):
                for t in nfa.gettransitions(s, symbol):
                    next_states.update(nfa.getEClose(t))

        return dfs(next_states, index + 1)

    start_states = nfa.getEClose(nfa.startstate)
    return dfs(start_states, 0)


class AutomataGUI:

    def __init__(self, root, dotFound):
        self.root = root
        self.dotFound = dotFound
        self.selectedButton = 0
        self.initUI()
        startRegex = "(0+1)*.0.1*.0"
        self.regexVar.set(startRegex)
        self.handleBuildRegexButton()

    def initUI(self):
        self.root.title("Automata From Regular Expressions")
        ScreenSizeX = self.root.winfo_screenwidth()
        ScreenSizeY = self.root.winfo_screenheight()
        self.FrameSizeX = int(ScreenSizeX * 0.7)
        self.FrameSizeY = int(ScreenSizeY * 0.8)
        FramePosX = int((ScreenSizeX - self.FrameSizeX) / 2)
        FramePosY = int((ScreenSizeY - self.FrameSizeY) / 2)
        self.root.geometry(f"{self.FrameSizeX}x{self.FrameSizeY}+{FramePosX}+{FramePosY}")
        self.root.resizable(False, False)

        padX = 10
        padY = 10
        parentFrame = Frame(self.root, width=self.FrameSizeX - 2 * padX, height=self.FrameSizeY - 2 * padY)
        parentFrame.grid(padx=padX, pady=padY, sticky=E + W + N + S)

        regexFrame = Frame(parentFrame)
        Label(regexFrame, text="Enter regular expression [use + for union, . for concat, * for star]:").grid(row=0, column=0, sticky=W)
        self.regexVar = StringVar()
        self.regexField = Entry(regexFrame, width=80, textvariable=self.regexVar)
        self.regexField.grid(row=1, column=0, sticky=W)
        Button(regexFrame, text="Build", width=10, command=self.handleBuildRegexButton).grid(row=1, column=1, padx=5)

        testStringFrame = Frame(parentFrame)
        Label(testStringFrame, text="Enter a test string: ").grid(row=0, column=0, sticky=W)
        self.testVar = StringVar()
        self.testStringField = Entry(testStringFrame, width=80, textvariable=self.testVar)
        self.testStringField.grid(row=1, column=0, sticky=W)
        Button(testStringFrame, text="Test", width=10, command=self.handleTestStringButton).grid(row=1, column=1, padx=5)

        self.statusLabel = Label(parentFrame)

        buttonGroup = Frame(parentFrame)
        self.timingLabel = Label(buttonGroup, text="Idle...", width=50, justify=LEFT)
        nfaButton = Button(buttonGroup, text="NFA", width=15, command=self.handlenfaButton)
        transitionButton = Button(buttonGroup, text="Transitions", width=15, command=self.showTransitionTable)
        #graphButton = Button(buttonGroup, text="Show Graph", width=15, command=self.showGraph)

        self.timingLabel.grid(row=0, column=0, sticky=W)
        nfaButton.grid(row=0, column=1)
        transitionButton.grid(row=0, column=2)
        #graphButton.grid(row=0, column=3)

        automataCanvasFrame = Frame(parentFrame, height=100, width=100)
        self.cwidth = self.FrameSizeX - (2 * padX + 20)
        self.cheight = int(self.FrameSizeY * 0.6)
        self.automataCanvas = Canvas(automataCanvasFrame, bg='#FFFFFF', width=self.cwidth, height=self.cheight, scrollregion=(0, 0, self.cwidth, self.cheight))
        hbar = Scrollbar(automataCanvasFrame, orient=HORIZONTAL)
        hbar.pack(side=BOTTOM, fill=X)
        hbar.config(command=self.automataCanvas.xview)
        vbar = Scrollbar(automataCanvasFrame, orient=VERTICAL)
        vbar.pack(side=RIGHT, fill=Y)
        vbar.config(command=self.automataCanvas.yview)
        self.automataCanvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvasitems = []
        self.automataCanvas.pack()

        self.bottomLabel = Label(parentFrame, text="")

        regexFrame.grid(row=0, column=0, sticky=W, padx=(50, 0))
        testStringFrame.grid(row=1, column=0, sticky=W, padx=(50, 0))
        self.statusLabel.grid(row=2, column=0, sticky=W, padx=(50, 0))
        buttonGroup.grid(row=3, column=0)
        automataCanvasFrame.grid(row=4, column=0, sticky=E + W + N + S)
        self.bottomLabel.grid(row=5, column=0, sticky=W, pady=10)

    def handleBuildRegexButton(self):
        t = time.time()
        try:
            inp = self.regexVar.get().replace(' ', '')
            if inp == '':
                self.statusLabel.config(text="Detected empty regex!")
                return
            if self.createAutomata(inp):
                self.displayAutomata()
        except BaseException as e:
            self.statusLabel.config(text=f"Failure: {e}")
        self.timingLabel.configure(text="Operation completed in %.4f seconds" % (time.time() - t))

    def handleTestStringButton(self):
        t = time.time()
        input_str = self.testVar.get().strip()

        if not hasattr(self, 'nfa'):
            self.statusLabel.config(text="Please build the automaton first.")
            return

        if input_str == "":
            result = any(s in self.nfa.finalstates for s in self.nfa.getEClose(self.nfa.startstate))
        else:
            result = simulate_nfa(self.nfa, input_str)

        if result:
            self.statusLabel.config(text=" Accepts!")
        else:
            self.statusLabel.config(text=" Does not accept.")

        self.timingLabel.configure(text="Test completed in %.4f seconds" % (time.time() - t))

    def handlenfaButton(self):
        if not hasattr(self, 'nfa'):
            self.statusLabel.config(text="Please build the automaton first.")
            return

        transition_window = Toplevel(self.root)
        transition_window.title("NFA Transitions")
        transition_window.geometry("600x500")

        tree = ttk.Treeview(transition_window)
        tree["columns"] = ("From", "To", "Symbol")
        tree.column("#0", width=0, stretch=NO)
        tree.column("From", anchor=CENTER, width=100)
        tree.column("To", anchor=CENTER, width=100)
        tree.column("Symbol", anchor=CENTER, width=100)

        tree.heading("From", text="From State", anchor=CENTER)
        tree.heading("To", text="To State", anchor=CENTER)
        tree.heading("Symbol", text="Symbol", anchor=CENTER)

        for from_state in self.nfa.transitions:
            for to_state in self.nfa.transitions[from_state]:
                symbols = self.nfa.transitions[from_state][to_state]
                for symbol in symbols:
                    tree.insert("", "end", values=(from_state, to_state, symbol))

        tree.pack(expand=True, fill=BOTH)

    def showGraph(self):
        if not self.dotFound or not hasattr(self, 'nfaimg'):
            self.statusLabel.config(text="Graph image not available. Ensure GraphViz and PIL are installed.")
            return

        graph_window = Toplevel(self.root)
        graph_window.title("NFA Graph")
        graph_window.geometry("800x600")

        canvas = Canvas(graph_window, bg='white')
        canvas.pack(fill=BOTH, expand=True)
        canvas.create_image(10, 10, anchor=NW, image=self.nfaimg)

    def showTransitionTable(self):
        if not hasattr(self, 'nfa'):
            self.statusLabel.config(text="Please build the automaton first.")
            return

        transition_window = Toplevel(self.root)
        transition_window.title("NFA Transition Table")
        transition_window.geometry("600x500")

        Label(transition_window, text="", font=("Courier", 14)).pack(pady=10)

        frame = Frame(transition_window)
        frame.pack()

        columns = ["State", "0", "1", ":e:"]
        for col, text in enumerate(columns):
            Label(frame, text=text, font=("Courier", 12, "bold"), borderwidth=1, relief="solid", width=10).grid(row=0, column=col)

        states = sorted(self.nfa.states)
        for i, state in enumerate(states, start=1):
            Label(frame, text=str(state), font=("Courier", 12), borderwidth=1, relief="solid", width=10).grid(row=i, column=0)

            for j, symbol in enumerate(["0", "1", self.nfa.epsilon()], start=1):
                targets = []
                for to_state in self.nfa.transitions.get(state, {}):
                    symbols = self.nfa.transitions[state][to_state]
                    if symbol in symbols:
                        targets.append(str(to_state))
                cell_value = ",".join(sorted(targets)) if targets else "--"
                Label(frame, text=cell_value, font=("Courier", 12), borderwidth=1, relief="solid", width=10).grid(row=i, column=j)

    def createAutomata(self, inp):
        try:
            print("Regex: ", inp)
            nfaObj = NFAfromRegex(inp)
            self.nfa = nfaObj.getNFA()
            if self.dotFound:
                drawGraph(self.nfa, "nfa")
                nfafile = "graphnfa.png"
                self.nfaimagefile = Image.open(nfafile)
                self.nfaimg = ImageTk.PhotoImage(self.nfaimagefile)
            return True
        except Exception as e:
            self.statusLabel.config(text=f"Regex build error: {e}")
            return False

    def displayAutomata(self):
        for item in self.canvasitems:
            self.automataCanvas.delete(item)

        if self.selectedButton == 0:
            header = "Regex-NFA"
            automata = self.nfa
            if self.dotFound:
                image = self.nfaimg
                imagefile = self.nfaimagefile

        font = tkFont.Font(family="times", size=20)
        headerheight = font.metrics("linespace") + 10
        itd = self.automataCanvas.create_text(10, 10, text=header, font=font, anchor=NW)
        self.canvasitems.append(itd)

        [text, linecount] = automata.getPrintText()
        font = tkFont.Font(family="times", size=13)
        textheight = headerheight + linecount * font.metrics("linespace") + 20
        itd = self.automataCanvas.create_text(10, headerheight + 10, text=text, font=font, anchor=NW)
        self.canvasitems.append(itd)

        if self.dotFound:
            itd = self.automataCanvas.create_image(10, textheight, image=image, anchor=NW)
            self.canvasitems.append(itd)
            totalwidth = imagefile.size[0] + 10
            totalheight = imagefile.size[1] + textheight + 10
        else:
            totalwidth = self.cwidth + 10
            totalheight = textheight + 10

        if totalheight < self.cheight:
            totalheight = self.cheight
        if totalwidth < self.cwidth:
            totalwidth = self.cwidth

        self.automataCanvas.config(scrollregion=(0, 0, totalwidth, totalheight))

def main():
    global dotFound
    dotFound = isInstalled("dot")
    if dotFound:
        try:
            from PIL import Image, ImageTk
        except ImportError as err:
            print("Notice: %s. The PIL library is required for displaying the graphs." % err)
            dotFound = False
    else:
        print("Notice: The GraphViz software is required for displaying the graphs.")

    root = Tk()
    app = AutomataGUI(root, dotFound)
    root.mainloop()

if __name__ == '__main__':
    main()
