from rrcgeoviz.JsonCreatorClasses.Sections.ColumnSetter import ColumnSetter
import panel as pn

from rrcgeoviz.JsonCreatorClasses.Sections.DownloadSection import DownloadSection

from rrcgeoviz.JsonCreatorClasses.Sections.FeatureSetter import FeatureSetter

from rrcgeoviz.JsonCreatorClasses.Sections.CacheSetter import CacheSetter

from rrcgeoviz.JsonCreatorClasses.Sections.FeatureCustomizationsSetter import (
    FeatureCustomizationsSetter,
)


def main_javacreator():
    json_page = pn.Column()
    sections = [
        ColumnSetter(),
        FeatureSetter(),
        FeatureCustomizationsSetter(),
        CacheSetter(),
    ]
    for section in sections:
        json_page.append(section.generate_section())
    json_page.append(DownloadSection(sections).generate_section())

    json_page.servable()
    pn.serve(json_page)
