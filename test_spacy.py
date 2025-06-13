# test_spacy.py
import spacy

# Charger le modèle français
nlp = spacy.load("fr_core_news_lg")

# Texte de test
text = "Le tribunal administratif a rendu une décision importante concernant le droit des contrats administratifs."

# Traitement du texte
doc = nlp(text)

# Afficher les entités nommées
print("Entités nommées :")
for ent in doc.ents:
    print(f"{ent.text} ({ent.label_})")

# Afficher les lemmes et les parties du discours
print("\nAnalyse morphosyntaxique :")
for token in doc:
    print(f"{token.text:<15} {token.lemma_:<15} {token.pos_:<10} {token.dep_:<10}")