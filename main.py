from mainFrame import MainFrame
from tkinter import Tk

def main():
    root = Tk()
    root.wm_title("Segundo Proyecto de Modelación de Sistemas de Redes")
    app = MainFrame(root)
    app.mainloop()

if __name__=="__main__":
    main()