import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import PIL
from PIL import Image, ImageTk, ImageDraw
import platform
import numpy as np
import math, json
from a_star import AStar


class Creation(tk.Frame):
    """
    Frame gérant la scène de création de labyrinthe

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

        self.reset()

    def create_widgets(self):
        """
        Crée les différents widgets présents sur la frame et initialise les variables qui y sont liées
        """
        self.side_panel = tk.Frame(self, width=self.width_side_panel)
        self.side_panel.pack(side=tk.RIGHT, fill=tk.Y)

        self.top_panel = tk.Frame(self, height=self.height_top_panel, relief=tk.RIDGE, bd=5)
        self.top_panel.pack(side=tk.TOP, fill=tk.X)

        self.canvas = tk.Canvas(self, width=self.width_canvas, height=self.height_canvas, bg="purple",
                                highlightthickness=0, cursor="none")
        self.canvas.pack()

        ################################# TOP PANEL #################################

        self.top_panel.grid_propagate(False)
        self.top_panel.grid_rowconfigure(0, weight=1)
        self.top_panel.grid_rowconfigure(1, weight=1)
        for i in range(14):
            self.top_panel.grid_columnconfigure(i, weight=1)

        button_size = self.height_top_panel * 3 // 5

        i = 1

        # Taille du labyrinthe
        self.text_lab_size = tk.StringVar()
        self.lab_width, self.lab_height = self.min_canvas_width, self.min_canvas_height
        self.resize_factor = self.height_canvas // self.lab_height
        widget = tk.Label(self.top_panel, text="Taille Labyrinthe :")
        widget.grid(row=0, column=i, sticky="s")
        self.lab_size_combobox = ttk.Combobox(self.top_panel, state="readonly", textvariable=self.text_lab_size,  width=9,
                                              values=[f"{self.min_canvas_width * 2 ** j} x {self.min_canvas_height * 2 ** j}" for j in range(self.scale+1)])
        self.lab_size_combobox.bind('<<ComboboxSelected>>', self.update_lab_size)
        self.lab_size_combobox.grid(row=1, column=i, sticky="n")

        i += 1

        # Pinceau forme carrée
        self.pen_type = "square"    # Type de pinceau
        self.buttons = []           # Liste des boutons de type de pinceau
        img = Image.open("GUI/Button images/square.png").resize((button_size, button_size))
        self.square_button_image = ImageTk.PhotoImage(img)
        widget = tk.Button(self.top_panel, image=self.square_button_image, width=button_size, height=button_size, state=tk.DISABLED)
        widget.grid(row=0, column=i, rowspan=2)
        widget.bind("<Button-1>", self.square_button_callback)
        self.buttons.append(widget)

        i += 1

        # Pinceau forme ronde
        img = Image.open("GUI/Button images/circle.png").resize((button_size, button_size))
        self.circle_button_image = ImageTk.PhotoImage(img)
        widget = tk.Button(self.top_panel, image=self.circle_button_image, width=button_size, height=button_size)
        widget.grid(row=0, column=i, rowspan=2)
        widget.bind("<Button-1>", self.circle_button_callback)
        self.buttons.append(widget)

        i += 1

        # Pinceau ligne
        img = Image.open("GUI/Button images/line.png").resize((button_size, button_size))
        self.line_button_image = ImageTk.PhotoImage(img)
        widget = tk.Button(self.top_panel, image=self.line_button_image, width=button_size, height=button_size)
        widget.grid(row=0, column=i, rowspan=2)
        widget.bind("<Button-1>", self.line_button_callback)
        self.buttons.append(widget)

        i += 1

        # Taille du pinceau
        widget = tk.Label(self.top_panel, text="Taille pinceau :")
        widget.grid(row=0, column=i, sticky="s")
        self.pen_size = 1
        self.var_pen_size = tk.IntVar(value=self.pen_size)
        self.spinbox_pen_size = tk.Spinbox(self.top_panel, width=4, textvariable=self.var_pen_size, command=self.update_pen_size,
                                           values=list(range(1, self.lab_height // self.min_canvas_height + 1)))
        self.spinbox_pen_size.grid(row=1, column=i, sticky="n")
        self.spinbox_pen_size.bind("<Return>", self.update_pen_size)

        i += 1

        # Pinceau seau (Remplir d'une couleur)
        img = Image.open("GUI/Button images/bucket.png").resize((button_size, button_size))
        self.bucket_button_image = ImageTk.PhotoImage(img)
        widget = tk.Button(self.top_panel, image=self.bucket_button_image, width=button_size, height=button_size)
        widget.grid(row=0, column=i, rowspan=2)
        widget.bind("<Button-1>", self.bucket_button_callback)
        self.buttons.append(widget)

        i += 1

        # Choix de la couleur (type de case)
        self.color = (0, 0, 0, 255)
        self.text_color = tk.StringVar()
        widget = tk.Label(self.top_panel, text="Couleur :")
        widget.grid(row=0, column=i, sticky="s")
        self.color_combobox = ttk.Combobox(self.top_panel, values=["Noir (mur)", "Rouge (laser)", "Blanc (chemin)"], width=12,
                              state="readonly", textvariable=self.text_color)
        self.color_combobox.bind('<<ComboboxSelected>>', self.update_color)
        self.color_combobox.grid(row=1, column=i, sticky="n")

        i += 1

        # Insérer une image
        self.base_image_image = None        # Image originale redimensionnée aux dimensions max du canvas si elle les dépasse
        self.base_image_image_pen = None    # Image originale semi-transparente redimensionnée aux dimensions max du canvas si elle les dépasse
        self.image_image = None             # Image aux dimensions du pinceau, que l'on colle sur l'image du labyrinthe
        self.image_image_pen = None         # Image semi-transparente aux dimensions du pinceau
        self.image_image_pen_tk = None      # Version ImageTk.PhotoImage de self.image_image_pen, que l'on affiche en tant que pinceau
        img = Image.open("GUI/Button images/image.png").resize((button_size, button_size))
        self.image_button_image = ImageTk.PhotoImage(img)
        widget = tk.Button(self.top_panel, image=self.image_button_image, width=button_size, height=button_size)
        widget.grid(row=0, column=i, rowspan=2)
        widget.bind("<Button-1>", self.image_button_callback)

        i += 1

        # Placer la case départ
        img = Image.open("GUI/Button images/start.png").resize((button_size, button_size))
        self.start_button_image = ImageTk.PhotoImage(img)
        widget = tk.Button(self.top_panel, image=self.start_button_image, width=button_size, height=button_size)
        widget.grid(row=0, column=i, rowspan=2)
        widget.bind("<Button-1>", self.start_button_callback)
        self.buttons.append(widget)

        i += 1

        # Placer la case d'arrivée
        img = Image.open("GUI/Button images/end.png").resize((button_size, button_size))
        self.end_button_image = ImageTk.PhotoImage(img)
        widget = tk.Button(self.top_panel, image=self.end_button_image, width=button_size, height=button_size)
        widget.grid(row=0, column=i, rowspan=2)
        widget.bind("<Button-1>", self.end_button_callback)
        self.buttons.append(widget)

        i += 1

        # Annuler la dernière action
        self.all_lab_images = []        # Liste des images de labyrinthe sur lesquelles on peut revenir avec les flèches
        self.i_lab_image = 0            # Indice de l'image actuelle du labyrinthe dans la liste
        img = Image.open("GUI/Button images/go_back.png").resize((button_size, button_size))
        self.go_back_button_image = ImageTk.PhotoImage(img)
        self.go_back_button = tk.Button(self.top_panel, image=self.go_back_button_image, width=button_size,
                                        height=button_size, state=tk.DISABLED)
        self.go_back_button.grid(row=0, column=i, rowspan=2)
        self.go_back_button.bind("<Button-1>", self.go_back_button_callback)

        i += 1

        # Refaire l'action annulée
        img = Image.open("GUI/Button images/go_forward.png").resize((button_size, button_size))
        self.go_forward_button_image = ImageTk.PhotoImage(img)
        self.go_forward_button = tk.Button(self.top_panel, image=self.go_forward_button_image, width=button_size,
                                           height=button_size, state=tk.DISABLED)
        self.go_forward_button.grid(row=0, column=i, rowspan=2)
        self.go_forward_button.bind("<Button-1>", self.go_forward_button_callback)

        ################################# SIDE PANEL #################################

        self.side_panel.grid_propagate(False)

        nb_rows = 8
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

        widget = tk.Button(self.side_panel, text="Tout effacer", font=("Bernard MT Condensed", 14))
        widget.grid(row=3, column=1, sticky='w')
        widget.bind('<Button-1>', self.erase_all)

        widget = tk.Button(self.side_panel, text="Résoudre", font=("Bernard MT Condensed", 14))
        widget.grid(row=4, column=1, sticky='w')
        widget.bind('<Button-1>', self.solve_button_callback)

        self.valid = True
        self.check_show_search = tk.IntVar(value=1)
        widget = tk.Checkbutton(self.side_panel, variable=self.check_show_search,
                                text="Affichage de la recherche", font=("Bernard MT Condensed", 10))
        widget.grid(row=5, column=0, columnspan=2, sticky="n")

        widget = tk.Label(self.side_panel, image=self.image_label, bg="#92D4F7")
        widget.grid(row=6, column=0)

        widget = tk.Button(self.side_panel, text="Enregistrer", font=("Bernard MT Condensed", 14))
        widget.grid(row=6, column=1, sticky='w')
        widget.bind('<Button-1>', self.save_button_callback)

        ################################# CANVAS #################################

        # Image du labyrinthe
        self.lab_image = Image.new(mode="RGB", size=(self.lab_width, self.lab_height), color=(255, 255, 255))
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
        self.end_image_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.start_image_tk)

        # Image du pinceau
        self.pen_image_tk = ImageTk.PhotoImage("RGBA", (1, 1))
        self.pen_image_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.pen_image_tk)

        self.outlines_pen_size = 8
        self.outlines_pen_image = Image.new(mode="RGBA", size=(1, 1), color=(255, 255, 255, 0))
        self.outlines_pen_image_tk = ImageTk.PhotoImage(self.outlines_pen_image)
        self.outlines_pen_image_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.outlines_pen_image_tk)

        self.x_press, self.y_press = None, None     # Coordonnées d'appui du pinceau
        self.shift_direction = None                 # Direction choisie lorsque l'on dessine en pressant shift pour
                                                    # tracer de manière horizontale ou verticale

        # Bind des actions possibles sur le canvas
        self.canvas.bind("<Motion>", self.motion)
        self.canvas.bind("<MouseWheel>", self.wheel_update_pen_size)
        self.canvas.bind("<Button-1>", self.draw_press)
        self.canvas.bind("<ButtonRelease-1>", self.draw_release)
        self.canvas.bind("<Shift-ButtonRelease-1>", self.draw_shift_release)
        self.canvas.bind("<B1-Motion>", self.draw_motion)
        self.canvas.bind("<Shift-B1-Motion>", self.draw_shift_motion)

    def reset(self):
        """
        Réinitialise la frame
        """
        self.lab_size_combobox.current(min(3, self.scale))
        self.var_pen_size.set(1)
        self.update_lab_size()

        self.color_combobox.current(0)
        self.update_color()

        self.buttons[0].event_generate("<Button-1>")    # Pinceau carré

        self.erase_all()

        self.parent.protocol("WM_DELETE_WINDOW", self.close_window)

    def erase_all(self, event=None):
        """
        Efface tout ce qui est dessiné (réinitialise l'image)

        Paramètres :
            event: Événement tkinter
        """
        self.lab_image = Image.new(mode="RGB", size=(self.lab_width, self.lab_height), color=(255, 255, 255))
        self.update_lab_image_canvas()

        self.all_lab_images = [self.lab_image.copy()]
        self.i_lab_image = 0
        self.go_back_button["state"] = tk.DISABLED
        self.go_forward_button["state"] = tk.DISABLED

        self.start_x, self.start_y = 0, 0
        self.start_image_tk = ImageTk.PhotoImage(self.start_image.resize((self.resize_factor, self.resize_factor)))
        self.canvas.itemconfigure(self.start_image_canvas, image=self.start_image_tk)
        self.canvas.coords(self.start_image_canvas, self.start_x * self.resize_factor, self.start_y * self.resize_factor)

        self.end_x, self.end_y = self.lab_width - 1, self.lab_height - 1
        self.end_image_tk = ImageTk.PhotoImage(self.end_image.resize((self.resize_factor, self.resize_factor)))
        self.canvas.itemconfigure(self.end_image_canvas, image=self.end_image_tk)
        self.canvas.coords(self.end_image_canvas, self.end_x * self.resize_factor, self.end_y * self.resize_factor)

    def close_window(self):
        """
        Ferme la fenêtre graphique en arrêtant le thread AStar s'il est lancé
        """
        self.a_star.quit()
        self.parent.destroy()

    ################ FONCTIONS CALLBACK BOUTONS ################

    def disable_button_enable_others(self, button=None):
        """
        Désactive un bouton et active tout les autres

        Paramètres :
            tk.Button button: Bouton à désactiver
        """
        for widget in self.buttons:
            widget["state"] = tk.NORMAL

        if button is not None:
            button["state"] = tk.DISABLED

    def square_button_callback(self, event):
        """
        Change de pinceau pour la forme carrée

        Paramètres :
            event: Événement tkinter
        """
        if event.widget["state"] != tk.DISABLED:
            self.disable_button_enable_others(event.widget)

            self.pen_type = "square"

    def circle_button_callback(self, event):
        """
        Change de pinceau pour la forme ronde

        Paramètres :
            event: Événement tkinter
        """
        if event.widget["state"] != tk.DISABLED:
            self.disable_button_enable_others(event.widget)

            self.pen_type = "circle"

    def line_button_callback(self, event):
        """
        Change de pinceau pour le mode ligne

        Paramètres :
            event: Événement tkinter
        """
        if event.widget["state"] != tk.DISABLED:
            self.disable_button_enable_others(event.widget)

            self.pen_type = "line"

    def bucket_button_callback(self, event):
        """
        Change de pinceau pour le mode seau (remplir une zone d'une couleur)

        Paramètres :
            event: Événement tkinter
        """
        if event.widget["state"] != tk.DISABLED:
            self.disable_button_enable_others(event.widget)

            self.pen_type = "bucket"

    def image_button_callback(self, event):
        """
        Change de pinceau pour le mode coller une image

        Paramètres :
            event: Événement tkinter

        Renvoi :
            "break": Permet d'éviter que le bouton ne reste bloqué dans son visuel pressé
        """
        if event.widget["state"] != tk.DISABLED:
            path = filedialog.askopenfilename(title="Importer une image", filetypes=[("Toutes les images", "*.*"), ("Image png", ".png"), ("Image jpg", ".jpg")])

            if path: # si l'on a pas annulé la sélection d'image
                self.disable_button_enable_others()

                try:
                    image = Image.open(path)
                    if image.mode != "RGBA":
                        image = image.convert(mode="RGBA")

                    ratio = image.width / image.height
                    if image.width > self.width_canvas or image.height > self.height_canvas:
                        if ratio >= self.width_canvas / self.height_canvas:
                            image = image.resize((self.width_canvas, int(self.width_canvas / ratio)), Image.NEAREST)
                        else:
                            image = image.resize((int(self.height_canvas * ratio), self.height_canvas), Image.NEAREST)

                    array_image = np.array(image)
                    rgb, alpha = array_image[:, :, :3], array_image[:, :, 3:]

                    available_colors = [(0, 0, 0), (255, 0, 0), (255, 255, 255)]

                    alpha[alpha > 100] = 255
                    alpha[alpha <= 100] = 0
                    alpha_s = np.squeeze(alpha)
                    rgb[alpha_s == 0] = (255, 255, 255)

                    # Traite l'image pour changer toutes les couleurs n'étant pas dans celles disponibles pour le
                    # labyrinthe la couleur la plus proche dans celles disponibles.

                    image_colors = {}

                    for r, g, b in rgb[alpha_s == 255]:
                        color = (r, g, b)
                        if color not in image_colors and color not in available_colors:
                            min_diff = -1
                            min_dist_color = (255, 255, 255)
                            for r1, g1, b1 in available_colors:
                                diff = abs(r1 - r) + abs(g1 - g) + abs(b1 - b)
                                if min_diff == -1 or diff < min_diff:
                                    min_diff = diff
                                    min_dist_color = (r1, g1, b1)

                            image_colors[color] = min_dist_color

                    for i in range(len(array_image)):
                        for j in range(len(array_image[0])):
                            color = tuple(rgb[i][j])
                            if color in image_colors:
                                rgb[i][j] = image_colors[color]

                    self.base_image_image = Image.fromarray(np.append(rgb, alpha, axis=-1))
                    self.base_image_image_pen = Image.fromarray(np.append(rgb, alpha // 2, axis=-1))

                    self.pen_type = "image"

                    self.var_pen_size.set(self.lab_height // self.min_canvas_height)
                    self.update_pen_size()

                except PIL.UnidentifiedImageError:  # Erreur
                    tk.messagebox.showerror("Erreur", "Le fichier sélectionné n'est pas une image !")

        return "break"

    def start_button_callback(self, event):
        """
        Change de pinceau pour le mode placer le départ

        Paramètres :
            event: Événement tkinter
        """
        if event.widget["state"] != tk.DISABLED:
            self.disable_button_enable_others(event.widget)

            self.pen_type = "start"

            pen_image = self.start_image.resize((self.resize_factor, self.resize_factor))
            pen_image.putalpha(200)
            self.pen_image_tk = ImageTk.PhotoImage(pen_image)
            self.canvas.itemconfigure(self.pen_image_canvas, image=self.pen_image_tk)

    def end_button_callback(self, event):
        """
        Change de pinceau pour le mode placer l'arrivée

        Paramètres :
            event: Événement tkinter
        """
        if event.widget["state"] != tk.DISABLED:
            self.disable_button_enable_others(event.widget)

            self.pen_type = "end"

            pen_image = self.end_image.resize((self.resize_factor, self.resize_factor))
            pen_image.putalpha(200)
            self.pen_image_tk = ImageTk.PhotoImage(pen_image)
            self.canvas.itemconfigure(self.pen_image_canvas, image=self.pen_image_tk)

    def go_back_button_callback(self, event):
        """
        Annule le dernier dessin réalisé (Revient sur l'image de labyrinthe précédente)

        Paramètres :
            event: Événement tkinter
        """
        if event.widget["state"] != tk.DISABLED:
            self.i_lab_image -= 1
            self.lab_image = self.all_lab_images[self.i_lab_image].copy()

            self.update_lab_image_canvas()

            if self.i_lab_image == 0:
                self.go_back_button["state"] = tk.DISABLED

            self.go_forward_button["state"] = tk.NORMAL

            # Permet d'actualiser la couleur des contours du pinceau sans le déplacer
            pen_x, pen_y = self.canvas.coords(self.pen_image_canvas)
            self.move_pen(pen_x // self.resize_factor, pen_y // self.resize_factor)

    def go_forward_button_callback(self, event):
        """
        Refait le dernier dessin annulé (Revient sur l'image de labyrinthe suivante)

        Paramètres :
            event: Événement tkinter
        """
        if event.widget["state"] != tk.DISABLED:
            self.i_lab_image += 1
            self.lab_image = self.all_lab_images[self.i_lab_image].copy()

            self.update_lab_image_canvas()

            if self.i_lab_image == len(self.all_lab_images) - 1:
                self.go_forward_button["state"] = tk.DISABLED

            self.go_back_button["state"] = tk.NORMAL

            # Permet d'actualiser la couleur des contours du pinceau sans le déplacer
            pen_x, pen_y = self.canvas.coords(self.pen_image_canvas)
            self.move_pen(pen_x // self.resize_factor, pen_y // self.resize_factor)

    def menu_button_callback(self, event):
        """
        Change la scène pour la Frame Menu

        Paramètres :
            event: Événement tkinter
        """
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

            nb_rows = 4
            nb_columns = 2

            for i in range(nb_rows):
                self.instructions_toplevel.grid_rowconfigure(i, weight=1)
            for i in range(nb_columns):
                self.instructions_toplevel.grid_columnconfigure(i, weight=1)

            self.icone11 = Image.open('GUI/Menu images/homer_bouton.png').resize((int(self.width * 0.056), int(self.width * 0.056)))
            self.icone11_tk = ImageTk.PhotoImage(self.icone11)
            self.label_icone11 = tk.Label(self.instructions_toplevel, image=self.icone11_tk, bg="#92D4F7")
            self.label_icone11.grid(row=0, column=0)

            widget1 = tk.Label(self.instructions_toplevel, text="Mode Création", font=("Showcard Gothic", 20), bg="#92D4F7")
            widget1.grid(row=0, column=1)
            widget11 = tk.Label(self.instructions_toplevel,
                                text="Dans le mode création, il est possible de confectionner son propre Labybouffe. "
                                     "Pour cela, vous avez à votre disposition plusieurs fonctions :\n"
                                     "Les boutons sur le panneau du dessus vous permettent de choisir la forme du pinceau,\n"
                                     "de changer la taille du Labybouffe ainsi que celle du pinceau et même d'importer des images !\n\n"
                                     "Oops! Vous vous êtes trompé à cause de vos doigts trop gras ?? Pas de problème! "
                                     "Les boutons 'Annuler/Répéter' et 'Tout effacer' sont là pour vous aider.\n"
                                     "Afin de vous assurer que Homer peut bel et bien atteindre son donut, utilisez le bouton 'Résoudre'.\n"
                                     "Conservez votre magnifique création en utilisant le bouton 'Enregistrer'.",
                                font=("Rockwell Condensed", 15), bg="#92D4F7")
            widget11.grid(row=1, column=1)

            widget2 = tk.Label(self.instructions_toplevel, text="Conseils", font=("Showcard Gothic", 20), bg="#92D4F7")
            widget2.grid(row=2, column=1)
            self.label_icone44 = tk.Label(self.instructions_toplevel, image=self.icone11_tk, bg="#92D4F7")
            self.label_icone44.grid(row=2, column=0)
            widget22 = tk.Label(self.instructions_toplevel, text="", font=("Rockwell Condensed", 15), bg="#92D4F7")

            if platform.system() == "Linux":
                widget22["text"] = "Vous devez utiliser pouvez entrer directement un nombre dans la spinbox pour changer la taille du pinceau.\n" \
                                   "Malheureusement votre OS n'est pas compatible pour utiliser la molette de la souris.\n" \
                                   "Lorsque vous importez une image, modifiez la taille du pinceau pour changer sa taille\n\n" \
                                   "Maintenez la touche Maj Gauche pour vous aider à tracer des lignes verticales et horizontales !"
            else:
                widget22["text"] = "Vous pouvez entrer directement un nombre dans la spinbox pour changer la taille du pinceau.\n" \
                                   "Il est aussi possible de la modifier en utilisant la molette de la souris.\n" \
                                   "Lorsque vous importez une image, modifiez la taille du pinceau pour changer sa taille\n" \
                                   "Attention ! Importer de grandes images peut prendre du temps !\n\n" \
                                   "Maintenez la touche Maj Gauche pour vous aider à tracer des lignes verticales et horizontales !"

            widget22.grid(row=3, column=1)

            self.instructions_toplevel.protocol("WM_DELETE_WINDOW", self.destroy_instructions_toplevel)

    def destroy_instructions_toplevel(self):
        """
        Supprime la fenêtre de mode d'emploi et la met à None.
        """
        self.instructions_toplevel.destroy()
        self.instructions_toplevel = None

    def solve_button_callback(self, event=None):
        """
        Résout le labyrinthe dessiné

        Paramètres :
            event: Événement tkinter
        """
        if not self.a_star.running:
            self.a_star.run((self.start_x, self.start_y), (self.end_x, self.end_y), show_search=self.check_show_search.get())

    def save_button_callback(self, event):
        """
        Sauvegarde le niveau dessiné

        Paramètres :
            event: Événement tkinter

        Renvoi :
            "break": Permet d'éviter que le bouton ne reste bloqué dans son visuel pressé
        """
        if not self.valid:
            if tk.messagebox.askokcancel("Erreur", "Veuillez d'abord tester de la validité du labyrinthe"):
                self.solve_button_callback()
        else:
            path = tk.filedialog.asksaveasfilename(title="Sauvegarder le labyrinthe", filetypes=[("Image png", ".png")],
                                                   initialdir="data/lab_images")
            if len(path) < 4 or path[-4:] != ".png":
                if path[-4:].lower() == ".png":
                    path = path[:-4] + ".png"
                else:
                    path += ".png"

            self.lab_image.save(path)

            name = path.split("/")[-1][:-4]

            with open("data/levels.json", "r") as file:
                dico_niveaux = json.load(file)

            dico_niveaux[name] = {
                "name": name,
                "width": self.lab_width,
                "height": self.lab_height,
                "image_path": path,
                "start": [self.start_x, self.start_y],
                "end": [self.end_x, self.end_y]
            }

            with open("data/levels.json", "w") as file:
                file.write(json.dumps(dico_niveaux, indent=4))

            if tk.messagebox.askyesno("Info", "Labyrinthe enregistré !\nVoulez vous le tester en mode jeu ?"):
                self.parent.switch_frame("Jeu", param=dico_niveaux[name])

        return "break"

    ################ FONCTIONS CALLBACK SPINBOX / COMBOBOX ################

    def update_lab_size(self, event=None):
        """
        Met à jour la taille du labyrinthe

        Paramètres :
            event: Événement tkinter
        """
        text_to_lab_size = {f"{self.min_canvas_width * 2 ** j} x {self.min_canvas_height * 2 ** j}":
                               (self.min_canvas_width * 2 ** j, self.min_canvas_height * 2 ** j) for j in range(8)}

        self.lab_width, self.lab_height = text_to_lab_size[self.text_lab_size.get()]

        self.resize_factor = self.height_canvas // self.lab_height

        size = self.pen_size
        self.spinbox_pen_size["values"] = list(range(1, self.lab_height // self.min_canvas_height + 1))

        if size > self.lab_height // self.min_canvas_height:
            size = self.lab_height // self.min_canvas_height
        self.var_pen_size.set(size)
        self.pen_size = size

        if self.pen_type == "start":
            pen_image = self.start_image.resize((self.resize_factor, self.resize_factor))
            pen_image.putalpha(200)
            self.pen_image_tk = ImageTk.PhotoImage(pen_image)
            self.canvas.itemconfigure(self.pen_image_canvas, image=self.pen_image_tk)
        elif self.pen_type == "end":
            pen_image = self.end_image.resize((self.resize_factor, self.resize_factor))
            pen_image.putalpha(200)
            self.pen_image_tk = ImageTk.PhotoImage(pen_image)
            self.canvas.itemconfigure(self.pen_image_canvas, image=self.pen_image_tk)

        # Replace le départ et l'arrivée
        if self.start_x >= self.lab_width:
            self.start_x = self.lab_width - 1
        if self.start_y >= self.lab_height:
            self.start_y = self.lab_height - 1

        if self.end_x >= self.lab_width:
            self.end_x = self.lab_width - 1
        if self.end_y >= self.lab_height:
            self.end_y = self.lab_height - 1

        if (self.start_x, self.start_y) == (self.end_x, self.end_y):
            if (self.end_x, self.end_y) == (0, 0):
                self.end_x, self.end_y = self.lab_width - 1, self.lab_height - 1
            else:
                self.start_x, self.start_y = 0, 0

        self.start_image_tk = ImageTk.PhotoImage(self.start_image.resize((self.resize_factor, self.resize_factor)))
        self.canvas.itemconfigure(self.start_image_canvas, image=self.start_image_tk)
        self.canvas.coords(self.start_image_canvas, self.start_x * self.resize_factor, self.start_y * self.resize_factor)

        self.end_image_tk = ImageTk.PhotoImage(self.end_image.resize((self.resize_factor, self.resize_factor)))
        self.canvas.itemconfigure(self.end_image_canvas, image=self.end_image_tk)
        self.canvas.coords(self.end_image_canvas, self.end_x * self.resize_factor, self.end_y * self.resize_factor)

        # Créée la nouvelle image et y copie l'ancienne
        new_lab_img = Image.new(mode="RGB", size=(self.lab_width, self.lab_height), color=(255, 255, 255))
        new_lab_img.paste(self.lab_image)
        self.lab_image = new_lab_img

        # Empêche le départ et l'arrivée d'êtres sur des murs
        self.lab_image.putpixel((self.start_x, self.start_y), (255, 255, 255))
        self.lab_image.putpixel((self.end_x, self.end_y), (255, 255, 255))

        if self.i_lab_image != 0:
            self.all_lab_images = [Image.new(mode="RGB", size=(self.lab_width, self.lab_height), color=(255, 255, 255)),
                                   self.lab_image.copy()]

            self.i_lab_image = 1
            self.go_back_button["state"] = tk.NORMAL
        else:
            self.all_lab_images = [self.lab_image.copy()]

            self.i_lab_image = 0
            self.go_back_button["state"] = tk.DISABLED

        self.go_forward_button["state"] = tk.DISABLED

        self.update_lab_image_canvas()
        self.update_pen_size()

    def update_color(self, event=None):
        """
        Met à jour la couleur de dessin (le type de mur)

        Paramètres :
            event: Événement tkinter
        """
        text_to_color = {"Noir (mur)": (0, 0, 0, 255), "Rouge (laser)": (255, 0, 0, 255), "Blanc (chemin)": (255, 255, 255, 255)}
        self.color = text_to_color[self.text_color.get()]

    def update_pen_size(self, event=None):
        """
        Met à jour la taille du pinceau

        Paramètres :
            event: Événement tkinter
        """
        try:
            size = self.var_pen_size.get()

            if size > self.lab_height // self.min_canvas_height:
                self.pen_size = self.lab_height // self.min_canvas_height
            elif size < 1:
                self.pen_size = 1
            else:
                self.pen_size = size

            if self.pen_size * self.resize_factor > 8:
                self.canvas.coords(self.outlines_pen_image_canvas, self.width_canvas + 1, 0)

            if self.pen_type == "image":
                ratio = self.base_image_image_pen.width / self.base_image_image_pen.height
                if ratio >= self.lab_width / self.lab_height:
                    width = self.min_canvas_width * self.pen_size
                    self.image_image = self.base_image_image.resize((width, int(width / ratio)), Image.NEAREST)
                else:
                    height = self.min_canvas_height * self.pen_size
                    self.image_image = self.base_image_image.resize((int(height * ratio), height), Image.NEAREST)

                temp = self.base_image_image_pen.resize((self.image_image.width, self.image_image.height),
                                                         Image.NEAREST)
                self.image_image_pen = temp.resize((self.image_image.width * self.resize_factor, self.image_image.height * self.resize_factor),
                                                   Image.NEAREST)
                self.image_image_pen_tk = ImageTk.PhotoImage(self.image_image_pen)
                self.canvas.itemconfigure(self.pen_image_canvas, image=self.image_image_pen_tk)

        except tk.TclError:
            # Si la valeur entrée n'est pas un nombre
            pass

        self.var_pen_size.set(self.pen_size)

    def wheel_update_pen_size(self, event):
        """
        Met à jour la taille du pinceau avec la rotation de la molette de la souris

        Paramètres :
            event: Événement tkinter
        """
        if event.delta > 0:
            size_dif = 1
        else:
            size_dif = -1

        self.var_pen_size.set(self.pen_size + size_dif)
        self.update_pen_size()

        x_lab, y_lab = self.get_pos_on_lab(event.x, event.y)
        self.move_pen(x_lab, y_lab)

    ################ FONCTIONS CALLBACK CANVAS ################

    def update_lab_image_canvas(self):
        """
        Mets à jour l'image du labyrinthe affichée
        """
        self.a_star.running = False
        self.valid = False

        self.lab_image_tk = ImageTk.PhotoImage(self.lab_image.resize((self.width_canvas, self.height_canvas), Image.NEAREST))
        self.canvas.itemconfigure(self.lab_image_canvas, image=self.lab_image_tk)

    def get_pos_on_lab(self, x, y):
        """
        Calcules les coordonnées du point en haut à gauche du pinceau sur l'image du labyrinthe à partir des
        coordonnées d'un point du canvas qui en sera le centre

        Paramètres :
            int x: Abscisse du point du canvas
            int y: Ordonnée du point du canvas

        Renvoi :
            int x_lab: Abscisse du point en haut à gauche du pinceau
            int y_lab: Ordonnée du point en haut à gauche du pinceau
        """

        # Pour faire en sorte que le point (x, y) soit au centre du pinceau
        if self.pen_type == "image":
            padx = self.image_image_pen.width // 2
            pady = self.image_image_pen.height // 2
        elif self.pen_type in {"bucket", "start", "end"}:
            padx = self.resize_factor // 2
            pady = self.resize_factor // 2
        else:
            padx = self.pen_size * self.resize_factor // 2
            pady = self.pen_size * self.resize_factor // 2

        # Pour ne pas pouvoir sortir du canvas
        x = min(max(padx, x), self.width_canvas - padx - self.pen_size * self.resize_factor % 2)
        y = min(max(pady, y), self.height_canvas - pady - self.pen_size * self.resize_factor % 2)

        # Equivalent :
        # if self.pen_size * self.resize_factor % 2 == 1:
        #     x = min(max(padx, x), self.width_canvas - padx - 1)
        #     y = min(max(pady, y), self.height_canvas - pady - 1)
        # else:
        #     x = min(max(padx, x), self.width_canvas - padx)
        #     y = min(max(pady, y), self.height_canvas - pady)

        x_lab = (x - padx) // self.resize_factor
        y_lab = (y - pady) // self.resize_factor

        return x_lab, y_lab

    def motion(self, event):
        """
        Déplace le pinceau à la position de la souris

        Paramètres :
            event: Événement tkinter
        """
        x_lab, y_lab = self.get_pos_on_lab(event.x, event.y)
        self.move_pen(x_lab, y_lab)

    def draw_press(self, event):
        """
        Déplace le pinceau à la position de la souris et dessine à cette position
        Met à jour les coordonnées d'appui du pinceau

        Paramètres :
            event: Événement tkinter
        """
        x_lab, y_lab = self.get_pos_on_lab(event.x, event.y)
        self.draw(x_lab, y_lab)
        self.move_pen(x_lab, y_lab)

        self.x_press, self.y_press = x_lab, y_lab
        self.shift_direction = None

    def draw_motion(self, event):
        """
        Déplace le pinceau à la position de la souris et dessine à cette position si l'on a un pinceau permettant de
        dessiner en se déplaçant

        Paramètres :
            event: Événement tkinter
        """
        x_lab, y_lab = self.get_pos_on_lab(event.x, event.y)
        if self.pen_type in {"square", "circle"}:
            self.draw(x_lab, y_lab)
        self.move_pen(x_lab, y_lab)

    def draw_shift_motion(self, event):
        """
        Déplace le pinceau sur une ligne par rapport aux coordonnées d'appui du pinceau et à la position de la souris
        Dessine à cette position si l'on a un pinceau permettant de dessiner en se déplaçant

        Paramètres :
            event: Événement tkinter
        """
        x_lab, y_lab = self.get_pos_on_lab(event.x, event.y)

        if  self.shift_direction is None:
            if abs(self.x_press - x_lab) > abs(self.y_press - y_lab):
                y_lab = self.y_press
                if self.pen_type != "line":
                    self.shift_direction = "x"

            elif abs(self.x_press - x_lab) < abs(self.y_press - y_lab):
                x_lab = self.x_press
                if self.pen_type != "line":
                    self.shift_direction = "y"

        else:
            if self.shift_direction == "x":
                y_lab = self.y_press
            else:
                x_lab = self.x_press

        if self.pen_type in {"square", "circle"}:
            self.draw(x_lab, y_lab)

        self.move_pen(x_lab, y_lab)

    def draw_release(self, event):
        """
        Déplace le pinceau à la position de la souris et dessine à cette position si l'on est en mode ligne
        Ajoute l'image du labyrinthe actuelle à la liste des images sur lesquelles on peut revenir

        Paramètres :
            event: Événement tkinter
        """
        x_lab, y_lab = self.get_pos_on_lab(event.x, event.y)

        if self.pen_type == "line":
            self.draw(x_lab, y_lab)

        self.x_press, self.y_press = None, None
        self.shift_direction = None

        self.move_pen(x_lab, y_lab)

        if self.pen_type not in {"start", "end"}:
            while self.i_lab_image != len(self.all_lab_images) - 1:
                self.all_lab_images.pop()

            self.all_lab_images.append(self.lab_image.copy())
            self.i_lab_image += 1

            self.go_back_button["state"] = tk.NORMAL
            self.go_forward_button["state"] = tk.DISABLED

    def draw_shift_release(self, event):
        """
        Déplace le pinceau sur une ligne par rapport aux coordonnées d'appui du pinceau et à la position de la souris
        Dessine à cette position si l'on est en mode ligne
        Ajoute l'image du labyrinthe actuelle à la liste des images sur lesquelles on peut revenir

        Paramètres :
            event: Événement tkinter
        """
        x_lab, y_lab = self.get_pos_on_lab(event.x, event.y)
        if abs(self.x_press - x_lab) > abs(self.y_press - y_lab):
            y_lab = self.y_press
        elif abs(self.x_press - x_lab) < abs(self.y_press - y_lab):
            x_lab = self.x_press

        if self.pen_type == "line":
            self.draw(x_lab, y_lab)

        self.x_press, self.y_press = None, None

        self.move_pen(x_lab, y_lab)

        while self.i_lab_image != len(self.all_lab_images) - 1:
            self.all_lab_images.pop()

        self.all_lab_images.append(self.lab_image.copy())
        self.i_lab_image += 1

        self.go_back_button["state"] = tk.NORMAL
        self.go_forward_button["state"] = tk.DISABLED

    def get_pen_size_square(self):
        """
        Génère un tableau de bool formant un carré de la taille du pinceau
        False correspond à une case chemin et True une case mur

        Renvoi :
            np.ndarray: Tableau de dimensions (self.pen_size, self.pen_size) représentant le carré
        """
        return np.ones((self.pen_size, self.pen_size), dtype=bool)

    def get_pen_size_circle(self):
        """
        Génère un tableau de bool formant un rond de la taille du pinceau
        False correspond à une case chemin et True une case mur

        Renvoi :
            np.ndarray array: Tableau de dimensions (self.pen_size, self.pen_size) représentant le rond
        """
        array = np.zeros((self.pen_size, self.pen_size), dtype=bool)
        r = self.pen_size / 2

        i_center, j_center = r - 0.5, r - 0.5

        for i in range(self.pen_size):
            dj = math.sqrt(r ** 2 - (i - i_center) ** 2)

            for j in range(int(j_center - dj + 1), int(j_center + dj) + 1):
                array[i][j] = True

        return array

    def get_pen_size_line(self, start, end, outlines_only=False):
        """
        Génère un tableau de bool formant une ligne d'épaisseur la taille du pinceau de start vers end
        False correspond à une case chemin et True une case mur

        Paramètres :
            tuple(int, int) start: Coordonnées d'une des extrémités de la ligne
            tuple(int, int) end: Coordonnées de l'autre extrémité de la ligne

        Renvoi :
            np.ndarray array: Tableau de dimensions (abs(x1 - x0) + self.pen_size, abs(y1 - y0) + self.pen_size) représentant la ligne
        """
        x0, y0 = start
        x1, y1 = end

        # On normalise pour avoir des valeurs entre 0 et abs(x1 - x0) et abs(y1 - y0) respectivement
        x0, x1 = x0 - min(x0, x1), x1 - min(x0, x1)
        y0, y1 = y0 - min(y0, y1), y1 - min(y0, y1)

        # On fait en sorte que le point d'abscisse la plus petite soit (x0, y0)
        if x0 > x1:
            x0, y0, x1, y1 = x1, y1, x0, y0

        sx = 1

        array = np.zeros((abs(y1 - y0) + self.pen_size, abs(x1 - x0) + self.pen_size), dtype=bool)

        start_points = []
        end_points = []

        if not outlines_only:
            if y0 > y1:
                sy = -1

                for i in range(self.pen_size):
                    start_points.append((x0, y0 + i))
                    end_points.append((x1 + i, y1))

                for i in range(1, self.pen_size):
                    start_points.append((x0 + i, y0 + self.pen_size - 1))
                    end_points.append((x1 + self.pen_size - 1, y1 + i))

            else:
                sy = 1

                for i in range(self.pen_size):
                    start_points.append((x0 + i, y0))
                    end_points.append((x1 + self.pen_size - 1, y1 + self.pen_size - 1 - i))

                for i in range(1, self.pen_size):
                    start_points.append((x0, y0 + i))
                    end_points.append((x1 + self.pen_size - 1 - i, y1 + self.pen_size - 1))

        else:
            if y0 > y1:
                sy = -1

                for i in range(1, self.pen_size):
                    array[y0 + i][x0] = True
                    array[y1][x1 + i] = True

                start_points.append((x0, y0))
                end_points.append((x1, y1))

                for i in range(1, self.pen_size - 1):
                    array[y0 + self.pen_size - 1][x0 + i] = True
                    array[y1 + i][x1 + self.pen_size - 1] = True

                if self.pen_size > 1:
                    start_points.append((x0 + self.pen_size - 1, y0 + self.pen_size - 1))
                    end_points.append((x1 + self.pen_size - 1, y1 + self.pen_size - 1))

            else:
                sy = 1

                for i in range(self.pen_size - 1):
                    array[y0][x0 + i] = True
                    array[y1 + self.pen_size - 1 - i][x1 + self.pen_size - 1] = True

                start_points.append((x0 + self.pen_size - 1, y0))
                end_points.append((x1 + self.pen_size - 1, y1))

                for i in range(1, self.pen_size - 1):
                    array[y0 + i][x0] = True
                    array[y1 + self.pen_size - 1][x1 + self.pen_size - 1 - i] = True

                if self.pen_size > 1:
                    start_points.append((x0, y0 + self.pen_size - 1))
                    end_points.append((x1, y1 + self.pen_size - 1))

        for i in range(len(start_points)):
            x2, y2 = start_points[i]
            x3, y3 = end_points[i]

            dx = abs(x3 - x2)
            dy = -abs(y3 - y2)
            error = dx + dy

            while x2 != x3 or y2 != y3:
                array[y2][x2] = True

                error_2 = 2 * error
                if error_2 >= dy:
                    error += dy
                    x2 += sx
                if error_2 <= dx:
                    error += dx
                    y2 += sy

            array[y2][x2] = True

        array[y1 + self.pen_size - 1][x1 + self.pen_size - 1] = True

        return array

    def move_pen(self, x_lab, y_lab):
        """
        Déplace et génère l'image du pinceau sur le canvas en fonction de son type et de ses coordonnées sur le labyrinthe
        À l'exception des modes image, placer le départ et l'arrivée, les contours du pinceau sont générés de couleur
        opposée à la couleur de la case de labyrinthe sur laquelle ils sont afin de toujours bien pouvoir repérer le pinceau

        Paramètres :
            int x_lab: Abscisse du point en haut à gauche du pinceau sur l'image du labyrinthe
            int y_lab: Ordonnée du point en haut à gauche du pinceau sur l'image du labyrinthe
        """
        snap_x = x_lab * self.resize_factor
        snap_y = y_lab * self.resize_factor

        array_pen_img = np.full((self.pen_size * self.resize_factor, self.pen_size * self.resize_factor, 4),
                                (255, 255, 255, 0), dtype=np.uint8)

        # Ajoute des traits autour du pinceau s'il est trop petit pour être visible
        if self.pen_size * self.resize_factor <= 8 and self.pen_type != "image" or \
                self.resize_factor <= 8 and self.pen_type in {"bucket", "start", "end"}:

            pen_size = 1 if self.pen_type in {"bucket", "start", "end"} else self.pen_size

            outlines_size = self.outlines_pen_size * 2 + pen_size * self.resize_factor
            self.outlines_pen_image = Image.new(mode="RGBA", size=(outlines_size, outlines_size),
                                                color=(255, 255, 255, 0))

            for i in range(self.outlines_pen_size):
                for dx1, dy1 in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
                    dx2 = pen_size * self.resize_factor if dx1 > 0 else -1
                    dy2 = pen_size * self.resize_factor if dy1 > 0 else -1

                    x = snap_x + dx1 * i + dx2
                    y = snap_y + dy1 * i + dy2

                    if 0 <= x < self.width_canvas and 0 <= y < self.height_canvas:
                        r, g, b = self.lab_image.getpixel((x // self.resize_factor, y // self.resize_factor))

                        pos = self.outlines_pen_size + dx1 * i + dx2, self.outlines_pen_size + dy1 * i + dy2
                        self.outlines_pen_image.putpixel(pos, (255 - r, 255 - g, 255 - b, 255))     # couleur inverse

            self.outlines_pen_image_tk = ImageTk.PhotoImage(self.outlines_pen_image)
            self.canvas.itemconfigure(self.outlines_pen_image_canvas, image=self.outlines_pen_image_tk)
            self.canvas.coords(self.outlines_pen_image_canvas, snap_x - self.outlines_pen_size, snap_y - self.outlines_pen_size)

        # On trace les contours du pinceau en couleur inverse de celle de fond
        if self.pen_type in {"square", "circle", "line","bucket"}:

            if self.pen_type == "square":
                array_draw_image = self.get_pen_size_square()
            elif self.pen_type == "circle":
                array_draw_image = self.get_pen_size_circle()
            elif self.pen_type == "line":
                if self.x_press is not None:
                    array_draw_image = self.get_pen_size_line((self.x_press, self.y_press), (x_lab, y_lab), outlines_only=True)
                    array_pen_img = np.full((len(array_draw_image) * self.resize_factor, len(array_draw_image[0]) * self.resize_factor, 4),
                                            (255, 255, 255, 0), dtype=np.uint8)
                    snap_x = min(snap_x, self.x_press * self.resize_factor)
                    snap_y = min(snap_y, self.y_press * self.resize_factor)
                else:
                    array_draw_image = self.get_pen_size_square()
            else:
                array_draw_image = np.ones((1, 1), dtype=bool)

            i, j = 0, 0
            k, l = 0, 0

            while i < len(array_draw_image) and not array_draw_image[i][j]:
                l += 1
                j = l // self.resize_factor
                if j >= self.pen_size:
                    l = 0
                    j = 0
                    k += 1
                    i = k // self.resize_factor

            start = None
            last_k, last_l = k, l - 1

            if 0 <= i < len(array_draw_image) and 0 <= j < len(array_draw_image[0]):
                r, g, b = self.lab_image.getpixel(((snap_x + l) // self.resize_factor, (snap_y + k) // self.resize_factor))
                array_pen_img[k][l] = (255 - r, 255 - g, 255 - b, 255)  # couleur inverse

            # On fait le tour en sens horaire
            while (k, l) != start:
                if start is None:
                    start = (k, l)

                if self.pen_type == "line":
                    d = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
                else:
                    d = [(0, 1), (1, 0), (0, -1), (-1, 0)]

                q0 = d.index((k - last_k, l - last_l)) - 1
                last_k, last_l = k, l

                q = 0
                while q < len(d) and (k, l) == (last_k, last_l):
                    dk, dl = d[(q0 + q) % len(d)]

                    i = (k + dk) // self.resize_factor
                    j = (l + dl) // self.resize_factor

                    if 0 <= i < len(array_draw_image) and 0 <= j < len(array_draw_image[0]) and array_draw_image[i][j]:
                        k += dk
                        l += dl
                        r, g, b = self.lab_image.getpixel(((snap_x + l) // self.resize_factor, (snap_y + k) // self.resize_factor))
                        array_pen_img[k][l] = (255 - r, 255 - g, 255 - b, 255)

                    q += 1

            self.pen_image_tk = ImageTk.PhotoImage(Image.fromarray(array_pen_img, mode="RGBA"))
            self.canvas.itemconfigure(self.pen_image_canvas, image=self.pen_image_tk)

        self.canvas.coords(self.pen_image_canvas, snap_x, snap_y)

    def draw(self, x_lab, y_lab):
        """
        Dessine la forme correspondant au type de pinceau actuel aux coordonnées demandées

        Paramètres :
            int x_lab: Abscisse du point en haut à gauche du pinceau sur l'image du labyrinthe
            int y_lab: Ordonnée du point en haut à gauche du pinceau sur l'image du labyrinthe
        """
        if self.pen_type == "square" or self.pen_type == "circle":

            if self.pen_type == "square":
                mask_draw_image = self.get_pen_size_square()
            else:
                mask_draw_image = self.get_pen_size_circle()

            array_draw_image = np.full((self.pen_size, self.pen_size, 4), (255, 255, 255, 0), dtype=np.uint8)
            array_draw_image[mask_draw_image] = self.color
            draw_image = Image.fromarray(array_draw_image)
            self.lab_image.paste(draw_image, box=(x_lab, y_lab), mask=draw_image)

        elif self.pen_type == "line":
            if self.x_press is not None:
                mask_draw_image = self.get_pen_size_line((self.x_press, self.y_press), (x_lab, y_lab))
                array_draw_image = np.full((len(mask_draw_image), len(mask_draw_image[0]), 4), (255, 255, 255, 0), dtype=np.uint8)
                array_draw_image[mask_draw_image] = self.color
                draw_image = Image.fromarray(array_draw_image)
                self.lab_image.paste(draw_image, box=(min(self.x_press, x_lab), min(self.y_press, y_lab)), mask=draw_image)

        elif self.pen_type == "bucket":
            ImageDraw.floodfill(self.lab_image, (x_lab, y_lab), self.color)

        elif self.pen_type == "image":
            self.lab_image.paste(self.image_image, box=(x_lab, y_lab), mask=self.image_image)

        elif self.pen_type == "start":
            if (x_lab, y_lab) != (self.end_x, self.end_y):
                self.start_x, self.start_y = x_lab, y_lab
                self.canvas.coords(self.start_image_canvas, self.start_x * self.resize_factor, self.start_y * self.resize_factor)
                self.lab_image.putpixel((self.start_x, self.start_y), (255, 255, 255))

        elif self.pen_type == "end":
            if (x_lab, y_lab) != (self.start_x, self.start_y):
                self.end_x, self.end_y = x_lab, y_lab
                self.canvas.coords(self.end_image_canvas, self.end_x * self.resize_factor, self.end_y * self.resize_factor)
                self.lab_image.putpixel((self.end_x, self.end_y), (255, 255, 255))

        # Empêche le départ et l'arrivée d'êtres sur des murs
        self.lab_image.putpixel((self.start_x, self.start_y), (255, 255, 255))
        self.lab_image.putpixel((self.end_x, self.end_y), (255, 255, 255))

        self.update_lab_image_canvas()
