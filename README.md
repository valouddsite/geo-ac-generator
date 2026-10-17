# Geo → Assetto Corsa Generator

Prototype indépendant pour extraire une zone géographique, examiner les données des bâtiments et préparer une scène 3D. Ce dépôt est autonome et ne dépend pas de l'ancien site.

## Ouvrir directement dans le navigateur

Le workflow `.github/workflows/pages.yml` publie le dossier `frontend` sur GitHub Pages après un push sur `main`.

**Activation une seule fois :**
1. Ouvre les paramètres du dépôt GitHub.
2. Va dans **Pages**.
3. Dans la source de publication, sélectionne **GitHub Actions**.
4. Ouvre l'onglet **Actions** et vérifie que le workflow « Deploy browser app to GitHub Pages » se termine correctement.
5. L'URL publique sera affichée dans l'exécution du workflow et dans les paramètres Pages.

GitHub peut demander quelques minutes pour la première publication. Cette configuration publie uniquement le site navigateur, pas l'API Python.

## Fonctionnalités
- Sélection d'un rectangle sur une carte.
- Extraction de routes, empreintes de bâtiments et points OpenStreetMap via Overpass.
- Si l'API Python n'est pas présente, tentative d'extraction directe depuis le navigateur auprès de services publics Overpass.
- Métadonnées de provenance et indicateurs heuristiques pour les bâtiments.
- Export GeoJSON et manifeste JSON.
- Aperçu 3D dans le navigateur depuis un fichier GeoJSON.
- Chargement facultatif d’un relief depuis l’API d’altitude Open-Meteo, fondée sur Copernicus DEM GLO-90 (~90 m); aperçu sur une grille de 10 × 10 points (une seule requête) pour limiter les erreurs de disponibilité. Le terrain et les routes/bâtiments sont positionnés selon les altitudes interpolées.
- Export OBJ simplifié de l’aperçu 3D (format intermédiaire, pas un fichier Assetto Corsa).

## Utiliser l'aperçu 3D
Ouvre le lien « Ouvrir l'aperçu 3D » depuis la carte, puis charge `export.geojson`. Le bouton « Charger l'exemple » permet de tester la vue sans extraction. Le rendu utilise Three.js depuis un CDN et nécessite une connexion Internet. La géométrie importée est traitée dans l'onglet du navigateur; le fichier GeoJSON n'est pas envoyé à un serveur tiers par le visualiseur.

## Lancer l'API en local (facultatif)
Python 3.10+ recommandé.

```bash
python -m venv .venv
# Windows : .venv\\Scripts\\activate
# macOS/Linux : source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app:app --reload
```

Puis ouvre http://127.0.0.1:8000. L'API locale offre une autre voie pour interroger Overpass. Pour une API publique permanente, il faudra déployer FastAPI sur un hébergeur séparé et configurer son URL côté frontend; GitHub Pages n'exécute pas Python.

## Limites importantes
- Les services publics Overpass peuvent être lents, indisponibles ou limiter les requêtes. Réduis la zone et réessaie si nécessaire.
- La limite côté navigateur est de 25 km² par extraction.
- Les hauteurs estimées sont des heuristiques, pas des mesures; les façades et toitures ne sont pas reconstruites fidèlement.
- Le relief utilise Copernicus DEM GLO-90 via Open-Meteo (résolution d’environ 90 m) : il montre les pentes générales, mais ne garantit pas la précision d’une chaussée de course. L’altitude dépend d’un service externe. Attribuer Open-Meteo et Copernicus si les données de relief sont redistribuées.
- L’aperçu OBJ est une géométrie de départ : il ne contient pas de textures de façades, de collisions optimisées ni de matériaux finalisés.
- Le projet ne produit pas encore de KN5 ni de piste Assetto Corsa prête à jouer.
- Aucune imagerie satellite n'est téléchargée. Utiliser uniquement des modèles, orthophotos et textures dont les licences autorisent explicitement la transformation et la redistribution dans un mod.

Les données OpenStreetMap sont soumises à l'ODbL; conserver l'attribution et vérifier les obligations de licence avant de redistribuer un jeu de données dérivé.

## Pipeline à compléter
1. Extraire GeoJSON et manifeste.
2. Créer un terrain depuis un MNT/DEM autorisé.
3. Générer les routes, bâtiments, UV, matériaux et collisions.
4. Corriger la géométrie et optimiser la scène.
5. Convertir avec les outils compatibles vers le format du jeu (souvent KN5).
6. Configurer les fichiers de piste, surfaces, spawn, timing et AI line, puis tester dans Assetto Corsa.

Voir [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md).
