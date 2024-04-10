from enum import Enum

import dash_bootstrap_components as dbc


class Themes(Enum):
    BOOTSTRAP = dbc.themes.BOOTSTRAP
    CERULEAN = dbc.themes.CERULEAN
    COSMO = dbc.themes.COSMO
    CYBORG = dbc.themes.CYBORG
    DARKLY = dbc.themes.DARKLY
    FLATLY = dbc.themes.FLATLY
    JOURNAL = dbc.themes.JOURNAL
    LITERA = dbc.themes.LITERA
    LUMEN = dbc.themes.LUMEN
    LUX = dbc.themes.LUX
    MATERIA = dbc.themes.MATERIA
    MINTY = dbc.themes.MINTY
    MORPH = dbc.themes.MORPH
    PULSE = dbc.themes.PULSE
    QUARTZ = dbc.themes.QUARTZ
    SANDSTONE = dbc.themes.SANDSTONE
    SIMPLEX = dbc.themes.SIMPLEX
    SKETCHY = dbc.themes.SKETCHY
    SLATE = dbc.themes.SLATE
    SOLAR = dbc.themes.SOLAR
    SPACELAB = dbc.themes.SPACELAB
    SUPERHERO = dbc.themes.SUPERHERO
    UNITED = dbc.themes.UNITED
    VAPOR = dbc.themes.VAPOR
    YETI = dbc.themes.YETI
    ZEPHYR = dbc.themes.ZEPHYR

    @classmethod
    def from_string(cls, theme: str):
        return cls[theme.upper()]


if __name__ == "__main__":
    print(Themes.BOOTSTRAP.name)
    print(Themes.from_string("BOOTSTRAP"))
