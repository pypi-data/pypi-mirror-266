-- ############################################################################
-- Table COVID19 Diagnosis

CREATE TABLE covid_symptom__dx AS
WITH define_dx AS (
    SELECT
        code,
        system,
        display
    FROM covid_symptom__define_dx_icd10
    UNION
    SELECT
        code,
        system,
        display
    FROM covid_symptom__define_dx_snomed
)

SELECT DISTINCT
    c.subject_ref,
    c.encounter_ref,
    s.status,
    c.code AS cond_code, -- noqa: LT01,RF02
    c.recordeddate_week AS cond_week,
    c.recordeddate_month AS cond_month,
    c.recordeddate_year AS cond_year,
    s.enc_class_display,
    s.age_at_visit,
    s.ed_note,
    s.variant_era
FROM core__condition AS c,
    covid_symptom__study_period AS s,
    define_dx
WHERE
    c.code = define_dx.code -- noqa: LT01,RF02
    AND c.encounter_ref = s.encounter_ref;
