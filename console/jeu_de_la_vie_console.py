import time

taille_grille = int(input("Entrez la taille du tableau (sera arrondi au nombre pair inférieur) "))

taille_grille = taille_grille // 2 * 2
taille_tableaux = taille_grille // 2

coords_plus_plus = [[{"valeur": False} for i in range(taille_tableaux)] for j in range(taille_tableaux)]
coords_moins_plus = [[{"valeur": False} for i in range(taille_tableaux)] for j in range(taille_tableaux)]
coords_moins_moins = [[{"valeur": False} for i in range(taille_tableaux)] for j in range(taille_tableaux)]
coords_plus_moins = [[{"valeur": False} for i in range(taille_tableaux)] for j in range(taille_tableaux)]

coords = [coords_plus_plus, coords_moins_plus, coords_moins_moins, coords_plus_moins]

#coordonnées relatives des cases présentes autour d'une case
coords_autour = [(1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1)]

cellules_vivantes = []

generation = 1


def coords_vers_indices(x, y):
  """
  Renvoie les indice menants à l'élément d'une cellule sur la grille de jeu en fonction de ses coordonnées x et y (chaque cellule vaut 1 unité)
  IN: x (int) - la coordonnée x de la cellule dont on cherche les informations
  IN: y (int) - la coordonnée y de la cellule dont on cherche les informations
  OUT: (tuple) - un tuple contenant l'indice du tableau cadran, l'indice correpondant au tableau de la ligne et l'indice correspondant au tableau de la colonne
  """
  if x > 0:
    if y > 0:
      return (0, x - 1, y - 1)
    else:
      return (3, x - 1, abs(y) - 1)
  else:
    if y > 0:
      return (1, abs(x) - 1, y - 1)
    else:
      return (2, abs(x) - 1, abs(y) - 1)


def coords_cases_voisines(case_x, case_y):
  """
  Renvoie la liste des coordonnées des cases autour d'une case donnée (diagonales comprises)
  IN: case_x (int) - la coordonnée x de la case centrale
  IN: case_y (int) - la coordonnée y de la case centrale
  OUT: (list) - une liste contenant des tuples de la forme (x, y) des cases voisines de la case donnée
  """
  cases_autour = []
  for decalage_coords in coords_autour:
    x = case_x + decalage_coords[0]
    y = case_y + decalage_coords[1]

    # gère le cas où l'on doit passer d'un tableau à l'autre (on saute le 0)
    if case_x + decalage_coords[0] == 0:
      x = case_x + decalage_coords[0] * 2

    if case_y + decalage_coords[1] == 0:
      y = case_y + decalage_coords[1] * 2

    if abs(x) <= taille_tableaux and abs(y) <= taille_tableaux:
      cases_autour.append((x, y))
  return cases_autour


def affiche_grille(affiche_coords):
  """
  Affiche la grille
  IN: affiche_coords (bool) - spécifie le mode d'affichage (cellules ou coordonnées), True affiche les coordonnées à la place des cases vides
  """
  for i in [x for x in range(taille_tableaux, -taille_tableaux - 1, -1) if x != 0]:
    ligne = ""
    for j in [x for x in range(-taille_tableaux, taille_tableaux + 1) if x != 0]:
      indices = coords_vers_indices(j, i)
      if coords[indices[0]][indices[1]][indices[2]]["valeur"]:
        if affiche_coords:
          ligne += "    ■    "
        else:
          ligne += "■  "
      else:
        if affiche_coords:
          ligne += str((j, i)) + "  "
        else:
          ligne += "□  "
    print(ligne)
  for i in range(3):
    print("")

"""
tests
coords[0][0][0]["valeur"] = True
coords[0][1][0]["valeur"] = True

indices = coords_vers_indices(-1, 1)
coords[indices[0]][indices[1]][indices[2]]["valeur"] = True

# coords[0][1][1]["valeur"] = True
cellules_vivantes.append((1, 1))
# cellules_vivantes.append((2, 2))
cellules_vivantes.append((2, 1))
cellules_vivantes.append((-1, 1))
"""

affiche_grille(True)

fini = False
print("Pour lancer le jeu, tapez '0'")
while not fini:
  case = (eval(input("Entrez les coordonnées d'une cellule à placer (sous la forme 'x, y') : ")))
  if case == 0:
    fini = True
  else:
    if case in cellules_vivantes:
      print("Cette case est déjà une cellule")
    else:
      indices = coords_vers_indices(case[0], case[1])
      coords[indices[0]][indices[1]][indices[2]]["valeur"] = True
      cellules_vivantes.append(case)
      print("")
      affiche_grille(True)

for i in range(5):
  print("")

while True:
  print("Génération", generation)
  generation += 1
  
  affiche_grille(False)
  time.sleep(1)
  
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
    for case in coords_cases_voisines(case_centre[0], case_centre[1]):
      indices = coords_vers_indices(case[0], case[1])
      if coords[indices[0]][indices[1]][indices[2]]["valeur"]:
        total_cellules_voisines += 1
        
    indices = coords_vers_indices(case_centre[0], case_centre[1])
    case_habite = coords[indices[0]][indices[1]][indices[2]]["valeur"]
    
    if (total_cellules_voisines < 2 or total_cellules_voisines > 3) and case_habite:
      cellules_a_retirer.append(indices)
      cellules_vivantes.remove(case_centre)
      
    elif case_habite == False and total_cellules_voisines == 3:
      cellules_a_ajouter.append(indices)
      cellules_vivantes.append(case_centre)
      
  for indices_cellule in cellules_a_retirer:
    coords[indices_cellule[0]][indices_cellule[1]][indices_cellule[2]]["valeur"] = False
  for indices_cellule in cellules_a_ajouter:
    coords[indices_cellule[0]][indices_cellule[1]][indices_cellule[2]]["valeur"] = True
