"""
Finnish noun cases as value objects.
"""

from enum import Enum, auto
from typing import List


class Case(str, Enum):
    """Finnish noun cases."""
    
    NOMINATIVE = "nominative"  # nominatiivi (basic form)
    GENITIVE = "genitive"      # genetiivi (-n)
    PARTITIVE = "partitive"    # partitiivi (-a/-ä)
    INESSIVE = "inessive"      # inessiivi (-ssa/-ssä)
    ELATIVE = "elative"        # elatiivi (-sta/-stä)
    ILLATIVE = "illative"      # illatiivi (-Vn/-hVn/-seen)
    ADESSIVE = "adessive"      # adessiivi (-lla/-llä)
    ABLATIVE = "ablative"      # ablatiivi (-lta/-ltä)
    ALLATIVE = "allative"      # allatiivi (-lle)
    ESSIVE = "essive"          # essiivi (-na/-nä)
    TRANSLATIVE = "translative"# translatiivi (-ksi)
    INSTRUCTIVE = "instructive"# instruktiivi (-n)
    ABESSIVE = "abessive"      # abessiivi (-tta/-ttä)
    COMITATIVE = "comitative"  # komitatiivi (-ne-) 