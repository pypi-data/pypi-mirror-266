

from sqlalchemy.dialects import registry

registry.register("chipmunkdb", "chipmunkdb.jdbc", "ChipmunkdbDialect_jdbc")
