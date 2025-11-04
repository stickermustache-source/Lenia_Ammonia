import numpy as np
import copy
import sys
from stl import mesh  # Importer la bibliothèque que vous venez d'installer
from skimage import measure # scikit-image fait le travail difficile !

# --- 1. CONFIGURATION LENIA (LE MÊME HACK 3D) ---
LENIA_SCRIPT_NAME = "Lenia_Ammonia_V3_Test" 
try:
    LeniaModule = __import__(LENIA_SCRIPT_NAME)
except ModuleNotFoundError:
    print(f"ERREUR CRITIQUE : Impossible de trouver le fichier '{LENIA_SCRIPT_NAME}.py'")
    sys.exit()

# Patch 3D
LeniaModule.DIM = 3
LeniaModule.CN = 3  
LeniaModule.KN = 1
LeniaModule.XN = 0
LeniaModule.CHANNEL = range(LeniaModule.CN)
LeniaModule.KERNEL = range(LeniaModule.KN * LeniaModule.CN)
# Importation après le patch
from Lenia_Ammonia_V3_Test import Board, Automaton, Analyzer

# --- 2. CONSTANTES ET GÈNES GAGNANTS ---
RUN_STEPS = 300      # Combien de temps laisser la créature grandir
SIM_SIZE = [100, 100, 100] # DOIT être la même taille que celle utilisée pour l'évolution

# Les 15 gènes de votre Superorganisme (Proto-Eukaryote)
WINNING_GENES = [0.1787, 0.1491, 0.5377, 0.6870, 0.1369,  # C0 (s/2, w/2)
                 0.1802, 0.0448, 0.7162, 0.5989, 0.0909,  # C1 (s/2, w/2)
                 0.3718, 0.2498, 0.3965, 0.9791, 0.3330] # C2 (s/2, w/2)

def create_start_pattern_3d():
    """Crée une 'graine' 3D 10x10x10."""
    seed_shape_3d = (4, 4, 4) 
    pattern = Board.from_values([
        np.random.rand(*seed_shape_3d), # C0
        np.random.rand(*seed_shape_3d), # C1
        np.random.rand(*seed_shape_3d)  # C2
    ])
    ##pattern.cells[1] = np.copy(pattern.cells[0])
    ##pattern.cells[2] = np.copy(pattern.cells[0])
    return pattern

START_PATTERN_3D = create_start_pattern_3d()

# --- 3. FONCTION DE SIMULATION ET D'EXPORTATION ---
def build_and_export_model():
    print(f"Initialisation du monde 3D ({SIM_SIZE[0]}x{SIM_SIZE[1]}x{SIM_SIZE[2]})...")
    
    # 1. Configurer le monde
    world = Board(size=SIM_SIZE) 
    world.model['gn'] = 1
    automaton = Automaton(world, use_gpu=False) # Pas besoin de GPU pour l'export
    
    # 2. Appliquer les 15 gènes gagnants
    for k in range(3):
        p_index = k * 5
        world.params[k]['m'] = WINNING_GENES[p_index]
        world.params[k]['s'] = WINNING_GENES[p_index+1]
        world.params[k]['rings'] = [{'r': WINNING_GENES[p_index+3], 'w': WINNING_GENES[p_index+4], 'b': WINNING_GENES[p_index+2]}]
        world.params[k]['c0'] = k
        world.params[k]['c1'] = k

    # 3. Ajouter la graine
    world.add(copy.deepcopy(START_PATTERN_3D), is_centered=True)
    
    # 4. Exécuter la simulation pour laisser la créature grandir
    print(f"Simulation de {RUN_STEPS} étapes pour faire grandir l'organisme...")
    automaton.is_nutrients_enabled = True # Environnement complet
    automaton.is_waste_enabled = True
    
    for i in range(RUN_STEPS):
        automaton.calc_once(is_update=True)
        if i % 50 == 0:
            print(f"  Étape {i}/{RUN_STEPS}...")
            
    print("Simulation terminée.")

    # 5. Combiner les 3 canaux en une seule "masse"
    # Nous prenons la masse maximale de n'importe quel canal pour la visualisation
    print("Combinaison des 3 canaux en un seul maillage...")
    A = automaton.world.cells
    combined_mass = np.maximum(A[0], A[1])
    combined_mass = np.maximum(combined_mass, A[2])
    print("Combinaison des 3 canaux en un seul maillage...")
    A = automaton.world.cells
    combined_mass = np.maximum(A[0], A[1])
    combined_mass = np.maximum(combined_mass, A[2])
    
    # AJOUTEZ CETTE LIGNE :
    print(f"DEBUG: Plage de données de combined_mass: min={np.min(combined_mass)}, max={np.max(combined_mass)}")
    
    # 6. Calculer le maillage 3D (Mesh)
    # ...
    
    # 6. Calculer le maillage 3D (Mesh)
    # C'est ici que la "magie" opère.
    # On utilise "marching cubes" pour trouver la surface 3D où la masse = 0.5
    print("Calcul du maillage 3D (marching cubes)...")
    verts, faces, normals, values = measure.marching_cubes(
        combined_mass, 
        level=0.5, # Le "niveau de la mer" de votre organisme (0.5 est un bon début)
        spacing=(1.0, 1.0, 1.0) # Garde la bonne échelle
    )

    # 7. Créer le fichier STL
    print("Création du fichier STL...")
    organism_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        # Récupérer les 3 sommets (vertices) du triangle
        v0 = verts[f[0]]
        v1 = verts[f[1]]
        v2 = verts[f[2]]
        
        # --- CORRECTION DU VOLUME NÉGATIF ---
        # Nous inversons l'ordre de v1 et v2.
        # [v0, v1, v2] devient [v0, v2, v1]
        # Cela "retourne" le triangle et inverse sa normale.
        organism_mesh.vectors[i] = [v0, v2, v1] 

    # 8. Sauvegarder le fichier !
    # Je sauvegarde sous un nouveau nom pour être sûr
    output_filename = "superorganisme_3d_CORRIGE.stl"
    organism_mesh.save(output_filename)
    
    print("\n" + "="*30)
    print(f"🎉 SUCCÈS (Corrigé) ! 🎉")
    print(f"Modèle 3D sauvegardé sous : {output_filename}")
    print("="*30)


# --- 4. LANCEMENT ---
if __name__ == "__main__":
    build_and_export_model()