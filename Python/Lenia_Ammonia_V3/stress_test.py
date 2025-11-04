import pygad
import numpy as np
import copy
import sys
import math

# --- 1. CONFIGURATION LENIA (HACK) ---
# Le nom de votre script Lenia principal (à modifier si nécessaire)
LENIA_SCRIPT_NAME = "Lenia_Ammonia_V3_Test" 

try:
    # Importation du module après le patch pour forcer la configuration
    LeniaModule = __import__(LENIA_SCRIPT_NAME)
except ModuleNotFoundError:
    print(f"ERREUR CRITIQUE: Impossible de trouver le fichier '{LENIA_SCRIPT_NAME}.py'")
    print("Veuillez vérifier le nom de votre fichier principal.")
    sys.exit()

# Patch sur les variables globales du module pour forcer le mode 3 canaux
LeniaModule.CN = 3  
LeniaModule.KN = 1
LeniaModule.XN = 0
LeniaModule.CHANNEL = range(LeniaModule.CN)
LeniaModule.KERNEL = range(LeniaModule.KN * LeniaModule.CN)

# Importation des classes après le patch
from Lenia_Ammonia_V3_Test import Board, Automaton, Analyzer

# --- 2. CONSTANTES ET GÈNES ---
SIM_STEPS = 250        # Durée de la simulation pour chaque test
SIM_SIZE = [128, 128]  # Taille de la grille
INITIAL_NUTRIENTS = float(SIM_SIZE[0] * SIM_SIZE[1])
STABILIZATION_STEPS = 50 
TEST_STEPS = SIM_STEPS - STABILIZATION_STEPS

def create_start_pattern():
    """Crée la graine de départ aléatoire 10x10 sur les trois canaux."""
    pattern = Board.from_values([
        np.random.rand(10, 10), 
        np.random.rand(10, 10), 
        np.random.rand(10, 10)
    ])
    pattern.cells[1] = np.copy(pattern.cells[0])
    pattern.cells[2] = np.copy(pattern.cells[0])
    return pattern

START_PATTERN = create_start_pattern()


# Définition des 15 gènes (5 par canal)
gene_space_bouche = [
    {'low': 0.1, 'high': 0.5},    # m
    {'low': 0.1, 'high': 0.3},    # s
    {'low': 0.5, 'high': 1.0},    # b
    {'low': 0.2, 'high': 1.0},    # r
    {'low': 0.05, 'high': 0.3}    # w
]
gene_space_moteur = [
    {'low': 0.1, 'high': 0.3},    # m
    {'low': 0.05, 'high': 0.15},  # s
    {'low': 0.5, 'high': 1.0},    # b
    {'low': 0.5, 'high': 1.0},    # r
    {'low': 0.05, 'high': 0.15}   # w
]
gene_space_coquille = [
    {'low': 0.2, 'high': 0.6},    # m
    {'low': 0.1, 'high': 0.4},    # s
    {'low': 0.1, 'high': 1.0},    # b
    {'low': 0.1, 'high': 1.0},    # r
    {'low': 0.1, 'high': 0.5}     # w
]

gene_space = gene_space_bouche + gene_space_moteur + gene_space_coquille
num_genes = len(gene_space)


# --- 3. FONCTION DE FITNESS (Mini-Jeu de Collaboration) ---
def fitness_func(ga_instance, solution, solution_idx):
    try:
        # 1. Configurer le monde (3 canaux)
        world = Board(size=SIM_SIZE) 
        
        # 2. Appliquer les 15 gènes
        for k in range(3):
            p_index = k * 5
            world.params[k]['m'] = solution[p_index]
            world.params[k]['s'] = solution[p_index+1]
            world.params[k]['rings'] = [{'r': solution[p_index+3], 'w': solution[p_index+4], 'b': solution[p_index+2]}]
            world.params[k]['c0'] = k
            world.params[k]['c1'] = k

        # 3. Ajouter la graine
        world.add(copy.deepcopy(START_PATTERN), is_centered=True)
        
        # 4. Initialiser et préparer l'environnement
        automaton = Automaton(world, use_gpu=False)
        analyzer = Analyzer(automaton)
        
        # Désactiver l'environnement pour la stabilisation
        automaton.is_nutrients_enabled = False
        automaton.is_waste_enabled = False
        
        # Boucle 4a : STABILISATION (50 étapes)
        for _ in range(STABILIZATION_STEPS):
            automaton.calc_once(is_update=True)
            if analyzer.is_empty: return 0.0
        
        # Activer l'environnement pour le test de chasse
        automaton.is_nutrients_enabled = True
        automaton.is_waste_enabled = True

        # Boucle 4b : TEST DE CHASSE (200 étapes)
        for _ in range(TEST_STEPS):
            automaton.calc_once(is_update=True)
            analyzer.calc_stats()
            analyzer.center_world()
            if analyzer.is_empty: return 0.0
        
        # 5. Calculer le score final
        mass_total = world.cells[0].sum() + world.cells[1].sum() + world.cells[2].sum()
        distance_travelled = np.linalg.norm(analyzer.total_shift_idx)
        
        # FACTEUR DE MASSE : Nous utilisons la masse totale, pas seulement C2 (pour plus de robustesse)
        
        # --- Formule de Fitness Multicanaux ---
        # Le score est la force combinée (Masse * Distance)
        if mass_total < 10 or distance_travelled < 1.0: # Minimum pour survivre
            return 0.0
        
        # Score final : favoriser la survie (masse) et l'exploration (distance)
        fitness = mass_total * distance_travelled
        final_fitness = np.cbrt(fitness) # Utilisation de la racine cubique pour garder les nombres gérables
        
        return final_fitness

    except Exception as e:
        # Affiche l'ID de la solution qui a échoué pour le débogage (si cela se produit encore)
        print(f"Erreur de simulation (Solution {solution_idx}) : {e}")
        return 0.0


# --- 4. CONFIGURATION ET LANCEMENT PYGAD ---
ga_instance = pygad.GA(
    num_generations=100,
    num_parents_mating=15,
    sol_per_pop=100,
    num_genes=num_genes,
    gene_space=gene_space,
    fitness_func=fitness_func,
    parent_selection_type="sss",
    crossover_type="single_point",
    mutation_type="random",
    mutation_percent_genes=15,
    parallel_processing=['thread', 0]
)

# --- LANCEMENT ---
if __name__ == "__main__":
    print(f"Début de l'évolution multi-canaux (15 gènes)...")
    
    ga_instance.run()

    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    
    genes_bouche = solution[0:5]
    genes_moteur = solution[5:10]
    genes_coquille = solution[10:15]

    print("="*30)
    print("Évolution multi-canaux terminée !")
    print(f"Meilleur score de Fitness (combiné) : {solution_fitness:.4f}")
    print("--- Gènes 'Bouche' (C0) ---")
    print(f"  m={genes_bouche[0]:.4f}, s={genes_bouche[1]:.4f}, b={genes_bouche[2]:.4f}, r={genes_bouche[3]:.4f}, w={genes_bouche[4]:.4f}")
    print("--- Gènes 'Moteur' (C1) ---")
    print(f"  m={genes_moteur[0]:.4f}, s={genes_moteur[1]:.4f}, b={genes_moteur[2]:.4f}, r={genes_moteur[3]:.4f}, w={genes_moteur[4]:.4f}")
    print("--- Gènes 'Coquille' (C2) ---")
    print(f"  m={genes_coquille[0]:.4f}, s={genes_coquille[1]:.4f}, b={genes_coquille[2]:.4f}, r={genes_coquille[3]:.4f}, w={genes_coquille[4]:.4f}")
    print("="*30)

    ga_instance.plot_fitness()