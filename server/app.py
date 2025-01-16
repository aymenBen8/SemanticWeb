from hashlib import md5
from flask import Flask, render_template, abort, request, redirect, url_for
from sparql_service import SparqlService

app = Flask(__name__)

SPARQL_ENDPOINT = "http://localhost:3030/bulbapedia/sparql"  
sparql_service = SparqlService(SPARQL_ENDPOINT)

@app.template_filter('hash_md5')
def hash_md5_filter(s):
    """
    Filtre Jinja2 pour calculer le hash MD5 d'une chaîne
    """
    return md5(s.encode('utf-8')).hexdigest()


@app.route('/')
def home():
    try:
        return render_template('index.html', 
                              featured_pokemon=[],  
                              featured_trainers=[],
                              featured_moves=[],
                              featured_items=[],
                              featured_locations=[],
                              featured_abilities=[])
    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération des données pour la page d'accueil : {e}")
        return render_template('error.html', message="Une erreur s'est produite."), 500

@app.route('/search', methods=['GET'])
def search():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return redirect(url_for('home'))

        search_results = {
            'pokemon': sparql_service.search_pokemon(query),
            'trainers': sparql_service.search_trainers(query),
            'moves': sparql_service.search_moves(query),
            'items': sparql_service.search_items(query),
            'locations': sparql_service.search_locations(query),
            'abilities': sparql_service.search_abilities(query)
        }

        return render_template('search_results.html', query=query, results=search_results)
    except Exception as e:
        app.logger.error(f"Erreur lors de la recherche : {e}")
        return render_template('error.html', message="Une erreur s'est produite."), 500

@app.route('/pokemon')
def pokemon_list():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 24  

        result = sparql_service.get_pokemon_list(page, per_page)
        pokemon_list = result["pokemon_list"]
        total_pokemon = result["total_pokemon"]

        if not pokemon_list:
            return render_template('error.html', message="Aucun Pokémon trouvé."), 404
        total_pages = (total_pokemon + per_page - 1) // per_page
        return render_template('pokemon/list.html', 
                              pokemon_list=pokemon_list, 
                              page=page, 
                              total_pages=total_pages,
                              total_pokemon=total_pokemon)  
    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération de la liste des Pokémon : {e}")
        return render_template('error.html', message="Une erreur s'est produite."), 500

@app.route('/pokemon/<name>')
def pokemon_detail(name):
    try:
        pokemon_details = sparql_service.get_pokemon_details(name)
        if not pokemon_details:
            return render_template('error.html', message=f"Pokémon '{name}' non trouvé."), 404

        details = {
            "name": next((item['value']['value'] for item in pokemon_details if item['property']['value'] == "http://example.org/ontology/pokemon#name"), None),
            "image": next((item['value']['value'] for item in pokemon_details if item['property']['value'] == "http://schema.org/image"), None),
            "category": next((item['value']['value'] for item in pokemon_details if item['property']['value'] == "http://example.org/ontology/pokemon#category"), None),
            "types": [item['value']['value'].split('#')[-1] for item in pokemon_details if item['property']['value'] == "http://example.org/ontology/pokemon#hasType"],
            "height": next((item['value']['value'] for item in pokemon_details if item['property']['value'] == "http://example.org/ontology/pokemon#height"), None),
            "weight": next((item['value']['value'] for item in pokemon_details if item['property']['value'] == "http://example.org/ontology/pokemon#weight"), None),
            "baseExperience": next((item['value']['value'] for item in pokemon_details if item['property']['value'] == "http://example.org/ontology/pokemon#baseExperience"), None),
            "catchRate": next((item['value']['value'] for item in pokemon_details if item['property']['value'] == "http://example.org/ontology/pokemon#catchRate"), None),
            "genderRatio": next((item['value']['value'] for item in pokemon_details if item['property']['value'] == "http://example.org/ontology/pokemon#genderRatio"), None),
            "eggSteps": next((item['value']['value'] for item in pokemon_details if item['property']['value'] == "http://example.org/ontology/pokemon#eggSteps"), None),
            "baseHappiness": next((item['value']['value'] for item in pokemon_details if item['property']['value'] == "http://example.org/ontology/pokemon#baseHappiness"), None),
            "bodyShape": next((item['value']['value'] for item in pokemon_details if item['property']['value'] == "http://example.org/ontology/pokemon#bodyShape"), None),
            "color": next((item['value']['value'] for item in pokemon_details if item['property']['value'] == "http://example.org/ontology/pokemon#color"), None),
            "number": next((item['value']['value'] for item in pokemon_details if item['property']['value'] == "http://example.org/ontology/pokemon#number"), None),
            "totalEV": next((item['value']['value'] for item in pokemon_details if item['property']['value'] == "http://example.org/ontology/pokemon#totalEV"), None),
            "labels": [item['value']['value'] for item in pokemon_details if item['property']['value'] == "http://www.w3.org/2000/01/rdf-schema#label"],
            "abilities": [item['value']['value'].split('#')[-1].replace('_', ' ') for item in pokemon_details if item['property']['value'] == "http://example.org/ontology/pokemon#hasAbility"],
            "sameAs": next((item['value']['value'] for item in pokemon_details if item['property']['value'] == "http://www.w3.org/2002/07/owl#sameAs"), None),
            "relatedTo": next((item['value']['value'] for item in pokemon_details if item['property']['value'] == "http://example.org/ontology/pokemon#relatedTo"), None),
            "images": [item['value']['value'] for item in pokemon_details if item['property']['value'] == "http://schema.org/image"]
        }

        if details["sameAs"]:
            dbpedia_url = details["sameAs"]
            pokemon_name = dbpedia_url.split('/')[-1]  
            pokemon_name = pokemon_name.replace("Pokémon_", "")  
            details["sameAs"] = f"https://dbpedia.org/page/{pokemon_name}"

       
        if details["relatedTo"]:
            pokemon_name = details["relatedTo"].split('#')[-1].replace('_(Pokémon)', '')
            details["relatedTo"] = f"http://127.0.0.1:5000/pokemon/{pokemon_name}"

        return render_template('pokemon/detail.html', pokemon_details=details)
    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération des détails du Pokémon {name} : {e}")
        return render_template('error.html', message="Une erreur s'est produite."), 500

@app.route('/trainers')
def trainer_list():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 24  

        result = sparql_service.get_trainer_list(page, per_page)
        trainer_list = result["trainer_list"]
        total_trainers = result["total_trainers"]

        if not trainer_list:
            return render_template('error.html', message="Aucun dresseur trouvé."), 404

        total_pages = (total_trainers + per_page - 1) // per_page

        return render_template('trainers/list.html', 
                              trainer_list=trainer_list, 
                              page=page, 
                              total_pages=total_pages,
                              total_trainers=total_trainers) 
    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération de la liste des dresseurs : {e}")
        return render_template('error.html', message="Une erreur s'est produite."), 500

@app.route('/trainers/<name>')
def trainer_detail(name):
    try:
        trainer = sparql_service.get_trainer_by_name(name)
        
        if not trainer:
            return render_template('error.html', message="Dresseur non trouvé."), 404

        return render_template('trainers/detail.html', trainer=trainer)
    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération des détails du dresseur : {e}")
        return render_template('error.html', message="Une erreur s'est produite."), 500


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', message="Page non trouvée."), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error.html', message="Une erreur interne s'est produite."), 500



@app.route('/abilities')
def ability_list():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 24 

        result = sparql_service.get_ability_list(page, per_page)
        ability_list = result["ability_list"]
        total_abilities = result["total_abilities"]

        if not ability_list:
            return render_template('error.html', message="Aucune Ability trouvée."), 404
        total_pages = (total_abilities + per_page - 1) // per_page
        return render_template('ability/list.html', 
                              ability_list=ability_list, 
                              page=page, 
                              total_pages=total_pages,
                              total_abilities=total_abilities)
    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération de la liste des Abilities : {e}")
        return render_template('error.html', message="Une erreur s'est produite."), 500
    


@app.route('/abilities/<name>')
def ability_detail(name):
    try:
        ability = sparql_service.get_ability_by_name(name)
        
        if not ability:
            return render_template('error.html', message="Ability non trouvée."), 404
        return render_template('ability/detail.html', ability=ability)
    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération des détails de l'Ability : {e}")
        return render_template('error.html', message="Une erreur s'est produite."), 500




@app.route('/items')
def item_list():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 24

        result = sparql_service.get_item_list(page, per_page)
        item_list = result["item_list"]
        total_items = result["total_items"]

        if not item_list:
            return render_template('error.html', message="Aucun Item trouvé."), 404

        total_pages = (total_items + per_page - 1) // per_page

        print(f"Page: {page}, Total Items: {total_items}, Total Pages: {total_pages}")

        return render_template('item/list.html', 
                              item_list=item_list, 
                              page=page, 
                              total_pages=total_pages,
                              total_items=total_items)
    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération de la liste des Items : {e}")
        return render_template('error.html', message="Une erreur s'est produite."), 500


@app.route('/items/<name>')
def item_detail(name):
    try:
        item_details = sparql_service.get_item_details(name)
        if not item_details:
            return render_template('error.html', message=f"Item '{name}' non trouvé."), 404

        details = {
            "name": item_details["name"],
            "japaneseName": item_details["japaneseName"],
            "selectedImage": item_details["selectedImage"],
        }

        return render_template('item/detail.html', item_details=details)
    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération des détails de l'Item {name} : {e}")
        return render_template('error.html', message="Une erreur s'est produite."), 500
    








@app.route('/moves')
def move_list():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 24  

        result = sparql_service.get_move_list(page, per_page)
        move_list = result["move_list"]
        total_moves = result["total_moves"]

        if not move_list:
            return render_template('error.html', message="Aucun Move trouvé."), 404

        total_pages = (total_moves + per_page - 1) // per_page
        return render_template('move/list.html', 
                              move_list=move_list, 
                              page=page, 
                              total_pages=total_pages,
                              total_moves=total_moves)
    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération de la liste des Moves : {e}")
        return render_template('error.html', message="Une erreur s'est produite."), 500





@app.route('/moves/<name>')
def move_detail(name):
    try:
        move_details = sparql_service.get_move_details(name)
        if not move_details:
            return render_template('error.html', message=f"Move '{name}' non trouvé."), 404
        details = {
            "name": move_details["name"]["value"],
            "japaneseName": move_details["japaneseName"]["value"],
            "relatedToList": move_details["relatedToList"]["value"].split(", "),
        }

        return render_template('move/detail.html', move_details=details)
    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération des détails du Move {name} : {e}")
        return render_template('error.html', message="Une erreur s'est produite."), 500

if __name__ == '__main__':
    app.run(debug=True)