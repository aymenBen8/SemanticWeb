import requests
import time
from rdflib import Graph, Literal, URIRef, Namespace, DC
from rdflib.namespace import RDF, RDFS, OWL, FOAF
import logging
from tqdm import tqdm
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BulbapediaEnricher:
   def __init__(self):
       self.ns1 = Namespace("http://example.org/ontology/pokemon#")
       self.schema = Namespace("http://schema.org/")
       self.base_api_url = "https://bulbapedia.bulbagarden.net/w/api.php"
       self.headers = {
           'User-Agent': 'PokemonRDFEnricher/1.0'
       }

   def get_page_metadata(self, page_title):
       params = {
           "action": "parse",
           "page": page_title,
           "prop": "templates|images|links|externallinks",
           "format": "json"
       }
       time.sleep(0.1)
       try:
           response = requests.get(self.base_api_url, params=params, headers=self.headers)
           response.raise_for_status()
           return response.json()
       except requests.exceptions.RequestException as e:
           logging.error(f"Erreur API pour {page_title}: {e}")
           return None

   def clean_image_name(self, image_name):
       return f"https://bulbapedia.bulbagarden.net/wiki/File:{image_name.replace('File:', '').replace(' ', '_')}"

   def clean_template_name(self, template_name):
       return template_name.split(':')[-1].strip()

   def process_templates(self, g, entity_uri, templates):
       for template in templates:
           if isinstance(template, dict) and '*' in template:
               template_name = self.clean_template_name(template['*'])
               template_uri = self.ns1[f"Template_{template_name.replace(' ', '_')}"]
               g.add((URIRef(entity_uri), self.ns1.usesTemplate, URIRef(template_uri)))
               g.add((URIRef(template_uri), RDF.type, self.ns1.Template))
               g.add((URIRef(template_uri), RDFS.label, Literal(template_name)))

   def process_images(self, g, entity_uri, images):
       for image in images:
           if isinstance(image, str) and any(ext in image.lower() for ext in ['.png', '.jpg', '.gif']):
               image_uri = self.clean_image_name(image)
               g.add((URIRef(entity_uri), self.schema.image, URIRef(image_uri)))
               g.add((URIRef(entity_uri), FOAF.depiction, URIRef(image_uri)))

   def process_links(self, g, entity_uri, links):
       for link in links:
           if isinstance(link, dict) and 'ns' in link and link['ns'] == 0:
               link_uri = self.ns1[link['*'].replace(' ', '_')]
               g.add((URIRef(entity_uri), self.ns1.relatedTo, URIRef(link_uri)))

   def enrich_entity_data(self, g, entity_uri, metadata):
       if not metadata or 'parse' not in metadata:
           return False
       
       parse_data = metadata['parse']
       
       if 'templates' in parse_data:
           self.process_templates(g, entity_uri, parse_data['templates'])
       if 'images' in parse_data:
           self.process_images(g, entity_uri, parse_data['images'])
       if 'links' in parse_data:
           self.process_links(g, entity_uri, parse_data['links'])
       
       return True

   def enrich_rdf(self, input_file, output_file):
       start_time = datetime.datetime.now()
       print(f"\nDébut du processus d'enrichissement: {start_time.strftime('%H:%M:%S')}")
       
       g = Graph()
       g.parse(input_file, format='turtle')
       
       entity_types = [self.ns1.Pokémon, self.ns1.Move, self.ns1.Item, self.ns1.Location, self.ns1.Trainer, self.ns1.Ability]
       total_processed = 0
       total_entities = 0
       
       for entity_type in entity_types:
           entities = list(g.subjects(RDF.type, entity_type))
           type_name = str(entity_type).split('#')[-1]
           total_entities += len(entities)
           
           print(f"\nTraitement des entités de type {type_name} ({len(entities)} entités)")
           
           with tqdm(total=len(entities), desc=f"Progression {type_name}") as pbar:
               for entity in entities:
                   name = str(g.value(entity, self.ns1.name))
                   try:
                       metadata = self.get_page_metadata(name)
                       if metadata and self.enrich_entity_data(g, entity, metadata):
                           total_processed += 1
                   except Exception as e:
                       logging.error(f"Erreur pour {name}: {e}")
                   pbar.update(1)
       
       end_time = datetime.datetime.now()
       duration = end_time - start_time
       
       print(f"\nEnregistrement du fichier enrichi...")
       g.serialize(destination=output_file, format='turtle')
       
       print(f"\nStatistiques finales:")
       print(f"Temps total d'exécution: {duration}")
       print(f"Entités traitées avec succès: {total_processed}/{total_entities}")
       print(f"Fichier enrichi sauvegardé dans: {output_file}")

def main():
   enricher = BulbapediaEnricher()
   input_file = 'pokemonMultiLang.ttl'
   output_file = 'pokemon_enriched.ttl'
   enricher.enrich_rdf(input_file, output_file)

if __name__ == "__main__":
   main()