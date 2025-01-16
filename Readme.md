# 🎮 Pokémon Knowledge Graph
By Aymen BEN ABDALLAH & Saad KEMLANE

## 📝 Description

Pokémon Knowledge Graph is a semantic web application that creates an interactive database of the Pokémon universe. The application allows users to explore relationships between Pokémon, their types, abilities, and evolutions through an intuitive web interface.

<div align="center">
  <img src="server\static\images\liste_pokemon.png" alt="Pokemon List Interface">
  <p><em>Main Interface - Pokémon List</em></p>
</div>

## 🛠️ Technologies

### Back-end
- **Flask** (Python 3.8+)
- **RDFLib**
- **Apache Jena Fuseki**
- **SPARQLWrapper**

### Front-end
- **HTML5/CSS3**
- **JavaScript**

### Database
- **RDF/SPARQL**
- **Turtle (.ttl)**



## 🚀 Setup and Installation

### Prerequisites
- Python 3.8+
- Apache Jena Fuseki
- RDFLib
- Apache Jena Fuseki
- SPARQLWrapper
### Installation Steps

1. **Clone repository**
```bash
git clone https://github.com/aymenBen8/SemanticWeb
```

2. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Start Fuseki and load data**
```bash
fuseki-server

(create database then add Final_KG.ttl)
```

4. **Run application**
```bash
cd .\server\
python app.py
```

Access the application at: `http://localhost:5000`

## 💡 Key Features

### Pokémon Exploration
- Paginated Pokémon, Ability, Item,... list
- Search by name
- Detailed Pokémon view

<div align="center">
  <img src="server\static\images\detail_pokemon1.png" alt="Pokemon Details">
  <img src="server\static\images\detail_pokemon2.png" alt="Pokemon Details">
  <p><em>Detailed Pokémon View</em></p>
</div>






