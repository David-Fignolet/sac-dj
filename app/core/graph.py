from langgraph.graph import StateGraph
from .state import CSPEState
from .nodes import extract_entities

def create_workflow():
    workflow = StateGraph(CSPEState)
    
    # Ajout des nœuds
    workflow.add_node("extract_entities", extract_entities)
    # Ajoutez d'autres nœuds ici
    
    # Configuration du flux
    workflow.set_entry_point("extract_entities")
    # Définissez les connexions entre les nœuds
    # workflow.add_edge("extract_entities", "next_node")
    
    return workflow.compile()

# Instance du graphe compilé
agent_workflow = create_workflow()