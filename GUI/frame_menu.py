import tkinter as tk
from PIL import Image, ImageTk


class Menu(tk.Frame):
    """
    Frame gérant la scène de menu

    Attributs principaux :
        tk.Tk parent: Fenêtre parente sur laquelle est placée la frame. Doit posséder une méthode switch_frame pour
                      changer de scène et les attributs utilisés dans le init
        int width: Longueur de la fenêtre
        int height: Hauteur de la fenêtre
        int min_canvas_width: Longueur minimum possible pour le canvas
        int min_canvas_height: Hauteur minimum possible pour le canvas
        int scale: Facteur d'échelle pour le canvas
        int width_side_panel: Longueur que doit avoir le side panel
        int height_top_panel: Hauteur que doit avoir le top panel
    """

    def __init__(self, parent):
        """
        Initialise la frame et récupère les paramètres de taille du parent et de ses propres composants

        Paramètres :
            tk.Tk parent: Fenêtre parente sur laquelle est placée la frame. Doit posséder une méthode switch_frame pour
                          changer de scène et les attributs utilisés dans le init
        """
        self.parent = parent

        self.width, self.height = self.parent.width, self.parent.height
        self.min_canvas_width, self.min_canvas_height = self.parent.min_canvas_width, self.parent.min_canvas_height
        self.scale = self.parent.scale
        self.width_side_panel = self.parent.width_side_panel
        self.height_top_panel = self.parent.height_top_panel

        super().__init__(self.parent, width=self.width, height=self.height)

        self.create_widgets()

    def create_widgets(self):
        """
        Crée les différents widgets présents sur la frame et initialise les variables qui y sont liées
        """
        self.grid_propagate(False)

        nb_rows = 16
        nb_columns = 8

        for i in range(nb_rows):
            self.grid_rowconfigure(i, weight=1)
        for i in range(nb_columns):
            self.grid_columnconfigure(i, weight=1)

        self.image_bg = Image.open('GUI/Menu images/bg.png')
        self.image_bg = self.image_bg.resize((int(self.width), int(self.height)))
        self.image_bg_tk = ImageTk.PhotoImage(self.image_bg)
        self.label_bg = tk.Label(self, image = self.image_bg_tk)
        self.label_bg.grid(row=0, column=0, rowspan=nb_rows, columnspan=nb_columns)

        self.labelt1 = tk.Label(self, text="Bienvenue au LabyBouffe !", font = ("Showcard Gothic", 30), bg="#92D4F7")
        self.labelt1.grid(row=0, column=0, columnspan=nb_columns)
        self.labelt2 = tk.Label(self, text="Découvrez notre menu :", font = ("Showcard Gothic", 25), bg="#92D4F7")
        self.labelt2.grid(row=1, column=0, columnspan=nb_columns)

        self.bouton_1 = tk.Button(self, text="Plat du jour", font = ("Bernard MT Condensed", 15), bg="#FFFFFF")
        self.bouton_1.grid(row=4, column=1, sticky="w")
        self.bouton_1.bind("<Button-1>", self.creation_button_callback)
        self.labelb1 = tk.Label(self, text="Créez votre propre niveau et tentez de le battre!", font = ("Bernard MT Condensed", 12), bg="#92D4F7")
        self.labelb1.grid(row=5, column=1, sticky="w")

        self.bouton_2 = tk.Button(self, text="Menu étudiant", font = ("Bernard MT Condensed", 15), bg="#FFFFFF")
        self.bouton_2.grid(row=9, column=1, sticky="w")
        self.bouton_2.bind("<Button-1>", self.level_selection_button_callback)
        self.labelb2 = tk.Label(self, text="Tentez de battre les niveaux cuisinés spécialement pour vous!", font = ("Bernard MT Condensed", 12), bg="#92D4F7")
        self.labelb2.grid(row=10, column=1, sticky="w")

        self.image_bouton1 = Image.open('GUI/Menu images/homer_bouton.png')
        self.image_bouton1 = self.image_bouton1.resize((int(self.width*0.056), int(self.width*0.056)))
        self.image_bouton_tk1 = ImageTk.PhotoImage(self.image_bouton1)
        self.label_image1 = tk.Label(self, image = self.image_bouton_tk1, bg="#92D4F7")
        self.label_image1.grid(row=4, column=0)

        self.label_image2 = tk.Label(self, image = self.image_bouton_tk1, bg="#92D4F7")
        self.label_image2.grid(row=9, column=0)

        self.image_label1 = Image.open('GUI/Menu images/pointeur.png')
        self.image_label1 = self.image_label1.resize((int(self.width*0.056), int(self.height*0.06)))
        self.image_label_tk1 = ImageTk.PhotoImage(self.image_label1)
        self.label_pointeur = tk.Label(self, image = self.image_label_tk1, bg="#92D4F7")
        self.label_pointeur.grid(row=5, column=0)

        self.image_label2 = tk.Label(self, image = self.image_label_tk1, bg="#D5F0FF")
        self.image_label2.grid(row=10, column=0)

    def reset(self):
        """
        Réinitialise la frame (Rien besoin de faire pour cette Frame)
        """
        pass

    def creation_button_callback(self, event):
        """
        Change la scène pour la Frame Creation

        Paramètres :
            event: Événement tkinter
        """
        self.parent.switch_frame("Creation")

    def level_selection_button_callback(self, event):
        """
        Change la scène pour la Frame SelectionNiveau

        Paramètres :
            event: Événement tkinter
        """
        self.parent.switch_frame("SelectionNiveau")
