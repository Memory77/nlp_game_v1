version du nlp_game antérieur, juste avec la generation de text sans le speech text et le text speech. 

Prérequis : Python3

- cloner le projet
- creer un .env : 

OPENAI_API_KEY= ta clé 
OPENAI_MODEL= exemple gpt-3.5-turbo

- créer un environnement virtuel et l'activer : python3 -m venv venv + source venv/bin/activate(linux)
- installer les dépendances : pip install r requirements.txt
- python3 triv_poursuite.py -> pour lancer une db vide
- sqlite3 triv_ia_dlc.db < INSERT.sql
- python3 triv_poursuite.py