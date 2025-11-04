"""
Lenia Reproduction System (Seed-Based)
========================================
Module d'extension pour ajouter la reproduction génétique au système Lenia.

Usage:
    from lenia_reproduction import ReproductiveLenia
    
    # Wrapper autour de ton système existant
    reproductive_system = ReproductiveLenia(lenia_instance)
    
    # Dans ta boucle principale, remplace:
    # lenia.automaton.calc_once()
    # par:
    # reproductive_system.step()
"""

import numpy as np
import copy
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

@dataclass
class Seed:
    """
    Une graine avec génome qui sera insérée dans le champ Lenia.
    
    Attributes:
        genes: Dictionnaire des gènes (15 paramètres pour 3 canaux)
        position: Coordonnées [x, y] où insérer la graine
        size: Taille de la graine initiale (pixels)
        inserted: Flag pour savoir si déjà insérée
        parent_id: ID du parent (pour tracking des lignées)
        generation: Numéro de génération
    """
    genes: Dict
    position: Tuple[int, int]
    size: int = 4
    inserted: bool = False
    parent_id: Optional[int] = None
    generation: int = 0
    age: int = 0

class OrganismTracker:
    """
    Système de tracking des organismes et leurs génomes.
    Utilise la détection d'objets de Lenia pour associer blobs → génomes.
    """
    
    def __init__(self):
        self.organisms = {}  # {label_id: {'genes': {...}, 'mass': float, 'age': int, 'lineage_id': int}}
        self.next_lineage_id = 1
        self.reproduction_history = []  # Log des événements de reproduction
        
    def register_organism(self, label_id: int, genes: Dict, mass: float):
        """Enregistrer un nouvel organisme détecté."""
        if label_id not in self.organisms:
            self.organisms[label_id] = {
                'genes': copy.deepcopy(genes),
                'mass': mass,
                'age': 0,
                'lineage_id': self.next_lineage_id,
                'reproduced': False
            }
            self.next_lineage_id += 1
    
    def update_organism(self, label_id: int, mass: float):
        """Mettre à jour les stats d'un organisme existant."""
        if label_id in self.organisms:
            self.organisms[label_id]['mass'] = mass
            self.organisms[label_id]['age'] += 1
    
    def get_genes(self, label_id: int) -> Optional[Dict]:
        """Récupérer les gènes d'un organisme."""
        return self.organisms.get(label_id, {}).get('genes', None)
    
    def clean_dead_organisms(self, active_labels: List[int]):
        """Supprimer les organismes qui n'existent plus."""
        dead_labels = set(self.organisms.keys()) - set(active_labels)
        for label in dead_labels:
            del self.organisms[label]
    
    def log_reproduction(self, parent_id: int, child_genes: Dict, position: Tuple):
        """Logger un événement de reproduction."""
        self.reproduction_history.append({
            'parent_id': parent_id,
            'parent_lineage': self.organisms.get(parent_id, {}).get('lineage_id', -1),
            'child_genes': copy.deepcopy(child_genes),
            'position': position,
            'timestamp': len(self.reproduction_history)
        })

class GeneticOperations:
    """
    Opérations génétiques : mutation, crossover, génération aléatoire.
    """
    
    @staticmethod
    def random_genes() -> Dict:
        """
        Générer un génome aléatoire complet (15 gènes pour 3 canaux).
        Format compatible avec Lenia params.
        """
        genes = {}
        for channel in range(3):  # 3 canaux : Bouche, Moteur, Coquille
            prefix = f'C{channel}_'
            genes[prefix + 'm'] = np.random.uniform(0.05, 0.40)  # Moyenne
            genes[prefix + 's'] = np.random.uniform(0.005, 0.30)  # Écart-type
            genes[prefix + 'b'] = np.random.uniform(0.30, 0.90)  # Hauteur
            genes[prefix + 'r'] = np.random.uniform(0.40, 0.99)  # Rayon
            genes[prefix + 'w'] = np.random.uniform(0.05, 0.50)  # Largeur
        return genes
    
    @staticmethod
    def mutate(genes: Dict, mutation_rate: float = 0.10, mutation_strength: float = 0.05) -> Dict:
        """
        Muter un génome avec probabilité mutation_rate par gène.
        
        Args:
            genes: Génome parent
            mutation_rate: Probabilité de mutation par gène (0-1)
            mutation_strength: Amplitude de la mutation (écart-type gaussien)
        
        Returns:
            Nouveau génome muté
        """
        mutated = copy.deepcopy(genes)
        
        for gene_name, value in mutated.items():
            if random.random() < mutation_rate:
                # Mutation gaussienne
                delta = np.random.normal(0, mutation_strength)
                mutated[gene_name] = np.clip(value + delta, 0.0, 1.0)
        
        return mutated
    
    @staticmethod
    def crossover(genes1: Dict, genes2: Dict) -> Dict:
        """
        Croisement génétique entre 2 parents.
        Prend chaque gène de façon aléatoire du parent 1 ou 2.
        """
        child_genes = {}
        for gene_name in genes1:
            if random.random() < 0.5:
                child_genes[gene_name] = genes1[gene_name]
            else:
                child_genes[gene_name] = genes2[gene_name]
        return child_genes
    
    @staticmethod
    def genes_to_lenia_params(genes: Dict, ammonia_mode: bool = True):
        """
        Convertir le format génome compact vers format params Lenia.
        
        Returns:
            Liste de 3 paramètres (un par canal)
        """
        from copy import deepcopy
        
        # Paramètres de base ammonia
        if ammonia_mode:
            base_ring = {'r': 0.75, 'w': 0.6, 'b': 1}
        else:
            base_ring = {'r': 0.5, 'w': 0.5, 'b': 1}
        
        params = []
        for channel in range(3):
            prefix = f'C{channel}_'
            param = {
                'rings': [deepcopy(base_ring)],
                'm': genes.get(prefix + 'm', 0.15),
                's': genes.get(prefix + 's', 0.015),
                'h': 1,
                'c0': channel,
                'c1': channel
            }
            # Modifier le ring selon les gènes
            param['rings'][0]['r'] = genes.get(prefix + 'r', 0.7)
            param['rings'][0]['w'] = genes.get(prefix + 'w', 0.4)
            param['rings'][0]['b'] = genes.get(prefix + 'b', 1.0)
            params.append(param)
        
        return params

class ReproductiveLenia:
    """
    Système Lenia avec reproduction génétique.
    Wrapper autour du système Lenia existant.
    """
    
    def __init__(self, lenia_instance, config: Optional[Dict] = None):
        """
        Args:
            lenia_instance: Instance de la classe Lenia principale
            config: Configuration optionnelle (seuils, etc.)
        """
        self.lenia = lenia_instance
        self.world = lenia_instance.world
        self.automaton = lenia_instance.automaton
        self.analyzer = lenia_instance.analyzer
        
        # Configuration
        default_config = {
            'reproduction_mass_threshold': 400,  # Masse minimale pour se reproduire
            'reproduction_nutrient_cost': 200,   # Coût en nutriments
            'reproduction_cooldown': 50,         # Étapes entre reproductions
            'max_population': 30,                # Population maximale
            'mutation_rate': 0.10,               # Taux de mutation
            'mutation_strength': 0.05,           # Force des mutations
            'seed_size': 4,                      # Taille initiale des graines
            'enable_sexual_reproduction': False, # Reproduction sexuée (non implémenté pour l'instant)
            'nutrient_depletion_radius': 10,     # Rayon d'épuisement des nutriments
        }
        self.config = {**default_config, **(config or {})}
        
        # Systèmes internes
        self.tracker = OrganismTracker()
        self.genetic_ops = GeneticOperations()
        self.pending_seeds = []  # Graines en attente d'insertion
        
        # Statistiques
        self.stats = {
            'total_births': 0,
            'total_deaths': 0,
            'current_population': 0,
            'generation_max': 0
        }
        
        # Dernière reproduction par organisme (pour cooldown)
        self.last_reproduction = {}  # {label_id: step_number}
        self.current_step = 0
        
    def step(self):
        """
        Étape de simulation complète : calcul Lenia + reproduction.
        Remplace lenia.automaton.calc_once() dans la boucle principale.
        """
        # 1. Calcul Lenia standard
        self.automaton.calc_once()
        self.current_step += 1
        
        # 2. Détection d'organismes (tous les 10 steps pour performance)
        if self.current_step % 10 == 0:
            self.analyzer.detect_objects()
            
            # 3. Mise à jour du tracking
            self._update_organism_tracking()
            
            # 4. Check reproduction
            self._check_reproduction()
            
            # 5. Insérer les graines en attente
            self._insert_pending_seeds()
            
            # 6. Mettre à jour les stats
            self._update_stats()
    
    def _update_organism_tracking(self):
        """
        Mettre à jour le tracking des organismes basé sur la détection.
        """
        if not hasattr(self.analyzer, 'object_list'):
            return
        
        active_labels = []
        
        for label_id, organism_data in enumerate(self.analyzer.object_list, start=1):
            # Calculer la masse totale de l'organisme
            mass = sum(channel.sum() for channel in organism_data)
            
            active_labels.append(label_id)
            
            # Si c'est un nouvel organisme sans gènes connus
            if self.tracker.get_genes(label_id) is None:
                # Assigner des gènes aléatoires (pourrait venir d'une graine)
                genes = self.genetic_ops.random_genes()
                self.tracker.register_organism(label_id, genes, mass)
            else:
                # Mettre à jour l'organisme existant
                self.tracker.update_organism(label_id, mass)
        
        # Nettoyer les organismes morts
        self.tracker.clean_dead_organisms(active_labels)
    
    def _check_reproduction(self):
        """
        Vérifier pour chaque organisme s'il peut se reproduire.
        """
        if not hasattr(self.analyzer, 'object_list'):
            return
        
        # Limiter la population
        if len(self.analyzer.object_list) >= self.config['max_population']:
            return
        
        for label_id, organism_data in enumerate(self.analyzer.object_list, start=1):
            # Vérifier les conditions de reproduction
            if not self._can_reproduce(label_id, organism_data):
                continue
            
            # REPRODUCTION !
            self._reproduce_organism(label_id, organism_data)
    
    def _can_reproduce(self, label_id: int, organism_data) -> bool:
        """
        Vérifier si un organisme peut se reproduire.
        """
        # 1. Masse suffisante
        mass = sum(channel.sum() for channel in organism_data)
        if mass < self.config['reproduction_mass_threshold']:
            return False
        
        # 2. Cooldown
        last_repro = self.last_reproduction.get(label_id, -999)
        if self.current_step - last_repro < self.config['reproduction_cooldown']:
            return False
        
        # 3. Nutriments suffisants dans la région
        # Trouver la position de l'organisme
        org_info = self.tracker.organisms.get(label_id, {})
        if not org_info:
            return False
        
        # Vérifier qu'il a déjà reproduit récemment
        if org_info.get('reproduced', False):
            return False
        
        return True
    
    def _reproduce_organism(self, label_id: int, organism_data):
        """
        Effectuer la reproduction d'un organisme.
        """
        # Récupérer les gènes du parent
        parent_genes = self.tracker.get_genes(label_id)
        if parent_genes is None:
            return
        
        # Muter les gènes
        child_genes = self.genetic_ops.mutate(
            parent_genes,
            mutation_rate=self.config['mutation_rate'],
            mutation_strength=self.config['mutation_strength']
        )
        
        # Trouver une position pour le bébé (proche du parent mais pas trop)
        parent_position = self._get_organism_center(organism_data, label_id)
        if parent_position is None:
            return
        
        child_position = self._find_empty_space_near(parent_position)
        if child_position is None:
            return  # Pas de place disponible
        
        # Créer la graine
        parent_org = self.tracker.organisms.get(label_id, {})
        seed = Seed(
            genes=child_genes,
            position=child_position,
            size=self.config['seed_size'],
            parent_id=label_id,
            generation=parent_org.get('generation', 0) + 1
        )
        self.pending_seeds.append(seed)
        
        # Coût énergétique : dépleter les nutriments autour du parent
        self._deplete_nutrients(parent_position, self.config['nutrient_depletion_radius'])
        
        # Marquer la reproduction
        self.last_reproduction[label_id] = self.current_step
        self.tracker.organisms[label_id]['reproduced'] = True
        
        # Logger
        self.tracker.log_reproduction(label_id, child_genes, child_position)
        self.stats['total_births'] += 1
        
        print(f"🧬 REPRODUCTION ! Parent #{label_id} (gen {parent_org.get('generation', 0)}) → Bébé à {child_position}")
    
    def _get_organism_center(self, organism_data, label_id: int) -> Optional[Tuple[int, int]]:
        """
        Trouver le centre de masse d'un organisme.
        Utilise la object_map de l'analyzer pour trouver les coordonnées spatiales.
        """
        # Vérifier que l'analyzer a une object_map
        if not hasattr(self.analyzer, 'object_map'):
            return None
        
        # Créer un masque pour cet organisme spécifique
        mask = (self.analyzer.object_map == label_id)
        
        if not mask.any():
            return None
        
        # Combiner tous les canaux du monde
        combined = sum(self.world.cells)
        
        # Appliquer le masque
        masked_mass = combined * mask
        
        if masked_mass.sum() == 0:
            return None
        
        # Calculer le centre de masse
        indices = np.indices(combined.shape)
        center_x = int(np.sum(indices[0] * masked_mass) / masked_mass.sum())
        center_y = int(np.sum(indices[1] * masked_mass) / masked_mass.sum())
        
        return (center_x, center_y)
    
    def _find_empty_space_near(self, position: Tuple[int, int], 
                                min_distance: int = 15, 
                                max_distance: int = 40) -> Optional[Tuple[int, int]]:
        """
        Trouver un espace vide près d'une position donnée.
        """
        x, y = position
        
        # Essayer plusieurs positions aléatoires
        for _ in range(20):
            angle = random.uniform(0, 2 * np.pi)
            distance = random.uniform(min_distance, max_distance)
            
            new_x = int(x + distance * np.cos(angle))
            new_y = int(y + distance * np.sin(angle))
            
            # Vérifier les limites
            if not (0 <= new_x < self.world.cells[0].shape[0] and 
                    0 <= new_y < self.world.cells[0].shape[1]):
                continue
            
            # Vérifier si c'est vide (peu de masse)
            region_mass = sum(channel[
                max(0, new_x-5):min(channel.shape[0], new_x+5),
                max(0, new_y-5):min(channel.shape[1], new_y+5)
            ].sum() for channel in self.world.cells)
            
            if region_mass < 10:  # Zone suffisamment vide
                return (new_x, new_y)
        
        return None  # Pas d'espace trouvé
    
    def _deplete_nutrients(self, position: Tuple[int, int], radius: int):
        """
        Épuiser les nutriments autour d'une position (coût de reproduction).
        """
        if not hasattr(self.world, 'nutrients'):
            return
        
        x, y = position
        y_grid, x_grid = np.ogrid[:self.world.nutrients.shape[0], :self.world.nutrients.shape[1]]
        mask = (x_grid - x)**2 + (y_grid - y)**2 <= radius**2
        
        # Réduire les nutriments de 50%
        self.world.nutrients[mask] *= 0.5
    
    def _insert_pending_seeds(self):
        """
        Insérer toutes les graines en attente dans le champ Lenia.
        """
        for seed in self.pending_seeds:
            if not seed.inserted:
                self._insert_seed(seed)
                seed.inserted = True
        
        # Nettoyer les graines insérées
        self.pending_seeds = [s for s in self.pending_seeds if not s.inserted]
    
    def _insert_seed(self, seed: Seed):
        """
        Insérer une graine dans le champ Lenia.
        Crée un petit blob avec les paramètres génétiques de la graine.
        """
        x, y = seed.position
        size = seed.size
        
        # Créer un petit pattern circulaire
        for c in range(3):  # Pour chaque canal
            # Extraire les gènes du canal
            prefix = f'C{c}_'
            intensity = seed.genes.get(prefix + 'b', 0.5) * 0.8  # Intensité initiale
            
            # Créer un disque
            for dx in range(-size, size+1):
                for dy in range(-size, size+1):
                    px, py = x + dx, y + dy
                    
                    # Vérifier les limites
                    if not (0 <= px < self.world.cells[c].shape[0] and 
                            0 <= py < self.world.cells[c].shape[1]):
                        continue
                    
                    # Distance au centre
                    dist = np.sqrt(dx**2 + dy**2)
                    
                    if dist <= size:
                        # Profil gaussien
                        value = intensity * np.exp(-(dist**2) / (2 * (size/2)**2))
                        self.world.cells[c][px, py] = max(self.world.cells[c][px, py], value)
        
        print(f"   🌱 Graine insérée à {seed.position} (gen {seed.generation})")
    
    def _update_stats(self):
        """
        Mettre à jour les statistiques de population.
        """
        if hasattr(self.analyzer, 'object_list'):
            self.stats['current_population'] = len(self.analyzer.object_list)
        
        # Génération maximale
        max_gen = 0
        for org in self.tracker.organisms.values():
            max_gen = max(max_gen, org.get('generation', 0))
        self.stats['generation_max'] = max_gen
    
    def get_stats_string(self) -> str:
        """
        Obtenir un string formaté des statistiques.
        """
        return (f"Pop: {self.stats['current_population']}/{self.config['max_population']} | "
                f"Births: {self.stats['total_births']} | "
                f"Max Gen: {self.stats['generation_max']}")
    
    def seed_initial_population(self, num_seeds: int = 5):
        """
        Ensemencer la population initiale avec des génomes aléatoires.
        
        Args:
            num_seeds: Nombre de graines initiales
        """
        print(f"\n🌱 Ensemencement de {num_seeds} organismes initiaux...")
        
        for i in range(num_seeds):
            # Génome aléatoire
            genes = self.genetic_ops.random_genes()
            
            # Position aléatoire
            x = random.randint(20, self.world.cells[0].shape[0] - 20)
            y = random.randint(20, self.world.cells[0].shape[1] - 20)
            
            seed = Seed(
                genes=genes,
                position=(x, y),
                size=self.config['seed_size'],
                generation=0
            )
            self.pending_seeds.append(seed)
        
        # Insérer immédiatement
        self._insert_pending_seeds()
        print("✅ Population initiale ensemencée\n")


# ============================================================================
# EXEMPLE D'UTILISATION
# ============================================================================

if __name__ == '__main__':
    """
    Exemple d'intégration avec Lenia existant.
    """
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║         Lenia Reproduction System - Seed Based              ║
    ║                                                              ║
    ║  Pour intégrer dans ton code principal:                     ║
    ║                                                              ║
    ║  1. Importer:                                                ║
    ║     from lenia_reproduction import ReproductiveLenia        ║
    ║                                                              ║
    ║  2. Wrapper ton système:                                     ║
    ║     reproductive_system = ReproductiveLenia(lenia)          ║
    ║                                                              ║
    ║  3. Remplacer dans la boucle:                                ║
    ║     # lenia.automaton.calc_once()                            ║
    ║     reproductive_system.step()                              ║
    ║                                                              ║
    ║  4. Ensemencer population initiale:                          ║
    ║     reproductive_system.seed_initial_population(5)          ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
