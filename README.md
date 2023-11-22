# LabyBouffe

Notre projet d'Algo de fin d'année 2022-2023 est un outil de création de Labyrinthe.

On utilise **[tkinter](https://docs.python.org/3/library/tkinter.html)** pour l'interface graphique.

### 2 modes sont disponibles

- Plat du jour : Mode création, tout un matériel de dessin (on peut même importer des images !) est à votre disposition pour créer votre propre labyrinthe.

<div align="center">
    <img src=images/mode_creation.png>
</div> &nbsp;

- Menu étudiant : Mode jeu, aidez Homer à atteindre son donut tout en évitant les obstacles et les lasers.

<div align="center">
    <img src=images/mode_jeu.png>
</div>

## Résolution de labyrtinthe

Si vous vous retrouvez bloqué dans un labyrinthe, pas de panique nous avons tout prévu. Un bouton résoudre permet de vous guider vers la sortie.

<div align="center">
    <img src=images/resolution.png>
</div> &nbsp;

On retrouve en vert le chemin à suivre et en rose les cases ayant été visitées par l'algo de recherche.

En parlant de cela, l'algorithme utilisé pour la recherche de plus court chemin est **[l'algorithme de A*](https://fr.wikipedia.org/wiki/Algorithme_A*)**.

Cet outil de résolution de labyrinthe est également utile dans le mode création d'une part pour tester le labyrinthe mais surtout pour vérifier qu'il est bien solvable avant de l'enregistrer.

Petite démo de l'algo sur un grand labyrinthe :

<div align="center">
    <img src=images/demo_a_star.gif>
</div>

## Architecture du code

Voici l'organisation du code, structuré sous forme de classes :

<div align="center">
    <img src=images/diagramme_classes.png>
</div>

## Petit bonus

La taille de la fenêtre de l'interface graphique est fixe mais est calculée en fonction de la taille de l'écran.

Pour l'affichage d'un labyrinthe, l'image peut être agrandie mais jamais réduite afin de ne pas perdre des cases.
Ainsi, les labyrinthes trop grands ne sont pas disponibles si l'écran ne permet pas de les afficher à l'echelle 1:1.

## Prérequis

- python ≥ 3.10

- numpy ≥ 1.24.3

- Pillow ≥ 9.5.0

## Utilisation

- Lancer main.py ou l'exécutable

- Have fun !

## Credits

### Images

- Images tirées de *The Simpsons* et de *Charlotte aux fraises*.

## Auteurs

- **[Polo](https://github.com/polo-diemunsch)**
- Lucile
- Mayssa
- Valentin
