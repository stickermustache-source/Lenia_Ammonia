import numpy as np
from stl import mesh

def analyse_stl_pour_ia(filename):
    """
    Charge un fichier STL et affiche ses propriétés clés 
    sous forme de texte compréhensible par une IA.
    """
    try:
        # 1. Charger le maillage (mesh)
        # Assurez-vous que le fichier est dans le même dossier
        my_mesh = mesh.Mesh.from_file(filename)
        
        # 2. Obtenir les propriétés de masse
        #    (volume, centre de gravité, tenseur d'inertie)
        # Celles-ci ne sont valides que si le maillage est "étanche"
        volume, cog, inertia = my_mesh.get_mass_properties()

        # 3. Calculer les limites (bounding box)
        min_vals = my_mesh.min_
        max_vals = my_mesh.max_
        dimensions = max_vals - min_vals

        # 4. Compter les triangles et les sommets uniques
        num_triangles = len(my_mesh.vectors)
        # my_mesh.vectors est (n, 3, 3). Reshape en (n*3, 3) pour avoir tous les sommets
        all_vertices = my_mesh.vectors.reshape(-1, 3)
        num_unique_vertices = len(np.unique(all_vertices, axis=0))
        
        # 5. Calculer la surface totale
        total_area = my_mesh.areas.sum()

        # 6. Générer le rapport textuel que je peux lire
        print("="*30)
        print(f"🤖 RAPPORT D'ANALYSE STL 🤖")
        print(f"Fichier: {filename}")
        print("="*30)
        
        print("\n### 1. Statistiques de base du maillage")
        print(f"* **Nombre de triangles (facettes):** {num_triangles:,}")
        print(f"* **Nombre de sommets uniques:** {num_unique_vertices:,}")

        print("\n### 2. Propriétés physiques")
        print(f"* **Volume total:** {volume:.2f} unités³")
        print(f"* **Surface totale:** {total_area:.2f} unités²")
        print(f"* **Centre de masse (X, Y, Z):** ({cog[0]:.2f}, {cog[1]:.2f}, {cog[2]:.2f})")

        print("\n### 3. Dimensions (Bounding Box)")
        print(f"* **Taille (Largeur, Prof., Hauteur):**")
        print(f"    * Axe X: {dimensions[0]:.2f}")
        print(f"    * Axe Y: {dimensions[1]:.2f}")
        print(f"    * Axe Z: {dimensions[2]:.2f}")
        print(f"* **Coordonnées minimales (X, Y, Z):** ({min_vals[0]:.2f}, {min_vals[1]:.2f}, {min_vals[2]:.2f})")
        print(f"* **Coordonnées maximales (X, Y, Z):** ({max_vals[0]:.2f}, {max_vals[1]:.2f}, {max_vals[2]:.2f})")
        print("\n" + "="*30)

    except FileNotFoundError:
        print(f"ERREUR: Le fichier '{filename}' n'a pas été trouvé.")
        print("Assurez-vous qu'il est dans le même dossier que ce script.")
    except Exception as e:
        print(f"Une erreur est survenue lors de l'analyse du fichier {filename}: {e}")
        print("Le maillage est peut-être vide ou corrompu.")

# --- Lancement de l'analyse ---
if __name__ == "__main__":
    analyse_stl_pour_ia("superorganisme_3d.stl")