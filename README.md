# Les Rieurs de Deauville
### *ou le Festival du Rire, roman en Python*

> « Le rire est le soleil qui chasse l'hiver du visage humain. »
> Et le code est la nuit studieuse qui prépare ce soleil.

## Livre premier : Ce que c'est que ce projet

C'était en juin 1827… non, en juin **2027**, du dix au treize, sur cette côte
normande où la mer, éternelle et grise, regarde rire les hommes. Deauville
attendait son festival. Les planches attendaient les pas. Les salles
attendaient les foules. Et derrière le site, derrière l'admin, derrière ces
pages que d'autres mains avaient déjà tissées, il manquait une chose,
la plus humble et la plus grande : **un cœur**. Ce cœur, c'est ce backend.

Il y a ici un modèle, qui est la loi ; un stockage, qui est la mémoire ;
une ligne de commande, qui est la voix ; et un serveur web, qui est la place
publique où le peuple vient lire le programme.

## Livre deuxième : De l'installation, ou comment l'on entre dans l'œuvre

Il faut d'abord [uv](https://docs.astral.sh/uv/). Celui qui n'a point uv
est comme le voyageur sans lanterne : il marche, mais il ne voit pas.

```bash
git clone https://github.com/Nourkarim69/deauville-starter.git
cd deauville-starter
uv sync
```

Trois lignes. Trois coups frappés à la porte. Et la porte s'ouvre.

## Livre troisième : La voix, ou la ligne de commande

Interrogez le festival, il vous répondra.

```bash
uv run main.py programme 2027-06-11              # le programme d'un jour
uv run main.py artists                           # les artistes et leur nombre de spectacles
uv run main.py now --at 2027-06-11T21:00         # ce qui se joue, et les trois qui suivent
```

Et voyez ce prodige : le spectacle de une heure du matin, le douze, appartient
au onze. Car **une journée du festival ne meurt qu'à six heures**. La nuit
n'est pas la fin du jour ; elle en est le dernier soupir.

## Livre quatrième : La place publique, ou le serveur web

```bash
uv run uvicorn festival.api:app --reload
```

Alors s'ouvrent les trois portes de la cité :
- http://127.0.0.1:8000, le site, où le peuple lit ;
- http://127.0.0.1:8000/admin/, l'admin, où l'organisateur décide ;
- http://127.0.0.1:8000/docs, la documentation, où le curieux comprend.

## Livre cinquième : Les épreuves

```bash
uv run pytest
uvx ruff check .
uvx ruff format --check .
uv build
```

Cinquante-huit tests. Cinquante-huit sentinelles qui veillent dans l'ombre.
Que l'une tombe, et le développeur est averti. Le code sans tests est une
ville sans remparts.

## Livre sixième : La cité, ou la structure

```
festival/
├── errors.py       les malheurs, nommés et classés
├── text.py         slugify, qui ôte aux noms leurs accents comme l'exil ôte aux hommes leur patrie
├── venue.py        Venue, la salle, qui a des murs et des places
├── artist.py       Artist, l'artiste, qui a un nom et une âme
├── performance.py  Performance (abstraite), Solo, Lineup, Workshop
├── festival.py     Festival, qui rassemble tout et juge les conflits
├── storage.py      Storage (abstraite) et JsonStorage, la mémoire
├── cli.py          la voix
└── api.py          la place publique
tests/              les sentinelles
```

## Livre septième : Les choix, ou la conscience de l'auteur

**Quels sont les êtres de ce monde, et que gardent-ils ?**
Chaque objet est gardien de lui-même. `Venue`, `Artist` et les spectacles
vérifient leurs propres lois dans leur constructeur : un nom vide, une salle
sans place, une durée hors de un à trois cent soixante minutes, et l'objet
refuse de naître. Ce qui n'est pas juste n'existe pas. Leurs attributs sont
privés, et les `@property` sont des fenêtres et non des portes : on regarde,
on ne touche pas. Telle est l'**encapsulation**.

**Ce que les spectacles ont en commun, et ce qui les sépare.**
Il y a des pères et des fils. `Performance` est le père, et le père est
**abstrait** : il n'existe pas seul, il n'existe que dans ses enfants. Il leur
lègue le titre, la salle, l'heure, la durée, et ces vérités qui se calculent
au lieu de se stocker : `end`, `id`, `festival_day`, `capacity`. Il leur
impose deux devoirs, `kind` et `artists()`, et nul fils ne peut vivre sans
les accomplir. `Solo` est l'homme seul face à la foule. `Lineup` est la
procession, un présentateur et ses artistes, chacun dix minutes, et trois
minutes entre eux pour respirer. `Workshop` est l'école. Tous appellent
`super().__init__()`, comme on honore son père ; tous ajoutent leurs propres
lois. Et `Workshop` répond à sa manière à `capacity`, car une école de douze
élèves dans une cabane de trois places n'a que trois places : c'est le
**polymorphisme**, ou l'art de répondre chacun selon sa nature à la même
question.

**Où vit la loi, pour que nul ne l'élude ?**
Dans `Festival._check`. C'est là que se jugent les conflits : la salle
occupée, l'artiste qui ne peut être en deux lieux à la fois, la date qui fuit
hors du festival, le nom que nul ne connaît. Trente minutes, dit la loi, entre
deux spectacles d'une même salle ; trente minutes entre deux apparitions d'un
même artiste. La ligne de commande, l'API, le chargement du fichier, tous
passent par ce tribunal. Et la sentence est sans appel mais sans dommage :
**une modification refusée ne change rien**, car on juge avant d'agir.

**Comment sait-on quelle loi fut brisée ?**
Les malheurs ont une famille. `FestivalError` est l'aïeule ; ses enfants sont
`NotFoundError`, l'absence ; `ConflictError`, la discorde ;
`InvalidValueError`, l'erreur ; `StorageError`, l'oubli. Chacun parle la
langue de l'organisateur et non celle de la machine. La ligne de commande dit
le message ; l'API le traduit en nombres : 404, 409, 422, 500.

**Et si demain la mémoire changeait de demeure ?**
Si le fichier JSON cédait la place à une base de données, un seul fichier
tremblerait : `storage.py`. `Storage` est abstraite, comme une promesse ;
il suffirait d'un `SqliteStorage` pour la tenir autrement. Le modèle, lui, ne
saurait même pas que le monde a changé.

## Livre huitième : Ce qui est accompli

- le modèle tout entier, et toutes les lois de la consigne ;
- la mémoire qui se relit en revérifiant chaque loi, et qui s'écrit après chaque changement ;
- les trois commandes de la voix ;
- toutes les routes d'`API.md`, le site et l'admin ;
- cinquante-huit tests, `ruff` satisfait, `uv build` triomphant.

## Livre neuvième : Ce qui reste dans l'ombre

- l'extension SQLite, qui attend son heure (la classe `Storage` lui a préparé la place) ;
- les docstrings, qui ne sont pas encore partout.

L'œuvre n'est jamais finie ; elle est seulement rendue.

## Épilogue : Des compagnons de route

Nul ne marche seul. J'ai cheminé avec Claude, une intelligence artificielle,
qui m'a expliqué Git, GitHub et les mystères de la programmation orientée
objet, et qui m'a aidé à écrire et à relire ce code. Je le dis, car la vérité
est la première des lois.

---

*Fait à ECPROUT, en octobre 2026, sous un ciel gris qui rêvait de Deauville.*