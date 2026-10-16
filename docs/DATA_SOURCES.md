# Sources, licences et confiance

## OpenStreetMap
Les routes, empreintes et points viennent d'OpenStreetMap via Overpass. Attribution : © OpenStreetMap contributors. Respecter l'ODbL 1.0 et ses obligations applicables aux bases dérivées redistribuées.
- https://www.openstreetmap.org/copyright
- https://wiki.openstreetmap.org/wiki/Overpass_API

Les serveurs Overpass publics ont des limites de débit et peuvent refuser de grandes zones.

## Imagerie aérienne
Ce prototype ne télécharge aucune image satellite. Le fait de pouvoir afficher une image dans un service cartographique ne donne pas automatiquement le droit de la télécharger, de la transformer en texture ou de la redistribuer dans un jeu. Ne pas extraire de tuiles Google ni de modèles 3D Google pour construire un mod. Vérifier les droits de dérivation, stockage, attribution et redistribution du fournisseur d'orthophotos.

## Confiance des bâtiments
Les tags OSM `height`, `building:levels` et `roof:shape` sont des indices. Le niveau de confiance reflète la présence d'attributs, pas une vérification terrain. Les hauteurs de secours sont des heuristiques et restent explicitement marquées comme estimées.

## Relief et assets
Intégrer un MNT/DEM dont la licence permet l'usage prévu et enregistrer résolution, fournisseur, système de coordonnées et licence. Pour chaque texture ou modèle, conserver source, licence, attribution, version et restrictions.

## Pipeline Assetto Corsa
Ce prototype ne produit pas encore de KN5 ni de piste jouable. Il faut encore construire le relief, les routes roulables, UV, matériaux, collisions, objets, fichiers de piste, points de départ, timing et AI line, puis tester le circuit.
