-- ############################################################################
-- Table COVID19 PCR tests for COVID performed at the local hospital

CREATE TABLE covid_symptom__pcr AS
WITH obs_interpret AS (
    SELECT
        system,
        code,
        'Negative' AS display
    FROM covid_symptom__define_pcr_negative
    UNION
    SELECT
        system,
        code,
        'Positive' AS display
    FROM covid_symptom__define_pcr_positive
    UNION
    SELECT
        from_system,
        from_code AS code,
        display
    FROM covid_symptom__define_pcr_custom
)

SELECT DISTINCT
    obs_interpret.display AS covid_pcr_result_display,
    o.observation_code AS covid_pcr_code,
    o.effectivedatetime_day AS covid_pcr_date,
    o.effectivedatetime_week AS covid_pcr_week,
    o.effectivedatetime_month AS covid_pcr_month,
    s.status,
    s.variant_era,
    s.author_date,
    s.author_week,
    s.author_month,
    s.ed_note,
    s.start_date,
    s.start_week,
    s.start_month,
    s.age_at_visit,
    s.gender,
    s.race_display,
    o.subject_ref,
    o.encounter_ref,
    o.observation_ref
FROM core__observation_lab AS o,
    covid_symptom__define_period AS p,
    covid_symptom__study_period AS s,
    covid_symptom__define_pcr AS pcr,
    obs_interpret
WHERE
    (s.encounter_ref = o.encounter_ref)
    AND (s.variant_era = p.variant_era)
    AND (o.effectivedatetime_week BETWEEN p.variant_start AND p.variant_end)
    AND (o.observation_code = pcr.code)
    AND (o.valuecodeableconcept_code = obs_interpret.code);

-- TODO Cerner specific handling of lab RESULT
-- https://github.com/smart-on-fhir/cumulus-library-covid/issues/13
