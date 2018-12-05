
import tkinter as tk
from PIL import Image, ImageTk
from game.GameState import GameState

class TreeViewer:
    def __init__(self):

        pass
    
    def show(self, state):
        root = tk.Tk()
        root.geometry("640x480")

        img = Image.open('./gameboard.png', 'r')
        img = img.resize((640, 480), Image.ANTIALIAS)
        self.img_gameboard = ImageTk.PhotoImage(img)

        label = tk.Label(root, image=self.img_gameboard)
        label.pack()

        root.mainloop()


if __name__ == '__main__':
    TreeViewer().show(None)