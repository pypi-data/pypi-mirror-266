""" util for sql view creation"""

import ctakesclient


def main():
    """convenice script for writing define sql views"""
    symptoms_list = ctakesclient.filesystem.covid_symptoms()

    values_sql = [
        f"('{bsv.cui}','{bsv.tui}','{bsv.code}','{bsv.vocab}','{bsv.text}','{bsv.pref}')"
        for bsv in symptoms_list
    ]
    values_sql = "\n,".join(values_sql)

    table_cols = "AS t (cui, tui, code, system, text, pref);"
    create_view = (
        "create or replace view covid_symptom__define_symptom as "
        f"select * from (VALUES \n {values_sql}) \n {table_cols}"
    )

    with open("define_symptom.sql", "w", encoding="UTF-8") as f:
        f.write(create_view)


if __name__ == "__main__":
    main()
