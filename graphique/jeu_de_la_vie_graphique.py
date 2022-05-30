import pygame
import numpy
import math
import colorsys
import random

# ---Déclaration des variables globales et initialisations---
taille_grille = 6

taille_grille = taille_grille // 2 * 2
taille_tableaux = taille_grille // 2

coords_plus_plus = [[{"valeur": False, "traitee": False} for _ in range(taille_tableaux)] for _ in range(taille_tableaux)]
coords_moins_plus = [[{"valeur": False, "traitee": False} for _ in range(taille_tableaux)] for _ in range(taille_tableaux)]
coords_moins_moins = [[{"valeur": False, "traitee": False} for _ in range(taille_tableaux)] for _ in range(taille_tableaux)]
coords_plus_moins = [[{"valeur": False, "traitee": False} for _ in range(taille_tableaux)] for _ in range(taille_tableaux)]

coords = [coords_plus_plus, coords_moins_plus, coords_moins_moins, coords_plus_moins]

# coordonnées relatives des cases présentes autour d'une case
coords_autour = [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]

cellules_vivantes = []

generation = 1

taille_cases = 50
valeur_taille_cases = 1

pygame.init()
montre = pygame.time.Clock()
quitter = False

# Donne les dimensions de la fenetre
infos_fenetre = pygame.display.Info()
ecran = pygame.display.set_mode((infos_fenetre.current_w, infos_fenetre.current_h))
pygame.display.set_caption("Jeu de la vie")

rect_grille = pygame.Rect(infos_fenetre.current_w / 5 + 5, infos_fenetre.current_h / 5, infos_fenetre.current_w / 5 * 3, infos_fenetre.current_h / 5 * 3)
surf_grille = pygame.Surface((rect_grille.width, rect_grille.height))
rect_interface_droite = pygame.Rect(infos_fenetre.current_w / 5 * 4, 0, infos_fenetre.current_w / 5, infos_fenetre.current_h)

# permet d'éxécuter cet évènement (passage à la génération suivante) toute les x milisecondes
evenement_nouv_gen = pygame.USEREVENT + 1
vitesse_evolution = 1000
pygame.time.set_timer(evenement_nouv_gen, vitesse_evolution)
evolution = False

cellule_survolee = ()
decalage = (0, 0)
pos_base = ()

option_cliquee = "non"

police_options = pygame.font.Font('seguisym.ttf', int(infos_fenetre.current_h / 30))

couleur_cellules = (255, 0, 0)
mode_couleurs = True

cases_traitees = []

zone_placement_rect = pygame.Rect(0, 0, taille_cases, taille_cases)
probabilite_placement = 100
mode_placement = True

aide = False


# --- créations des boutons et barres d'option ---
class Bouton(pygame.sprite.Sprite):
    def __init__(self, pos, taille_bouton, texte, taille_police, action):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(0, 0, taille_bouton[0], taille_bouton[1])
        self.rect.center = (pos[0], pos[1])
        self.image = pygame.Surface((self.rect.w, self.rect.h))
        self.texte = texte
        self.pos_texte = (pos[0], pos[1] - 2)
        self.action = action
        self.police = pygame.font.Font('seguisym.ttf', taille_police)

    def update(self):
        pygame.draw.rect(ecran, "white", self.rect, 5)
        if self.rect.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
            pygame.draw.rect(ecran, "#12192b", self.rect, 2)
        surf_texte = self.police.render(self.texte, True, "white")
        rect_texte = surf_texte.get_rect(center=self.pos_texte)
        ecran.blit(surf_texte, rect_texte)


# fonctions boutons
def taille_grille_plus():
    global taille_tableaux
    global taille_grille

    taille_tableaux += 1
    taille_grille += 2
    for tab in coords:
        for tab2 in tab:
            tab2.append({"valeur": False, "traitee": False})
        tab.append([{"valeur": False, "traitee": False} for _ in range(taille_tableaux)])


def taille_grille_moins():
    global taille_tableaux
    global taille_grille
    global cellules_vivantes

    if taille_tableaux > 1:
        taille_tableaux -= 1
        taille_grille -= 2
        for tab in coords:
            for tab2 in tab:
                tab2.pop()
            tab.pop()

    cellule_a_retirer = []
    for cellule in cellules_vivantes:
        if cellule[0] > taille_tableaux or cellule[1] > taille_tableaux:
            cellule_a_retirer.append(cellule)
    for cellule in cellule_a_retirer:
        cellules_vivantes.remove(cellule)


def lance_stop_evolution(bouton):
    global evolution
    evolution = not evolution
    if evolution:
        bouton.texte = "❚❚"
    else:
        bouton.texte = "▶"


def active_desactive_couleurs():
    global mode_couleurs
    mode_couleurs = not mode_couleurs
    if mode_couleurs:
        bouton.texte = "✖"
    else:
        bouton.texte = ""


def active_desactive_placement():
    global mode_placement
    mode_placement = not mode_placement
    if mode_placement:
        bouton.texte = "✖"
    else:
        bouton.texte = ""


def quitter_jeu():
    global quitter
    quitter = True


def entre_ou_sort_fenetre_aide():
    global aide
    aide = True


def reinitialiser():
    global generation
    global cellules_vivantes
    global coords_plus_plus
    global coords_moins_plus
    global coords_moins_moins
    global coords_plus_moins
    global coords

    generation = 1
    cellules_vivantes = []

    coords_plus_plus = [[{"valeur": False, "traitee": False} for _ in range(taille_tableaux)] for _ in range(taille_tableaux)]
    coords_moins_plus = [[{"valeur": False, "traitee": False} for _ in range(taille_tableaux)] for _ in range(taille_tableaux)]
    coords_moins_moins = [[{"valeur": False, "traitee": False} for _ in range(taille_tableaux)] for _ in range(taille_tableaux)]
    coords_plus_moins = [[{"valeur": False, "traitee": False} for _ in range(taille_tableaux)] for _ in range(taille_tableaux)]

    coords = [coords_plus_plus, coords_moins_plus, coords_moins_moins, coords_plus_moins]


boutons = []
bouton_taille_grille_plus = Bouton((infos_fenetre.current_w / 40 * 37 + 30, infos_fenetre.current_h / 40 * 9), (30, 30), "+", 30, "taille_grille_plus()")
bouton_taille_grille_moins = Bouton((infos_fenetre.current_w / 40 * 37 - 30, infos_fenetre.current_h / 40 * 9), (30, 30), "-", 30, "taille_grille_moins()")
bouton_lance_evolution = Bouton((infos_fenetre.current_w / 10, infos_fenetre.current_h / 2), (60, 60), "▶", 40, "lance_stop_evolution(bouton)")
bouton_couleurs = Bouton((infos_fenetre.current_w / 40 * 33, infos_fenetre.current_h / 5 * 4), (20, 20), "✖", 20, "active_desactive_couleurs()")
bouton_placement = Bouton((infos_fenetre.current_w / 40 * 33, infos_fenetre.current_h / 20 * 9), (20, 20), "✖", 20, "active_desactive_placement()")
bouton_quitter = Bouton((65, 40), (90, 40), "QUITTER", 20, "quitter_jeu()")
bouton_reinitialiser = Bouton((infos_fenetre.current_w / 2, infos_fenetre.current_h / 5 * 4 + 30), (140, 40), "RÉINITIALISER", 20, "reinitialiser()")
bouton_aide = Bouton((50, infos_fenetre.current_h - 50), (60, 40), "AIDE", 20, "entre_ou_sort_fenetre_aide()")
bouton_sortir_aide = Bouton((infos_fenetre.current_w - 50, 50), (90, 40), "RETOUR", 20, "entre_ou_sort_fenetre_aide()")
boutons.append(bouton_taille_grille_plus)
boutons.append(bouton_taille_grille_moins)
boutons.append(bouton_lance_evolution)
boutons.append(bouton_couleurs)
boutons.append(bouton_placement)
boutons.append(bouton_quitter)
boutons.append(bouton_reinitialiser)
boutons.append(bouton_aide)


class BarreOption(pygame.sprite.Sprite):
    curseur = False

    def __init__(self, rect, cache):
        pygame.sprite.Sprite.__init__(self)
        self.rect = rect
        self.image = pygame.Surface((rect.w, rect.h))
        self.cache = cache

    def update(self):
        if not self.cache:
            pygame.draw.rect(ecran, "white", self.rect, 0, 50)


class CurseurOption(pygame.sprite.Sprite):
    clique = False
    curseur = True
    pos_texte = ()
    ratio = 0

    def __init__(self, rect, extremes, intervalle, valeur, cache):
        pygame.sprite.Sprite.__init__(self)
        self.rect = rect
        self.ratio = (extremes[1] - extremes[0]) / (intervalle[1] - intervalle[0])
        self.rect.center = (extremes[0] + self.ratio * (valeur - intervalle[0]), rect.center[1])
        self.image = pygame.Surface((rect.w, rect.h))
        self.image.fill("white")
        self.extremes = extremes
        self.intervalle = intervalle
        self.valeur = valeur
        self.pos_texte = (extremes[0] + (extremes[1] - extremes[0]) / 2, rect.center[1] - rect.height)
        self.cache = cache

    def update(self):
        pygame.draw.rect(ecran, "white", self.rect, 0, 50)
        if not self.cache:
            surf_texte = police_options.render(str(round(self.valeur)), True, "white")
            rect_texte = surf_texte.get_rect(center=self.pos_texte)
            ecran.blit(surf_texte, rect_texte)

        if self.clique:
            self.rect.center = (max(self.extremes[0], min(pygame.mouse.get_pos()[0], self.extremes[1])), self.rect.center[1])
            self.valeur = self.intervalle[0] + (self.rect.center[0] - self.extremes[0]) / self.ratio


def cree_barre_option(pos, taille, intervalle, valeur, cache=False):
    """
    Créé une barre avec un curseur pour récupérer une entrée d'utilisateur
    IN: pos (tuple) - la position centrale de la barre
    IN: taille (tuple) - la largeur et la hauteur de la barre
    IN: intervalle (tuple) - l'intervalle de valeurs pouvant etre prises par la variable gérée par la barre d'option
    IN: valeur (int) - la valeur de base de la variable gérée par la barre d'option
    IN: cache (bool) - défini si la barre doit être visible ou non (le rendu de la barre saturation est fait ailleurs)
    OUT: (pygame.sprite.Group()) - un groupe de sprite contenant la barre et le curseur
    """
    groupe_sprite = pygame.sprite.Group()
    rect_barre = pygame.Rect(0, 0, taille[0], taille[1])
    rect_barre.center = pos
    rect_curseur = pygame.Rect(0, 0, taille[1] * 4, taille[1] * 4)
    rect_curseur.center = pos

    groupe_sprite.add(BarreOption(rect_barre, cache))
    groupe_sprite.add(CurseurOption(rect_curseur, (pos[0] - taille[0] / 2, pos[0] + taille[0] / 2), intervalle, valeur, cache))
    return groupe_sprite


longueur_barres = int(infos_fenetre.current_w / 20 * 2)
barres_option = {}
barre_vitesse = cree_barre_option((infos_fenetre.current_w / 40 * 37, infos_fenetre.current_h / 40 * 3), (longueur_barres, 5), (1, 20), 5)
barre_zoom = cree_barre_option((infos_fenetre.current_w / 40 * 37, infos_fenetre.current_h / 40 * 6), (longueur_barres, 5), (1, 10), 5)
barre_saturation = cree_barre_option((infos_fenetre.current_w / 15 * 14, infos_fenetre.current_h / 15 * 14), (longueur_barres, 5), (1, 255), 255, True)
barre_taille_placement = cree_barre_option((infos_fenetre.current_w / 15 * 14, infos_fenetre.current_h / 20 * 11), (longueur_barres, 5), (1, 10), 1)
barre_probabilite_placement = cree_barre_option((infos_fenetre.current_w / 15 * 14, infos_fenetre.current_h / 20 * 8 + 10), (longueur_barres, 5), (1, 100), 100)

barres_option["vitesse_evolution"] = barre_vitesse
barres_option["zoom"] = barre_zoom
barres_option["saturation"] = barre_saturation
barres_option["taille_placement"] = barre_taille_placement
barres_option["probabilite_placement"] = barre_probabilite_placement


# --- fonctions de conversions ---
def coords_vers_indices(x, y):
    """
    Renvoie les indice menants à l'élément d'une cellule sur la grille de jeu en fonction de ses coordonnées x et y (chaque cellule vaut 1 unité)
    IN: x (int) - la coordonnée x de la cellule dont on cherche les informations
    IN: y (int) - la coordonnée y de la cellule dont on cherche les informations
    OUT: (tuple) - un tuple contenant l'indice du tableau cadran, l'indice correpondant au tableau de la ligne et l'indice correspondant au tableau de la colonne
    """
    if x > 0:
        if y > 0:
            return 0, x - 1, y - 1
        else:
            return 3, x - 1, abs(y) - 1
    else:
        if y > 0:
            return 1, abs(x) - 1, y - 1
        else:
            return 2, abs(x) - 1, abs(y) - 1


def pos_vers_coords(pos):
    """
    Renvoie les coordonnées d'une cases sur la grille (ex : [1, 1], [-3, 5]...) se trouvant à la position donnée (position sur l'écran)
    IN: pos (tuple) - la position de la case sur l'écran
    OUT: (tuple) - les coordonnées de la case
    """
    coord_case_x = (pos[0] - infos_fenetre.current_w / 2 - decalage[0]) / taille_cases / 2
    coord_case_x = int(coord_case_x + (abs(coord_case_x) + 1) * numpy.sign(coord_case_x))
    coord_case_y = (pos[1] - infos_fenetre.current_h / 2 - decalage[1]) / taille_cases / 2
    coord_case_y = - int(coord_case_y + (abs(coord_case_y) + 1) * numpy.sign(coord_case_y))
    return coord_case_x, coord_case_y


def coords_vers_pos(coords):
    """
    Renvoie la position centrale d'une case se trouvant aux coordonnées données
    IN: coords (tuple) - les coordonnées de la case (ex : [3, 7], [-2, 6])
    OUT: (tuple) - la position centrale de la case
    """
    # reviens à transformer [-3, -2, -1, 1, 2, 3] en [-5, -3, -1, 1, 3, 5] (coordonnées des cases)
    posx = rect_grille.width / 2 + decalage[0] + taille_cases / 2 * (coords[0] + (abs(coords[0]) - 1) * numpy.sign(coords[0]))
    posy = rect_grille.height / 2 + decalage[1] + taille_cases / 2 * -((coords[1]) + (abs(coords[1]) - 1) * numpy.sign(coords[1]))
    return posx, posy


# --- fonctions liées aux tableaux ---
def coords_cases_voisines(case_x, case_y):
  """
  Renvoie la liste des coordonnées des cases autour d'une case donnée (diagonales comprises)
  IN: case_x (int) - la coordonnée x de la case centrale
  IN: case_y (int) - la coordonnée y de la case centrale
  OUT: (list) - une liste contenant des tuples de la forme (x, y) des cases voisines de la case donnée
  """
  global taille_grille
  global taille_tableaux
  global coords

  cases_autour = []
  for decalage_coords in coords_autour:
      x = case_x + decalage_coords[0]
      y = case_y + decalage_coords[1]

      # gère le cas où l'on doit passer d'un tableau à l'autre (on saute le 0)
      if case_x + decalage_coords[0] == 0:
          x = case_x + decalage_coords[0] * 2

      if case_y + decalage_coords[1] == 0:
          y = case_y + decalage_coords[1] * 2

      # aggrandis la grille si une case à traiter est à l'extérieur
      if abs(x) > taille_tableaux or abs(y) > taille_tableaux:
          taille_grille += 2
          taille_tableaux += 1
          for tab in coords:
            for tab2 in tab:
              tab2.append({"valeur": False, "traitee": False})
            tab.append([{"valeur": False, "traitee": False} for _ in range(taille_tableaux)])

      cases_autour.append((x, y))
  return cases_autour


def affiche_grille():
  """
  Fait le rendu de la grille sur l'écran
  """
  # coords des cellules aux extrémités de la grille (fait le rendu des cellules seulement si elle sont visibles sur la zone de la grille)
  coords_haut_gauche = pos_vers_coords((rect_grille.left, rect_grille.top - taille_cases))
  coords_bas_droite = pos_vers_coords((rect_grille.right + taille_cases, rect_grille.bottom))

  surf_grille.fill("#222F52")
  for i in [x for x in range(coords_bas_droite[1], coords_haut_gauche[1]) if x != 0 and -taille_tableaux <= x <= taille_tableaux]:
      for j in [x for x in range(coords_haut_gauche[0], coords_bas_droite[0]) if x != 0 and -taille_tableaux <= x <= taille_tableaux]:
        pos = coords_vers_pos((j, i))
        rect_case = pygame.Rect(0, 0, taille_cases, taille_cases)
        rect_case.center = (pos[0], pos[1])

        indices = coords_vers_indices(j, i)
        if coords[indices[0]][indices[1]][indices[2]]["valeur"]:
            if mode_couleurs:
              pygame.draw.rect(surf_grille, coords[indices[0]][indices[1]][indices[2]]["couleur"], rect_case)
              pygame.draw.rect(surf_grille, "white", rect_case, int(0.05 * taille_cases) + 1)
            else:
              pygame.draw.rect(surf_grille, "white", rect_case)
        else:
          pygame.draw.rect(surf_grille, "white", rect_case, int(0.05 * taille_cases) + 1)
  if mode_placement:
    pygame.draw.rect(surf_grille, "red", zone_placement_rect, 5)
  ecran.blit(surf_grille, (rect_grille.left, rect_grille.top))


def nouvelle_generation():
    """
    Fait avancer l'état de la grille à la génération suivante (fait un tour de créations/suppréssions de cellules)
    """
    global generation
    generation += 1

    # toutes les modifications de cellules se font après les calculs car les cellules sont sensées toutes se mettre à jour en même temps
    cases_a_traiter = []
    cellules_a_retirer = []
    cellules_a_ajouter = []

    for cellule in cellules_vivantes:
        if not cellule in cases_a_traiter:
            cases_a_traiter.append(cellule)
        for coords_cellule in coords_cases_voisines(cellule[0], cellule[1]):
            if not coords_cellule in cases_a_traiter:
                cases_a_traiter.append(coords_cellule)

    for case_centre in cases_a_traiter:
        total_cellules_voisines = 0
        cellules_voisines = []
        for case in coords_cases_voisines(case_centre[0], case_centre[1]):
            indices = coords_vers_indices(case[0], case[1])
            if coords[indices[0]][indices[1]][indices[2]]["valeur"]:
                total_cellules_voisines += 1
                cellules_voisines.append(case)

        indices = coords_vers_indices(case_centre[0], case_centre[1])
        case_habite = coords[indices[0]][indices[1]][indices[2]]["valeur"]

        if (total_cellules_voisines < 2 or total_cellules_voisines > 3) and case_habite:
            cellules_a_retirer.append(indices)
            cellules_vivantes.remove(case_centre)

        elif not case_habite and total_cellules_voisines == 3:
            # fait la moyenne des couleurs des cases voisines
            r, g, b = 0, 0, 0
            for cellule in cellules_voisines:
                indices_cellule = coords_vers_indices(cellule[0], cellule[1])
                couleur_cellule = coords[indices_cellule[0]][indices_cellule[1]][indices_cellule[2]]["couleur"]
                r += couleur_cellule[0]
                g += couleur_cellule[1]
                b += couleur_cellule[2]
            couleur = (r / 3, g / 3, b / 3)

            cellules_a_ajouter.append((indices, couleur))
            cellules_vivantes.append(case_centre)

    for indices_cellule in cellules_a_retirer:
        coords[indices_cellule[0]][indices_cellule[1]][indices_cellule[2]]["valeur"] = False
    for indices_cellule, couleur_cellule in cellules_a_ajouter:
        coords[indices_cellule[0]][indices_cellule[1]][indices_cellule[2]]["valeur"] = True
        coords[indices_cellule[0]][indices_cellule[1]][indices_cellule[2]]["couleur"] = couleur_cellule


def change_case():
    """
    Pose ou retire des cellule dans les cases présente dans la zone de placement ou a la position de la souris
    """
    coord_haut_gauche = pos_vers_coords((zone_placement_rect.left + rect_grille[0] + taille_cases / 2, zone_placement_rect.top + rect_grille[1] + taille_cases / 2))
    coord_bas_droite = pos_vers_coords((zone_placement_rect.right + rect_grille[0] - taille_cases / 2, zone_placement_rect.bottom + rect_grille[1] - taille_cases / 2))
    if mode_placement:
        for x in range(coord_haut_gauche[0], coord_bas_droite[0] + 1):
            for y in range(coord_bas_droite[1], coord_haut_gauche[1] + 1):
                if abs(x) <= taille_tableaux and abs(y) <= taille_tableaux and x != 0 and y != 0:
                    indices = coords_vers_indices(x, y)
                    if not coords[indices[0]][indices[1]][indices[2]]["traitee"]:
                        # probabilite_placement:
                        prob_max = int(100 / max(1, min(100, probabilite_placement)))
                        if random.randint(1, prob_max) == 1:
                            if coords[indices[0]][indices[1]][indices[2]]["valeur"]:
                                coords[indices[0]][indices[1]][indices[2]]["valeur"] = False
                                cellules_vivantes.remove((x, y))
                            else:
                                coords[indices[0]][indices[1]][indices[2]]["valeur"] = True
                                coords[indices[0]][indices[1]][indices[2]]["couleur"] = couleur_cellules
                                cellules_vivantes.append((x, y))
                        coords[indices[0]][indices[1]][indices[2]]["traitee"] = True
                        cases_traitees.append((x, y))
    else:
      coords_cellule = pos_vers_coords(pygame.mouse.get_pos())
      if abs(coords_cellule[0]) <= taille_tableaux and abs(coords_cellule[1]) <= taille_tableaux and coords_cellule[0] != 0 and coords_cellule[1] != 0:
        indices = coords_vers_indices(coords_cellule[0], coords_cellule[1])
        if not coords[indices[0]][indices[1]][indices[2]]["traitee"]:
            if coords[indices[0]][indices[1]][indices[2]]["valeur"]:
                coords[indices[0]][indices[1]][indices[2]]["valeur"] = False
            else:
                coords[indices[0]][indices[1]][indices[2]]["valeur"] = True
                coords[indices[0]][indices[1]][indices[2]]["couleur"] = couleur_cellules
                cellules_vivantes.append((coords_cellule[0], coords_cellule[1]))
            coords[indices[0]][indices[1]][indices[2]]["traitee"] = True
            cases_traitees.append((coords_cellule[0], coords_cellule[1]))


def rendu_plusieurs_lignes(texte, pos_depart):
  """
  Fait le rendu d'un texte sur l'écran en revenant à la ligne si le texte sort de l'écran ou si un retour à la ligne est spécifié (caractère "|")
  IN: texte (string) - le texte dont le rendu est fait
  IN: pos_depart (tuple) - la position "midleft" du premier mot du texte
  OUT: (int) - la position y finale du texte
  """
  posy_texte = pos_depart[1]
  hauteur_mots = 0
  for ligne in texte.split("|"):
    posx_texte = pos_depart[0]
    for mot in ligne.split(" "): 
      surf_texte_mot = police_options.render(mot, True, "White")
      largeur_mot, hauteur_mots = surf_texte_mot.get_size()
      if posx_texte + largeur_mot >= infos_fenetre.current_w:
        posy_texte += hauteur_mots
        posx_texte = pos_depart[0]
      ecran.blit(surf_texte_mot, surf_texte_mot.get_rect(midleft=(posx_texte, posy_texte)))
      posx_texte += largeur_mot + 10
    posy_texte += hauteur_mots
  return posy_texte
# --- création de la partie couleur de l'interface ---

cercle_chromatique_surf = pygame.Surface((110, 110))
cercle_chromatique_surf.fill("#18213a")
cercle_chromatique_rect = cercle_chromatique_surf.get_rect(center=(infos_fenetre.current_w / 15 * 14, infos_fenetre.current_h / 15 * 11))

for i in range(60):
    couleur = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(i / 60, 1, 1))
    pos_depart = (cercle_chromatique_rect.width / 2 + math.cos(math.radians(i * 6)) * 50, cercle_chromatique_rect.width / 2 + math.sin(math.radians(i * 6)) * 50)
    pos_arrivee = (cercle_chromatique_rect.width / 2 + math.cos(math.radians((i + 1) * 6)) * 50, cercle_chromatique_rect.width / 2 + math.sin(math.radians((i + 1) * 6)) * 50)
    pygame.draw.line(cercle_chromatique_surf, couleur, pos_depart, pos_arrivee, 5)

curseur_cercle_chromatique_rect = pygame.Rect(0, 0, 15, 15)
curseur_cercle_chromatique_rect.center = (cercle_chromatique_rect.center[0] + 50, cercle_chromatique_rect.center[1])

barre_saturation_surf = pygame.Surface((longueur_barres, 40))
barre_saturation_surf.fill("#18213a")
barre_saturation_rect = barre_saturation_surf.get_rect(center=(infos_fenetre.current_w / 15 * 14, infos_fenetre.current_h / 15 * 14))

for i in range(longueur_barres):
    couleur = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(colorsys.rgb_to_hsv(0, 0, 0)[0], i / longueur_barres, 1))
    pos_depart = (i - 1, barre_saturation_rect.height / 2)
    pos_arrivee = (i, barre_saturation_rect.height / 2)
    pygame.draw.line(barre_saturation_surf, couleur, pos_depart, pos_arrivee, 5)

# ---boucle infinie du jeu---
while not quitter:
    if aide:
        ecran.fill("#222F52")

        surf_text_titre = police_options.render("Aide", True, "White")
        ecran.blit(surf_text_titre, surf_text_titre.get_rect(midleft=(infos_fenetre.current_w / 2, 20)))
        surf_text_general = police_options.render("Général :", True, "White")
        ecran.blit(surf_text_general, surf_text_general.get_rect(midleft=(80, infos_fenetre.current_h / 20 * 2)))
        texte_general = "-La zone centrale possède la grille de jeu où les cellules peuvent être placées, pour placer une cellule, faites un clique gauche sur une case ou laissez appuyer et glissez pour en placer sur toutes les cases survolées. Pour la retirer, cliquez à nouveau dessus||-Pour vous déplacer sur la grille, laissez appuyé le clique droit et déplacez la souris|-Pour lancer l'évolution des cellules, cliquez le bouton à gauche de la grille|-Le bouton 'réinitialiser' permet de supprimer toutes les cellules de la grille"
        pos_suivante = rendu_plusieurs_lignes(texte_general, (30, infos_fenetre.current_h / 20 * 3))
      
        surf_texte_options = police_options.render("Options :", True, "White")
        ecran.blit(surf_texte_options, surf_texte_options.get_rect(midleft=(80, pos_suivante + 40)))
        texte_options = "À droite de la fenêtre se trouvent les options, il y a dans l'ordre :|1-La vitesse d'évolution des cellules|2-Le zoom|3-La taille de la grille (s'agrandit automatiquement si des cellules se développent près des bords)|4-Les paramètres de placement permettant de placer des cellules dans la zone représentée par le carré rouge (désactivables en décochant la case à leur gauche)|5-La couleur des cellules lors de leur placement, les cellules crées à partir du lancement de l'évolution prennent la moyenne des couleurs des cellules autour (option désactivable elle aussi)"
        rendu_plusieurs_lignes(texte_options, (30, pos_suivante + surf_texte_options.get_width()))

        bouton_sortir_aide.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if bouton_sortir_aide.rect.collidepoint(event.pos[0], event.pos[1]):
                        aide = False
    else:
        # --Affichage de différents éléments--
        ecran.fill("#222F52")
        pos_souris = pygame.mouse.get_pos()
        zone_placement_rect.center = (pos_souris[0] - rect_grille.left, pos_souris[1] - rect_grille.top)
        affiche_grille()

        pygame.draw.rect(ecran, "#18213a", rect_grille, 5)
        pygame.draw.rect(ecran, "#18213a", rect_interface_droite)
        pygame.draw.rect(ecran, "#12192b", rect_interface_droite, 5)
        pygame.draw.line(ecran, "#12192b", (infos_fenetre.current_w / 5 * 4, infos_fenetre.current_h / 5 * 3), (infos_fenetre.current_w, infos_fenetre.current_h / 5 * 3), 5)
        pygame.draw.line(ecran, "#12192b", (infos_fenetre.current_w / 5 * 4, infos_fenetre.current_h / 10 * 3), (infos_fenetre.current_w, infos_fenetre.current_h / 10 * 3), 5)
        pygame.draw.line(ecran, "#12192b", (infos_fenetre.current_w / 20 * 17, infos_fenetre.current_h / 10 * 3), (infos_fenetre.current_w / 20 * 17, infos_fenetre.current_h), 5)

        generation_texte_surf = police_options.render("Génération " + str(generation), True, "White")
        generation_texte_rect = generation_texte_surf.get_rect(center=(infos_fenetre.current_w / 10, infos_fenetre.current_h / 2 + 50))
        ecran.blit(generation_texte_surf, generation_texte_rect)

        ecran.blit(cercle_chromatique_surf, (cercle_chromatique_rect.left, cercle_chromatique_rect.top))
        ecran.blit(barre_saturation_surf, (barre_saturation_rect.left, barre_saturation_rect.top))

        surf_text_prob1 = police_options.render("Probabilité de", True, "white")
        surf_text_prob2 = police_options.render("placement", True, "white")
        ecran.blit(surf_text_prob1, surf_text_prob1.get_rect(center=(infos_fenetre.current_w / 15 * 14, infos_fenetre.current_h / 10 * 4 - 60)))
        ecran.blit(surf_text_prob2, surf_text_prob2.get_rect(center=(infos_fenetre.current_w / 15 * 14, infos_fenetre.current_h / 10 * 4 - 40)))
        if vitesse_evolution >= 500:
            surf_text_vitesse = police_options.render("🐌", True, "white")
        elif vitesse_evolution >= 250:
            surf_text_vitesse = police_options.render("🏃", True, "white")
        else:
            surf_text_vitesse = police_options.render("🚗", True, "white")
        ecran.blit(surf_text_vitesse, surf_text_vitesse.get_rect(center=(infos_fenetre.current_w / 40 * 33, infos_fenetre.current_h / 40 * 3)))
        surf_text_zoom = police_options.render("🔍", True, "white")
        ecran.blit(surf_text_zoom, surf_text_zoom.get_rect(center=(infos_fenetre.current_w / 40 * 33, infos_fenetre.current_h / 40 * 6)))
        surf_text_taille = police_options.render("⊞", True, "white")
        ecran.blit(surf_text_taille, surf_text_taille.get_rect(center=(infos_fenetre.current_w / 40 * 33, infos_fenetre.current_h / 40 * 9)))

        surf_text_placement = police_options.render("Taille", True, "white")
        ecran.blit(surf_text_placement, surf_text_placement.get_rect(center=(infos_fenetre.current_w / 15 * 14, infos_fenetre.current_h / 20 * 11 - 50)))

        # --Mise à jour des couleurs--
        if option_cliquee == "couleurs":
            # place le curseur sur le cercle et met à jour la couleur
            vecteur_souris_centre = [pos_souris[0] - cercle_chromatique_rect.center[0], pos_souris[1] - cercle_chromatique_rect.center[1]]
            longueur_vecteur = math.sqrt(vecteur_souris_centre[0] ** 2 + vecteur_souris_centre[1] ** 2)
            vecteur_unitaire = (vecteur_souris_centre[0] / longueur_vecteur, vecteur_souris_centre[1] / longueur_vecteur)
            curseur_cercle_chromatique_rect.center = (cercle_chromatique_rect.center[0] + vecteur_unitaire[0] * 50, cercle_chromatique_rect.center[1] + vecteur_unitaire[1] * 50)
            angle = math.degrees(math.atan2(-vecteur_unitaire[1], -vecteur_unitaire[0])) + 180
            couleur_cellules = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(angle / 360, colorsys.rgb_to_hsv(*couleur_cellules)[1], 1))


            # met à jour la barre de saturation
            for i in range(longueur_barres):
                couleur = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(colorsys.rgb_to_hsv(couleur_cellules[0], couleur_cellules[1], couleur_cellules[2])[0], i / longueur_barres, 1))
                pos_depart = (i - 1, barre_saturation_rect.height / 2)
                pos_arrivee = (i, barre_saturation_rect.height / 2)
                pygame.draw.line(barre_saturation_surf, couleur, pos_depart, pos_arrivee, 5)

        pygame.draw.rect(ecran, "white", curseur_cercle_chromatique_rect, 0, 50)

        # --Mise à jour des barres d'option--
        for variable, barre in barres_option.items():
            barre.update()
            for sprite in barre:
                if sprite.curseur:
                    if sprite.clique:
                        if variable == "vitesse_evolution":
                            vitesse_evolution = 4000 / (sprite.valeur + 1)
                            pygame.time.set_timer(evenement_nouv_gen, 0)
                            pygame.time.set_timer(evenement_nouv_gen, int(vitesse_evolution))
                        elif variable == "zoom":
                            taille_cases = sprite.valeur * 10
                            zone_placement_rect.width = taille_cases * valeur_taille_cases
                            zone_placement_rect.height = taille_cases * valeur_taille_cases
                        elif variable == "saturation":
                            couleur_cellules = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(
                                colorsys.rgb_to_hsv(couleur_cellules[0], couleur_cellules[1], couleur_cellules[2])[0],
                                sprite.valeur / 255, 1))
                        elif variable == "taille_placement":
                            zone_placement_rect.width = taille_cases * sprite.valeur
                            zone_placement_rect.height = taille_cases * sprite.valeur
                            valeur_taille_cases = sprite.valeur
                        elif variable == "probabilite_placement":
                            probabilite_placement = round(sprite.valeur)

        # --Mise à jour des boutons---
        for bouton in boutons:
            bouton.update()

        # --Récupération des entrées utilisateur--
        for event in pygame.event.get():
            if evolution:
                if event.type == evenement_nouv_gen:
                    nouvelle_generation()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for variable, barre in barres_option.items():
                        clique = False
                        for sprite in barre:
                            if sprite.rect.collidepoint(event.pos[0], event.pos[1]):
                                clique = True
                                option_cliquee = variable
                            if sprite.curseur and clique:
                                sprite.clique = True
                    for bouton in boutons:
                        if bouton.rect.collidepoint(event.pos[0], event.pos[1]):
                            option_cliquee = "oui"
                            eval(bouton.action)
                    if curseur_cercle_chromatique_rect.collidepoint(event.pos[0], event.pos[1]):
                        option_cliquee = "couleurs"

                elif event.button == 3:
                    pos_base = (event.pos[0] - decalage[0], event.pos[1] - decalage[1])
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if option_cliquee != "non":
                        for variable, barre in barres_option.items():
                            if option_cliquee == variable:
                                for sprite in barre:
                                    if sprite.curseur:
                                        sprite.clique = False
                        option_cliquee = "non"
                    else:
                        for case in cases_traitees:
                            indices = coords_vers_indices(case[0], case[1])
                            coords[indices[0]][indices[1]][indices[2]]["traitee"] = False
                        cases_traitees = []

                elif event.button == 2:
                    pos_base = ()

        if pygame.mouse.get_pressed()[0] and option_cliquee == "non":
            change_case()

        if pygame.mouse.get_pressed()[2] and pos_base != ():
            decalage = (pos_souris[0] - pos_base[0], pos_souris[1] - pos_base[1])

    # défini le nombre de mises à jour (passage de boucle) par secondes
    montre.tick(60)

    pygame.display.update()
    infos_fenetre = pygame.display.Info()
