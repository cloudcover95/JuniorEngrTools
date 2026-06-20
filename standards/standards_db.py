# JuniorEngrTools/standards/standards_db.py
# Categorized standards with BitNet semantic search.

class StandardsDatabase:
    def __init__(self):
        self.db = {
            'pressure_vessels': ['API 650', 'ASME BPVC'],
            'aerospace_structures': ['MMPDS', 'MIL-HDBK-5'],
            'quality_systems': ['ISO 9001', 'GMP'],
            'maritime_offshore': ['LR Rules', 'DNV GL', 'BV Rules'],
            'general_mechanical': ['ISO', 'ANSI', 'ASTM', 'ASME'],
            'piping': ['ASME B31.3', 'API 570']
        }

    def search(self, query):
        results = []
        for cat, standards in self.db.items():
            if query.lower() in cat.lower() or any(query.lower() in s.lower() for s in standards):
                results.extend(standards)
        return list(set(results)) or ['Consult relevant ISO/ANSI for application']