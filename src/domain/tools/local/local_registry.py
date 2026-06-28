from __future__ import annotations
import logging
import struct
import re  # Added missing import
from src.domain.tools.models import ToolManifest, EmbeddingProvider
from src.domain.db.database import DatabaseManager
from src.domain.tools.local.register_local_tool import _GLOBAL_TOOL_REGISTRY

logger = logging.getLogger(__name__)

def serialize_vector(vector: list[float]) -> bytes:
    # "f" means float (4 bytes), times the length of the vector
    return struct.pack(f"{len(vector)}f", *vector)

class LocalSQLiteRegistry:
    def __init__(self, db_manager: DatabaseManager, embedder: EmbeddingProvider):
        self.db = db_manager
        self.embedder = embedder
        self._local_executors = _GLOBAL_TOOL_REGISTRY
        self._initialized = False  # Fixed variable name

    async def initialize(self):  # Renamed to initialize (verb)
        is_valid = await self.verify_vector_dimension()
        if not is_valid:
            logger.warning("Wiping outdated db to re-align")
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DROP TABLE IF EXISTS vec_tools")
                cursor.execute("DROP TABLE IF EXISTS tools")
                conn.commit()
            
        await self._auto_sync_db()  # Fixed missing parentheses
        self._initialized = True  # Fixed variable name
    
    async def verify_vector_dimension(self) -> bool:
        expected_size = await self.embedder.get_embedding_size()

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # Fixed table name mismatch (tools_vectors -> vec_tools)
            cursor.execute("""
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name='vec_tools' 
            """)
            row = cursor.fetchone()
            if not row or not row[0]:
                return True
            
            sql_definition = row[0]
            
        match = re.search(r"float\[(\d+)\]", sql_definition, re.IGNORECASE)
        if match:
            existing_size = int(match.group(1))
            if existing_size != expected_size:
                logger.warning(f"Dimension Mismatch: DB uses {existing_size} embedder requires {expected_size}")
                return False
            return True
        return False

    # Fixed missing async keyword
    async def _auto_sync_db(self):
        target_dim = await self.embedder.get_embedding_size()

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                callable_name TEXT,
                name TEXT,
                description TEXT
                )
            """)

            cursor.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS vec_tools USING vec0(
                    embedding float[{target_dim}]
                )
            """)

            for callable_name, meta in self._local_executors.items():
                cursor.execute("SELECT id, description FROM tools WHERE callable_name = ?", (callable_name,))
                existing = cursor.fetchone()

                if existing and existing[1] == meta["description"]:
                    continue
            
                logger.info(f"Generating embedding for tool: {callable_name}")
                # Fixed nested quotes syntax
                text_to_embed = f"Tool Name: {meta['name']}. Description: {meta['description']}"
                # Fixed missing await
                vector = await self.embedder.get_embedding(text_to_embed)

                if existing:
                    cursor.execute("UPDATE tools SET name = ?, description = ? WHERE id = ?", (meta['name'], meta['description'], existing[0]))
                    cursor.execute("UPDATE vec_tools SET embedding = ? WHERE rowid = ?", (serialize_vector(vector), existing[0]))

                else:
                    cursor.execute("INSERT INTO tools (callable_name, name, description) VALUES (?, ?, ?)", 
                                   (callable_name, meta["name"], meta["description"]))
                    new_id = cursor.lastrowid
                    cursor.execute("INSERT INTO vec_tools (rowid, embedding) VALUES (?, ?)", 
                                   (new_id, serialize_vector(vector)))

            # PRUNE PHASE
            current_keys = list(self._local_executors.keys())
            if current_keys:
                placeholders = ",".join(["?"] * len(current_keys))
                cursor.execute(f"DELETE FROM tools WHERE callable_name NOT IN ({placeholders})", current_keys)
                cursor.execute(f"DELETE FROM vec_tools WHERE rowid NOT IN (SELECT id FROM tools)")
            else:
                cursor.execute("DELETE FROM tools")
                cursor.execute("DELETE FROM vec_tools")

            conn.commit()
            # Fixed variable name (callable_names -> current_keys)
            logger.info(f"Synced {len(current_keys)} local tools to SQLite")

    async def get_relevant_tools(self, intent: str, top_k: int = 3) -> list[ToolManifest]:
        # Fixed state variable check
        if not self._initialized:
            raise RuntimeError("You must await local_db.initialize() before querying.")

        intent_vector = await self.embedder.get_embedding(intent)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT t.callable_name, t.name, t.description 
                FROM vec_tools v
                JOIN tools t ON t.id = v.rowid
                WHERE v.embedding MATCH ? AND k = ?
            """
            cursor.execute(query, (serialize_vector(intent_vector), top_k))
            rows = cursor.fetchall()

        manifests = []
        for callable_name, db_name, db_desc in rows:
            actual_function = self._local_executors.get(callable_name)
            if actual_function:
                manifests.append(
                    ToolManifest(
                        name=db_name,
                        description=db_desc,
                        callable_func=actual_function["func"]
                    )
                )
        return manifests