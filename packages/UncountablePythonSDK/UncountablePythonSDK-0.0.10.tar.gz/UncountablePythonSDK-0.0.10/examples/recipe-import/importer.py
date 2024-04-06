from typing import Iterable, Optional
import itertools
from dataclasses import dataclass
from src.client.requests_client import Client
from src.types.api.recipes.external_create_recipes import (
    Arguments,
    ExternalCreateRecipeDefinition,
)
from src.types.api.entity.external_resolve_entity_identifiers import (
    EntityIdentifier
)
from src.types.base import ObjectId



@dataclass(kw_only=True)
class RecipeIngredientData:
    ingredient_identifier: EntityIdentifier
    recipe_step_id: Optional[ObjectId] = None
    value_numeric: Optional[str] = None
    value_str: Optional[str] = None
    set_actual_value: bool = False


def import_recipes(
    client: Client,
    material_family_id: ObjectId,
    project_id: Optional[ObjectId],
    recipe_data: Iterable[ExternalCreateRecipeDefinition],
    batch_size: int = 100,
) -> None:
    for batch in itertools.batched(recipe_data, batch_size):
        client.external_create_recipes(
            Arguments(
                material_family_id=material_family_id,
                project_id=project_id,
                recipe_definitions=list(batch),
            )
        )
