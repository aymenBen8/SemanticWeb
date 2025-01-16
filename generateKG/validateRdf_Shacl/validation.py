import rdflib
from pyshacl import validate
import logging
import json
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PokemonValidator:
    def __init__(self, data_file, vocab_file, shapes_file):
        self.data_file = data_file  # Sauvegarde du chemin du fichier de données
        self.vocab_file = vocab_file
        self.shapes_file = shapes_file
        self.data_graph = rdflib.Graph()
        self.vocab_graph = rdflib.Graph()
        self.shapes_graph = rdflib.Graph()
        
        # Chargement des graphes avec gestion d'erreurs
        try:
            logger.info("Chargement du graphe de données...")
            self.data_graph.parse(data_file, format="turtle")
            
            logger.info("Chargement du vocabulaire...")
            self.vocab_graph.parse(vocab_file, format="turtle")
            
            logger.info("Chargement des shapes SHACL...")
            self.shapes_graph.parse(shapes_file, format="turtle")
            
            logger.info(f"Nombre de triplets dans le graphe de données : {len(self.data_graph)}")
            logger.info(f"Nombre de triplets dans le vocabulaire : {len(self.vocab_graph)}")
            logger.info(f"Nombre de triplets dans les shapes : {len(self.shapes_graph)}")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des fichiers : {str(e)}")
            raise

    def validate_data(self):
        """
        Valide le graphe de données contre les shapes SHACL
        """
        logger.info("Début de la validation SHACL...")
        try:
            validation_graph = self.data_graph + self.vocab_graph
            
            conforms, results_graph, results_text = validate(
                validation_graph,
                shacl_graph=self.shapes_graph,
                inference='rdfs',
                debug=True
            )
            
            return conforms, results_graph, results_text
            
        except Exception as e:
            logger.error(f"Erreur lors de la validation : {str(e)}")
            raise

    def generate_validation_report(self, results_text, output_file):
        """
        Génère un rapport de validation détaillé
        """
        try:
            validation_results = {
                "timestamp": str(datetime.datetime.now()),
                "validation_successful": results_text == "",
                "violations": []
            }
            
            if results_text:
                for violation in results_text.split('\n\n'):
                    if violation.strip():
                        validation_results["violations"].append({
                            "description": violation.strip(),
                            "severity": "Violation" if "Violation" in violation else "Warning"
                        })
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(validation_results, f, indent=2, ensure_ascii=False)
                
            return validation_results
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport : {str(e)}")
            raise

    def remove_violating_triples(self, results_graph):
        """
        Supprime les triplets problématiques du graphe de données
        en fonction des violations détectées par SHACL.
        Retourne le nombre de triplets supprimés.
        """
        logger.info("Début de la suppression des triplets problématiques...")
        try:
            # Extraire les nœuds et propriétés problématiques
            violations = set()
            for violation in results_graph.query("""
                PREFIX sh: <http://www.w3.org/ns/shacl#>
                SELECT ?node ?path
                WHERE {
                    ?report a sh:ValidationResult ;
                            sh:focusNode ?node ;
                            sh:resultPath ?path .
                }
            """):
                violations.add((violation.node, violation.path))

            # Nombre de triplets supprimés
            num_triples_deleted = 0

            # Supprimer les triplets problématiques
            for node, path in violations:
                # Récupérer les triplets à supprimer
                triples_to_delete = list(self.data_graph.triples((node, path, None)))
                num_triples_deleted += len(triples_to_delete)

                # Supprimer les triplets
                for triple in triples_to_delete:
                    self.data_graph.remove(triple)
                    logger.info(f"Suppression du triplet : {triple}")

            logger.info("✅ Les triplets problématiques ont été supprimés.")
            return num_triples_deleted
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression des triplets : {str(e)}")
            raise

    def count_lines_in_file(self, file_path):
        """
        Compte le nombre de lignes dans un fichier.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for line in f if line.strip())

def main():
    try:
        validator = PokemonValidator(
            data_file='pokemon_enriched_with_trainers.ttl',
            vocab_file='pokemon-vocab.ttl',
            shapes_file='pokemon-shapes.ttl'
        )
        
        conforms, results_graph, results_text = validator.validate_data()
        
        report = validator.generate_validation_report(
            results_text,
            'validation_report.json'
        )
        
        if conforms:
            logger.info("✅ La validation est un succès ! Aucune violation détectée.")
        else:
            logger.error("❌ Des violations ont été détectées.")
            logger.info(f"Nombre de violations : {len(report['violations'])}")
            logger.info("Consultez validation_report.json pour plus de détails.")

            # Supprimer les triplets problématiques
            num_triples_deleted = validator.remove_violating_triples(results_graph)

            # Sauvegarder le graphe corrigé
            output_file = 'rdf_enriched_corrected.ttl'
            validator.data_graph.serialize(destination=output_file, format='turtle')
            logger.info(f"✅ Le graphe corrigé a été enregistré sous '{output_file}'.")

            # Calculer la différence de lignes entre le fichier d'entrée et de sortie
            input_lines = validator.count_lines_in_file(validator.data_file)
            output_lines = validator.count_lines_in_file(output_file)
            lines_removed = input_lines - output_lines

            # Afficher le résumé à la fin
            logger.info("\n=== Résumé de la suppression ===")
            logger.info(f"Nombre total de triplets supprimés : {num_triples_deleted}")
            logger.info(f"Nombre total de lignes supprimées : {lines_removed}")
            
    except Exception as e:
        logger.error(f"Une erreur s'est produite : {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()