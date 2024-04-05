from dotenv import load_dotenv
load_dotenv()

import os
import requests
import typesense
from typesense import exceptions
from typesense.collection import Collection

from inoopa_utils.inoopa_logging import create_logger


EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_CONTEXT_MAX_LENGTH = 8191
EMBEDDING_ENCODING = "cl100k_base"
# For the model name to typesense's namming convention
EMBEDDING_MODEL_TYPESENSE_NAME = f"openai/{EMBEDDING_MODEL}"
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


class TypesenseManager:
    """
    This class is a client to interact with the Typesense search engine server (deployed in InfraV2).
    You can then is the client outside of the class to interact with the Typesense server.

    It also take care of creating the collections if they don't exist.
    ! Please maintain the schemas in the same file as the TypesenseManager class. !

    :attribute typesense_url: The typesense server URL.
    :attribute client: The typesense client object to interact with the typesense server.
    :attribute collection_nace_codes: The nace_codes collection object.
    :attribute collection_companies_names: The companies_names collection object.
    :attribute collection_online_content: The online_content collection object.
    """
    def __init__(
        self,
        host: str = os.environ["TYPESENSE_HOST"],
        port: str = os.getenv("TYPESENSE_PORT", 443), # Default port is 443 for HTTPS
        api_key: str = os.environ["TYPESENSE_API_KEY"],
        protocol: str = "https",
    ):
        """
        :param host: Typesense's server host
        :param port: Typesense's server port
        :param api_key: Typesense's API key
        :param mongo_db_collection_name : define which MongoDB collection will be used
        """
        self._logger = create_logger("INOOPA.TYPESENSE.CLIENT")
        self.typesense_url = f"https://{host}"
        self.client: typesense.Client = typesense.Client({
            'api_key': api_key,
            'nodes': [{
                'host': host,
                'port': port,
                'protocol': protocol,
            }],
            'connection_timeout_seconds': 10
        })

        # 1. Check the API's health
        self._check_server_heatlh()
        # 2. Create collections if they don't exist
        self._create_collections()

        # Expose collections
        self.collection_nace_codes: Collection = self.client.collections['nace_codes']
        self.collection_companies_names: Collection = self.client.collections['companies_names']
        self.collection_online_content: Collection = self.client.collections['online_content']
        self._logger.debug("Typesense Manager ready!")

    def _check_server_heatlh(self) -> None:
        """Check if typesense server is up and running."""
        response = requests.get(f"{self.typesense_url }/health")
        response.raise_for_status()
        if response.json()['ok'] != True:
            raise Exception("Typesense is not running!")
        self._logger.info("Typesense server is up and running!")

    def _create_collections(self) -> Collection :
        """Create a Typesense schema so MongoDB's collection can be interpreted."""
        for collection in [naces_collection_schema, companies_names_collection_schema, online_content_collection_schema]:
            try:
                self.client.collections.create(collection)
                self._logger.warning(f"Typesense collection {collection['name']} created!")
            except exceptions.ObjectAlreadyExists:
                self._logger.debug(f"Typesense collection {collection['name']} already exists!")
        return collection


# Define the schemas for each collection
# Contains all the naces codes, their labels and translations
naces_collection_schema = {
    "name": "nace_codes",
    "enable_nested_fields": True,
    "fields": [
        {
            "optional": False,
            "name": "country",
            "type": "string"
        },
        {
            "optional": False,
            "name": "level",
            "type": "int32"
        },
        {
            "optional": False,
            "name": "code",
            "type": "string"
        },
        {
            "optional": False,
            "name": "section_label",
            "type": "string",
        },
        {
            "optional": False,
            "name": "section_code",
            "type": "string",
        },
        {
            "optional": False,
            "name": "label_en",
            "type": "string"
        },
        {
            "optional": True,
            "name": "label_en_embedding",
            "type": "float[]",
            "embed": {
                "from": [
                    "label_en"
                ],
                "model_config": {
                    "model_name": EMBEDDING_MODEL_TYPESENSE_NAME,
                    "api_key": OPENAI_API_KEY
                }
            }
        },
        {
            "optional": True,
            "name": "label_fr",
            "type": "string"
        },
        {
            "optional": True,
            "name": "label_fr_embedding",
            "type": "float[]",
            "embed": {
                "from": [
                    "label_fr"
                ],
                "model_config": {
                    "model_name": EMBEDDING_MODEL_TYPESENSE_NAME,
                    "api_key": OPENAI_API_KEY
                }
            }
        },
        {
            "optional": True,
            "name": "label_nl",
            "type": "string"
        },
        {
            "optional": True,
            "name": "label_nl_embedding",
            "type": "float[]",
            "embed": {
                "from": [
                    "label_nl"
                ],
                "model_config": {
                    "model_name": EMBEDDING_MODEL_TYPESENSE_NAME,
                    "api_key": OPENAI_API_KEY
                }
            }
        },
    ]
}

# Contains all the companies and establishment names for name matching puprose
companies_names_collection_schema = {
    "name": "companies_names",
    "enable_nested_fields": True,
    "fields": [
        {"optional": False, "name": "_id", "type": "string"},
        {"optional": True, "name": "name", "type": "string"},
        {"optional": True, "name": "name_embeddings", "type": "float[]"},
        {"optional": True, "name": "name_fr", "type": "string"},
        {"optional": True, "name": "name_fr_embeddings", "type": "float[]"},
        {"optional": True, "name": "name_nl", "type": "string"},
        {"optional": True, "name": "name_nl_embeddings", "type": "float[]"},
        {"optional": True, "name": "name_de", "type": "string"},
        {"optional": True, "name": "name_de_embeddings", "type": "float[]"},
        {
            "optional": True,
            "name": "establishments",
            "type": "object[]",
            "facet": False,
            "index": False,
            "optional": True,
            "fields": [
                {"name": "name", "type": "string", "optional": True},
                {"name": "name_embedding", "type": "float[]", "optional": True},
                {"name": "name_fr", "type": "string", "optional": True},
                {"name": "name_fr_embedding", "type": "float[]", "optional": True},
                {"name": "name_nl", "type": "string", "optional": True},
                {"name": "name_nl_embedding", "type": "float[]", "optional": True},
                {"name": "name_de", "type": "string", "optional": True},
                {"name": "name_de_embedding", "type": "float[]", "optional": True},
            ]
        }
    ]
}


# Contain an online content. Ex: website, social network,... Used for search
online_content_collection_schema = {
    "name": "online_content",
    "enable_nested_fields": True,
    "fields": [
        # ---- IDs ----
        {
            "name": "companies_id",
            "optional": True,
            "type": "string[]"
        },

        # ---- Facebook's content ----
        {
            "name": "facebook_page_url",
            "optional": True,
            "type": "string"
        },
        {
            "name": "facebook_page_text",
            "optional": True,
            "type": "string"
        },
        {
            "name": "facebook_page_embedding",
            "optional": True,
            "type": "float[]",
            "embed": {
                "from": ["facebook_page_text"],
                "model_config": {
                    "model_name": EMBEDDING_MODEL_TYPESENSE_NAME,
                    "api_key": OPENAI_API_KEY
                }
            }
        },

        # ---- Google's content ----
        {
            "name": "google_my_business_url",
            "optional": True,
            "type": "string"
        },
        {
            "name": "google_my_business_text",
            "optional": True,
            "type": "string"
        },
        {
            "name": "google_my_business_embedding",
            "optional": True,
            "type": "float[]",
            "embed": {
                "from": ["google_my_business_text"],
                "model_config": {
                    "model_name": EMBEDDING_MODEL_TYPESENSE_NAME,
                    "api_key": OPENAI_API_KEY
                }
            }
        },

        # ---- Websites' content ----
        {
            "name": "website_base_url",
            "optional": True,
            "type": "string"
        },
        # - Home page -
        {
            "optional": True,
            "name": "website_home_page_url",
            "type": "string"
        },
        {
            "optional": True,
            "name": "website_home_page_status_code",
            "type": "int32"
        },
        {
            "optional": True,
            "name": "website_home_page_text",
            "type": "string"
        },
        {
            "optional": True,
            "name": "website_home_page_embedding",
            "type": "float[]",
            "embed": {
                "from": ["website_home_page_text"],
                "model_config": {
                    "model_name": EMBEDDING_MODEL_TYPESENSE_NAME,
                    "api_key": OPENAI_API_KEY
                }
            }
        },
        # - About page -
        {
            "optional": True,
            "name": "website_about_page_url",
            "type": "string"
        },
        {
            "optional": True,
            "name": "website_about_page_status_code",
            "type": "int32"
        },
        {
            "optional": True,
            "name": "website_about_page_text",
            "type": "string"
        },
        {
            "optional": True,
            "name": "website_about_page_embedding",
            "type": "float[]",
            "embed": {
                "from": ["website_about_page_text"],
                "model_config": {
                    "model_name": EMBEDDING_MODEL_TYPESENSE_NAME,
                    "api_key": OPENAI_API_KEY
                }
            }
        },
        # - Contact page -
        {
            "optional": True,
            "name": "website_contact_page_url",
            "type": "string"
        },
        {
            "optional": True,
            "name": "website_contact_page_status_code",
            "type": "int32"
        },
        {
            "optional": True,
            "name": "website_contact_page_text",
            "type": "string"
        },
        {
            "optional": True,
            "name": "website_contact_page_embedding",
            "type": "float[]",
            "embed": {
                "from": ["website_contact_page_text"],
                "model_config": {
                    "model_name": EMBEDDING_MODEL_TYPESENSE_NAME,
                    "api_key": OPENAI_API_KEY
                }
            }
        }
    ]
}


if __name__ == "__main__":
    typesense_manager = TypesenseManager()
    print("OK!")