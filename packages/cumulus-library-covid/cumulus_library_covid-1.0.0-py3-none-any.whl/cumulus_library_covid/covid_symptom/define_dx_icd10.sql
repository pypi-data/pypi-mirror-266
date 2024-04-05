CREATE OR REPLACE VIEW covid_symptom__define_dx_icd10 AS SELECT * FROM (
    VALUES
    ('http://hl7.org/fhir/sid/icd-10-cm', 'U07.1', 'COVID-19')
) AS t (system, code, display); --noqa: AL05
