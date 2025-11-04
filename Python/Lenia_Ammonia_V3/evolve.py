import pygad
import numpy as np
import copy
import sys

# --- DÉBUT DU HACK ---
# Nous devons "patcher" le script Lenia AVANT de l'importer
# pour qu'il sache qu'il doit fonctionner en mode 3 canaux.

# Assurez-vous que c'est le bon nom de fichier !
LENIA_SCRIPT_NAME = "Lenia_Ammonia_V3_Test" 

try:
    # Importez le module lui-même
    LeniaModule = __import__(LENIA_SCRIPT_NAME)
except ModuleNotFoundError:
    print(f"ERREUR CRITIQUE : Impossible de trouver le fichier '{LENIA_SCRIPT_NAME}.py'")
    print("Veuillez vous assurer que le nom est correct et qu'il se trouve dans le même dossier.")
    sys.exit()

# Appliquez le patch sur les variables globales du module
LeniaModule.CN = 3  # Forcer 3 canaux
LeniaModule.KN = 1  # 1 noyau par canal
LeniaModule.XN = 0  # 0 noyau croisé (pour rester simple)
LeniaModule.CHANNEL = range(LeniaModule.CN)
# KERNEL = range(KN*CN + XN*CN*(CN-1)) = range(1*3 + 0) = range(3)
LeniaModule.KERNEL = range(LeniaModule.KN * LeniaModule.CN)
# --- FIN DU HACK ---


# Maintenant, importez les classes du module patché
from Lenia_Ammonia_V3_Test import Board, Automaton, Analyzer

# --- Constantes pour l'évolution ---
SIM_STEPS = 200
SIM_SIZE = [128, 128]
INITIAL_NUTRIENTS = float(SIM_SIZE[0] * SIM_SIZE[1])

def create_start_pattern():
    """Crée un petit organisme de départ standard pour 3 canaux."""
    # Board() va maintenant créer 3 canaux par défaut grâce au hack
    pattern = Board.from_values([
        np.random.rand(10, 10), # Graine pour Canal 0
        np.random.rand(10, 10), # Graine pour Canal 1
        np.random.rand(10, 10)  # Graine pour Canal 2
    ])
    # Assurons-nous qu'ils commencent au même endroit
    pattern.cells[1] = np.copy(pattern.cells[0])
    pattern.cells[2] = np.copy(pattern.cells[0])
    return pattern

# Créez le patron de départ une seule fois
START_PATTERN = create_start_pattern()


# --- 1. Définition du Génome (total 15 gènes) ---
# Gènes 0-4: "Bouche" (Canal 0)
gene_space_bouche = [
    {'low': 0.1, 'high': 0.5},    # m
    {'low': 0.1, 'high': 0.3},    # s
    {'low': 0.5, 'high': 1.0},    # b
    {'low': 0.2, 'high': 1.0},    # r
    {'low': 0.05, 'high': 0.3}    # w
]
# Gènes 5-9: "Moteur" (Canal 1)
gene_space_moteur = [
    {'low': 0.1, 'high': 0.3},    # m
    {'low': 0.05, 'high': 0.15},  # s
    {'low': 0.5, 'high': 1.0},    # b
    {'low': 0.5, 'high': 1.0},    # r
    {'low': 0.05, 'high': 0.15}   # w
]
# Gènes 10-14: "Coquille" (Canal 2)
gene_space_coquille = [
    {'low': 0.2, 'high': 0.6},    # m
    {'low': 0.1, 'high': 0.4},    # s
    {'low': 0.1, 'high': 1.0},    # b
    {'low': 0.1, 'high': 1.0},    # r
    {'low': 0.1, 'high': 0.5}     # w
]

# On assemble le génome complet
gene_space = gene_space_bouche + gene_space_moteur + gene_space_coquille
num_genes = len(gene_space)


# --- 2. Définition de la Fonction de Fitness ---
def fitness_func(ga_instance, solution, solution_idx):
    try:
        # 1. Configurer le monde pour 3 CANAUX
        # Board() va maintenant utiliser CN=3 grâce au hack
        world = Board(size=SIM_SIZE) 
        
        # 2. Appliquer les 15 gènes
        # world.params a maintenant 3 items (KERNEL=range(3))
        
        # Gènes 0-4 pour le noyau C0->C0 (params[0])
        world.params[0]['m'] = solution[0]
        world.params[0]['s'] = solution[1]
        world.params[0]['rings'] = [{'r': solution[3], 'w': solution[4], 'b': solution[2]}]
        world.params[0]['c0'] = 0
        world.params[0]['c1'] = 0
        
        # Gènes 5-9 pour le noyau C1->C1 (params[1])
        world.params[1]['m'] = solution[5]
        world.params[1]['s'] = solution[6]
        world.params[1]['rings'] = [{'r': solution[8], 'w': solution[9], 'b': solution[7]}]
        world.params[1]['c0'] = 1
        world.params[1]['c1'] = 1
        
        # Gènes 10-14 pour le noyau C2->C2 (params[2])
        world.params[2]['m'] = solution[10]
        world.params[2]['s'] = solution[11]
        world.params[2]['rings'] = [{'r': solution[13], 'w': solution[14], 'b': solution[12]}]
        world.params[2]['c0'] = 2
        world.params[2]['c1'] = 2

        # 3. Ajouter la graine de départ
        world.add(copy.deepcopy(START_PATTERN), is_centered=True)
        
        # 4. Initialiser et exécuter la simulation
        # Automaton() va maintenant utiliser CN=3 et KERNEL=range(3) grâce au hack
        automaton = Automaton(world, use_gpu=False)
        analyzer = Analyzer(automaton)
        
        # Activer l'environnement
        automaton.is_nutrients_enabled = True
        automaton.is_waste_enabled = True
        
        for _ in range(SIM_STEPS):
            automaton.calc_once(is_update=True)
            analyzer.calc_stats()
            analyzer.center_world()
            if analyzer.is_empty:
                break
        
        # 5. Calculer le score final (LE MINI-JEU)
        if analyzer.is_empty:
            return 0.0

        nutrients_consumed = INITIAL_NUTRIENTS - world.nutrients.sum()
        distance_travelled = np.linalg.norm(analyzer.total_shift_idx)
        mass_of_shell = world.cells[2].sum() # Masse du Canal 2

        # Si l'un des trois objectifs échoue, le score est 0
        if nutrients_consumed < 1 or distance_travelled < 1 or mass_of_shell < 1:
            return 0.0
        
        # Le score final est la NOURRITURE * la DISTANCE * la MASSE
        fitness = nutrients_consumed * distance_travelled * mass_of_shell
        final_fitness = np.cbrt(fitness)
        
        return final_fitness

    except Exception as e:
        # Affiche l'ID de la simulation qui a échoué pour le débogage
        print(f"Erreur de simulation (Solution {solution_idx}) : {e}")
        return 0.0

# --- 3. Configuration de PyGAD ---
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

# --- 4. Lancement et Lecture des Résultats ---
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