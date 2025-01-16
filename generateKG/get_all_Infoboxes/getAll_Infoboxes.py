from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS
import requests
import re
import time

SCHEMA = Namespace("http://schema.org/")
EX = Namespace("http://example.org/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

def normalize_name(name):
    name = name.replace(" ", "_")
    name = re.sub(r"[^a-zA-Z0-9_\-.]", "", name)
    return name

def parse_infobox(infobox):
    data = {}
    for line in infobox.split("\n"):
        if line.strip().startswith("|"):
            match = re.match(r"\|([^=]+)=(.+)", line.strip())
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                data[key] = value
    return data

def get_wikitext_from_bulbapedia(page_title):
    api_url = "https://bulbapedia.bulbagarden.net/w/api.php"
    params = {
        "action": "parse",
        "page": page_title,
        "prop": "wikitext",
        "format": "json"
    }
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        if 'parse' in data and 'wikitext' in data['parse']:
            wikitext = data['parse']['wikitext']['*']



            if wikitext.strip().startswith("#REDIRECT") or wikitext.strip().startswith("#redirect"):
                target_title = re.search(r'\[\[([^]]+)\]\]', wikitext).group(1)
                print(f"Redirection détectée : {page_title} -> {target_title}")
                return get_wikitext_from_bulbapedia(target_title)
            return wikitext
        else:
            print(f"Aucun wikitext trouvé pour {page_title}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête pour {page_title}: {e}")
        return None

def extract_infobox(wikitext, infobox_marker):

    start_index = wikitext.find(infobox_marker)
    if start_index == -1:
        print(f"Infobox marker '{infobox_marker}' not found in wikitext.")
        print("Wikitext sample:", wikitext[:500])  
        return None  
    
    start_index += len(infobox_marker)
    brace_level = 1  
    end_index = start_index
    length = len(wikitext)
    
    while end_index < length and brace_level > 0:
        if wikitext[end_index] == '{':
            brace_level += 1
        elif wikitext[end_index] == '}':
            brace_level -= 1
        end_index += 1
    
    if brace_level != 0:
        print(f"Unbalanced braces in infobox for marker '{infobox_marker}'.")
        return None  
    
    infobox = wikitext[start_index:end_index-1]
    return infobox

def get_element_names(category, limit=None):
    api_url = "https://bulbapedia.bulbagarden.net/w/api.php"
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": "500",  
        "format": "json",
        "cmnamespace": "0"  
    }
    element_names = []
    while True:
        response = requests.get(api_url, params=params)
        data = response.json()
        if 'query' in data and 'categorymembers' in data['query']:
            for member in data['query']['categorymembers']:
                element_names.append(member['title'])
                if limit and len(element_names) >= limit:
                    return element_names
            if 'continue' in data:
                params['cmcontinue'] = data['continue']['cmcontinue']
            else:
                break
        else:
            break
    return element_names

def infobox_to_rdf(graph, element_name, infobox_data, element_type):
    normalized_name = normalize_name(element_name)
    element_uri = URIRef(f"http://example.org/{element_type}/{normalized_name}")

    if element_type == "pokemon":
        graph.add((element_uri, RDF.type, EX.Pokemon))
    elif element_type == "ability":
        graph.add((element_uri, RDF.type, EX.Ability))
    elif element_type == "move":
        graph.add((element_uri, RDF.type, EX.Move))
    elif element_type == "item":
        graph.add((element_uri, RDF.type, EX.Item))
    elif element_type == "location":
        graph.add((element_uri, RDF.type, EX.Location))
    elif element_type == "trainer":
        graph.add((element_uri, RDF.type, EX.Trainer))
    elif element_type == "episode":
        graph.add((element_uri, RDF.type, EX.Episode))

    graph.add((element_uri, RDFS.label, Literal(element_name)))

    mappings = {
        "name": SCHEMA.name,
        "jname": SCHEMA.alternateName,
        "jptranslit": SCHEMA.alternateName,
        "jptrans": SCHEMA.alternateName,
        "gen": SCHEMA.version,
        "effect": SCHEMA.description,
        "effectdesc": SCHEMA.description,
        "height-m": SCHEMA.height,
        "weight-kg": SCHEMA.weight,
        "ndex": SCHEMA.identifier,
        "category": SCHEMA.description,
        "type1": EX.hasType,
        "type2": EX.hasType,
        "ability1": EX.hasAbility,
        "ability2": EX.hasAbility,
        "abilityd": EX.hasHiddenAbility,
        "power": EX.power,
        "accuracy": EX.accuracy,
        "pp": EX.pp,
        "basepp": EX.pp,
        "maxpp": EX.pp,
        "damagecategory": EX.damageCategory,
        "category6": EX.category,
        "appealsc": EX.appeal,
        "scdesc": SCHEMA.description,
        "cost": SCHEMA.price,
        "description": SCHEMA.description,
        "image": SCHEMA.image,
        "other_info": SCHEMA.description,
        "region": SCHEMA.location,
        "area": SCHEMA.location,
        "color": EX.color,
        "corecolor": EX.coreColor,
        "bordercolor": EX.borderColor,
        "jpname": SCHEMA.alternateName,
        "epcode": SCHEMA.identifier,
        "colorscheme": EX.colorScheme,
        "title_en": SCHEMA.name,
        "title_ja": SCHEMA.alternateName,
        "title_ja_trans": SCHEMA.alternateName,
        "screen": EX.screenFormat,
        "broadcast_jp": SCHEMA.datePublished,
        "broadcast_us": SCHEMA.datePublished,
        "en_series": SCHEMA.partOfSeries,
        "en_op": SCHEMA.musicBy,
        "ja_op": SCHEMA.musicBy,
        "ja_ed": SCHEMA.musicBy,
        "olmteam": EX.productionTeam,
        "scenario": SCHEMA.author,
        "storyboard": EX.storyboardArtist,
        "director": SCHEMA.director,
        "art": SCHEMA.artDirector,
        "morecredits": SCHEMA.additionalCredits,
        "epstaffpage": SCHEMA.relatedLink,
        "footnotes": SCHEMA.footnote,
    }

    for key, value in infobox_data.items():
        if key in mappings:
            predicate = mappings[key]
            if key in ["type1", "type2", "type"]:
                graph.add((element_uri, predicate, EX[value]))
            elif key in ["ability1", "ability2", "abilityd"]:
                graph.add((element_uri, predicate, EX[value.replace(" ", "_")]))
            else:
                graph.add((element_uri, predicate, Literal(value)))

def save_rdf_to_turtle(graph, filename):
    """
    Sauvegarde le graphe RDF dans un fichier Turtle.
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(graph.serialize(format="turtle"))

def extract_and_save_infoboxes(category, element_type, infobox_marker, text_output_file, rdf_output_file, limit=None):

    rdf_graph = Graph()



    element_names = get_element_names(category, limit)
    print(f"Found {len(element_names)} {element_type}s.")

    infoboxes = []
    for element_name in element_names:
        print(f"Processing {element_name}...")
        wikitext = get_wikitext_from_bulbapedia(element_name)
        if wikitext:
            infobox = extract_infobox(wikitext, infobox_marker)
            if infobox:
                infoboxes.append(infobox)
                infobox_data = parse_infobox(infobox)
                if infobox_data:
                    infobox_to_rdf(rdf_graph, element_name, infobox_data, element_type)
            else:
                print(f"No infobox found for {element_name}")
        else:
            print(f"Failed to retrieve wikitext for {element_name}")
        time.sleep(0.1)  

    with open(text_output_file, "w", encoding="utf-8") as f:
        for infobox in infoboxes:
            f.write(f"=== BEGIN INFODex ===\n")
            f.write(infobox + "\n")
            f.write(f"=== END INFODex ===\n\n")

    print(f"All infoboxes saved to {text_output_file}")

    save_rdf_to_turtle(rdf_graph, rdf_output_file)
    print(f"All RDF triples saved to {rdf_output_file}")

if __name__ == "__main__":


    extract_and_save_infoboxes("Items", "item", "{{ItemInfobox", "items_infoboxes.txt", "items_infobox.ttl")
    extract_and_save_infoboxes("Locations", "location", "{{Infobox location", "locations_infoboxes.txt", "locations_infobox.ttl")

    extract_and_save_infoboxes("Trainer_classes", "trainer", "{{TrainerClassInfobox", "trainers_infoboxes.txt", "trainers_infobox.ttl")

 
    extract_and_save_infoboxes("Pokémon", "pokemon", "{{Pokémon Infobox", "pokemon_infoboxes.txt", "pokemon_infobox.ttl")

    extract_and_save_infoboxes("Abilities", "ability", "{{AbilityInfobox/header", "abilities_infoboxes.txt", "abilities_infobox.ttl")

    extract_and_save_infoboxes("Moves", "move", "{{MoveInfobox", "moves_infoboxes.txt", "moves_infobox.ttl")