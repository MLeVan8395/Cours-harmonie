# Cours d'écriture et d'harmonie

> 📱 **L'appli Atelier d'harmonie : [mlevan8395.github.io/Cours-harmonie/app](https://mlevan8395.github.io/Cours-harmonie/app/)**  
> Cours, cahier d'exercices sur la portée, chiffrage, chasse aux fautes, cadences à l'oreille et quiz. Installable sur téléphone, fonctionne hors connexion.

Un cours d'harmonie à quatre voix pour débutants, en français : du choral de Bach à l'harmonie de Fauré, Debussy et Ravel, en passant par Mozart, Beethoven et Schumann. On écrit pour le **quatuor vocal** (soprano, alto, ténor, basse) et pour le **quatuor à cordes**. Chaque chapitre contient des explications simples, des exemples gravés, des exercices et leurs corrigés.

Ce cours fait suite au [Cours de contrepoint](https://github.com/MLeVan8395/Cours-contrepoint) : le contrepoint t'a appris à écrire des lignes indépendantes, l'harmonie t'apprend à les faire sonner ensemble, accord après accord.

Auteur : Mickael Le Van, professeur de musiques actuelles et jazz.

## L'application : Atelier d'harmonie

👉 **https://mlevan8395.github.io/Cours-harmonie/app/**

Une appli web installable sur téléphone, tablette ou ordinateur, qui marche ensuite **hors connexion**. Elle réunit :

- **Cours** : tous les chapitres, avec un lecteur sous chaque exemple (sons de banque General MIDI : chœur, piano, orgue, quatuor à cordes) ;
- **Cahier d'exercices** : les 116 exercices, à faire directement sur la portée, corrigés au fur et à mesure ; la progression est enregistrée ;
- **Chiffrer** : trouver le degré et l'état (5, 6, 6/4) d'un accord, dans toutes les tonalités du cours (160 accords) ;
- **Chasse aux fautes** : deux accords, une faute à trouver (quintes, octaves, croisement, doublure, sensible…), ou aucune (150 enchaînements) ;
- **Cadences à l'oreille** : écouter une phrase et reconnaître la cadence (parfaite, imparfaite, demi, plagale, rompue) ;
- **Quiz de cours** : 38 questions sur les règles, avec l'explication et le lien vers le chapitre.

Les scores et le travail en cours sont gardés dans le navigateur.

### Installer l'application

- **Android (Chrome)** : ouvrir https://mlevan8395.github.io/Cours-harmonie/app/, puis menu ⋮ → **Installer l'application** (ou **Ajouter à l'écran d'accueil**).
- **iPhone / iPad (Safari)** : ouvrir la même adresse, puis bouton **Partager** → **Sur l'écran d'accueil**.
- **Ordinateur (Chrome, Edge)** : bouton « Installer l'appli » en haut de la page, ou icône d'installation dans la barre d'adresse.

Pour la mettre en ligne : dans les réglages du dépôt, **Settings → Pages**, choisir la branche `main` et le dossier `/ (root)`.

## Contenu du dépôt

| Dossier | Contenu |
| --- | --- |
| [`cours/`](cours/) | Le cours, un fichier Markdown par chapitre, lisible directement sur GitHub |
| [`cours/images/`](cours/images/) | Les exemples et exercices gravés (PNG) |
| [`cours/audio/`](cours/audio/) | Chaque exemple en MP3 et en MIDI |
| [`index.html`](index.html) | La version web du cours, avec un lecteur sous chaque exemple |
| [`cahier/`](cahier/README.md) | Le **cahier d'exercices** : 116 exercices qui suivent le cours, avec leurs corrigés |
| [`cahier.html`](cahier.html) | La version web du cahier : tous les exercices à faire sur la portée |
| [`app/`](app/) | L'application **Atelier d'harmonie** (PWA installable, hors connexion) |
| [`outils/`](outils/) | Le graveur, le vérificateur de règles et les outils audio |

## Sommaire

Les chapitres marqués ✅ sont rédigés. Les autres sont prévus : le plan peut encore évoluer.

### Première partie : les bases du 4 voix ✅

- [1. Les quatre voix](cours/01-les-quatre-voix.md) : tessitures SATB, deux portées, écarts, croisements, le quatuor à cordes
- [2. L'accord parfait à quatre voix](cours/02-l-accord-parfait-a-quatre-voix.md) : accords sur chaque degré, doublures, disposition serrée ou large
- [3. Enchaîner deux accords](cours/03-enchainer-deux-accords.md) : quintes et octaves, mouvements interdits, notes communes, la méthode
- [4. Exercices](cours/04-exercices.md)
- [5. Corrigés](cours/05-corriges.md)

### Deuxième partie : renversements et cadences ✅

- [6. Le premier renversement](cours/06-le-premier-renversement.md) : les trois états, chiffrage 6, doublures, I6, V6, II6
- [7. Les cadences](cours/07-les-cadences.md) : parfaite, imparfaite, demi-cadence, plagale, rompue ; préparer la cadence
- [8. L'accord de quarte et sixte](cours/08-l-accord-de-quarte-et-sixte.md) : de cadence, de passage, de broderie
- [9. Basse donnée et chant donné](cours/09-basse-donnee-et-chant-donne.md) : la méthode complète pour harmoniser
- [10. Le mode mineur](cours/10-le-mode-mineur.md) : sensible, seconde augmentée, chiffrage ♯
- [11. Exercices](cours/11-exercices.md)
- [12. Corrigés](cours/12-corriges.md)

### Troisième partie : le choral ✅

- [13. Les notes étrangères](cours/13-les-notes-etrangeres.md) : passage, broderie, échappée, anticipation, retard, appoggiature
- [14. Analyse : un choral de Bach](cours/14-analyse-un-choral-de-bach.md) : « Aus meines Herzens Grunde » (BWV 269), deux phrases
- [15. Harmoniser une mélodie de choral](cours/15-harmoniser-une-melodie-de-choral.md) : la méthode en six étapes
- [16. Exercices](cours/16-exercices.md)
- [17. Corrigés](cours/17-corriges.md)

### Quatrième partie : les accords de quatre sons ✅

- [18. La septième de dominante](cours/18-la-septieme-de-dominante.md) : résolution, doublures, renversements (7+, 6/5, +6, +4)
- [19. Les septièmes d'espèce et les marches harmoniques](cours/19-les-septiemes-d-espece-et-les-marches.md) : préparation et résolution, le II6/5, la chaîne de septièmes
- [20. La septième diminuée et la neuvième de dominante](cours/20-la-septieme-diminuee-et-la-neuvieme.md) : 9e de dominante, 7e de sensible, 7e diminuée
- [21. Les dominantes secondaires et la modulation](cours/21-les-dominantes-secondaires-et-la-modulation.md) : V7/V et les autres, tons voisins, accord pivot
- [22. Exercices](cours/22-exercices.md)
- [23. Corrigés](cours/23-corriges.md)

### Cinquième partie : le style classique (Mozart, Beethoven) ✅

- [24. La sixte napolitaine et les sixtes augmentées](cours/24-la-sixte-napolitaine-et-les-sixtes-augmentees.md) : N6, sixtes italienne, française et allemande, quintes « de Mozart »
- [25. Pédales et formules de cadence classiques](cours/25-pedales-et-formules-de-cadence.md) : pédales de tonique et de dominante, la grande cadence, la demi-cadence phrygienne, la coda
- [26. Écrire pour quatuor à cordes](cours/26-ecrire-pour-quatuor-a-cordes.md) : tessitures, batteries, basse en octaves, doubles cordes
- [27. Analyse : Beethoven, quatuor op. 18 n° 1, Adagio](cours/27-analyse-beethoven-op18-n1.md) : les neuf premières mesures
- [28. Exercices](cours/28-exercices.md)
- [29. Corrigés](cours/29-corriges.md)

### Sixième partie : le premier romantisme (Schumann, Chopin, Brahms) ✅

- [30. L'emprunt au mode mineur et les modulations par tierces](cours/30-l-emprunt-au-mode-mineur.md) : IVm, VI♭, IIø7, la fausse relation, de Do à La♭ et à Mi
- [31. Le chromatisme](cours/31-le-chromatisme.md) : notes de passage chromatiques, chaîne de dominantes, quinte augmentée
- [32. Du piano aux quatre voix](cours/32-du-piano-aux-quatre-voix.md) : arpèges, valse, réduire une pièce de piano
- [33. Analyse : Schumann, quatuor op. 41 n° 1, Intermezzo](cours/33-analyse-schumann-op41-n1.md) : pédale et lignes chromatiques
- [34. Exercices](cours/34-exercices.md)
- [35. Corrigés](cours/35-corriges.md)

### Septième partie : le romantisme tardif (Liszt, Wagner, Franck, Mahler) ✅

- [36. Enharmonie et modulations éloignées](cours/36-enharmonie-et-modulations-eloignees.md) : une 7e diminuée pour quatre tons, la sixte allemande qui devient V7
- [37. L'accord augmenté et les tierces](cours/37-l-accord-augmente-et-les-tierces.md) : Liszt, le cycle des tierces majeures (jusqu'à *Giant Steps*)
- [38. Wagner : l'accord de Tristan](cours/38-wagner-l-accord-de-tristan.md) : la résolution repoussée, la cadence évitée, le glissement chromatique
- [39. Franck et Mahler](cours/39-franck-et-mahler.md) : la phrase qui monte d'un demi-ton, majeur et mineur, la tonalité progressive
- [40. Analyse : le Prélude de *Tristan* et l'Adagietto de Mahler](cours/40-analyse-tristan-et-adagietto.md) : guide d'écoute
- [41. Exercices](cours/41-exercices.md)
- [42. Corrigés](cours/42-corriges.md)

### Huitième partie : vers l'harmonie moderne (Fauré, Debussy, Ravel)

- 43\. Fauré : couleurs modales, glissements, modulations inattendues
- 44\. Debussy : accords parallèles, gamme par tons, pentatonique, modes
- 45\. Ravel : accords de 9e, 11e et 13e, écriture pour cordes
- 46\. Des accords classés aux accords de couleur : le pont vers l'harmonie jazz
- 47\. Exercices
- 48\. Corrigés

### Prolongement possible : le XXe siècle (Scriabine, Bartók, Stravinsky, Prokofiev, Messiaen, Dutilleux)

Accord mystique et harmonie en quartes, l'écriture des quatuors de Bartók (système des axes, échelles acoustique et octatonique, symétries, clusters), bitonalité, modes à transposition limitée, accords pivots. Pour les compositeurs dont les œuvres sont encore protégées, les exemples seront originaux, avec des références précises pour l'écoute.

**Le quatuor à cordes, fil rouge** : chaque partie se termine par un exercice de transcription ou d'écriture pour quatuor (violon 1, violon 2, alto, violoncelle). À partir de la cinquième partie, le quatuor devient le format principal.

## Écouter les exemples

Chaque exemple peut s'écouter :

- **dans la version web** (`index.html`) : un bouton **▶ Écouter** sous chaque exemple. En haut de la page, on choisit le son (piano, chœur, orgue ou quatuor à cordes) et le tempo. Les sons viennent de la banque General MIDI FluidR3_GM. Sans connexion, le lecteur joue le MP3 de l'exemple ;
- **sur GitHub** : sous chaque figure, un lien 🔊 vers le MP3 et un lien vers le fichier MIDI (à ouvrir dans MuseScore, un séquenceur, etc.).

Pour mettre la version web en ligne gratuitement : dans les réglages du dépôt, **Settings → Pages**, choisir la branche `main` et le dossier `/ (root)`. Le cours sera alors accessible à l'adresse `https://mlevan8395.github.io/Cours-harmonie/`.

## Le cahier d'exercices

À côté du cours, le [cahier d'exercices](cahier/README.md) suit les chapitres un par un : accords séparés (chapitres 1-2), enchaînements (3), premier renversement (6), cadences (7), quarte et sixte (8), phrases plus longues (9), mode mineur (10), choral (13-15), accords de quatre sons (18-21), style classique (24-26), premier romantisme (30-32), romantisme tardif (36-39). Il compte **116 exercices**, dont 22 basses données (avec degrés ou chiffrées), 13 chants donnés, 10 exercices sur le choral (orner une phrase, harmoniser une mélodie) 26 exercices sur les accords de 7e, la 9e, les dominantes secondaires et la modulation, 16 sur la sixte napolitaine, les sixtes augmentées, les pédales et l'écriture pour quatuor, 11 sur les emprunts, le chromatisme et l'écriture pianistique, et 9 sur l'enharmonie, les modulations éloignées et le mélange majeur/mineur, en Do, Sol, Fa et Ré majeur, la, mi, ré et sol mineur. Chaque corrigé est gravé et s'écoute.

Les exercices sont fabriqués par `outils/build_cahier.py` : pour chaque phrase (degrés, états, basse ou mélodie), le générateur (`outils/generateur.py`) calcule une réalisation sans faute, contrôlée par le vérificateur. Pour ajouter un exercice, il suffit d'une ligne dans le catalogue de ce fichier.

## Faire les exercices sur la portée

Dans la version web du cahier (`cahier.html`), et pour les exercices d'écriture du cours (bouton **✏️ Faire l'exercice ici** dans `index.html`), on écrit directement sur la portée, comme dans l'Atelier de contrepoint :

- on choisit la voix à écrire, puis on clique sur la portée pour poser les notes (deux clics sur la même note pour l'altérer ; ▲ ▼ pour déplacer ; clavier possible) ;
- **▶ Écouter** joue la réalisation ;
- la **correction se fait au fil de l'écriture** : à chaque note posée, les fautes apparaissent (colonnes en rouge pour un accord, en orange pour un enchaînement, liste en dessous), avec des conseils (💡) qui ne sont pas des fautes. Une note qui n'appartient pas à l'accord demandé est signalée tout de suite. Pour les chasses aux fautes, la correction attend le bouton **✔ Vérifier** ;
- dans le **cahier d'exercices**, les basses données et les chants donnés sont **guidés pas à pas** : 1) choisir les degrés dans un menu sous chaque accord ; 2) écrire le soprano (basse donnée) ou la basse (chant donné) ; 3) compléter l'alto et le ténor. Chaque étape se débloque quand la précédente est juste ;
- **Voir une solution** (ou **Solution de cette étape**) affiche le corrigé ; **Recommencer** efface.

Le travail de l'élève est gardé dans son navigateur. La correction utilise `outils/verif.js`, traduction exacte du vérificateur Python (testée sur 400 enchaînements tirés au hasard : mêmes fautes, mêmes messages).

## Notation

- Une **note** s'écrit en solfège français : Do, Ré, Mi… Le « Do central » est le Do du milieu du piano (celui de la ligne supplémentaire entre les deux portées).
- Un **accord** s'écrit en lettres : C (Do majeur), Dm (Ré mineur), G7… Les tonalités restent en toutes lettres (« en Do majeur »).
- Les **degrés** s'écrivent en chiffres romains (I, IV, V…).
- Le **chiffrage** est le chiffrage français, écrit sous la basse (5, 6, 6/4, 7…). Le cours donne toujours les deux : degré et chiffrage.
- Les intervalles sont abrégés : 3ce, 5te, 6te, 8ve.

## Les outils

Tous les exemples du cours sont produits par de petits programmes Python :

- `outils/graveur.py` grave les exemples (grande portée SATB, quatuor à cordes avec clé d'ut) ;
- `outils/verif.py` vérifie les règles d'écriture : tessitures, écarts, croisements, doublures selon l'état de l'accord (5, 6, 6/4), quintes et octaves consécutives ou par mouvement contraire, octaves et quintes directes, chevauchements, sensible aux voix extrêmes, seconde augmentée et sauts interdits ;
- `outils/choral.py` reconnaît les notes étrangères (passage, broderie, échappée, anticipation, retard, appoggiature), vérifie l'écriture sur les notes réelles et repère les quintes et octaves créées par une note étrangère ; il sait aussi orner une phrase ;
- `outils/recherche.py` cherche automatiquement des réalisations sans faute : il a servi à préparer et contrôler les corrigés ;
- `outils/audio.py` fabrique le MP3 et le fichier MIDI de chaque exemple ;
- `outils/verif.js` et `outils/atelier.js` font fonctionner les exercices sur la portée (version web) ;
- `outils/build_site.py` construit la version web (`index.html` et `cahier.html`) ;
- `outils/build_app.py` construit l'application (`app/`) ; `outils/donnees_app.py` y prépare les entraînements (accords, fautes et cadences produits par le générateur et contrôlés par le vérificateur) et `outils/quiz_app.py` contient les questions du quiz.

`python3 outils/build_partie1.py`, `build_partie2.py` et `build_partie3.py` regénèrent les figures des trois premières parties (et la musique de chaque exemple) : **chaque exemple « juste » et chaque corrigé passe le vérificateur**, et chaque exemple « faux » contient exactement les fautes annoncées. Le même vérificateur corrige les exercices de l'application.

## Sources

- Les règles suivent la tradition des traités d'harmonie français (Théodore Dubois, *Traité d'harmonie théorique et pratique*, 1921) et la pratique du choral de J.-S. Bach.
- Les sons viennent de la banque General MIDI **FluidR3_GM** (Frank Wen, licence MIT), dans la version « une note par fichier » de Benjamin Gleitzman : [midi-js-soundfonts](https://github.com/gleitz/midi-js-soundfonts) (licence MIT). Pour regénérer les MP3 : récupérer les dossiers `FluidR3_GM/choir_aahs-mp3`, `violin-mp3`, `viola-mp3` et `cello-mp3` de ce dépôt, puis `python3 outils/audio.py CHEMIN/VERS/FluidR3_GM`.
- Les symboles musicaux (clés, altérations) viennent des polices GNU FreeFont (FreeSerif) et DejaVu Sans, comme dans le Cours de contrepoint. La clé d'ut est dessinée à la main.
- Tous les exemples ont été écrits pour ce cours, sauf trois extraits regravés d'après les fichiers MusicXML du [corpus music21](https://github.com/cuthbertLab/music21) (licence BSD, œuvres du domaine public) : le choral BWV 269 de J.-S. Bach (chapitre 14) et le début de l'Adagio du quatuor op. 18 n° 1 de Beethoven (chapitre 27). Les extraits des parties suivantes (Schumann, Fauré, Debussy, Ravel) seront regravés de la même façon.

## Licence

- **Contenu du cours** (textes, images) : [Creative Commons Attribution – Partage dans les mêmes conditions 4.0 (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/deed.fr).
- **Code des outils** : licence MIT (voir [`LICENSE`](LICENSE)).
