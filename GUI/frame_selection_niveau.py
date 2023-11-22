import tkinter as tk
from PIL import Image, ImageTk
import json


class SelectionNiveau(tk.Frame):
    """
    Frame gérant la scène de sélection de niveau

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
        int width_canvas: Longueur que doit avoir le canvas
        int height_canvas: Hauteur que doit avoir le canvas

        list(tk.Frame) frames: Liste contenant les frames sur lesquelles sont situés les boutons pour jouer aux différents niveaux
        int i_frame: Indice dans self.frames de la frame qui doit être affiché en premier plan
        list(ImageTk.PhotoImage) button_images: Liste pour stocker les images des boutons afin qu'elles soient correctement affichées
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

        self.width_canvas = self.min_canvas_width * 2 ** self.scale
        self.height_canvas = self.min_canvas_height * 2 ** self.scale

        self.frames = []
        self.i_frame = 0
        self.button_images = []

        self.create_widgets()
        self.reset()

    def create_widgets(self):
        """
        Crée les différents widgets présents sur la frame et initialise les variables qui y sont liées
        """
        self.grid_propagate(False)

        self.nb_rows = 16
        self.nb_columns = 16

        for i in range(self.nb_rows):
            self.grid_rowconfigure(i, weight=1)
        for i in range(self.nb_columns):
            self.grid_columnconfigure(i, weight=1)

        self.image_bg = Image.open('GUI/Menu images/ciel.png')
        self.image_bg = self.image_bg.resize((int(self.width), int(self.height)))
        self.image_bg_tk = ImageTk.PhotoImage(self.image_bg)
        self.label_bg = tk.Label(self, image=self.image_bg_tk)
        self.label_bg.grid(row=0, column=0, rowspan=self.nb_rows, columnspan=self.nb_columns)

        self.labelt2 = tk.Label(self, text="Sélectionnez un niveau !", font = ("Showcard Gothic", 25), bg="#92D4F7")
        self.labelt2.grid(row=0, column=0, columnspan=self.nb_columns)

        self.image_bouton1 = Image.open('GUI/Menu images/homer_bouton.png')
        self.image_bouton1 = self.image_bouton1.resize((int(self.width * 0.05), int(self.width * 0.05)))
        self.image_bouton_tk1 = ImageTk.PhotoImage(self.image_bouton1)
        self.label_image2 = tk.Label(self, image=self.image_bouton_tk1, bg="#92D4F7")
        self.label_image2.grid(row=0, column=0)

        self.bouton_menu = tk.Button(self, text ='Menu', font = ("Bernard MT Condensed", 15), bg="#FFFFFF")
        self.bouton_menu.grid(row=0, column=1, sticky="w")
        self.bouton_menu.bind("<Button-1>", self.menu_button_callback)

        self.image_suivant = Image.open('GUI/Menu images/pointeur.png')
        self.image_suivant = self.image_suivant.resize((int(self.width*0.06), int(self.height*0.075)))
        self.image_suivant_tk = ImageTk.PhotoImage(self.image_suivant)
        self.bouton_suivant = tk.Button(self, image = self.image_suivant_tk, bg="#92D4F7", state=tk.DISABLED)
        self.bouton_suivant.grid(row=self.nb_rows - 1, column=self.nb_columns - 1)
        self.bouton_suivant.bind("<Button-1>", self.next_page)

        self.image_precedent = self.image_suivant.transpose(Image.FLIP_LEFT_RIGHT)
        self.image_precedent_tk = ImageTk.PhotoImage(self.image_precedent)
        self.bouton_precedent = tk.Button(self, image = self.image_precedent_tk, bg="#92D4F7", state=tk.DISABLED)
        self.bouton_precedent.grid(row=self.nb_rows - 1, column=0)
        self.bouton_precedent.bind("<Button-1>", self.previous_page)

    def reset(self):
        """
        Réinitialise la frame, créer les boutons de sélection de niveau avec les images des niveaux
        """
        # Lit le fichier json
        with open("data/levels.json", "r") as file:
            self.dico_niveaux = json.load(file)

        # Supprime les anciens boutons
        for frame in self.frames:
            frame.destroy()

        self.frames = []
        self.i_frame = 0
        self.button_images = []

        nb_rows_frame = 4
        nb_columns_frame = 3

        width_img = self.min_canvas_width * 2 ** max(0, self.scale - 2)
        height_img = self.min_canvas_height * 2 ** max(0, self.scale - 2)

        i = 0
        j = 0

        for name, params in self.dico_niveaux.items():

            if params["width"] <= self.width_canvas and params["height"] <= self.height_canvas:

                # Crée une nouvelle frame où placer des boutons
                if i == 0 and j == 0:
                    frame = tk.Frame(self, bg="#92D4F7")
                    frame.grid(row=1, column=1, rowspan=self.nb_rows - 1, columnspan=self.nb_columns - 2)

                    for k in range(nb_rows_frame):
                        frame.grid_rowconfigure(k, weight=1)
                    for k in range(nb_columns_frame):
                        frame.grid_columnconfigure(k, weight=1)

                    self.frames.append(frame)

                img = Image.open(params["image_path"]).resize((width_img, height_img), Image.NEAREST)
                self.button_images.append(ImageTk.PhotoImage(img))
                button = tk.Button(frame, image=self.button_images[-1])
                button.grid(row=i, column=j, padx=self.width // 50, pady=self.height // 50)
                button.bind("<Button-1>", lambda event, p=params: self.game_button_callback(p))

                label = tk.Label(frame, text=name, font=("Bernard MT Condensed", 14))
                label.grid(row=i + 1, column=j, sticky="n", pady=self.height // 50)

                j += 1
                if j >= nb_columns_frame:
                    j = 0
                    i += 2
                if i >= nb_rows_frame:
                    i = 0

        # Rempli les espaces vides sur la dernière frame avec des boutons menant à la scène Creation de niveau
        img = Image.open("GUI/Menu images/construire.png").resize((width_img, height_img))
        self.construire_img_tk = ImageTk.PhotoImage(img)
        while i != 0 or j != 0:
            button = tk.Button(frame, image=self.construire_img_tk)
            button.grid(row=i, column=j, padx=self.width // 50, pady=self.height // 50)
            button.bind("<Button-1>", self.creation_button_callback)

            label = tk.Label(frame, text="A vous de construire vos niveaux !", font=("Bernard MT Condensed", 14))
            label.grid(row=i + 1, column=j, sticky="n", pady=self.height // 50)

            j += 1
            if j >= nb_columns_frame:
                j = 0
                i += 2
            if i >= nb_rows_frame:
                i = 0

        if len(self.frames) != 0:
            self.frames[self.i_frame].tkraise()

        self.bouton_precedent["state"] = tk.DISABLED

        if len(self.frames) > 1:
            self.bouton_suivant["state"] = tk.NORMAL
        else:
            self.bouton_suivant["state"] = tk.DISABLED

    def menu_button_callback(self, event):
        """
        Change la scène pour la Frame Menu

        Paramètres :
            event: Événement tkinter
        """
        self.parent.switch_frame("Menu")

    def creation_button_callback(self, event):
        """
        Change la scène pour la Frame Creation

        Paramètres :
            event: Événement tkinter
        """
        self.parent.switch_frame("Creation")

    def game_button_callback(self, dico):
        """
        Change la scène pour la Frame Jeu

        Paramètres :
            dict dico: Dictionnaire contenant les informations du niveau (nom, taille, chemin de l'image, départ, arrivée)
        """
        self.parent.switch_frame("Jeu", param=dico)

    def next_page(self, event):
        """
        Affiche la page suivante des niveaux

        Paramètres :
            event: Événement tkinter
        """
        if event.widget["state"] != tk.DISABLED:
            self.i_frame += 1
            self.frames[self.i_frame].tkraise()

            if self.i_frame == len(self.frames) - 1:
                self.bouton_suivant["state"] = tk.DISABLED

            self.bouton_precedent["state"] = tk.NORMAL

    def previous_page(self, event):
        """
        Affiche la page précédente des niveaux

        Paramètres :
            event: Événement tkinter
        """
        if event.widget["state"] != tk.DISABLED:
            self.i_frame -= 1
            self.frames[self.i_frame].tkraise()

            if self.i_frame == 0:
                self.bouton_precedent["state"] = tk.DISABLED

            self.bouton_suivant["state"] = tk.NORMAL
