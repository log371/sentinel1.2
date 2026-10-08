# SentinelIA — Document Intelligence

API RAG démontrable qui ingère des PDF/TXT/Markdown, retrouve les passages utiles et répond avec des citations vérifiables. Le projet fonctionne avec **Ollama en local** ou une **API compatible OpenAI**, sans coupler la logique métier à un fournisseur.

> Projet de portfolio : les documents d'exemple et toutes les entités sont fictifs.

## Ce que la démonstration prouve

- API FastAPI typée et documentée automatiquement (`/docs`)
- pipeline ingestion → découpage → recherche → réponse ancrée dans les sources
- citations structurées (fichier, page, extrait, score)
- refus explicite quand aucune source pertinente n'est trouvée
- interface fournisseur interchangeable : Ollama / OpenAI-compatible / mock de test
- garde-fous d'upload, tests Pytest, lint Ruff, CI GitHub Actions et conteneurs sans privilèges

## Démarrage reproductible

Prérequis : Python 3.12+, ou Docker avec Docker Compose.

### Option A — local, sans modèle (mode démonstration déterministe)

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
cp .env.example .env
LLM_PROVIDER=mock uvicorn sentinelia.main:app --reload
```

Dans un second terminal :

```bash
./scripts/demo.sh
```

### Option B — Ollama avec Docker Compose

```bash
docker compose up -d --build
docker compose exec ollama ollama pull mistral
./scripts/demo.sh
```

Swagger est disponible sur <http://localhost:8000/docs>.

## Appels API

```bash
curl -F 'file=@examples/documents/pv-assemblee-generale.md;type=text/markdown' \
  http://localhost:8000/v1/documents

curl -H 'Content-Type: application/json' \
  -d '{"question":"Quels travaux ont été votés et pour quel montant ?"}' \
  http://localhost:8000/v1/query
```

Une réponse contient `answer`, `grounded` et une liste `sources`. Chaque source porte un identifiant stable de fragment, le document, la page éventuelle, un extrait et son score.

## Fournisseur API interchangeable

Pour Mistral, OpenAI ou une passerelle compatible avec l'API Chat Completions :

```dotenv
LLM_PROVIDER=openai_compatible
LLM_BASE_URL=https://api.openai.com
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=...
```

Les secrets restent dans `.env`, ignoré par Git. Ne les placez jamais dans une image ou un commit.

## Tests et qualité

```bash
ruff check .
pytest
docker build -t sentinelia-document-intelligence .
```

La CI exécute ces contrôles sur chaque pull request et chaque push vers `main` avec des permissions GitHub minimales (`contents: read`).

## Sécurité des uploads

- extensions limitées à PDF, TXT et Markdown ;
- contrôle du type déclaré et de la signature `%PDF-` ;
- taille bornée avant traitement ;
- nom réduit à sa base puis assaini ;
- contenu binaire rejeté pour les formats texte ;
- aucune exécution du contenu et aucun chemin fourni par l'utilisateur utilisé pour écrire un fichier.

Cette version est une démonstration mono-processus avec index en mémoire. Avant production : authentification, isolation par locataire, antivirus, limitation de débit, stockage chiffré, base vectorielle et politique de rétention. Voir [SECURITY.md](SECURITY.md).

## Architecture

```text
Client → FastAPI → validation upload → extraction/découpage → index en mémoire
                                                        ↓
Réponse + citations ← fournisseur LLM interchangeable ← recherche top-k
```

Le retriever lexical léger rend le dépôt immédiatement exécutable sans service externe. L'interface `LLMProvider` permet de remplacer le fournisseur ; la prochaine étape naturelle consiste à introduire des embeddings et une base vectorielle derrière une interface similaire.

## Dépôt GitHub

Le projet est publié sur <https://github.com/log371/sentinel1.2>. Pour le récupérer :

```bash
git clone https://github.com/log371/sentinel1.2.git
cd sentinel1.2
```

## Licence

MIT — voir [LICENSE](LICENSE).
