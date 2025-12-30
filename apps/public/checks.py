from django.conf import settings
from django.core.checks import Error, Tags, register
from pymongo import MongoClient
from pymongo.errors import PyMongoError


@register(Tags.database)
def mongodb_connection_check(app_configs, **kwargs):
    """
    Ensure that Django can connect to MongoDB Atlas using the configured URI.
    """
    uri = getattr(settings, "MONGODB_URI", None)
    if not uri:
        return [
            Error(
                "MONGODB_URI is not configured.",
                hint="Set MONGODB_URI in your environment (e.g. .env).",
                id="portfolio.E002",
            )
        ]

    client = None
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
    except PyMongoError as err:
        return [
            Error(
                "Cannot reach MongoDB Atlas.",
                hint=f"Verify MONGODB_URI and network access. Details: {err}",
                obj=uri,
                id="portfolio.E001",
            )
        ]
    finally:
        if client is not None:
            client.close()

    return []
