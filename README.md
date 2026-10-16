# Geo → Assetto Corsa Generator

Prototype indépendant pour extraire une zone géographique, examiner les données des bâtiments et préparer une scène Blender. Ce dépôt est autonome et ne dépend pas de l'ancien site.

## Fonctionnalités
- Sélection d'un rectangle sur une carte.
- Extraction de routes, empreintes de bâtiments et points OpenStreetMap via Overpass.
- Métadonnées de provenance et indicateurs de confiance pour les bâtiments.
- Export GeoJSON et manifeste JSON.
- Script Blender de départ pour une scène géométrique.

## Lancer en local
Python 3.10+ recommandé.

```bash
python -m venv .venv
# Windows : .venv\Scripts\activate
# macOS/Linux : source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app:app --reload
```

Puis ouvrir http://127.0.0.1:8000.

La surface maximale est de 25 km² par défaut. Modifier la variable d'environnement `MAX_AREA_KM2` pour la changer. Les services Overpass publics ont des limites de débit.

## Limites importantes
Ce prototype ne produit pas encore de KN5 ni de piste Assetto Corsa prête à jouer. Les hauteurs estimées sont des heuristiques, pas des mesures. Il ne télécharge pas d'images satellite. Utiliser uniquement des modèles, orthophotos et textures dont les licences autorisent explicitement la transformation et la redistribution dans un mod.

## Pipeline à compléter
1. Extraire GeoJSON et manifeste.
2. Créer un terrain depuis un MNT/DEM autorisé.
3. Générer les routes, bâtiments, UV, matériaux et collisions dans Blender.
4. Corriger la géométrie et optimiser la scène.
5. Convertir avec les outils compatibles vers le format du jeu (souvent KN5).
6. Configurer les fichiers de piste, surfaces, spawn, timing et AI line, puis tester dans Assetto Corsa.

Voir [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md).
