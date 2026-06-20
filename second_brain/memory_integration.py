# JuniorEngrTools/second_brain/memory_integration.py
# Integration of Obsidian memory libraries with SovereignBlackboxBrain.
# Enables inference learning and tool compilation over time.

from ..obsidian_port.memory_libraries import MemoryLibraries

from .sovereign_blackbox_brain import SovereignBlackboxBrain

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryIntegratedBrain:
    def __init__(self):
        self.brain = SovereignBlackboxBrain()
        self.memory = MemoryLibraries()

    def infer_with_memory(self, task_type: str, input_data: Any, context: Dict = None):
        """Blackbox inference augmented with structured memory libraries."""
        # Retrieve relevant memory
        relevant = self.memory.search(str(input_data) if isinstance(input_data, str) else str(context), 
                                      library=context.get("library") if context else None)
        
        # Enrich context
        enriched_context = context or {}
        enriched_context["memory_context"] = relevant
        
        # Run inference
        result = self.brain.infer(task_type, input_data, enriched_context)
        
        # Optionally compile new knowledge
        if task_type in ["agi_orchestrate", "llm_reasoning"]:
            self.memory.compile_tools_over_time(self.brain)
        
        return result

    def learn_from_workflow(self, workflow_name: str, outcome: Dict):
        """Add workflow outcome to memory for future inference."""
        self.memory.add_entry("Workflows", workflow_name, json.dumps(outcome), 
                              {"outcome": outcome.get("status"), "learned": True})