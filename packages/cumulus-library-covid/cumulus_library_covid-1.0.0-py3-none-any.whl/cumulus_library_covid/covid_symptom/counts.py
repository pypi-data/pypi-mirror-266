from pathlib import Path
from cumulus_library.statistics.counts import CountsBuilder


class CovidCountsBuilder(CountsBuilder):
    display_text = "Creating covid counts..."

    def count_dx(self, duration="week"):
        """
        covid_symptom__count_dx_week
        covid_symptom__count_dx_month
        """
        view_name = self.get_table_name("count_dx", duration)
        from_table = self.get_table_name("dx")
        cols = [
            f"cond_{duration}",
            "enc_class_display",
            "age_at_visit",
            "ed_note",
            "variant_era",
        ]
        return self.count_encounter(
            view_name, from_table, cols, where_clauses=self.get_where_clauses()
        )

    def count_pcr(self, duration="week"):
        """
        covid_symptom__count_pcr_week
        covid_symptom__count_pcr_month
        """
        view_name = self.get_table_name("count_pcr", duration)
        from_table = self.get_table_name("pcr")
        cols = [
            f"covid_pcr_{duration}",
            "covid_pcr_result_display",
            "variant_era",
            "ed_note",
            "age_at_visit",
            "gender",
            "race_display",
        ]
        return self.count_encounter(
            view_name, from_table, cols, where_clauses=self.get_where_clauses()
        )

    def count_study_period(self, duration="month"):
        """
        covid_symptom__count_study_period_week
        covid_symptom__count_study_period_month
        covid_symptom__count_study_period_year
        """
        view_name = self.get_table_name("count_study_period", duration)
        from_table = self.get_table_name("study_period")
        cols = [
            f"start_{duration}",
            "variant_era",
            "ed_note",
            "gender",
            "age_group",
            "race_display",
        ]
        return self.count_encounter(
            view_name, from_table, cols, where_clauses=self.get_where_clauses()
        )

    def count_prevalence_ed(self, duration="month"):
        view_name = self.get_table_name("count_prevalence_ed", duration)
        from_table = self.get_table_name("prevalence_ed")
        cols = [
            f"author_{duration}",
            "covid_dx",
            "covid_icd10",
            "covid_pcr_result",
            "covid_symptom",
            "symptom_icd10_display",
            "variant_era",
            "age_group",
            "enc_class_display",
        ]
        return self.count_encounter(view_name, from_table, cols)

    def count_symptom(self, duration="week"):
        """
        covid_symptom__count_symptom_week
        covid_symptom__count_symptom_month
        """
        view_name = self.get_table_name("count_symptom", duration)
        from_table = self.get_table_name("symptom_ctakes_negation")
        cols = [
            f"author_{duration}",
            "symptom_display",
            "variant_era",
            "age_group",
            "gender",
            "race_display",
            "enc_class_display",
            "ed_note",
        ]
        return self.count_encounter(view_name, from_table, cols)

    def prepare_queries(self, cursor=None, schema=None, **kwargs):
        self.queries = [
            self.count_dx("month"),
            self.count_dx("week"),
            self.count_pcr("month"),
            self.count_pcr("week"),
            self.count_study_period("month"),
            self.count_study_period("week"),
            self.count_symptom("week"),
            self.count_symptom("month"),
            self.count_prevalence_ed("month"),
            self.count_prevalence_ed("week"),
        ]


if __name__ == "__main__":
    builder = CovidCountsBuilder()
    builder.write_counts(f"{Path(__file__).resolve().parent}/counts.sql")
