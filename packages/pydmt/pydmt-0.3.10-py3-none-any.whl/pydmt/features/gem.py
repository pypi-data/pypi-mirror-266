import os.path

from pydmt.api.feature import Feature
from pydmt.builders.gem import Installer
from pydmt.core.pydmt import PyDMT


class FeatureGem(Feature):
    def setup(self, pydmt: PyDMT) -> None:
        if os.path.isfile("Gemfile"):
            pydmt.add_builder(Installer(
                source="Gemfile",
                target="out/gem.stamp",
            ))
