# Sashimi - Study of the organisation and evolution of a corpus
#
# Author(s):
# * Ale Abdo <abdo@member.fsf.org>
#
# License:
# [GNU-GPLv3+](https://www.gnu.org/licenses/gpl-3.0.html)
#
# Project:
# <https://en.wikiversity.org/wiki/The_dynamics_and_social_organization_of
#  _innovation_in_the_field_of_oncology>
#
# Reference repository for this file:
# <https://gitlab.com/solstag/sashimi>
#
# Contributions are welcome, get in touch with the author(s).

"""
See README.md for usage information.
"""

__author__ = "Alexandre Hannud Abdo <abdo@member.fsf.org>"
__copyright__ = "Copyright 2016-2024 Alexandre Hannud Abdo"
__license__ = "GNU GPL version 3 or above"
__URL__ = "https://gitlab.com/solstag/sashimi/"

__version__ = "0.9.6"

#######################
# Expose main classes #
#######################

__all__ = ["Corpus", "GraphModels", "VectorModels"]

from .corpus import Corpus
from .graph_models import GraphModels
from .vector_models import VectorModels
