from motor.motor_asyncio import AsyncIOMotorClient
from mongomock_motor import AsyncMongoMockClient
try:
    from app.config import settings
except ModuleNotFoundError:
    from backend.app.config import settings

try:
    from app.auth.password import get_password_hash
except ModuleNotFoundError:
    from backend.app.auth.password import get_password_hash

from datetime import datetime
import logging
import sqlite3
import json
import os
from bson import ObjectId

logger = logging.getLogger(__name__)

# JSON Helpers for BSON/DateTime types
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return {"$date": obj.isoformat()}
        if isinstance(obj, ObjectId):
            return {"$oid": str(obj)}
        return super().default(obj)

def json_deserial(dct):
    if "$date" in dct:
        return datetime.fromisoformat(dct["$date"])
    if "$oid" in dct:
        return ObjectId(dct["$oid"])
    return dct

def parse_mongo_json(json_str):
    return json.loads(json_str, object_hook=json_deserial)

def mongo_json_dumps(obj):
    return json.dumps(obj, cls=MongoJSONEncoder)

class MongoDB:
    client = None
    db = None

db = MongoDB()

def get_sqlite_path():
    # SQLite file path in the project root directory (4 levels up from backend/app/db/mongo.py)
    path = os.path.abspath(__file__)
    for _ in range(4):
        path = os.path.dirname(path)
    return os.path.join(path, "database.db")

async def sync_to_sqlite():
    try:
        sqlite_path = get_sqlite_path()
        logger.info(f"Syncing MongoDB to SQLite database at {sqlite_path}...")
        
        # Open connection
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        # Prepare system settings
        cursor.execute("PRAGMA journal_mode=WAL;")
        
        # Create key-value table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mongo_collections (
                collection_name TEXT,
                doc_id TEXT,
                doc_json TEXT,
                PRIMARY KEY (collection_name, doc_id)
            );
        """)
        
        cols = await db.db.list_collection_names()
        
        for col_name in cols:
            # Query all documents in the collection
            cursor_mongo = db.db[col_name].find({})
            docs = []
            async for doc in cursor_mongo:
                docs.append(doc)
            
            # 1. Update the master JSON table for reloading
            for doc in docs:
                doc_id = str(doc.get("_id"))
                doc_json = mongo_json_dumps(doc)
                cursor.execute(
                    "INSERT OR REPLACE INTO mongo_collections (collection_name, doc_id, doc_json) VALUES (?, ?, ?);",
                    (col_name, doc_id, doc_json)
                )
            
            # Delete any docs in SQLite that were deleted in memory Mongo
            if docs:
                current_ids = [str(d.get("_id")) for d in docs]
                placeholders = ", ".join(["?"] * len(current_ids))
                cursor.execute(
                    f"DELETE FROM mongo_collections WHERE collection_name = ? AND doc_id NOT IN ({placeholders});",
                    [col_name] + current_ids
                )
            else:
                cursor.execute("DELETE FROM mongo_collections WHERE collection_name = ?;", (col_name,))

            # 2. Create/update standard tables for SQLite Viewer
            if not docs:
                cursor.execute(f"DROP TABLE IF EXISTS \"{col_name}\";")
                continue
                
            keys = set()
            for doc in docs:
                for k in doc.keys():
                    keys.add(k)
            
            columns = list(keys)
            if "_id" in columns:
                columns.remove("_id")
                columns.insert(0, "_id")
                
            col_defs = []
            for col in columns:
                col_type = "TEXT"
                sample_val = None
                for doc in docs:
                    if doc.get(col) is not None:
                        sample_val = doc.get(col)
                        break
                
                if isinstance(sample_val, int):
                    col_type = "INTEGER"
                elif isinstance(sample_val, float):
                    col_type = "REAL"
                
                if col == "_id":
                    col_defs.append(f"\"{col}\" TEXT PRIMARY KEY")
                else:
                    col_defs.append(f"\"{col}\" {col_type}")
            
            col_defs_str = ", ".join(col_defs)
            cursor.execute(f"DROP TABLE IF EXISTS \"{col_name}\";")
            cursor.execute(f"CREATE TABLE \"{col_name}\" ({col_defs_str});")
            
            for doc in docs:
                vals = []
                for col in columns:
                    val = doc.get(col)
                    if isinstance(val, (dict, list)):
                        vals.append(mongo_json_dumps(val))
                    elif isinstance(val, datetime):
                        vals.append(val.isoformat())
                    elif isinstance(val, ObjectId):
                        vals.append(str(val))
                    else:
                        vals.append(val)
                
                placeholders = ", ".join(["?"] * len(columns))
                col_names_str = ", ".join([f"\"{c}\"" for c in columns])
                cursor.execute(f"INSERT INTO \"{col_name}\" ({col_names_str}) VALUES ({placeholders});", vals)
                
        conn.commit()
        conn.close()
        logger.info("SQLite synchronization complete.")
    except Exception as e:
        logger.error(f"Error syncing to SQLite: {e}", exc_info=True)

async def load_from_sqlite():
    sqlite_path = get_sqlite_path()
    if not os.path.exists(sqlite_path):
        logger.info("No SQLite database found to load.")
        return False
        
    logger.info(f"Loading data from SQLite database at {sqlite_path}...")
    try:
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mongo_collections';")
        if not cursor.fetchone():
            logger.info("mongo_collections table does not exist in SQLite yet.")
            conn.close()
            return False
            
        cursor.execute("SELECT collection_name, doc_json FROM mongo_collections;")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            logger.info("No documents found in SQLite mongo_collections table.")
            return False
            
        from collections import defaultdict
        col_docs = defaultdict(list)
        for col_name, doc_json in rows:
            col_docs[col_name].append(parse_mongo_json(doc_json))
            
        for col_name, docs in col_docs.items():
            await db.db[col_name].delete_many({})
            if docs:
                await db.db[col_name].insert_many(docs)
                logger.info(f"Successfully loaded {len(docs)} documents into collection '{col_name}' from SQLite.")
        return True
    except Exception as e:
        logger.error(f"Error loading database from SQLite: {e}", exc_info=True)
        return False

async def connect_to_mongo():
    logger.info("Initializing MongoDB connection...")
    try:
        from mongomock_motor import AsyncMongoMockClient
        db.client = AsyncMongoMockClient()
        db.db = db.client[settings.MONGO_DB_NAME]
        logger.info("Using mongomock_motor for local development")
    except Exception as exc:
        logger.error("Failed to initialize database: %s", exc)
        raise

    loaded = await load_from_sqlite()

    cols = await db.db.list_collection_names()
    seeded = False

    if "users" not in cols or not loaded:
        # Check if users actually empty
        user_count = await db.db.users.count_documents({})
        if user_count == 0:
            await db.db.users.insert_one({
                "email": "admin@nexus.ai",
                "password_hash": get_password_hash("admin123"),
                "role": "admin",
                "full_name": "Admin User",
                "created_at": datetime.utcnow()
            })
            seeded = True

    if "categories" not in cols or not loaded:
        cat_count = await db.db.categories.count_documents({})
        if cat_count == 0:
            await db.db.categories.insert_many([
                {"name": "Electronics", "description": "Laptops, phones, and accessories"},
                {"name": "Furniture", "description": "Office chairs, desks, and tables"},
                {"name": "Stationery", "description": "Paper, pens, and office supplies"},
            ])
            seeded = True

    if "suppliers" not in cols or not loaded:
        sup_count = await db.db.suppliers.count_documents({})
        if sup_count == 0:
            await db.db.suppliers.insert_many([
                {"name": "TechCorp", "contact_email": "sales@techcorp.com", "contact_phone": "+1-555-1000", "address": "New York, USA", "rating": 4.8},
                {"name": "OfficeHub", "contact_email": "support@officehub.com", "contact_phone": "+1-555-2000", "address": "Chicago, USA", "rating": 4.5},
            ])
            seeded = True

    if "products" not in cols or not loaded:
        prod_count = await db.db.products.count_documents({})
        if prod_count == 0:
            categories = await db.db.categories.find({}, {"_id": 1}).to_list(length=10)
            suppliers = await db.db.suppliers.find({}, {"_id": 1}).to_list(length=10)
            await db.db.products.insert_many([
                {"sku": "LAP-MBP-14", "name": "MacBook Pro 14", "category_id": str(categories[0]["_id"]), "supplier_id": str(suppliers[0]["_id"]), "quantity": 5, "reorder_threshold": 10, "unit_price": 1999.0, "cost_price": 1600.0, "location": "Warehouse A", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()},
                {"sku": "CHR-01", "name": "Ergo Chair", "category_id": str(categories[1]["_id"]), "supplier_id": str(suppliers[1]["_id"]), "quantity": 12, "reorder_threshold": 8, "unit_price": 320.0, "cost_price": 240.0, "location": "Warehouse B", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()},
                {"sku": "MOU-01", "name": "Wireless Mouse", "category_id": str(categories[0]["_id"]), "supplier_id": str(suppliers[0]["_id"]), "quantity": 0, "reorder_threshold": 15, "unit_price": 25.0, "cost_price": 18.0, "location": "Warehouse A", "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()},
            ])
            seeded = True

    if "inventory_logs" not in cols or not loaded:
        log_count = await db.db.inventory_logs.count_documents({})
        if log_count == 0:
            products = await db.db.products.find({}, {"_id": 1}).to_list(length=10)
            await db.db.inventory_logs.insert_many([
                {"product_id": str(products[0]["_id"]), "change_type": "restock", "quantity_delta": 3, "resulting_quantity": 8, "note": "Initial replenishment", "created_by": "admin@nexus.ai", "created_at": datetime.utcnow()},
                {"product_id": str(products[1]["_id"]), "change_type": "sale", "quantity_delta": -2, "resulting_quantity": 10, "note": "Office order", "created_by": "admin@nexus.ai", "created_at": datetime.utcnow()},
            ])
            seeded = True

    if seeded or not loaded:
        await sync_to_sqlite()

async def close_mongo_connection():
    logger.info("Closing MongoDB connection...")
    await sync_to_sqlite()
    if db.client:
        db.client.close()
    logger.info("MongoDB connection closed.")

# Sync classes wrappers
class SQLiteSyncedCollection:
    def __init__(self, collection, sync_callback):
        self._collection = collection
        self._sync_callback = sync_callback

    def __getattr__(self, name):
        attr = getattr(self._collection, name)
        if callable(attr):
            if name in (
                "insert_one", "insert_many", "update_one", "update_many",
                "delete_one", "delete_many", "replace_one", "find_one_and_update",
                "find_one_and_delete", "find_one_and_replace"
            ):
                async def wrapper(*args, **kwargs):
                    import inspect
                    res = attr(*args, **kwargs)
                    if inspect.isawaitable(res):
                        res = await res
                    await self._sync_callback()
                    return res
                return wrapper
        return attr

class SQLiteSyncedDatabase:
    def __init__(self, db_instance, sync_callback):
        self._db = db_instance
        self._sync_callback = sync_callback
        self._collections = {}

    def __getattr__(self, name):
        if hasattr(self._db, name) and not name.startswith("_"):
            attr = getattr(self._db, name)
            if callable(attr):
                return attr
            return attr
        if name not in self._collections:
            coll = getattr(self._db, name)
            self._collections[name] = SQLiteSyncedCollection(coll, self._sync_callback)
        return self._collections[name]

    def __getitem__(self, name):
        return self.__getattr__(name)

def get_database():
    return SQLiteSyncedDatabase(db.db, sync_to_sqlite)
