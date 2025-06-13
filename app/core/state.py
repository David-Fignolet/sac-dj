from typing import List, Optional, Dict, Any, TypedDict

class CritereAnalysis(TypedDict):
    is_compliant: bool
    reasoning: str
    confidence: float
    source_quote: Optional[str]

class CSPEState(TypedDict):
    # Données initiales
    document_id: str
    document_content: str

    # Extraction
    extracted_dates: Optional[Dict[str, str]]
    extracted_applicant: Optional[str]

    # Analyses
    deadline_analysis: Optional[CritereAnalysis]
    quality_analysis: Optional[CritereAnalysis]
    object_analysis: Optional[CritereAnalysis]
    documents_analysis: Optional[CritereAnalysis]

    # Résultats
    final_classification: Optional[str]
    final_justification: Optional[str]
    final_confidence: Optional[float]
    is_review_required: bool

    # Gestion des erreurs
    error_message: Optional[str]