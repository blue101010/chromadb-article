# ChromaDB : Comment une base vectorielle transforme du texte en vecteurs cherchables

**Résumé vulgarisé de l'article technique `article_chromadb.tex`**

---

## En une phrase

ChromaDB est une base de données qui transforme automatiquement des phrases en listes de 384 nombres, puis retrouve les phrases les plus proches d'une question en comparant ces listes entre elles.

---

## 1. Le problème : chercher par le sens, pas par les mots

Quand on tape une recherche classique (comme dans un `CTRL+F`), l'ordinateur cherche des **mots identiques**. Mais si on demande *"Combien de temps pour recevoir mon colis ?"*, il ne trouvera pas la phrase *"La livraison standard prend 3 à 5 jours ouvrés"* parce qu'aucun mot ne correspond exactement.

Les **bases de données vectorielles** comme ChromaDB résolvent ce problème : elles comparent le **sens** des phrases, pas leurs mots exacts.

---

## 2. L'idée centrale : transformer du texte en vecteur

Un **vecteur** (ou *embedding*), c'est simplement une liste de nombres. Par exemple :

```
"Livraison standard en 3-5 jours" → [-0.075, 0.050, 0.014, ..., -0.020]
                                      ← 384 nombres au total →
```

L'astuce : deux phrases qui parlent du **même sujet** produisent des listes de nombres **similaires**. Deux phrases sans rapport produisent des listes très différentes.

---

## 3. Le pipeline en 5 étapes (ce que fait ChromaDB en coulisses)

Quand on écrit `collection.add(documents=["ma phrase"])`, voici ce qui se passe automatiquement :

```
  Texte brut
      ↓
┌─────────────────────────────┐
│ 1. TOKENISATION             │  La phrase est découpée en sous-mots.
│    "shipping" → [6554]      │  Vocabulaire de 30 522 tokens.
│    Ajout de [CLS] et [SEP]  │  Résultat : 256 numéros (avec du padding).
└─────────────┬───────────────┘
              ↓
┌─────────────────────────────┐
│ 2. TRANSFORMEUR (BERT)      │  Le modèle all-MiniLM-L6-v2 (22M paramètres)
│    6 couches, 12 têtes      │  analyse les relations entre chaque mot.
│    d'attention               │  Résultat : une matrice 256 × 384.
└─────────────┬───────────────┘
              ↓
┌─────────────────────────────┐
│ 3. MEAN POOLING             │  On fait la moyenne des 256 vecteurs-mots
│    (moyenne pondérée)        │  en ignorant le padding.
│                              │  Résultat : 1 seul vecteur de 384 nombres.
└─────────────┬───────────────┘
              ↓
┌─────────────────────────────┐
│ 4. NORMALISATION L2         │  On met le vecteur à "longueur 1"
│    (vecteur unitaire)        │  pour que la comparaison soit juste.
└─────────────┬───────────────┘
              ↓
┌─────────────────────────────┐
│ 5. INDEXATION HNSW          │  Le vecteur est rangé dans un graphe
│    (recherche rapide)        │  qui permet de retrouver les voisins
│                              │  en O(log N) au lieu de tout parcourir.
└─────────────────────────────┘
```

### En résumé pour chaque étape :

| Étape | Entrée | Sortie | Analogie du quotidien |
|-------|--------|--------|----------------------|
| **Tokenisation** | `"Livraison standard"` | `[101, 6554, 3115, 102, 0, 0, ...]` | Découper une phrase en syllabes |
| **Transformeur** | 256 numéros de tokens | Matrice 256 × 384 | Chaque mot "regarde" tous les autres pour comprendre le contexte |
| **Mean Pooling** | 256 vecteurs de 384 | 1 vecteur de 384 | Faire la moyenne d'un bulletin de notes |
| **Normalisation** | Vecteur brut | Vecteur de norme 1 | Mettre tout le monde sur la même échelle |
| **Index HNSW** | Vecteur normalisé | Position dans le graphe | Ranger un livre au bon endroit dans une bibliothèque |

---

## 4. Le code complet : 18 lignes pour tout faire

```python
import chromadb
import uuid

# Créer un client en mémoire
client = chromadb.Client()

# Créer une "collection" (l'équivalent d'une table SQL)
collection = client.create_collection(name="policies")

# Lire les phrases depuis un fichier texte
with open("policies.txt", "r", encoding="utf-8") as f:
    policies = f.read().splitlines()

# Ajouter les documents — les embeddings sont calculés automatiquement !
collection.add(
    ids=[str(uuid.uuid4()) for _ in policies],
    documents=policies,
    metadatas=[{"line": i} for i in range(len(policies))],
)

print(collection.peek())  # Voir les 10 premiers enregistrements
```

**Ce que l'utilisateur n'a PAS besoin de faire** : télécharger un modèle, écrire du code de machine learning, configurer un serveur. Tout est automatique.

---

## 5. La recherche sémantique : poser une question

```python
results = collection.query(
    query_texts=["Est-ce que vous livrez à l'étranger ?"],
    n_results=3,
)
```

**Résultat** (les 3 phrases les plus proches par le sens) :

| Distance | Phrase retrouvée |
|----------|-----------------|
| **0.32** | *"International shipping is available to over 200 destinations..."* |
| **0.53** | *"Customers are responsible for any local duties, taxes..."* |
| **0.58** | *"Standard domestic shipping takes 3-5 business days..."* |

Plus la **distance est petite**, plus la phrase est pertinente. ChromaDB utilise la **distance cosinus** : elle mesure l'angle entre deux vecteurs. Deux vecteurs qui pointent dans la même direction (angle ~ 0) ont une distance ~ 0.

---

## 6. Le modèle par défaut : all-MiniLM-L6-v2

| Caractéristique | Valeur |
|-----------------|--------|
| Nom complet | `sentence-transformers/all-MiniLM-L6-v2` |
| Architecture | BERT distillé (6 couches, 12 têtes d'attention) |
| Dimension des embeddings | **384** (nombres `float32`) |
| Vocabulaire | 30 522 tokens (WordPiece) |
| Longueur max en entrée | 256 tokens (~200 mots) |
| Taille du modèle | ~90 Mo (format ONNX) |
| Moteur d'exécution | ONNX Runtime (CPU, pas besoin de GPU) |
| Téléchargement | Automatique au premier lancement, mis en cache dans `~/.cache/chroma/` |

**Pourquoi ONNX ?** C'est un format standard qui permet de faire tourner le modèle sans installer PyTorch (qui pèse >2 Go). ChromaDB reste ainsi léger.

---

## 7. L'index HNSW : comment la recherche est rapide

HNSW (*Hierarchical Navigable Small World*) est un algorithme de recherche approximative qui organise les vecteurs en **graphe multi-couches** :

```
Couche 3 (peu de noeuds):    A ────── D
                              │
Couche 2 :                    A ── B ── D ── F
                              │    │    │
Couche 1 :                    A ── B ── C ── D ── E ── F
                              │    │    │    │    │    │
Couche 0 (tous les noeuds):  A ── B ── C ── D ── E ── F ── G ── H
```

**Pour chercher** : on part du haut (peu de noeuds, vue d'ensemble) et on descend en affinant. C'est comme chercher un pays sur un globe, puis zoomer sur la région, puis la ville.

| Paramètre | Défaut | Rôle |
|-----------|--------|------|
| `space` | cosine | Métrique de distance |
| `ef_construction` | 100 | Précision à la construction |
| `max_neighbors` (M) | 16 | Connexions par noeud |
| `ef_search` | 100 | Précision à la recherche |

**Complexité** : O(log N) par requête au lieu de O(N) en force brute. Pour 1 million de documents, c'est ~20 comparaisons au lieu de 1 000 000.

---

## 8. La similarité cosinus expliquée simplement

Imaginez deux flèches partant du même point :
- Si elles pointent dans la **même direction** → cosinus = 1, distance = 0 → **très similaires**
- Si elles sont **perpendiculaires** → cosinus = 0, distance = 1 → **aucun rapport**
- Si elles pointent en **sens opposé** → cosinus = -1, distance = 2 → **sens contraire**

ChromaDB stocke `distance = 1 - cosinus`. Donc :
- **0.0** = phrases identiques en sens
- **0.3** = phrases très proches (même sujet)
- **0.7** = peu de rapport
- **1.0+** = aucun rapport

---

## 9. Note sur Python 3.14

ChromaDB 1.4.1 ne fonctionne pas directement sur Python 3.14 à cause d'un bug dans la détection de version de Pydantic. Le correctif (inclus dans le dépôt `patch314/`) applique 5 modifications :

1. Remplace l'import `pydantic.v1` par `pydantic-settings`
2. Ajoute les annotations de type manquantes sur 3 champs
3. Convertit la classe `Config` interne en `model_config`
4. Installe la dépendance `pydantic-settings>=2.0`
5. Crée une sauvegarde automatique et vérifie le résultat

```bash
# Appliquer le patch en une commande :
bash patch314/patch.sh
```

---

## 10. Résumé en image mentale

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  VOTRE TEXTE │ ──→ │  384 NOMBRES │ ──→ │  GRAPHE HNSW │
│  (français,  │     │  (le "sens"  │     │  (index pour │
│   anglais,   │     │   du texte   │     │   recherche  │
│   etc.)      │     │   encodé)    │     │   rapide)    │
└──────────────┘     └──────────────┘     └──────────────┘
                                                 │
                     ┌──────────────┐             │
                     │  VOTRE       │ ──→ compare avec l'index
                     │  QUESTION    │     ──→ retourne les 3
                     └──────────────┘         phrases les plus
                                              proches par le sens
```

**L'essentiel** : ChromaDB fait tout le travail complexe (tokenisation, transformeur, normalisation, indexation) derrière un appel aussi simple que `collection.add(documents=[...])`. C'est ce qui le rend accessible aux débutants qui veulent construire des applications RAG sans être experts en machine learning.

---

*Ce résumé accompagne l'article LaTeX complet `article_chromadb.tex` disponible dans le même répertoire.*
