from .common.MultiEntitiesRelationshipAnnotator import MultiEntitiesRelationshipAnnotator, Config

from ..entities.MaterialAnnotator import MaterialAnnotator
from ..entities.ValueUnitAnnotator import ValueUnitAnnotator
from ..entities.PropertiesAnnotator import PropertiesAnnotator



class MaterialtoValueUnittoPropertiesAnnotator(MultiEntitiesRelationshipAnnotator):

    def __init__(self):
        super().__init__(
            Config(
                entities=[MaterialAnnotator().key(), ValueUnitAnnotator().key(), PropertiesAnnotator().key()]
            )
        )
