# Results Example 2 based on french polices.txt

 python main_fr_polices.py 
======================================================================
  ChromaDB — Polices e-commerce en français
  Modèle : paraphrase-multilingual-MiniLM-L12-v2
======================================================================

[1/4] Chargement du modèle 'paraphrase-multilingual-MiniLM-L12-v2'...
      (premier lancement : téléchargement ~470 Mo, patience...)

Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights: 100%|| 199/199 [00:00<00:00, 3782.85it/s, Materializing param=pooler.dense.weight]
BertModel LOAD REPORT from: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
Key                     | Status     |  |
------------------------+------------+--+
embeddings.position_ids | UNEXPECTED |  |

Notes:
- UNEXPECTED    :can be ignored when loading from different task/architecture; not ok if you expect identical arch.
      Modèle chargé en 3.2s

[2/4] Lecture de 'polices.txt'...
      56 polices chargées.

[3/4] Indexation dans ChromaDB...
      56 documents indexés en 0.3s
      Dimension des embeddings : 384
      Métrique de distance : cosine

[4/4] Recherche sémantique (top-5 par requête)

  ┌─ Requête : « Combien de temps prend la livraison ? »
  │
  │  1. [0.3759] ████████████
  │     (ligne  1, livraison)
  │     L’expédition standard nationale prend de 3 à 5 jours ouvrables après le traitement de la c...
  │
  │  2. [0.3973] ████████████
  │     (ligne  9, livraison)
  │     Nous offrons un délai de retour de 30 jours à compter de la date de livraison confirmée pa...
  │
  │  3. [0.4347] ███████████
  │     (ligne  2, livraison)
  │     L’expédition express nationale livre sous 1 à 2 jours ouvrables pour les commandes passées...
  │
  │  4. [0.4660] ██████████
  │     (ligne 17, retours)
  │     Les échanges sont traités dans un délai de 5 jours ouvrables après réception et inspection...
  │
  │  5. [0.5592] ████████
  │     (ligne 22, livraison)
  │     Si un colis est indiqué comme livré mais non reçu, le client doit nous contacter dans les ...
  │
  └────────────────────────────────────────────────────────────────────

  ┌─ Requête : « Est-ce que je peux retourner un maillot de bain ? »
  │
  │  1. [0.4119] ███████████
  │     (ligne 12, retours)
  │     Les maillots de bain ne peuvent être retournés que si les doublures hygiéniques et toutes ...
  │
  │  2. [0.6721] ██████
  │     (ligne 10, retours)
  │     Les articles retournés doivent être non portés, non lavés et exempts d’odeurs, de taches o...
  │
  │  3. [0.7637] ████
  │     (ligne 33, retours)
  │     Les défauts de fabrication signalés dans les 90 jours suivant l’achat peuvent donner droit...
  │
  │  4. [0.7725] ████
  │     (ligne  9, livraison)
  │     Nous offrons un délai de retour de 30 jours à compter de la date de livraison confirmée pa...
  │
  │  5. [0.7996] ████
  │     (ligne 11, livraison)
  │     Les chaussures doivent être retournées dans leur boîte d’origine, elle‑même placée dans un...
  │
  └────────────────────────────────────────────────────────────────────

  ┌─ Requête : « Livrez-vous à l'étranger ? »
  │
  │  1. [0.5872] ████████
  │     (ligne  3, livraison)
  │     La livraison internationale est disponible vers plus de 200 destinations, avec des délais ...
  │
  │  2. [0.7499] █████
  │     (ligne  1, livraison)
  │     L’expédition standard nationale prend de 3 à 5 jours ouvrables après le traitement de la c...
  │
  │  3. [0.8049] ███
  │     (ligne  4, général)
  │     Les clients sont responsables des droits, taxes ou frais d’importation imposés par les aut...
  │
  │  4. [0.8220] ███
  │     (ligne  2, livraison)
  │     L’expédition express nationale livre sous 1 à 2 jours ouvrables pour les commandes passées...
  │
  │  5. [0.8473] ███
  │     (ligne 18, retours)
  │     Les clients peuvent initier un retour ou un échange via le portail en libre‑service access...
  │
  └────────────────────────────────────────────────────────────────────

  ┌─ Requête : « Qu'en est-il des émissions de carbone ? »
  │
  │  1. [0.4412] ███████████
  │     (ligne  7, livraison)
  │     Nous compensons 100 % des émissions de carbone liées à l’expédition en investissant dans d...
  │
  │  2. [0.7637] ████
  │     (ligne  8, environnement)
  │     Les matériaux d’emballage sont fabriqués à partir de papier, carton et encres biodégradabl...
  │
  │  3. [0.8258] ███
  │     (ligne 21, retours)
  │     Nous prenons en charge les frais de retour pour tout article reçu endommagé, défectueux ou...
  │
  │  4. [0.8303] ███
  │     (ligne 34, qualité)
  │     L’usure normale, les dommages accidentels et une mauvaise utilisation ne sont pas considér...
  │
  │  5. [0.8378] ███
  │     (ligne 53, commandes)
  │     Nous pouvons mettre à jour ces politiques périodiquement, et la version en vigueur au mome...
  │
  └────────────────────────────────────────────────────────────────────

  ┌─ Requête : « Comment fonctionne le programme de fidélité ? »
  │
  │  1. [0.5832] ████████
  │     (ligne 47, fidélité)
  │     Nous pouvons modifier ou interrompre le programme de fidélité à tout moment, avec préavis ...
  │
  │  2. [0.5939] ████████
  │     (ligne 48, confidentialité)
  │     Les données personnelles sont traitées conformément à notre politique de confidentialité, ...
  │
  │  3. [0.5956] ████████
  │     (ligne 42, livraison)
  │     Une signature pourra être exigée pour les envois de grande valeur, à notre discrétion, afi...
  │
  │  4. [0.6402] ███████
  │     (ligne 46, retours)
  │     Les points gagnés sur une commande ultérieurement remboursée seront déduits du solde de ré...
  │
  │  5. [0.6438] ███████
  │     (ligne 45, fidélité)
  │     Les points de fidélité, lorsqu’ils sont offerts, sont non transférables et n’ont aucune va...
  │
  └────────────────────────────────────────────────────────────────────

  ┌─ Requête : « Puis-je annuler ma commande ? »
  │
  │  1. [0.4869] ██████████
  │     (ligne 23, commandes)
  │     Les commandes peuvent être annulées dans les 60 minutes suivant leur placement, via la pag...
  │
  │  2. [0.5229] █████████
  │     (ligne 41, livraison)
  │     Si une commande est retournée à l’expéditeur en raison d’une adresse non distribuable, nou...
  │
  │  3. [0.5882] ████████
  │     (ligne 22, livraison)
  │     Si un colis est indiqué comme livré mais non reçu, le client doit nous contacter dans les ...
  │
  │  4. [0.5916] ████████
  │     (ligne 30, commandes)
  │     En cas de retard important d’une précommande, les clients seront avisés et pourront choisi...
  │
  │  5. [0.6082] ███████
  │     (ligne 40, livraison)
  │     Les modifications d’adresse après commande ne sont pas garanties et dépendent des capacité...
  │
  └────────────────────────────────────────────────────────────────────

  ┌─ Requête : « Les articles en solde sont-ils échangeables ? »
  │
  │  1. [0.4123] ███████████
  │     (ligne 10, retours)
  │     Les articles retournés doivent être non portés, non lavés et exempts d’odeurs, de taches o...
  │
  │  2. [0.4890] ██████████
  │     (ligne 16, retours)
  │     Un échange de taille gratuit est permis par commande pour le même article, sous réserve de...
  │
  │  3. [0.5126] █████████
  │     (ligne 27, général)
  │     Nous pouvons limiter la quantité de certains articles par client afin d’assurer un accès é...
  │
  │  4. [0.5248] █████████
  │     (ligne 13, retours)
  │     Les articles en solde finale, y compris les modèles en liquidation et les promotions spéci...
  │
  │  5. [0.5621] ████████
  │     (ligne 35, retours)
  │     Les articles personnalisés ou monogrammés sont fabriqués sur commande et ne peuvent être r...
  │
  └────────────────────────────────────────────────────────────────────

======================================================================
  BONUS — Recherche cross-lingue
  Le modèle multilingue comprend le français ET l'anglais.
  On peut interroger en anglais une base indexée en français !
======================================================================

  ┌─ Query (EN) : « How long does shipping take? »
  │
  │  1. [0.3356] L’expédition standard nationale prend de 3 à 5 jours ouvrables après le traitement de la c...
  │  2. [0.4238] Nous offrons un délai de retour de 30 jours à compter de la date de livraison confirmée pa...
  │  3. [0.4249] L’expédition express nationale livre sous 1 à 2 jours ouvrables pour les commandes passées...
  └────────────────────────────────────────────────────────────────────

  ┌─ Query (EN) : « Can I return swimwear? »
  │
  │  1. [0.5243] Les maillots de bain ne peuvent être retournés que si les doublures hygiéniques et toutes ...
  │  2. [0.7104] Les articles retournés doivent être non portés, non lavés et exempts d’odeurs, de taches o...
  │  3. [0.7357] Nous offrons un délai de retour de 30 jours à compter de la date de livraison confirmée pa...
  └────────────────────────────────────────────────────────────────────

  ┌─ Query (EN) : « What is your carbon offset policy? »
  │
  │  1. [0.4542] Nous compensons 100 % des émissions de carbone liées à l’expédition en investissant dans d...

  ┌─ Query (EN) : « What is your carbon offset policy? »
  │
  │  1. [0.4542] Nous compensons 100 % des émissions de carbone liées à l’expédition en investissant dans d...
  │  2. [0.6586] Nous pouvons mettre à jour ces politiques périodiquement, et la version en vigueur au mome...
  │  3. [0.6924] Les commandes de plus de 75 $ sont admissibles à la livraison standard gratuite dans les r...
  └────────────────────────────────────────────────────────────────────


======================================================================
  Résumé
======================================================================
  Modèle            : paraphrase-multilingual-MiniLM-L12-v2
  Dimension          : 384
  Documents indexés  : 56
  Distance           : cosine
  Chargement modèle  : 3.2s
  Indexation          : 0.3s
  Langue des docs    : français
  Requêtes testées   : 7 FR + 3 EN (cross-lingue)
======================================================================


  ┌─ Query (EN) : « What is your carbon offset policy? »
  │
  │  1. [0.4542] Nous compensons 100 % des émissions de carbone liées à l’expédition en investissant dans d...
  │  2. [0.6586] Nous pouvons mettre à jour ces politiques périodiquement, et la version en vigueur au mome...
  │  3. [0.6924] Les commandes de plus de 75 $ sont admissibles à la livraison standard gratuite dans les r...
  └────────────────────────────────────────────────────────────────────


======================================================================
  Résumé
======================================================================
  Modèle            : paraphrase-multilingual-MiniLM-L12-v2
  Dimension          : 384
  Documents indexés  : 56
  Distance           : cosine
  Chargement modèle  : 3.2s
  Indexation          : 0.3s
  Langue des docs    : français

  ┌─ Query (EN) : « What is your carbon offset policy? »
  │
  │  1. [0.4542] Nous compensons 100 % des émissions de carbone liées à l’expédition en investissant dans d...
  │  2. [0.6586] Nous pouvons mettre à jour ces politiques périodiquement, et la version en vigueur au mome...
  │  3. [0.6924] Les commandes de plus de 75 $ sont admissibles à la livraison standard gratuite dans les r...
  └────────────────────────────────────────────────────────────────────


======================================================================
  Résumé
======================================================================
  Modèle            : paraphrase-multilingual-MiniLM-L12-v2
  Dimension          : 384
  Documents indexés  : 56
  Distance           : cosine

  ┌─ Query (EN) : « What is your carbon offset policy? »
  │
  │  1. [0.4542] Nous compensons 100 % des émissions de carbone liées à l’expédition en investissant dans d...
  │  2. [0.6586] Nous pouvons mettre à jour ces politiques périodiquement, et la version en vigueur au mome...
  │  3. [0.6924] Les commandes de plus de 75 $ sont admissibles à la livraison standard gratuite dans les r...
  └────────────────────────────────────────────────────────────────────


======================================================================
  Résumé
======================================================================
  Modèle            : paraphrase-multilingual-MiniLM-L12-v2

  ┌─ Query (EN) : « What is your carbon offset policy? »
  │
  │  1. [0.4542] Nous compensons 100 % des émissions de carbone liées à l’expédition en investissant dans d...
  │  2. [0.6586] Nous pouvons mettre à jour ces politiques périodiquement, et la version en vigueur au mome...
  │  3. [0.6924] Les commandes de plus de 75 $ sont admissibles à la livraison standard gratuite dans les r...
  └────────────────────────────────────────────────────────────────────


  ┌─ Query (EN) : « What is your carbon offset policy? »
  │
  │  1. [0.4542] Nous compensons 100 % des émissions de carbone liées à l’expédition en investissant dans d...
  │  2. [0.6586] Nous pouvons mettre à jour ces politiques périodiquement, et la version en vigueur au mome...
  │  3. [0.6924] Les commandes de plus de 75 $ sont admissibles à la livraison standard gratuite dans les r...

  ┌─ Query (EN) : « What is your carbon offset policy? »
  │
  │  1. [0.4542] Nous compensons 100 % des émissions de carbone liées à l’expédition en investissant dans d...
  │  2. [0.6586] Nous pouvons mettre à jour ces politiques périodiquement, et la version en vigueur au mome...
  │  3. [0.6924] Les commandes de plus de 75 $ sont admissibles à la livraison standard gratuite dans les r...
  │  1. [0.4542] Nous compensons 100 % des émissions de carbone liées à l’expédition en investissant dans d...
  │  2. [0.6586] Nous pouvons mettre à jour ces politiques périodiquement, et la version en vigueur au mome...
  │  3. [0.6924] Les commandes de plus de 75 $ sont admissibles à la livraison standard gratuite dans les r...
  └────────────────────────────────────────────────────────────────────



======================================================================
  Résumé
======================================================================
  Modèle            : paraphrase-multilingual-MiniLM-L12-v2
  Dimension          : 384
  Documents indexés  : 56
  Distance           : cosine
  Chargement modèle  : 3.2s
  Indexation          : 0.3s
  Langue des docs    : français
  Requêtes testées   : 7 FR + 3 EN (cross-lingue)
