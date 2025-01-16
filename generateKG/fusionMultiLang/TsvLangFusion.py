import csv
import re
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD

def clean_name(name):
    return re.sub(r'[^a-zA-Z0-9]', '', name.lower())

def get_language_tag(lang):
    language_mapping = {
        'Japanese': 'ja',
        'Korean': 'ko',
        'Chinese': 'zh',
        'French': 'fr',
        'German': 'de',
        'Spanish': 'es',
        'Italian': 'it',
        'English': 'en',
        'official roomaji': 'ja-Latn'
    }
    return language_mapping.get(lang, 'en')

def process_files(tsv_file, ttl_file, output_file):
    labels_by_english = {}
    with open(tsv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        current_id = None
        current_type = None
        current_labels = {}
        
        for row in reader:
            if row['type'] != 'region':
                if current_id != row['id']:
                    if current_id is not None:
                        english_label = current_labels.get('English', '')
                        if english_label:
                            labels_by_english[clean_name(english_label)] = {
                                'type': current_type,
                                'labels': current_labels.copy()
                            }
                    current_id = row['id']
                    current_type = row['type']
                    current_labels = {}
                current_labels[row['language']] = row['label']
        
        if current_id is not None:
            english_label = current_labels.get('English', '')
            if english_label:
                labels_by_english[clean_name(english_label)] = {
                    'type': current_type,
                    'labels': current_labels.copy()
                }

    g = Graph()
    g.parse(ttl_file, format='turtle')
    
    new_g = Graph()
    ns1 = Namespace("http://example.org/ontology/pokemon#")
    new_g.bind('ns1', ns1)
    new_g.bind('owl', OWL)
    new_g.bind('rdfs', RDFS)
    new_g.bind('xsd', XSD)

    for s, p, o in g:
        if isinstance(s, URIRef) and not str(s).startswith(str(ns1)):
            new_g.add((s, p, o))

    for s, p, o in g:
        if isinstance(s, URIRef) and str(s).startswith(str(ns1)):
            entity_name = None
            for _, name_pred, name_obj in g.triples((s, ns1.name, None)):
                entity_name = str(name_obj)
                break

            if entity_name:
                clean_entity_name = clean_name(entity_name)
                if clean_entity_name in labels_by_english:
                    labels_data = labels_by_english[clean_entity_name]
                    for lang, label in labels_data['labels'].items():
                        new_g.add((s, RDFS.label, Literal(label, lang=get_language_tag(lang))))

            new_g.add((s, p, o))

    new_g.serialize(destination=output_file, format='turtle')

process_files('pokedex-i18n.tsv', 'pokemon_kg_complete.ttl', 'pokemonMultiLang.ttl')