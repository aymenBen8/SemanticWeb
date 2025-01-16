import re
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, SKOS
import os
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime
from urllib.parse import quote

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=f'pokemon_kg_generation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
)

class PokemonKGGenerator:
    def __init__(self):
        self.ex = Namespace("http://example.org/ontology/pokemon#")
        self.schema = Namespace("http://schema.org/")
        self.dbo = Namespace("http://dbpedia.org/ontology/")
        self.dbr = Namespace("http://dbpedia.org/resource/")
        self.wdt = Namespace("http://www.wikidata.org/prop/direct/")
        self.wd = Namespace("http://www.wikidata.org/entity/")
        
        self.g = Graph()
        self.g.bind("ex", self.ex)
        self.g.bind("schema", self.schema)
        self.g.bind("owl", OWL)
        self.g.bind("rdf", RDF)
        self.g.bind("rdfs", RDFS)
        self.g.bind("xsd", XSD)
        self.g.bind("skos", SKOS)
        self.g.bind("dbo", self.dbo)
        self.g.bind("dbr", self.dbr)
        self.g.bind("wdt", self.wdt)
        self.g.bind("wd", self.wd)
        
        self.class_mappings = {
            'Pokémon': [self.schema.Animal, self.dbo.Species],
            'Ability': [self.schema.Thing, self.dbo.Feature],
            'Trainer': [self.schema.Person, self.dbo.Person],
            'Location': [self.schema.Place, self.dbo.Place],
            'Item': [self.schema.Product, self.dbo.Item],
            'Move': [self.schema.Action, self.dbo.Action],
            'Form': [self.schema.Thing],
            'Effect': [self.schema.Thing],
            'Gym': [self.schema.Place, self.dbo.Building],
            'Badge': [self.schema.Thing],
            'Philosophy': [self.schema.Thing, self.dbo.Philosophy],
            'Evolution': [self.schema.Process, self.dbo.Evolution],
            'StorageLocation': [self.schema.Place],
            'Type': [self.schema.Thing],
            'Category': [self.schema.Thing],
            'TargetType': [self.schema.Thing],
            'Level': [self.schema.QuantitativeValue],
            'TM': [self.schema.Product],
            'Region': [self.schema.Place, self.dbo.Region],
            'ClimateCondition': [self.schema.Thing],
            'Season': [self.schema.Thing],
            'Person': [self.schema.Person, self.dbo.Person],
            'Theme': [self.schema.Thing],
            'Contest': [self.schema.Event],
            'Berry': [self.schema.Product],
            'Game': [self.schema.VideoGame],
            'Generation': [self.schema.Thing],
            'Version': [self.schema.SoftwareApplication],
            'Species': [self.schema.Thing, self.dbo.Species],
            'EggGroup': [self.schema.Thing],
            'Nature': [self.schema.Thing],
            'Stat': [self.schema.QuantitativeValue],
            'Status': [self.schema.Thing],
            'Weather': [self.schema.Thing],
            'Terrain': [self.schema.Thing]
        }
        
        self.property_mappings = {
            'name': (XSD.string, ['schema:name', 'rdfs:label']),
            'japaneseName': (XSD.string, ['schema:alternateName']),
            'height': (XSD.float, ['schema:height']),
            'weight': (XSD.float, ['schema:weight']),
            'description': (XSD.string, ['schema:description', 'dbo:abstract']),
            'number': (XSD.integer, ['dbo:number']),
            'classification': (XSD.string, ['dbo:classification']),
            'generation': (XSD.integer, ['dbo:generation']),
            'category': (XSD.string, ['dbo:category']),
            'type': (None, ['dbo:type']),
            'ability': (None, ['dbo:ability']),
            'move': (None, ['dbo:move']),
            'evolution': (None, ['dbo:evolution']),
            'location': (None, ['dbo:location']),
            'region': (None, ['dbo:region']),
            'trainer': (None, ['dbo:trainer']),
            'game': (None, ['dbo:game']),
            'version': (None, ['dbo:version'])
        }

    def setup_ontology(self):
        self.g.add((URIRef(self.ex), RDF.type, OWL.Ontology))
        self.g.add((URIRef(self.ex), OWL.imports, URIRef("http://schema.org/")))
        self.g.add((URIRef(self.ex), RDFS.label, Literal("Pokemon Ontology", lang="en")))
        self.g.add((URIRef(self.ex), RDFS.comment, Literal("An ontology for the Pokemon universe", lang="en")))
        
        for class_name, parent_classes in self.class_mappings.items():
            class_uri = URIRef(self.ex + class_name)
            self.g.add((class_uri, RDF.type, OWL.Class))
            for parent_class in parent_classes:
                self.g.add((class_uri, RDFS.subClassOf, parent_class))
            self.g.add((class_uri, RDFS.label, Literal(class_name, lang="en")))
            
        self.create_object_properties()
        
        self.create_data_properties()
        
        self.add_axioms_and_restrictions()

    def create_object_properties(self):
        object_properties = [
            ('hasAbility', 'Pokémon', 'Ability', "Relates a Pokemon to its abilities"),
            ('canUseMove', 'Pokémon', 'Move', "Indicates moves a Pokemon can learn"),
            ('evolvedFrom', 'Pokémon', 'Pokémon', "Indicates evolution source"),
            ('evolvesInto', 'Pokémon', 'Pokémon', "Indicates evolution target"),
            ('hasType', 'Pokémon', 'Type', "Indicates Pokemon's type"),
            ('isFoundIn', 'Pokémon', 'Location', "Indicates where Pokemon can be found"),
            ('belongsToGeneration', 'Pokémon', 'Generation', "Indicates Pokemon's generation"),
            ('hasEggGroup', 'Pokémon', 'EggGroup', "Indicates Pokemon's egg groups"),
            ('hasBaseStats', 'Pokémon', 'Stat', "Indicates Pokemon's base stats"),
            ('learnsMoveAtLevel', 'Pokémon', 'Move', "Indicates level-up moves"),
            ('canLearnTM', 'Pokémon', 'Move', "Indicates TM moves"),
            ('hasForm', 'Pokémon', 'Form', "Indicates alternate forms"),
            ('affectedByWeather', 'Pokémon', 'Weather', "Indicates weather effects"),
            ('affectedByTerrain', 'Pokémon', 'Terrain', "Indicates terrain effects")
        ]

        for prop_name, domain, range_class, description in object_properties:
            prop_uri = URIRef(self.ex + prop_name)
            self.g.add((prop_uri, RDF.type, OWL.ObjectProperty))
            self.g.add((prop_uri, RDFS.domain, URIRef(self.ex + domain)))
            self.g.add((prop_uri, RDFS.range, URIRef(self.ex + range_class)))
            self.g.add((prop_uri, RDFS.comment, Literal(description, lang="en")))

    def create_data_properties(self):
        data_properties = [
            ('number', XSD.integer, "Pokemon's Pokedex number"),
            ('name', XSD.string, "Name in English"),
            ('japaneseName', XSD.string, "Name in Japanese"),
            ('height', XSD.float, "Height in meters"),
            ('weight', XSD.float, "Weight in kilograms"),
            ('baseHP', XSD.integer, "Base HP stat"),
            ('baseAttack', XSD.integer, "Base Attack stat"),
            ('baseDefense', XSD.integer, "Base Defense stat"),
            ('baseSpAtk', XSD.integer, "Base Special Attack stat"),
            ('baseSpDef', XSD.integer, "Base Special Defense stat"),
            ('baseSpeed', XSD.integer, "Base Speed stat"),
            ('catchRate', XSD.integer, "Catch rate"),
            ('baseExperience', XSD.integer, "Base experience yield"),
            ('baseHappiness', XSD.integer, "Base happiness"),
            ('genderRatio', XSD.float, "Gender ratio (female percentage)"),
            ('description', XSD.string, "Pokedex description"),
            ('generation', XSD.integer, "Generation introduced"),
            ('levelUpRate', XSD.string, "Experience growth rate"),
            ('eggSteps', XSD.integer, "Steps to hatch egg")
        ]

        for prop_name, datatype, description in data_properties:
            prop_uri = URIRef(self.ex + prop_name)
            self.g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            self.g.add((prop_uri, RDFS.range, datatype))
            self.g.add((prop_uri, RDFS.comment, Literal(description, lang="en")))

    def add_axioms_and_restrictions(self):
        pokemon_class = URIRef(self.ex + 'Pokémon')
        
        type_restriction = BNode()
        self.g.add((pokemon_class, RDFS.subClassOf, type_restriction))
        self.g.add((type_restriction, RDF.type, OWL.Restriction))
        self.g.add((type_restriction, OWL.onProperty, URIRef(self.ex + 'hasType')))
        self.g.add((type_restriction, OWL.minCardinality, Literal(1)))
        
        disjoint_classes = [
            ('Type', 'Ability'),
            ('Move', 'Ability'),
            ('Item', 'Move'),
            ('Location', 'Item'),
            ('Trainer', 'Pokémon')
        ]
        
        for class1, class2 in disjoint_classes:
            self.g.add((URIRef(self.ex + class1), OWL.disjointWith, URIRef(self.ex + class2)))

    def clean_value(self, value: str) -> str:
        if not value:
            return ""
            
        value = re.sub(r'\{\{.*?\}\}', '', value)
        
        value = re.sub(r'<.*?>', '', value)
        
        value = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', value)
        value = re.sub(r'[\[\]{}]', '', value)
        value = re.sub(r'<ref>.*?</ref>', '', value)        
        value = re.sub(r'\s+', ' ', value)
        
        return value.strip()

    def parse_infobox(self, content: str) -> Dict[str, str]:
        data = {}
        current_field = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            if not line or line.startswith('==='):
                continue
                
            if line.startswith('|'):
                parts = line[1:].split('=', 1)
                
                if len(parts) == 2:
                    key, value = parts
                    key = key.strip()
                    value = value.strip()
                    


                    if value:
                        data[key] = self.clean_value(value)
                    current_field = key
                    
                elif len(parts) == 1:
                    current_field = parts[0].strip()
                    data[current_field] = ""
                    
            elif current_field and line:
                if current_field in data:
                    data[current_field] += " " + line
                else:
                    data[current_field] = line
                    
        return data

    def convert_to_uri_safe(self, text: str) -> str:
        text = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
        text = re.sub(r'\s+', '_', text)
        uri_safe_text = quote(text)
        return uri_safe_text

    def add_triple(self, subject: URIRef, predicate: URIRef, value: str, 
                   datatype: Optional[URIRef] = None, is_resource: bool = False, graph: Graph = None):
        if not value or graph is None:
            return
        
        value = self.clean_value(value)
        if not value:
            return
        
        if is_resource:
            obj = URIRef(self.ex + self.convert_to_uri_safe(value))
        elif datatype:
            try:
                if datatype == XSD.integer:
                    value = int(re.sub(r'[^0-9-]', '', value))
                elif datatype == XSD.float:
                    value = float(re.sub(r'[^0-9.-]', '', value))
                obj = Literal(value, datatype=datatype)
            except (ValueError, TypeError):
                return
        else:
            obj = Literal(value)
            
        graph.add((subject, predicate, obj))

    def process_pokemon(self, data: Dict[str, str], graph: Graph):
        if 'name' not in data:
            return
            
        pokemon_uri = URIRef(self.ex + self.convert_to_uri_safe(data['name']))
        graph.add((pokemon_uri, RDF.type, self.ex.Pokémon))
        
        properties = {
            'name': (self.ex.name, XSD.string, False),
            'ndex': (self.ex.number, XSD.integer, False),
            'jname': (self.ex.japaneseName, XSD.string, False),
            'type1': (self.ex.hasType, None, True),
            'type2': (self.ex.hasType, None, True),
            'ability1': (self.ex.hasAbility, None, True),
            'ability2': (self.ex.hasAbility, None, True),
            'abilityd': (self.ex.hasAbility, None, True),
            'height-m': (self.ex.height, XSD.float, False),
            'weight-kg': (self.ex.weight, XSD.float, False),
            'category': (self.ex.category, XSD.string, False),
            'gendercode': (self.ex.genderRatio, XSD.float, False),
            'catchrate': (self.ex.catchRate, XSD.integer, False),
            'eggcycles': (self.ex.eggSteps, XSD.integer, False),
            'evtotal': (self.ex.totalEV, XSD.integer, False),
            'expyield': (self.ex.baseExperience, XSD.integer, False),
            'friendship': (self.ex.baseHappiness, XSD.integer, False),
            'generation': (self.ex.generation, XSD.integer, False),
            'color': (self.ex.color, XSD.string, False),
            'body': (self.ex.bodyShape, XSD.string, False)
        }

        for key, (predicate, datatype, is_resource) in properties.items():
            if key in data:
                self.add_triple(pokemon_uri, predicate, data[key], datatype, is_resource, graph)

        if 'egggroup1' in data:
            self.add_triple(pokemon_uri, self.ex.hasEggGroup, data['egggroup1'], None, True, graph)
        if 'egggroup2' in data:
            self.add_triple(pokemon_uri, self.ex.hasEggGroup, data['egggroup2'], None, True, graph)

        stats = {
            'hp': (self.ex.baseHP, XSD.integer),
            'at': (self.ex.baseAttack, XSD.integer),
            'df': (self.ex.baseDefense, XSD.integer),
            'sa': (self.ex.baseSpAtk, XSD.integer),
            'sd': (self.ex.baseSpDef, XSD.integer),
            'sp': (self.ex.baseSpeed, XSD.integer)
        }

        for key, (predicate, datatype) in stats.items():
            stat_key = f'base{key}'
            if stat_key in data:
                self.add_triple(pokemon_uri, predicate, data[stat_key], datatype, False, graph)

    def process_move(self, data: Dict[str, str], graph: Graph):
        if 'name' not in data:
            return

        move_uri = URIRef(self.ex + self.convert_to_uri_safe(data['name']))
        graph.add((move_uri, RDF.type, self.ex.Move))

        properties = {
            'name': (self.ex.name, XSD.string, False),
            'jname': (self.ex.japaneseName, XSD.string, False),
            'type': (self.ex.hasType, None, True),
            'category': (self.ex.category, XSD.string, False),
            'power': (self.ex.power, XSD.integer, False),
            'accuracy': (self.ex.accuracy, XSD.integer, False),
            'pp': (self.ex.pp, XSD.integer, False),
            'gen': (self.ex.generation, XSD.integer, False),
            'target': (self.ex.target, XSD.string, False),
            'damagecategory': (self.ex.damageCategory, XSD.string, False),
            'effect': (self.ex.effect, XSD.string, False)
        }

        for key, (predicate, datatype, is_resource) in properties.items():
            if key in data:
                self.add_triple(move_uri, predicate, data[key], datatype, is_resource, graph)

        flags = ['contact', 'protect', 'magiccoat', 'snatch', 'mirrormove', 'kingsrock']
        for flag in flags:
            if flag in data and data[flag].lower() == 'yes':
                graph.add((move_uri, self.ex.hasFlag, URIRef(self.ex + flag.title())))

    def process_ability(self, data: Dict[str, str], graph: Graph):
        if 'name' not in data:
            return

        ability_uri = URIRef(self.ex + self.convert_to_uri_safe(data['name']))
        graph.add((ability_uri, RDF.type, self.ex.Ability))

        properties = {
            'name': (self.ex.name, XSD.string, False),
            'jpname': (self.ex.japaneseName, XSD.string, False),
            'gen': (self.ex.generation, XSD.integer, False),
            'effect': (self.ex.effect, XSD.string, False)
        }

        for key, (predicate, datatype, is_resource) in properties.items():
            if key in data:
                self.add_triple(ability_uri, predicate, data[key], datatype, is_resource, graph)

    def process_location(self, data: Dict[str, str], graph: Graph):
        if 'location_name' not in data:
            return

        location_uri = URIRef(self.ex + self.convert_to_uri_safe(data['location_name']))
        graph.add((location_uri, RDF.type, self.ex.Location))

        properties = {
            'location_name': (self.ex.name, XSD.string, False),
            'japanese_name': (self.ex.japaneseName, XSD.string, False),
            'region': (self.ex.region, None, True),
            'generation': (self.ex.generation, XSD.integer, False),
            'type': (self.ex.locationType, XSD.string, False),
            'mapdesc': (self.ex.description, XSD.string, False)
        }

        for key, (predicate, datatype, is_resource) in properties.items():
            if key in data:
                self.add_triple(location_uri, predicate, data[key], datatype, is_resource, graph)

    def process_item(self, data: Dict[str, str], graph: Graph):
        if 'name' not in data:
            return

        item_uri = URIRef(self.ex + self.convert_to_uri_safe(data['name']))
        graph.add((item_uri, RDF.type, self.ex.Item))

        properties = {
            'name': (self.ex.name, XSD.string, False),
            'jname': (self.ex.japaneseName, XSD.string, False),
            'gen': (self.ex.generation, XSD.integer, False),
            'pocket': (self.ex.pocket, XSD.string, False),
            'price': (self.ex.price, XSD.integer, False),
            'effect': (self.ex.effect, XSD.string, False)
        }

        for key, (predicate, datatype, is_resource) in properties.items():
            if key in data:
                self.add_triple(item_uri, predicate, data[key], datatype, is_resource, graph)

    def process_trainer(self, data: Dict[str, str], graph: Graph):
        if 'name' not in data:
            return

        trainer_uri = URIRef(self.ex + self.convert_to_uri_safe(data['name']))
        graph.add((trainer_uri, RDF.type, self.ex.Trainer))

        properties = {
            'name': (self.ex.name, XSD.string, False),
            'jpname': (self.ex.japaneseName, XSD.string, False),
            'gender': (self.ex.gender, XSD.string, False),
            'hometown': (self.ex.hometown, None, True),
            'region': (self.ex.region, None, True),
            'trainerclass': (self.ex.trainerClass, XSD.string, False),
            'game': (self.ex.appearsIn, XSD.string, False),
            'generation': (self.ex.generation, XSD.integer, False)
        }

        for key, (predicate, datatype, is_resource) in properties.items():
            if key in data:
                self.add_triple(trainer_uri, predicate, data[key], datatype, is_resource, graph)

    def process_file(self, filename: str, processor_func, graph: Graph):
        if not os.path.exists(filename):
            logging.error(f"File not found: {filename}")
            return

        logging.info(f"Processing file: {filename}")
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                infoboxes = content.split('=== BEGIN INFODex ===')[1:]
                
                for infobox in infoboxes:
                    if '=== END INFODex ===' in infobox:
                        infobox = infobox.split('=== END INFODex ===')[0]
                    data = self.parse_infobox(infobox)
                    processor_func(data, graph)
                    
        except Exception as e:
            logging.error(f"Error processing {filename}: {str(e)}")

    def add_external_links(self):
        for s, p, o in self.g.triples((None, RDF.type, self.ex.Pokémon)):
            pokemon_name = self.g.value(s, self.ex.name)
            if pokemon_name:
                dbr_uri = URIRef(f"http://dbpedia.org/resource/Pokémon_{self.convert_to_uri_safe(pokemon_name)}")
                self.g.add((s, OWL.sameAs, dbr_uri))


    def generate_kg(self):
        self.g = Graph()        
        self.setup_ontology()
        file_processors = {
            'pokemon_infoboxes.txt': self.process_pokemon,
            'moves_infoboxes.txt': self.process_move,
            'abilities_infoboxes.txt': self.process_ability,
            'locations_infoboxes.txt': self.process_location,
            'items_infoboxes.txt': self.process_item,
            'trainers_infoboxes.txt': self.process_trainer
        }
        
        for filename, processor in file_processors.items():
            file_graph = Graph()
            
            self.process_file(filename, processor, file_graph)
            
            output_file = f'pokemon_kg_{filename.split(".")[0]}.ttl'
            file_graph.serialize(destination=output_file, format='turtle')
            logging.info(f"Knowledge graph for {filename} saved to {output_file}")            
            self.g += file_graph
        
        self.add_external_links()
        
        output_file = 'pokemon_kg_complete.ttl'
        self.g.serialize(destination=output_file, format='turtle')
        logging.info(f"Complete knowledge graph saved to {output_file}")
        
        logging.info(f"Total number of triples: {len(self.g)}")
        logging.info(f"Number of classes: {len(list(self.g.subjects(RDF.type, OWL.Class)))}")
        logging.info(f"Number of properties: {len(list(self.g.subjects(RDF.type, OWL.ObjectProperty | OWL.DatatypeProperty)))}")

def main():
    kg_generator = PokemonKGGenerator()
    kg_generator.generate_kg()

if __name__ == "__main__":
    main()