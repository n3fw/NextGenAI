# Rapport d'Évaluation Benchmark Text-to-SQL — Modèle Qwen 3.8 27B (Groq)

## 1. Contexte et Objectifs

L'objectif de cette étude est d'évaluer les performances du modèle de langage **`qwen/qwen3.8-27b`** hébergé sur la plateforme **Groq** dans le cadre du TD1. Le modèle est soumis à une suite de **20 requêtes de test** (numérotées de **C01 à C20**) visant à générer des requêtes SQL SQLite d'agrégation de chiffre d'affaires (HT) sur la base de données `boutique.sqlite`.

L'analyse repose sur le croisement de deux jeux de données :
* `traces-D.csv` : Les traces réelles d'exécution de l'API (contient les requêtes envoyées, les codes HTTP, le temps de réponse, les tokens, les requêtes SQL et la valeur calculée par le modèle).
* `model-question-comparison-en-D.csv` : Le fichier synthétique de comparaison des résultats par rapport aux valeurs de référence (`reference_cents`).

---

## 2. Synthèse Globale des Performances

### Statistiques clés (Traces réelles)

* **Nombre de cas de test :** 20 (C01 à C20)
* **Nombre total de tentatives d'appel API :** 23
* **Requêtes SQL VALIDES et CORRECTES (`correct`) :** **15 / 20 (75 %)**
* **Requêtes SQL Invalides (`sql_invalid`) :** **1 / 20 (5 %)** (Erreur de syntaxe SQLite)
* **Requêtes exécutées mais avec résultat INCORRECT (`incorrect`) :** **3 / 20 (15 %)** (Erreur de logique)
* **Requêtes Non Exécutées (`not_executed`) :** **1 / 20 (5 %)** (Bloquées par Rate Limit HTTP 429)

---

## 3. Analyse par Catégorie de Critères

Les requêtes ont été classées selon les dimensions de filtrage qu'elles sollicitent : **Période (dates)**, **Âge des clients**, et **Types de produits**.

| Catégorie | Requêtes concernées | Succès (`correct`) | Échecs | Taux de réussite |
| :--- | :--- | :--- | :--- | :--- |
| **Période seule** | C01, C04, C05, C06, C07, C20 | **6 / 6** | 0 | **100 %** |
| **Âge seul** | C02, C08, C09, C10, C11 | **4 / 5** | C10 (`sql_invalid`) | **80 %** |
| **Produit seul** | C12 | **1 / 1** | 0 | **100 %** |
| **Période + Produits** | C03, C13, C14 | **3 / 3** | 0 | **100 %** |
| **Période + Âge** | C15, C18 | **1 / 2** | C15 (`incorrect`) | **50 %** |
| **Produits + Âge** | C16 | **0 / 1** | C16 (`not_executed` HTTP 429) | **0 %** |
| **Période + Produits + Âge** | C17, C19 | **0 / 2** | C17 (`incorrect`), C19 (`incorrect`) | **0 %** |

---

## 4. Analyse Approfondie des Erreurs et Faiblesses

### 4.1. Erreurs de Syntaxe SQL (`sql_invalid`)
* **Cas C10** (*Âge du client au moment de la commande*) :
  * **Problème :** Le modèle a commis une faute de frappe dans le nom de la fonction SQLite, générant `COALESE(...)` au lieu de `COALESCE(...)`.
  * **Conséquence :** L'exécution SQLite a échoué avec `runtime_error: no such function: COALESE`.

### 4.2. Erreurs de Logique Métier (`incorrect`)
* **Cas C15, C17, C19** (*Combinaisons complexes d'âge et de période*) :
  * **Problème :** Dès que la requête combine la vérification de l'âge (ex: 25 ans à une date de référence) avec des contraintes d'intervalles de dates et/ou de produits, le modèle échoue dans la construction des clauses `WHERE` booléennes complexes (gestion des années de naissance bissextiles ou chevauchements de dates avec `strftime`).
  * **Cas C15 :** Résultat calculé `0` au lieu de `168 680` euro cents.
  * **Cas C17 :** Résultat calculé `248 490` au lieu de `258 180` euro cents.
  * **Cas C19 :** Résultat calculé `83 580` au lieu de `1 990` euro cents.

### 4.3. Contraintes d'Infrastructure et Rate Limits (`HTTP 429`)
* **Problème :** L'offre gratuite sur Groq fixe un plafond strict de **1 000 tokens de sortie par minute (OTPM)**.
* **Impact sur le Benchmark :**
  * **C16 :** Échec systématique après 2 tentatives (`HTTP 429: Rate limit reached`).
  * **C18 & C19 :** La première tentative a échoué en `HTTP 429`. Une seconde tentative automatique a permis d'exécuter la requête.

---

## 5. Audit des Anomales / Écarts de Données (`traces-D.csv` vs `model-question-comparison-en-D.csv`)

L'analyse croisée des deux fichiers a permis de déceler plusieurs incohérences dans le fichier de synthèse `model-question-comparison-en-D.csv` :

1. **Inversion C10 / C11 :** Dans le fichier de comparaison, C10 est noté `correct` et C11 est noté `sql_invalid` (`COALESE`), alors que les traces réelles montrent exactement l'inverse (C10 a échoué sur `COALESE` et C11 a réussi).
2. **Valeur brute de C02 :** Dans `model-question-comparison-en-D.csv`, la colonne `value_cents` indique `0` alors que le statut est `correct` et que la trace réelle indique bien `590320`.
3. **Faux positif sur C16 :** C16 est noté `correct` dans le fichier de comparaison alors que la trace confirme que le modèle n'a jamais pu exécuter la requête en raison du Rate Limit `HTTP 429`.
4. **Validation de C20 :** C20 est marqué `incorrect` dans le fichier de comparaison, mais la trace d'exécution confirme un statut `correct` avec la valeur exacte `1 106 090`.

---

## 6. Recommandations et Perspectives

1. **System Prompt & Anti-Typo :** Injecter une règle explicite dans le prompt du modèle pour la syntaxe des fonctions SQLite (`COALESCE`).
2. **Gestion de la Température / Retry :** Activer un délai d'attente (backoff exponentiel) pour contourner le plafond de 1 000 OTPM sur Groq.
3. **Inférence sur la logique temporelle :** Pour les calculs d'âge complexes, enrichir le prompt avec des exemples de formules SQLite éprouvées (`date(c.birth_date, '+25 years')`).
