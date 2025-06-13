EXTRACT_ENTITIES_PROMPT = """
**Tâche:** Extrais les informations clés du texte ci-dessous.
**Texte:**
---
{document_content}
---
**Informations à extraire:**
1. `date_decision`: La date de la décision contestée.
2. `date_recours`: La date à laquelle le recours est formé.
3. `demandeur`: Le nom de la personne ou de l'entreprise qui fait la demande.

**Format de réponse:** Réponds UNIQUEMENT avec un objet JSON.
Exemple: {"date_decision": "15 mars 2024", "date_recours": "10 mai 2024", "demandeur": "SARL du Pont"}
Si une information est introuvable, utilise la valeur `null`.
"""

# Ajoutez d'autres prompts selon les besoins