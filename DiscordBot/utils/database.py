import sqlite3
import logging
import json

# Fetch SQLite database file path
db_file_path = "database.db"  # Specify the path to your SQLite database file

# Initialize SQLite connection
conn = sqlite3.connect(db_file_path)
cursor = conn.cursor()


class Database:
    """SQLite database"""

    @classmethod
    async def guild_in_database(cls, guild_id: int) -> bool:
        """Return True if guild is already recorded in database"""
        count = await cls._collection.count_documents(
            {"guild_id": guild_id}
        )
        return count > 0

    @classmethod
    async def create_database(cls, guild_id: int, guild_name: str) -> None:
        """Initialize guild template in database"""
        await cls._collection.insert_one(
            {
                "guild_id": guild_id,
                "guild_name": guild_name,
                "members": [],
                "settings": "[]"  # JSON string
            }
        )
        logging.info(f"Guild added! {guild_name} with id {guild_id}")

    @classmethod
    async def update_guilds(cls):
        """Update all guilds in database to have a settings field if they don't already."""
        async for doc in cls._collection.find({}):
            if "settings" not in doc:
                await cls._collection.update_one(
                    {"guild_id": doc["guild_id"]}, {
                        "$set": {
                            "settings": "[]"
                        }
                    }
                )

    @classmethod
    async def get_internal_guild_settings(cls, guild_id: int) -> list:
        """Return guild settings as a list"""
        async for doc in cls._collection.find(
            {"guild_id": guild_id}
        ):
            try:
                return json.loads(doc["settings"])
            except KeyError:
                # If the guild doesn't have a settings field, add it.
                await cls._collection.update_one(
                    {"guild_id": guild_id}, {
                        "$set": {
                            "settings": "[]"
                        }
                    }
                )
                return []

    @classmethod
    async def update_guild_settings(cls, guild_id: int, settings: list) -> None:
        """Update guild settings"""
        await cls._collection.update_one(
            {"guild_id": guild_id}, {
                "$set": {
                    "settings": json.dumps(settings)
                }
            }
        )

    @classmethod
    async def get_guild_settings(cls, guild_id: int):
        new_settings = {}
        settings = await cls.get_internal_guild_settings(guild_id)
        for setting in settings:
            new_settings[setting["int_name"]] = setting
        return new_settings

    @classmethod
    async def member_in_database(
            cls, guild_id: int, member_id: int) -> object | None:
        """Return True if member is already recorded in guild database"""
        async for doc in cls._collection.aggregate(
            [
                {
                    "$match": {
                        "guild_id": guild_id,
                        # STORED AS AN INTEGER NOT STRING.
                        "members.id": member_id
                    }
                },
                {
                    "$unwind": "$members"
                },
                {
                    "$match": {
                        "members.id": member_id
                    }
                },
                {
                    "$replaceWith": "$members"
                }
            ]
        ):
            return doc

    @classmethod
    async def create_member(cls, guild_id, member_id, member_name) -> None:
        """Initialize member data in guild database"""
        await cls._collection.update_one(
            {"guild_id": guild_id}, {
                "$push": {
                    "members": {
                        "id": member_id,  # STORED AS AN INTEGER NOT STRING.
                        "name": member_name,
                        "low_honor_word_count": 0,
                    }
                }
            }
        )

    @classmethod
    async def increment_low_honor_word_count(cls, guild_id, member_id, count) -> None:
        """Add to low honor word count of person's data info in server"""
        await cls._collection.update_one(
            {
                "guild_id": guild_id,
                "members.id": member_id
            },
            {
                "$inc": {
                    "members.$.low_word_count": count
                }
            },
            upsert=False  # Don't create new document if not found.
        )

    @classmethod
    async def get_total_documents(cls) -> int:
        """Return total number of documents in database"""
        return await cls._collection.count_documents({})

    @classmethod
    async def get_low_honor_word_server_total(cls, guild_id) -> int:
        """Return integer sum of total low honor words said in a server"""
        async for doc in cls._collection.aggregate(
            [
                {
                    "$match": {
                        "guild_id": guild_id
                    }
                },
                {
                    "$unwind": "$members"
                },
                {
                    "$group": {
                        "_id": guild_id,
                        "total_low_honor_words": {
                            "$sum": "$members.low_honor_word_count"
                        }
                    }
                }
            ]
        ):
            return doc["total_low_honor_words"]
