import time
import tkinter as tk



class WASDHandler(tk.Frame):
    def __init__(self, parent, pycoordHandle):
        self.pycoordHandle = pycoordHandle
        tk.Frame.__init__(self, parent, width=400,  height=400)
        
        self.label = tk.Label(self, text="Press WASD to move! ", width=20)
        self.label.pack(fill="both", padx=100, pady=100)

        self.label.bind("<w>", self.onW)
        self.label.bind("<a>", self.onA)
        self.label.bind("<s>", self.onS)
        self.label.bind("<d>", self.onD)
        self.label.bind("<Return>", self.onEnter)

        # give keyboard focus to the label by default, and whenever
        # the user clicks on it
        self.label.focus_set()
        self.label.bind("<1>", lambda event: self.label.focus_set())

    def onW(self, event):
        self.pycoordHandle.relativePos(x= [50000,100000])


    def onA(self, event):
        self.pycoordHandle.relativePos(y= [50000,100000])


    def onS(self, event):
        self.pycoordHandle.relativePos(x= [-50000,100000])
         


    def onD(self, event):       
        self.pycoordHandle.relativePos(y= [-50000,100000])

    def onEnter(self, event):
        print("Enter")
        self.pycoordHandle.measurement_positions.append(self.pycoordHandle.getPos())
           

