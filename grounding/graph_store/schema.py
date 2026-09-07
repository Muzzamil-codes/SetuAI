SCHEMA_STATEMENTS = [
    # Node Tables: Entities in the factory
    "CREATE NODE TABLE IF NOT EXISTS Unit(name STRING, location STRING, PRIMARY KEY (name))",
    "CREATE NODE TABLE IF NOT EXISTS Equipment(tag STRING, type STRING, PRIMARY KEY (tag))",
    "CREATE NODE TABLE IF NOT EXISTS Vendor(name STRING, contact STRING, PRIMARY KEY (name))",
    "CREATE NODE TABLE IF NOT EXISTS SOP(code STRING, title STRING, PRIMARY KEY (code))",
    
    # Relationship Tables: Connections between entities
    "CREATE REL TABLE IF NOT EXISTS LOCATED_IN(FROM Equipment TO Unit)",
    "CREATE REL TABLE IF NOT EXISTS SUPPLIED_BY(FROM Equipment TO Vendor)",
    "CREATE REL TABLE IF NOT EXISTS GOVERNED_BY(FROM Equipment TO SOP)"
]