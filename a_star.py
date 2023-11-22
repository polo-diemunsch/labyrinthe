import tkinter as tk
from tkinter import messagebox
from PIL import Image
from queue import PriorityQueue
from threading import Thread
from time import time


class AStar:
    """
    Classe gérant la recherche de plus court chemin à l'aide de l'algorithme de A* (AStar)

    Attributs principaux :
        tk.Frame parent_frame: Frame parent sur laquelle se situe le labyrinthe à résoudre

        tuple(int, int) start: Point de départ de la recherche
        tuple(int, int) end: Point d'arrivée de la recherche
    """

    def __init__(self, parent_frame):
        """
        Initialise l'objet et récupère la frame parent

        Paramètres :
            tk.Frame parent_frame: Frame parent sur laquelle se situe le labyrinthe à résoudre
        """
        self.parent_frame = parent_frame

        self.reinitialisation()

        self.start = (0, 0)
        self.end = (0, 0)

        self.running = False    # Booléen permettant de stopper la recherche en cours
        self.dist = {}          # Dictionnaire de distances
        self.parent = {}        # Dictionnaire de parenté entre les points (au niveau de la recherche)

        self.shortest_path = [] # List des points formant le chemin le plus court

        self.thread = Thread(target=self.find_shortest_path)

    def reinitialisation(self):
        """"
        Réinitialise l'objet et récupère l'image du labyrinthe le canvas, l'id de l'image d'affichage, etc...
        """
        self.image = self.parent_frame.lab_image
        self.canvas = self.parent_frame.canvas
        self.id_image_canvas = self.parent_frame.lab_image_canvas

        self.img_gui = self.image.copy()
        self.image_tk = self.parent_frame.lab_image_tk

        self.img_canvas_width = int(self.canvas.cget("width"))
        self.img_canvas_height = int(self.canvas.cget("height"))

    @staticmethod
    def manhattan_distance(p0, p1):
        """
        Fonction heuristique utilisée pour estimer la distance entre deux points

        Paramètres :
            tuple(int, int) p0: Coordonnées du premier point
            tuple(int, int) p1: Coordonnées du deuxième point

        Renvoi :
            La distance de manhattan (ou norme 1) entre les deux points
        """
        return abs(p0[0] - p1[0]) + abs(p0[1] - p1[1])

    def find_shortest_path(self, show_search=False):
        """
        Fonction de recherche de plus court chemin entre le départ et l'arrivée sur l'image du labyrinthe

        Paramètres :
            bool show_search: Booléen définissant si l'on réalise l'affichage des points visités lors de la recherche
        """
        t0 = time()
        i = 0                       # Permet d'ordonner les points de même valeur de distance au départ + heuristique
        pq = PriorityQueue()        # File triée des points à visiter
        pq.put((self.manhattan_distance(self.start, self.end), -i, self.start))

        self.dist = {self.start: 0}
        self.parent = {self.start: None}
        self.shortest_path = []

        found = False

        while not pq.empty() and not found and self.running:
            weight, j, current = pq.get()

            if show_search:
                self.img_gui.putpixel(current, (255, 182, 193))

            if current == self.end:
                found = True

            elif weight - self.manhattan_distance(current, self.end) == self.dist[current]:

                if (current[0] + current[1]) % 2 == 0:
                    moves = [(-1, 0), (0, 1), (0, -1), (1, 0)]
                else:
                    moves = [(1, 0), (0, -1), (0, 1), (-1, 0)]

                for dx, dy in moves:
                    neighbour = (current[0] + dx, current[1] + dy)

                    if 0 <= neighbour[0] < self.image.width and 0 <= neighbour[1] < self.image.height:

                        if self.image.getpixel(neighbour) == (255, 255, 255):

                            if neighbour not in self.dist or self.dist[neighbour] > self.dist[current] + 1:
                                self.dist[neighbour] = self.dist[current] + 1
                                self.parent[neighbour] = current

                                i += 1
                                pq.put((self.dist[neighbour] + self.manhattan_distance(neighbour, self.end), -i, neighbour))

                                if show_search:
                                    self.img_gui.putpixel(neighbour, (180, 0, 255))

        if self.running:
            if found:
                current = self.end
                while current is not None:
                    self.img_gui.putpixel(current, (0, 255, 0))

                    self.shortest_path.append(current)
                    current = self.parent[current]
                self.shortest_path.reverse()

                t1 = time()

                self.image_tk.paste(self.img_gui.resize((self.img_canvas_width, self.img_canvas_height), Image.NEAREST))

                self.parent_frame.valid = True
                tk.messagebox.showinfo("Info", f"Le chemin a été trouvé en {t1 - t0: .2f} s !")
            else:
                t1 = time()
                tk.messagebox.showerror("Erreur", f"Le labyrinthe n'est pas solvable ({t1 - t0: .2f} s)")

            self.running = False

    def update(self, delay):
        """
        Mets à jour l'image affichée du labyrinthe

        Paramètres :
            int delay: Délai (en ms) après lequel on appelle à nouveau la fonction
        """
        self.image_tk.paste(self.img_gui.resize((self.img_canvas_width, self.img_canvas_height), Image.NEAREST))
        if self.thread.is_alive():
            self.canvas.after(delay, lambda: self.update(delay))

    def run(self, start, end, show_search=False):
        """
        Lance la recherche de plus court chemin dans un Thread

        Paramètres :
            bool show_search: Booléen définissant si l'on réalise l'affichage des points visités lors de la recherche
        """
        self.reinitialisation()
        self.start = start
        self.end = end
        self.running = True

        self.img_gui = self.image.copy()
        self.thread = Thread(target=self.find_shortest_path, args=(show_search,))
        self.thread.start()
        if show_search:
            self.update(50)

    def quit(self):
        """
        Stoppe la recherche et attend que le thread se termine
        """
        self.running = False

        # Attend que le thread se finisse
        if self.thread.is_alive():
            self.thread.join()
