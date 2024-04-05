# Variables d'environnement
NO_DB_DUMP (default FALSE):
if not already existing, preview will be mounted without dump from prod instance, but with demo datas

MODULES_WITHOUT_DEMO (Optionnel) :
list of modules for --without-demo option (modules that will be loaded without demo data)

NESTOR_NAME_PREFIX (Optionnel) :
Le nom et l'url de la preview commenceront par cette variable si présente. Ceci permet de différencier les preview de 2 projets (par exemple core et filiale) qui utilisent la même branche.

NESTOR_NAME (Optionnel) :
Le nom de la previews et son url utiliseront cette variable à la place du nom de la branche

ENABLE_QUEUE_JOB (Optionnel) :
Les jobs sont activés si True. Charge le server_wide module queue_job, community doit être en dépendance 

ALWAYS_DELETE (Optionnel) :
Si True, l'instance est supprimée et recrée à chaque preview up

ALWAYS_RESTORE (Optionnel) :
Si True, la base est restaurée à chaque preview up, même si l'instance existe déjà

# Dev interaction

### déploiement
Penser à changer la version dans le `setup.cfg` pour que le pipeline de deploy se lance
### lancement en local pour tester le mode interactif :
`python -m pynestor preview --interactive --up`
