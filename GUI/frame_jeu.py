import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from a_star import AStar


class Jeu(tk.Frame):
    """
    Frame gérant la scène de jeu

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

        Astar astar: Objet servant à réaliser la recherche de plus court chemin

        tk.Toplevel instructions_toplevel: Fenêtre où vont être affiché le mode d'emploi et conseils

        tk.Frame side_panel: Frame pour le panneau contenant les boutons sur le côté
        tk.Frame top_panel: Frame pour le panneau contenant les boutons sur le dessus
        tk.Canvas canvas: Canvas où est affiché le labyrinthe
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

        self.create_widgets()

        self.a_star = AStar(self)

        self.instructions_toplevel = None

    def create_widgets(self):
        """
        Crée les différents widgets présents sur la frame et initialise les variables qui y sont liées
        """
        self.side_panel = tk.Frame(self, width=self.width_side_panel)
        self.side_panel.pack(side=tk.RIGHT, fill=tk.Y)

        self.top_panel = tk.Frame(self, height=self.height_top_panel, relief=tk.RIDGE, bd=5)
        self.top_panel.pack(side=tk.TOP, fill=tk.X)

        self.canvas = tk.Canvas(self, width=self.min_canvas_width * 2 ** self.scale,
                                height=self.min_canvas_height * 2 ** self.scale)
        self.canvas.pack()

        ################################# TOP PANEL #################################

        self.top_panel.grid_propagate(False)
        self.top_panel.grid_rowconfigure(0, weight=1)
        self.top_panel.grid_columnconfigure(0, weight=1)
        self.top_panel.grid_columnconfigure(1, weight=1)

        self.level_name_label = tk.Label(self.top_panel, text="", font=("Bernard MT Condensed", 16))
        self.level_name_label.grid(row=0, column=0)

        self.level_size_label = tk.Label(self.top_panel, text="Taille : ", font=("Bernard MT Condensed", 16))
        self.level_size_label.grid(row=0, column=1)

        ################################# SIDE PANEL #################################

        self.side_panel.grid_propagate(False)

        nb_rows = 7
        nb_columns = 2

        for i in range(nb_rows):
            self.side_panel.grid_rowconfigure(i, weight=1)
        for i in range(nb_columns):
            self.side_panel.grid_columnconfigure(i, weight=1)

        img = Image.open('GUI/Menu images/ciel.png').resize((self.width, self.height))
        img = img.crop((self.width - self.width_side_panel, 0, self.width, self.height))
        self.image_bg_tk = ImageTk.PhotoImage(img)
        widget = tk.Label(self.side_panel, image=self.image_bg_tk)
        widget.grid(row=0, column=0, rowspan=nb_rows, columnspan=nb_columns)

        img = Image.open('GUI/Menu images/homer_bouton.png').resize((int(self.width * 0.04), int(self.width * 0.04)))
        self.image_label = ImageTk.PhotoImage(img)

        nb_buttons = 4
        for i in range(1, 1 + nb_buttons):
            widget = tk.Label(self.side_panel, image=self.image_label, bg="#92D4F7")
            widget.grid(row=i, column=0)

        widget = tk.Button(self.side_panel, text="Menu", font=("Bernard MT Condensed", 14))
        widget.grid(row=1, column=1, sticky='w')
        widget.bind('<Button-1>', self.menu_button_callback)

        widget = tk.Button(self.side_panel, text="Mode d'emploi", font=("Bernard MT Condensed", 14))
        widget.grid(row=2, column=1, sticky='w')
        widget.bind('<Button-1>', self.instructions_button_callback)

        widget = tk.Button(self.side_panel, text="Recommencer", font=("Bernard MT Condensed", 14))
        widget.grid(row=3, column=1, sticky='w')
        widget.bind('<Button-1>', self.start_again)

        widget = tk.Button(self.side_panel, text="Résoudre", font=("Bernard MT Condensed", 14))
        widget.grid(row=4, column=1, sticky='w')
        widget.bind('<Button-1>', self.solve_button_callback)

        self.check_show_search = tk.IntVar(value=0)
        widget = tk.Checkbutton(self.side_panel, variable=self.check_show_search,
                                text="Affichage de la recherche", font=("Bernard MT Condensed", 10))
        widget.grid(row=5, column=0, columnspan=2, sticky="n")

        ################################# CANVAS #################################

        # Image du labyrinthe
        self.lab_width, self.lab_height = self.min_canvas_width, self.min_canvas_height
        self.resize_factor = self.height_canvas // self.lab_height
        self.lab_image = Image.new(mode="RGB", size=(1, 1), color=(255, 255, 255))
        self.lab_image_tk = ImageTk.PhotoImage(self.lab_image.resize((self.width_canvas, self.height_canvas), Image.NEAREST))
        self.lab_image_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.lab_image_tk)

        # Image du départ
        self.start_x, self.start_y = 0, 0
        self.start_image = Image.open("GUI/Game images/start.png")
        self.start_image_tk = ImageTk.PhotoImage(self.start_image.resize((self.resize_factor, self.resize_factor)))
        self.start_image_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.start_image_tk)

        # Image de l'arrivée
        self.end_x, self.end_y = 0, 0
        self.end_image = Image.open("GUI/Game images/end.png")
        self.end_image_tk = ImageTk.PhotoImage(self.end_image.resize((self.resize_factor, self.resize_factor)))
        self.end_image_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.end_image_tk)

        # Image du joueur
        self.player_x, self.player_y = 0, 0
        self.move_x, self.move_y = 0, 0
        self.player_image = Image.open("GUI/Game images/player.png")
        self.player_image_tk = ImageTk.PhotoImage(self.player_image.resize((self.resize_factor, self.resize_factor)))
        self.player_image_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.player_image_tk)

        self.keys_pressed = []
        self.timer = None

    def reset(self, dico_niveau):
        """
        Réinitialise la frame, si dico_niveau n'est pas None, charge le niveau. Sinon, réinitialise le niveau actuel.

        Paramètres :
            Dict dico_niveau: Dictionnaire contenant les informations du niveau (nom, taille, chemin de l'image, départ, arrivée)
        """
        self.lab_image = Image.open(dico_niveau["image_path"])
        self.lab_width = dico_niveau["width"]
        self.lab_height = dico_niveau["height"]
        self.resize_factor = self.height_canvas // self.lab_height

        self.start_image_tk = ImageTk.PhotoImage(self.start_image.resize((self.resize_factor, self.resize_factor)))
        self.canvas.itemconfigure(self.start_image_canvas, image=self.start_image_tk)

        self.end_image_tk = ImageTk.PhotoImage(self.end_image.resize((self.resize_factor, self.resize_factor)))
        self.canvas.itemconfigure(self.end_image_canvas, image=self.end_image_tk)

        self.player_image_tk = ImageTk.PhotoImage(self.player_image.resize((self.resize_factor, self.resize_factor)))
        self.canvas.itemconfigure(self.player_image_canvas, image=self.player_image_tk)

        self.start_x, self.start_y = dico_niveau["start"]  # placement perso
        self.canvas.coords(self.start_image_canvas, self.start_x * self.resize_factor, self.start_y * self.resize_factor)

        self.end_x, self.end_y = dico_niveau["end"]
        self.canvas.coords(self.end_image_canvas, self.end_x * self.resize_factor, self.end_y * self.resize_factor)

        self.level_name_label["text"] = f"Niveau : {dico_niveau['name']}"
        self.level_size_label["text"] = f"Taille : {dico_niveau['width']}x{dico_niveau['height']}"

        actions = ["<Right>", "<Left>", "<Up>", "<Down>", "<KeyRelease-Right>", "<KeyRelease-Left>", "<KeyRelease-Up>",
                   "<KeyRelease-Down>"]
        for action in actions:
            self.parent.bind(action, self.move)

        self.keys_pressed = []
        self.timer = None

        self.start_again()

        self.focus()

        self.parent.protocol("WM_DELETE_WINDOW", self.close_window)

    def start_again(self, event=None):
        """
        Recommence le niveau actuel

        Paramètres :
            event: Événement tkinter
        """
        self.lab_image_tk = ImageTk.PhotoImage(self.lab_image.resize((self.width_canvas, self.height_canvas), Image.NEAREST))
        self.canvas.itemconfigure(self.lab_image_canvas, image=self.lab_image_tk)

        self.player_x, self.player_y = self.start_x, self.start_y
        self.move_player()

    def close_window(self):
        """
        Ferme la fenêtre graphique en arrêtant le thread AStar s'il est lancé
        """
        self.a_star.quit()
        self.parent.destroy()

    def move_player(self):
        """
        Mets à jour la position de l'image du joueur
        """
        self.canvas.coords(self.player_image_canvas, self.player_x * self.resize_factor, self.player_y * self.resize_factor)

    def move(self, event):
        """
        Fonction appelée lorsque l'on appuie sur une des flèches
        Mets à jour les valeurs de déplacement en x (self.move_x) et en y (self.move_y)

        Paramètres :
            event: Événement tkinter
        """
        directions = {"Left": (-1, 0), "Right": (1, 0), "Up": (0, -1), "Down": (0, 1)}

        if event.keysym in directions:
                            # Press
            condition1 = event.type == "2" and event.keysym not in self.keys_pressed    # Si l'on appuie sur une nouvelle touche
            condition2 = event.type == "3"      # Si l'on relâche une touche
                            # Release

            if condition1 or condition2:

                if condition1:
                    self.keys_pressed.append(event.keysym)

                elif condition2:
                    self.keys_pressed.remove(event.keysym)

                self.move_x, self.move_y = 0, 0

                for key in self.keys_pressed:
                    dx, dy = directions[key]
                    self.move_x += dx
                    self.move_y += dy

                # Empêche de bouger en diagonale
                if self.move_x != 0 and self.move_y != 0:
                    self.move_x, self.move_y = directions[self.keys_pressed[-1]]

                if self.move_x == 0 and self.move_y == 0:
                    if self.timer is not None:
                        self.canvas.after_cancel(self.timer)
                        self.timer = None

                else:
                    if self.timer is None:
                        self.move_timer()

    def move_timer(self):
        """
        Calcule la prochaine position du joueur avec les valeurs de déplacement
        Vérifie si la case est un sol, un mur, un laser ou l'arrivée
        Mets à jour la position du joueur en fonction
        """
        x = self.player_x + self.move_x
        y = self.player_y + self.move_y

        self.timer = None

        if 0 <= x < self.lab_width and 0 <= y < self.lab_height:

            color = self.lab_image.getpixel((x, y))

            #                   sol         laser
            if color in {(255, 255, 255), (255, 0, 0)}:
                self.player_x, self.player_y = x, y
                self.move_player()

                if color == (255, 0, 0):
                    self.start_again()

                elif self.player_x == self.end_x and self.player_y == self.end_y:
                    self.end_level()

                else:
                    self.timer = self.canvas.after(75, self.move_timer)

    def end_level(self):
        """
        Affiche un message pour féliciter le joueur d'avoir réussi le niveau
        Puis change la scène pour celle de menu
        """
        tk.messagebox.showinfo(title="WINNER WINNER CHICKEN DINNER", message="Bravo ! Vous avez réussi ce niveau :)")
        self.parent.switch_frame("Menu")

    def menu_button_callback(self, event):
        """
        Change la scène pour la Frame Menu

        Paramètres :
            event: Événement tkinter
        """
        actions = ["<Right>", "<Left>", "<Up>", "<Down>", "<KeyRelease-Right>", "<KeyRelease-Left>", "<KeyRelease-Up>",
                   "<KeyRelease-Down>"]
        for action in actions:
            self.parent.unbind(action)

        self.a_star.quit()
        self.parent.switch_frame("Menu")

    def instructions_button_callback(self, event):
        """
        Créé et affiche la fenêtre présentant le mode d'emploi et les conseils

        Paramètres :
            event: Événement tkinter
        """
        if self.instructions_toplevel is None:      # Permet de n'avoir qu'une seule fenêtre de mode d'emploi à la fois
            self.instructions_toplevel = tk.Toplevel(self.parent, bg="#92D4F7")
            self.instructions_toplevel.resizable(False, False)

            nb_rows = 6
            nb_columns = 2

            for i in range(nb_rows):
                self.instructions_toplevel.grid_rowconfigure(i, weight=1)
            for i in range(nb_columns):
                self.instructions_toplevel.grid_columnconfigure(i, weight=1)

            self.icone11 = Image.open('GUI/Menu images/homer_bouton.png').resize(
                (int(self.width * 0.056), int(self.width * 0.056)))
            self.icone11_tk = ImageTk.PhotoImage(self.icone11)
            self.label_icone11 = tk.Label(self.instructions_toplevel, image=self.icone11_tk, bg="#92D4F7")
            self.label_icone11.grid(row=0, column=0)

            widget1 = tk.Label(self.instructions_toplevel, text="Objectif", font=("Showcard Gothic", 20), bg="#92D4F7")
            widget1.grid(row=0, column=1)
            widget11 = tk.Label(self.instructions_toplevel,
                                text="Le but du jeu est de trouver le chemin menant au donut à travers le Labybouffe.\n"
                                     "Pour cela, utilisez les flèches directionnelles du clavier pour vous orienter.\n"
                                     "Une fois le donut trouvé c'est gagné!\n"
                                     "Attention, pour votre santé, évitez de manger trop gras, trop sucré, trop salé.",
                                font=("Rockwell Condensed", 15), bg="#92D4F7")
            widget11.grid(row=1, column=1)

            widget2 = tk.Label(self.instructions_toplevel, text="Eléments", font=("Showcard Gothic", 20), bg="#92D4F7")
            widget2.grid(row=2, column=1)
            self.label_icone22 = tk.Label(self.instructions_toplevel, image=self.icone11_tk, bg="#92D4F7")
            self.label_icone22.grid(row=2, column=0)
            widget22 = tk.Label(self.instructions_toplevel,
                                text="Le Labybouffe est composé de plusieurs éléments: des cases blanches, noires et murs rouges.\n"
                                     "Attention ! Les cases noires sont des murs vous empêchant de passer et les rouges sont des lasers.\n"
                                     "Si jamais vous trébuchez sur vos bourrelets et que vous tombez sur une case rouge, c'est perdu !!",
                                font=("Rockwell Condensed", 15), bg="#92D4F7")
            widget22.grid(row=3, column=1)

            widget3 = tk.Label(self.instructions_toplevel, text="Mode Jeu", font=("Showcard Gothic", 20), bg="#92D4F7")
            widget3.grid(row=4, column=1)
            self.label_icone44 = tk.Label(self.instructions_toplevel, image=self.icone11_tk, bg="#92D4F7")
            self.label_icone44.grid(row=4, column=0)
            widget33 = tk.Label(self.instructions_toplevel,
                                text="Dans le mode jeu, vous jouez les niveaux déjà cuisinés par les meilleurs chefs, ou goûtez votre propre plat.\n"
                                     "Le plat est beaucoup trop gras pour vous ? Ne vous inquiétez pas ! Le bouton 'Résoudre' est à votre secours ici aussi.",
                                font=("Rockwell Condensed", 15), bg="#92D4F7")
            widget33.grid(row=5, column=1)

            self.instructions_toplevel.protocol("WM_DELETE_WINDOW", self.destroy_instructions_toplevel)

    def destroy_instructions_toplevel(self):
        """
        Supprime la fenêtre de mode d'emploi et la met à None.
        """
        self.instructions_toplevel.destroy()
        self.instructions_toplevel = None

    def solve_button_callback(self, event):
        """
        Résout le labyrinthe dessiné

        Paramètres :
            event: Événement tkinter
        """
        if not self.a_star.running:
            self.a_star.run((self.player_x, self.player_y), (self.end_x, self.end_y), show_search=self.check_show_search.get())
