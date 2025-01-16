from SPARQLWrapper import SPARQLWrapper, JSON

class SparqlService:
    def __init__(self, endpoint_url):
        self.sparql = SPARQLWrapper(endpoint_url)
        self.sparql.setReturnFormat(JSON)

    def query(self, query):
        """Exécute une requête SPARQL et retourne les résultats."""
        self.sparql.setQuery(query)
        try:
            results = self.sparql.query().convert()
            return results["results"]["bindings"]
        except Exception as e:
            print(f"Erreur lors de l'exécution de la requête SPARQL : {e}")
            return []

    

    






    def get_pokemon_list(self, page=1, per_page=24):
    
        offset = (page - 1) * per_page
        query = f"""
        PREFIX ns1: <http://example.org/ontology/pokemon#>
        PREFIX ns2: <http://schema.org/>
        SELECT ?pokemon ?name 
            (GROUP_CONCAT(DISTINCT ?typeName; separator=", ") AS ?types) 
            (SAMPLE(?image) AS ?selectedImage) 
        WHERE {{
            ?pokemon a ns1:Pokémon ;
                    ns1:name ?name ;
                    ns1:hasType ?type ;
                    ns2:image ?image .
            BIND(REPLACE(STR(?type), "^.*#", "") AS ?typeName)  # Extrait le nom du type après le #
            FILTER(STRENDS(STR(?image), CONCAT(?name, ".png")))  # Filtre pour ne garder que les URLs se terminant par "<nom_du_pokemon>.png"
        }}
        GROUP BY ?pokemon ?name
        LIMIT {per_page} OFFSET {offset}
        """
        pokemon_list = self.query(query)

        total_query = """
        PREFIX ns1: <http://example.org/ontology/pokemon#>
        SELECT (COUNT(?pokemon) AS ?total) WHERE {
            ?pokemon a ns1:Pokémon .
        }
        """
        total_result = self.query(total_query)
        total_pokemon = int(total_result[0]['total']['value']) if total_result else 0

        return {
            "pokemon_list": pokemon_list,
            "total_pokemon": total_pokemon
        }
    
    def get_pokemon_details(self, name):

        query = f"""
        PREFIX ns1: <http://example.org/ontology/pokemon#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX ns2: <http://schema.org/>

        SELECT ?property ?value
        WHERE {{
        ?pokemon a ns1:Pokémon ;
                ns1:name "{name}"^^xsd:string ;
                ?property ?value .
        FILTER (
            ?property != ns1:usesTemplate &&
            ?property != foaf:depiction
        )
        # Garder uniquement l'image qui se termine par "<nom_du_pokemon>.png"
        FILTER (
            !(?property = ns2:image && !STRENDS(STR(?value), "{name}.png"))
        )
        }}
        """
        return self.query(query)

    def get_total_pokemon(self):
        query = """
        PREFIX ns1: <http://example.org/ontology/pokemon#>
        SELECT (COUNT(?pokemon) AS ?total) WHERE {
            ?pokemon a ns1:Pokémon .
        }
        """
        result = self.query(query)
        return int(result[0]['total']['value']) if result else 0
    


    def get_ability_list(self, page=1, per_page=24):
        """
        Récupère la liste des Abilities avec pagination, triés par ordre alphabétique.
        """
        offset = (page - 1) * per_page

        query = f"""
        PREFIX ns1: <http://example.org/ontology/pokemon#>
        SELECT ?ability ?name ?japaneseName
        WHERE {{
            ?ability a ns1:Ability ;
                ns1:name ?name ;
                ns1:japaneseName ?japaneseName .
        }}
        ORDER BY ?name
        LIMIT {per_page} OFFSET {offset}
        """
        ability_list = self.query(query)

        total_query = """
        PREFIX ns1: <http://example.org/ontology/pokemon#>
        SELECT (COUNT(?ability) AS ?total) WHERE {
            ?ability a ns1:Ability .
        }
        """
        total_result = self.query(total_query)
        total_abilities = int(total_result[0]['total']['value']) if total_result else 0

        return {
            "ability_list": ability_list,
            "total_abilities": total_abilities
    }


    def get_ability_by_name(self, name):
        """
        Récupère les détails d'une Ability par son nom.
        """
        query = f"""
        PREFIX ns1: <http://example.org/ontology/pokemon#>
        SELECT ?ability ?name ?japaneseName
        WHERE {{
            ?ability a ns1:Ability ;
                ns1:name "{name}" ;
                ns1:japaneseName ?japaneseName .
        }}
        """
        result = self.query(query)
        return result[0] if result else None



    def get_trainer_list(self, page=1, per_page=24):
        """
        Récupère la liste des dresseurs avec pagination, triés par ordre alphabétique.
        """
        offset = (page - 1) * per_page
        query = f"""
        PREFIX ns1: <http://example.org/ontology/pokemon#>
        PREFIX ns2: <http://schema.org/>
        SELECT ?trainer ?name ?gender ?japaneseName ?relatedTo 
            (SAMPLE(?image) AS ?selectedImage)  # Sélectionne une seule image par dresseur
        WHERE {{
            ?trainer a ns1:Trainer ;
                    ns1:name ?name ;
                    ns1:gender ?gender ;
                    ns1:japaneseName ?japaneseName ;
                    ns1:relatedTo ?relatedTo ;
                    ns2:image ?image .
            FILTER(STRENDS(STR(?image), CONCAT(?name, ".png")))  # Filtre pour ne garder que les URLs se terminant par "<nom_du_dresseur>.png"
        }}
        GROUP BY ?trainer ?name ?gender ?japaneseName ?relatedTo  # Groupe par dresseur
        ORDER BY ?name
        LIMIT {per_page} OFFSET {offset}
        """
        trainer_list = self.query(query)
        total_query = """
        PREFIX ns1: <http://example.org/ontology/pokemon#>
        SELECT (COUNT(?trainer) AS ?total) WHERE {
            ?trainer a ns1:Trainer .
        }
        """
        total_result = self.query(total_query)
        total_trainers = int(total_result[0]['total']['value']) if total_result else 0
        return {
            "trainer_list": trainer_list,
            "total_trainers": total_trainers
        }

    def get_trainer_by_name(self, name):
        query = f"""
        PREFIX ns1: <http://example.org/ontology/pokemon#>
        PREFIX ns2: <http://schema.org/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?trainer ?name ?gender ?japaneseName ?relatedTo ?image
        WHERE {{
            ?trainer a ns1:Trainer ;
                    ns1:name "{name}" ;
                    ns1:gender ?gender ;
                    ns1:japaneseName ?japaneseName ;
                    ns1:relatedTo ?relatedTo ;
                    ns2:image ?image .
        }}
        """
        result = self.query(query)
        return result[0] if result else None
    
    def get_move_list(self, page=1, per_page=24):
        offset = (page - 1) * per_page

        query = f"""
        PREFIX ns1: <http://example.org/ontology/pokemon#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?move ?name ?japaneseName
            (GROUP_CONCAT(DISTINCT ?relatedTo; separator=", ") AS ?relatedToList)
        WHERE {{
            ?move a ns1:Move ;
                ns1:name ?name ;
                ns1:japaneseName ?japaneseName ;
                ns1:relatedTo ?relatedTo .
        }}
        GROUP BY ?move ?name ?japaneseName
        ORDER BY ?name
        LIMIT {per_page} OFFSET {offset}
        """
        move_list = self.query(query)

        total_query = """
        PREFIX ns1: <http://example.org/ontology/pokemon#>
        SELECT (COUNT(?move) AS ?total)
        WHERE {
            ?move a ns1:Move .
        }
        """
        total_result = self.query(total_query)
        total_moves = int(total_result[0]['total']['value']) if total_result else 0

        return {
            "move_list": move_list,
            "total_moves": total_moves
        }

    def get_move_details(self, name):
        query = f"""
        PREFIX ns1: <http://example.org/ontology/pokemon#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?move ?name ?japaneseName
            (GROUP_CONCAT(DISTINCT ?relatedTo; separator=", ") AS ?relatedToList)
        WHERE {{
            ?move a ns1:Move ;
                ns1:name "{name}"^^xsd:string ;
                ns1:japaneseName ?japaneseName ;
                ns1:relatedTo ?relatedTo .
        }}
        GROUP BY ?move ?name ?japaneseName
        """
        result = self.query(query)
        return result[0] if result else None



    def get_item_list(self, page=1, per_page=24):
        offset = (page - 1) * per_page

        query = f"""
        PREFIX ns1: <http://example.org/ontology/pokemon#>
        PREFIX ns2: <http://schema.org/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?item ?name ?japaneseName
            (SAMPLE(?image) AS ?selectedImage) 
        WHERE {{
            ?item a ns1:Item ;
                ns1:name ?name ;
                ns1:japaneseName ?japaneseName ;
                ns2:image ?image .
            FILTER(STRENDS(STR(?image), CONCAT(?name, ".png")))  # Filtre pour ne garder que les URLs se terminant par "<nom_de_l'item>.png"
        }}
        GROUP BY ?item ?name ?japaneseName
        ORDER BY ?name
        LIMIT {per_page} OFFSET {offset}
        """
        item_list = self.query(query)

        print(f"Page: {page}, Offset: {offset}, Results: {len(item_list)}")
        for item in item_list:
            print(item)

        total_query = """
        PREFIX ns1: <http://example.org/ontology/pokemon#>
        SELECT (COUNT(?item) AS ?total) WHERE {
            ?item a ns1:Item .
        }
        """
        total_result = self.query(total_query)
        total_items = int(total_result[0]['total']['value']) if total_result else 0

        print(f"Total Items: {total_items}")

        return {
            "item_list": item_list,
            "total_items": total_items
        }


def get_item_details(self, name):
    query = f"""
    PREFIX ns1: <http://example.org/ontology/pokemon#>
    PREFIX ns2: <http://schema.org/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?item ?name ?japaneseName ?image
    WHERE {{
        ?item a ns1:Item ;
              ns1:name "{name}" ;
              ns1:japaneseName ?japaneseName ;
              ns2:image ?image .
    }}
    LIMIT 1
    """
    results = self.query(query)

    if not results:
        return None
    return {
        "item": results[0]["item"]["value"],
        "name": results[0]["name"]["value"],
        "japaneseName": results[0]["japaneseName"]["value"],
        "selectedImage": results[0]["image"]["value"]
    }







