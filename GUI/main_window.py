import tkinter as tk
from GUI.frame_menu import Menu
from GUI.frame_selection_niveau import SelectionNiveau
from GUI.frame_jeu import Jeu
from GUI.frame_creation import Creation


class MainWindow(tk.Tk):
    """
    Application gérant la fenêtre principale

    Attributs principaux :
        int width: Longueur de la fenêtre
        int height: Hauteur de la fenêtre
        int min_canvas_width: Longueur minimum possible pour le canvas
        int min_canvas_height: Hauteur minimum possible pour le canvas
        int scale: Facteur d'échelle pour le canvas
        int width_side_panel: Longueur que doit avoir le side panel
        int height_top_panel: Hauteur que doit avoir le top panel

        dict(str: tk.Frame) frames: Dictionnaire contenant les frames correspondant aux différentes scènes.
    """

    def __init__(self):
        """
        Initialise l'application, défini le titre, l'icône, la taille de la fenêtre, etc...
        """
        super().__init__()
        self.title("Labybouffe")
        self.wm_iconphoto(True, tk.PhotoImage(file="GUI/Menu images/icon.png"))

        self.width, self.height = 0, 0
        self.min_canvas_width, self.min_canvas_height = 11, 6
        self.scale = 1
        self.width_side_panel = 0
        self.height_top_panel = 0

        self.find_width_height()

        pos_right = int(self.winfo_screenwidth() / 2 - self.width / 2)
        pos_down = int(self.winfo_screenheight() / 2.25 - self.height / 2)
        self.geometry(f"{self.width}x{self.height}+{pos_right}+{pos_down}")
        self.resizable(False, False)
        self.unbind_all('<<NextWindow>>')

        self.create_widgets()

    def find_width_height(self):
        """
        Mets à jour les variables de taille et d'échelle des éléments de la fenêtre graphique en fonction de la taille de l'écran
        """
        self.width_side_panel = self.winfo_screenwidth() * 2 // 15
        self.height_top_panel = self.winfo_screenheight() * 1 // 15

        width = 0
        height = 0
        i = 1
        while width < self.winfo_screenwidth() and height < self.winfo_screenheight() and i <= 7:
            i += 1
            width = self.min_canvas_width * 2**i + self.width_side_panel
            height = self.min_canvas_height * 2**i + self.height_top_panel

        self.scale = i - 1
        self.width = self.min_canvas_width * 2**self.scale + self.width_side_panel
        self.height = self.min_canvas_height * 2**self.scale + self.height_top_panel

    def create_widgets(self):
        """
        Crée les widgets Frame, les initialise et les place
        """
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for Frame in (Menu, SelectionNiveau, Jeu, Creation):
            page_name = Frame.__name__
            frame = Frame(parent=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.switch_frame("Menu")

    def switch_frame(self, frame_name, param=None):
        """
        Mets au premier plan la Frame de nom frame_name et appelle sa fonction d'initialisation

        Paramètres :
            str frame_name: Nom de la classe de la frame qui doit être mise au premier plan
            Any param: (Optionnel) Paramètre qui doit être passé à la fonction d'initialisation
        """
        self.frames[frame_name].tkraise()

        if param is not None:
            self.frames[frame_name].reset(param)
        else:
            self.frames[frame_name].reset()
