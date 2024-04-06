from uncountable.client import HTTPRequestsClient, AuthDetailsApiKey
from uncountable.types.api import external_create_entities


if __name__ == "__main__":
    client = HTTPRequestsClient(
        "https://app.uncountable.com", AuthDetailsApiKey(api_id="X", api_secret_key="X")
    )
    connection = client.connect()
    entities = connection.external_create_entities(
        external_create_entities.Arguments(
            definition_id=1,
            entity_type="lab_request",
            entities_to_create=[
                external_create_entities.EntityToCreate(field_values=None)
            ],
        )
    )
