import numpy as np


from openfisca_core.model_api import MONTH, set_input_dispatch_by_period, Variable
from openfisca_france_dotations_locales.entities import Commune


class nom(Variable):
    value_type = str
    entity = Commune
    definition_period = MONTH
    label = "Nom de la commune"
    reference = "https://www.insee.fr/fr/information/6051727"
    set_input = set_input_dispatch_by_period


class code_insee(Variable):
    value_type = str
    entity = Commune
    definition_period = MONTH
    label = "Code INSEE de la commune"
    reference = "https://www.insee.fr/fr/information/6051727"
    set_input = set_input_dispatch_by_period


def safe_divide(a, b, value_if_error=0):
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.where(b != 0, np.divide(a, b), value_if_error)
