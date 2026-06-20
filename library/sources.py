# JuniorEngrTools/library/sources.py
# Curated, maintainable library of core engineering sources and references.
# Includes engineeringtoolbox.com, engineersedge.com style data + standards.
# Self-maintaining: versioned, with BitNet search and update hooks via long-horizon agent.

from ..standards.standards_db import StandardsDatabase

from ..agi_integration.engineering_long_horizon import EngineeringLongHorizon

class SourcesLibrary:
    def __init__(self):
        self.sources = {
            'materials': 'engineeringtoolbox.com + ASTM/ASM/ISO specs (shape-dependent)',
            'calculators': 'MITCalc + custom lean implementations',
            'motion': 'A3 Motion Control program logic + custom',
            'standards': 'Categorized (see standards_db)',
            'references': ['engineeringtoolbox.com', 'engineersedge.com', 'matweb.com (local cache)']
        }
        self.standards = StandardsDatabase()
        self.long_horizon = EngineeringLongHorizon()

    def search(self, query):
        # BitNet semantic + direct
        std_results = self.standards.search(query)
        return {'standards': std_results, 'references': [s for s in self.sources['references'] if query.lower() in s.lower()]}

    def maintain(self):
        # Self-maintenance hook for long-horizon agent (update versions, add new standards)
        plan = self.long_horizon.plan_project({'type': 'library_maintenance', 'action': 'update_standards_and_materials'})
        return plan

    def get_material_example(self):
        return 'AL6061-T6: Yield varies significantly by form (bar ~276 MPa, tube ~241 MPa per ASTM specs) - always check form-specific tables.'