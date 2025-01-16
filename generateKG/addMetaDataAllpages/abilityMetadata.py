import requests
import time
from rdflib import Graph, Literal, URIRef, Namespace, DC
from rdflib.namespace import RDF, RDFS, OWL, FOAF, XSD
import logging
from tqdm import tqdm
import datetime
from urllib.parse import quote

class AbilityEnricher:
    def __init__(self):
        self.ns1 = Namespace("http://example.org/ontology/pokemon#")
        self.schema = Namespace("http://schema.org/")
        self.base_api_url = "https://bulbapedia.bulbagarden.net/w/api.php"
        self.headers = {
            'User-Agent': 'AbilityRDFEnricher/1.0 (contact@example.com)'
        }

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='ability_enrichment.log'
        )
        self.logger = logging.getLogger(__name__)

    def get_page_metadata(self, page_title):
        search_title = f"{page_title} (Ability)"
        
        params = {
            "action": "parse",
            "page": search_title,
            "prop": "templates|images|links|externallinks|categories",
            "format": "json"
        }
        
        try:
            response = requests.get(
                self.base_api_url, 
                params=params, 
                headers=self.headers,
                timeout=30  
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erreur lors de la récupération des métadonnées pour {search_title}: {str(e)}")
            return None

    def clean_url(self, url):
        """
        Nettoie et encode correctement les URLs
        """
        return quote(url.replace(' ', '_'), safe=':/')

    def process_templates(self, g, entity_uri, templates):
        """
        Traite les templates spécifiques aux abilities
        """
        for template in templates:
            if isinstance(template, dict) and '*' in template:
                template_name = template['*'].split(':')[-1].strip()
                template_uri = self.ns1[f"Template_{template_name.replace(' ', '_')}"]
                
                g.add((URIRef(entity_uri), self.ns1.usesTemplate, URIRef(template_uri)))
                g.add((URIRef(template_uri), RDF.type, self.ns1.Template))
                g.add((URIRef(template_uri), RDFS.label, Literal(template_name)))

    def process_images(self, g, entity_uri, images):
        for image in images:
            if isinstance(image, str) and any(ext in image.lower() for ext in ['.png', '.jpg', '.gif']):
                image_url = f"https://bulbapedia.bulbagarden.net/wiki/File:{image.replace('File:', '').replace(' ', '_')}"
                image_uri = URIRef(self.clean_url(image_url))
                
                g.add((URIRef(entity_uri), self.schema.image, image_uri))
                g.add((URIRef(entity_uri), FOAF.depiction, image_uri))

    def process_external_links(self, g, entity_uri, external_links):
        for link in external_links:
            if 'wikipedia.org' in link.lower():
                wiki_title = link.split('/')[-1]
                dbpedia_uri = f"http://dbpedia.org/resource/Pokemon_ability_{wiki_title}"
                g.add((URIRef(entity_uri), OWL.sameAs, URIRef(dbpedia_uri)))

    def enrich_ability_data(self, g, entity_uri, metadata):
        if not metadata or 'parse' not in metadata:
            return False

        parse_data = metadata['parse']
        
        if 'templates' in parse_data:
            self.process_templates(g, entity_uri, parse_data['templates'])
        
        if 'images' in parse_data:
            self.process_images(g, entity_uri, parse_data['images'])
        
        if 'externallinks' in parse_data:
            self.process_external_links(g, entity_uri, parse_data['externallinks'])

        return True

    def enrich_ability_rdf(self, input_file, output_file):
        start_time = datetime.datetime.now()
        print(f"\nDébut du processus d'enrichissement des Abilities: {start_time.strftime('%H:%M:%S')}")

        g = Graph()
        g.parse(input_file, format='turtle')
        
        ability_entities = list(g.subjects(RDF.type, self.ns1.Ability))
        
        if not ability_entities:
            self.logger.warning("Aucune Ability trouvée dans le fichier d'entrée")
            return
            
        total_processed = 0
        
        print(f"\nTraitement de {len(ability_entities)} Abilities")
        
        with tqdm(total=len(ability_entities), desc="Progression") as pbar:
            for ability_uri in ability_entities:
                try:
                    ability_name = str(g.value(ability_uri, self.ns1.name))
                    if ability_name:
                        metadata = self.get_page_metadata(ability_name)
                        if metadata and self.enrich_ability_data(g, ability_uri, metadata):
                            total_processed += 1
                        
                        time.sleep(0.5)
                
                except Exception as e:
                    self.logger.error(f"Erreur lors du traitement de {ability_uri}: {str(e)}")
                
                pbar.update(1)

        print("\nEnregistrement du fichier enrichi...")
        g.serialize(destination=output_file, format='turtle')

        end_time = datetime.datetime.now()
        duration = end_time - start_time
        
        print(f"\nStatistiques finales:")
        print(f"Temps total d'exécution: {duration}")
        print(f"Abilities traitées avec succès: {total_processed}/{len(ability_entities)}")
        print(f"Fichier enrichi sauvegardé dans: {output_file}")

def main():
    enricher = AbilityEnricher()
    input_file = 'pokemon_enriched_pokemon2.ttl'  
    output_file = 'pokemon_enriched_with_abilities.ttl'
    enricher.enrich_ability_rdf(input_file, output_file)

if __name__ == "__main__":
    main()