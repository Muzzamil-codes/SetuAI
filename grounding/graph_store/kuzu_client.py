import os
import kuzu
from grounding.graph_store.schema import SCHEMA_STATEMENTS

# Save the database into a file named 'graph.db' inside data/kuzu_store
STORE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "kuzu_store")
)
KUZU_DB_FILE = os.path.join(STORE_DIR, "graph.db")

class KuzuGraphStore:
    def __init__(self, db_file: str = KUZU_DB_FILE):
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        self.db = kuzu.Database(db_file)
        self.conn = kuzu.Connection(self.db)
        self._init_schema()

    def _init_schema(self):
        for stmt in SCHEMA_STATEMENTS:
            try:
                self.conn.execute(stmt)
            except Exception:
                pass  # Tables already created

    def seed_initial_data(self):
        seed_queries = [
            "MERGE (:Unit {name: 'Unit-1', location: 'North Wing'})",
            "MERGE (:Unit {name: 'Unit-2', location: 'South Wing'})",
            "MERGE (:Vendor {name: 'Vendor A', contact: 'sales@vendora.com'})",
            "MERGE (:SOP {code: 'SOP-114', title: 'Unit-2 Valve Specs'})",
            "MERGE (:Equipment {tag: 'Valve V-204', type: 'Pressure Valve'})",
            """
            MATCH (e:Equipment {tag: 'Valve V-204'}), (u:Unit {name: 'Unit-2'})
            MERGE (e)-[:LOCATED_IN]->(u)
            """,
            """
            MATCH (e:Equipment {tag: 'Valve V-204'}), (s:SOP {code: 'SOP-114'})
            MERGE (e)-[:GOVERNED_BY]->(s)
            """
        ]
        for q in seed_queries:
            try:
                self.conn.execute(q)
            except Exception:
                pass

    def query(self, cypher_query: str) -> list[dict]:
        response = self.conn.execute(cypher_query)
        results = []
        while response.has_next():
            results.append(response.get_next())
        return results

if __name__ == "__main__":
    kg = KuzuGraphStore()
    kg.seed_initial_data()
    print("✅ KuzuDB initialized and seeded!")
    res = kg.query("MATCH (e:Equipment)-[:GOVERNED_BY]->(s:SOP) RETURN e.tag, s.code")
    print("Graph Query Result:", res)