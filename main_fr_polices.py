"""
main_fr_polices.py — ChromaDB avec des polices e-commerce en français
Utilise le modèle multilingue paraphrase-multilingual-MiniLM-L12-v2
au lieu du modèle anglais par défaut (all-MiniLM-L6-v2).

Prérequis :
    pip install chromadb sentence-transformers

Le modèle (~470 Mo) est téléchargé automatiquement au premier lancement
et mis en cache dans ~/.cache/torch/sentence_transformers/
"""

import subprocess
import sys
import os
import time
import uuid

# Force UTF-8 sur la console Windows (sinon cp1252 tronque les accents/box-drawing)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

# ═══════════════════════════════════════════════════════════════════════════
#  Auto-installation des dépendances manquantes
# ═══════════════════════════════════════════════════════════════════════════

REQUIREMENTS = [
    ("chromadb", "chromadb"),
    ("sentence_transformers", "sentence-transformers"),
]

for module_name, pip_name in REQUIREMENTS:
    try:
        __import__(module_name)
    except ImportError:
        print(f"[auto-install] '{pip_name}' manquant, installation...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pip_name],
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

import chromadb


# ═══════════════════════════════════════════════════════════════════════════
#  Fonction utilitaire : catégorisation simple par mots-clés
# ═══════════════════════════════════════════════════════════════════════════

def _categorize(text: str) -> str:
    """Catégorise une police par mots-clés simples (pour les métadonnées)."""
    t = text.lower()
    if any(w in t for w in ["livraison", "expédition", "envoi", "colis", "transporteur"]):
        return "livraison"
    if any(w in t for w in ["retour", "rembours", "échange"]):
        return "retours"
    if any(w in t for w in ["prix", "dollar", "promo", "rabais", "code"]):
        return "tarification"
    if any(w in t for w in ["fidélité", "points", "récompense"]):
        return "fidélité"
    if any(w in t for w in ["donnée", "confidentialité", "courriel", "marketing"]):
        return "confidentialité"
    if any(w in t for w in ["défaut", "garantie", "qualité", "entretien"]):
        return "qualité"
    if any(w in t for w in ["annul", "commande", "paiement", "fraude"]):
        return "commandes"
    if any(w in t for w in ["carbone", "emballage", "recyclé", "durable"]):
        return "environnement"
    return "général"


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  1. CONFIGURATION                                                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# -- Modèle multilingue (50+ langues dont le français) --------------------
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
# Alternatives :
#   "paraphrase-multilingual-mpnet-base-v2"   → 768 dim, plus précis, plus lent
#   "distiluse-base-multilingual-cased-v2"    → 512 dim, léger

# -- Fichier de polices --------------------------------------------------
POLICES_FILE = "polices.txt"

# -- Métrique de distance -------------------------------------------------
#   "cosine" (défaut)  : mesure l'angle entre vecteurs, insensible à la norme
#   "l2"               : distance euclidienne
#   "ip"               : produit scalaire (inner product)
DISTANCE_METRIC = "cosine"

# -- Nombre de résultats par requête --------------------------------------
TOP_K = 5


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  2. CRÉATION DE L'EMBEDDING FUNCTION MULTILINGUE                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def main():
    print(f"{'='*70}")
    print(f"  ChromaDB — Polices e-commerce en français")
    print(f"  Modèle : {MODEL_NAME}")
    print(f"{'='*70}\n")

    from chromadb.utils.embedding_functions import (
        SentenceTransformerEmbeddingFunction,
    )

    # -- Instancier la fonction d'embedding -------------------------------
    # Le modèle est téléchargé automatiquement au premier appel (~470 Mo).
    # Les appels suivants utilisent le cache local.
    print(f"[1/4] Chargement du modèle '{MODEL_NAME}'...")
    print(f"      (premier lancement : téléchargement ~470 Mo, patience...)\n")

    t0 = time.time()
    embedding_fn = SentenceTransformerEmbeddingFunction(
        model_name=MODEL_NAME,
        # device="cuda"  # Décommenter pour utiliser un GPU NVIDIA
    )
    t_model = time.time() - t0
    print(f"      Modèle chargé en {t_model:.1f}s\n")

    # ╔══════════════════════════════════════════════════════════════════════╗
    # ║  3. LECTURE DES POLICES FRANÇAISES                                 ║
    # ╚══════════════════════════════════════════════════════════════════════╝

    print(f"[2/4] Lecture de '{POLICES_FILE}'...")

    if not os.path.isfile(POLICES_FILE):
        print(f"ERREUR : fichier '{POLICES_FILE}' introuvable.")
        print(f"         Assurez-vous qu'il existe dans : {os.getcwd()}")
        sys.exit(1)

    with open(POLICES_FILE, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    # Filtrer les lignes vides et la ligne d'en-tête (si présente)
    polices = [line.strip() for line in lines if line.strip()]
    # Retirer la première ligne si c'est un en-tête de traduction
    if polices and polices[0].lower().startswith("voici une traduction"):
        header = polices.pop(0)
        print(f"      (en-tête ignoré : '{header[:50]}...')")

    print(f"      {len(polices)} polices chargées.\n")

    # ╔══════════════════════════════════════════════════════════════════════╗
    # ║  4. INDEXATION DANS CHROMADB                                       ║
    # ╚══════════════════════════════════════════════════════════════════════╝

    print("[3/4] Indexation dans ChromaDB...")

    # Créer un client en mémoire (éphémère)
    # Pour persister sur disque : chromadb.PersistentClient(path="./chroma_db")
    client = chromadb.Client()

    # Créer la collection avec notre fonction d'embedding multilingue
    collection = client.create_collection(
        name="polices_fr",
        embedding_function=embedding_fn,
        metadata={"hnsw:space": DISTANCE_METRIC},
    )

    # Générer les IDs et métadonnées
    ids = [str(uuid.uuid4()) for _ in polices]
    metadatas = [
        {
            "ligne": i,
            "categorie": _categorize(doc),
            "langue": "fr",
        }
        for i, doc in enumerate(polices)
    ]

    t0 = time.time()
    collection.add(
        ids=ids,
        documents=polices,
        metadatas=metadatas,
    )
    t_index = time.time() - t0

    print(f"      {len(polices)} documents indexés en {t_index:.1f}s")
    peek = collection.peek(1)
    embed_dim = peek["embeddings"].shape[1] if hasattr(peek["embeddings"], "shape") else len(peek["embeddings"][0])
    print(f"      Dimension des embeddings : {embed_dim}")
    print(f"      Métrique de distance : {DISTANCE_METRIC}\n")

    # ╔══════════════════════════════════════════════════════════════════════╗
    # ║  5. REQUÊTES SÉMANTIQUES EN FRANÇAIS                               ║
    # ╚══════════════════════════════════════════════════════════════════════╝

    print(f"[4/4] Recherche sémantique (top-{TOP_K} par requête)\n")

    requetes = [
        "Combien de temps prend la livraison ?",
        "Est-ce que je peux retourner un maillot de bain ?",
        "Livrez-vous à l'étranger ?",
        "Qu'en est-il des émissions de carbone ?",
        "Comment fonctionne le programme de fidélité ?",
        "Puis-je annuler ma commande ?",
        "Les articles en solde sont-ils échangeables ?",
    ]

    for query in requetes:
        results = collection.query(
            query_texts=[query],
            n_results=TOP_K,
        )

        print(f"  ┌─ Requête : « {query} »")
        print(f"  │")

        for rank, (doc, dist, meta) in enumerate(
            zip(
                results["documents"][0],
                results["distances"][0],
                results["metadatas"][0],
            ),
            start=1,
        ):
            # Tronquer l'affichage à 90 caractères
            doc_short = doc[:90] + "..." if len(doc) > 90 else doc
            bar = "█" * int((1 - dist) * 20)  # barre de pertinence visuelle
            print(f"  │  {rank}. [{dist:.4f}] {bar}")
            print(f"  │     (ligne {meta['ligne']:>2}, {meta['categorie']})")
            print(f"  │     {doc_short}")
            print(f"  │")

        print(f"  └{'─'*68}\n")

    # ╔══════════════════════════════════════════════════════════════════════╗
    # ║  6. BONUS : RECHERCHE CROSS-LINGUE (EN → FR)                       ║
    # ╚══════════════════════════════════════════════════════════════════════╝

    print(f"{'='*70}")
    print("  BONUS — Recherche cross-lingue")
    print(f"  Le modèle multilingue comprend le français ET l'anglais.")
    print(f"  On peut interroger en anglais une base indexée en français !")
    print(f"{'='*70}\n")

    requetes_en = [
        "How long does shipping take?",
        "Can I return swimwear?",
        "What is your carbon offset policy?",
    ]

    for query in requetes_en:
        results = collection.query(
            query_texts=[query],
            n_results=3,
        )

        print(f"  ┌─ Query (EN) : « {query} »")
        print(f"  │")

        for rank, (doc, dist) in enumerate(
            zip(results["documents"][0], results["distances"][0]),
            start=1,
        ):
            doc_short = doc[:90] + "..." if len(doc) > 90 else doc
            print(f"  │  {rank}. [{dist:.4f}] {doc_short}")

        print(f"  └{'─'*68}\n")

    # ╔══════════════════════════════════════════════════════════════════════╗
    # ║  7. STATISTIQUES FINALES                                           ║
    # ╚══════════════════════════════════════════════════════════════════════╝

    print(f"\n{'='*70}")
    print(f"  Résumé")
    print(f"{'='*70}")
    print(f"  Modèle            : {MODEL_NAME}")
    print(f"  Dimension          : {embed_dim}")
    print(f"  Documents indexés  : {collection.count()}")
    print(f"  Distance           : {DISTANCE_METRIC}")
    print(f"  Chargement modèle  : {t_model:.1f}s")
    print(f"  Indexation          : {t_index:.1f}s")
    print(f"  Langue des docs    : français")
    print(f"  Requêtes testées   : {len(requetes)} FR + {len(requetes_en)} EN (cross-lingue)")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
