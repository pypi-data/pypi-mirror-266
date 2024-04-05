from aleksis.core.util.apps import AppConfig


class DefaultConfig(AppConfig):
    name = "aleksis.apps.cursus"
    verbose_name = "AlekSIS — Cursus"
    dist_name = "AlekSIS-App-Cursus"

    urls = {
        "Repository": "https://edugit.org/AlekSIS/onboarding//AlekSIS-App-Cursus",
    }
    licence = "EUPL-1.2+"
    copyright_info = (([2023], "Jonathan Weth", "dev@jonathanweth.de"),)

    def _maintain_default_data(self):
        super()._maintain_default_data()

        # Ensure that default group types for school structure exist
        from .util.group_types import get_school_class_group_type, get_school_grade_group_type

        get_school_grade_group_type()
        get_school_class_group_type()
