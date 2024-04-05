CREATE TABLE covid_symptom__study_period AS
SELECT DISTINCT
    v.variant_era,
    s.period_start_day AS start_date,
    s.period_start_week AS start_week,
    s.period_start_month AS start_month,
    s.period_end_day AS end_date,
    s.age_at_visit,
    s.author_day AS author_date,
    s.author_week,
    s.author_month,
    s.author_year,
    s.gender,
    s.race_display,
    s.subject_ref,
    s.encounter_ref,
    s.documentreference_ref,
    s.diff_enc_note_days,
    s.enc_class_code,
    s.enc_class_display,
    s.doc_type_code,
    s.doc_type_display,
    s.ed_note, -- TODO https://github.com/smart-on-fhir/cumulus-library-covid/issues/10
    a.age_group,
    s.status
FROM core__study_period AS s,
    covid_symptom__define_period AS v,
    covid_symptom__define_age AS a
WHERE
    s.age_at_visit = a.age
    AND s.gender IN ('female', 'male')
    AND s.author_day BETWEEN v.variant_start AND v.variant_end
    AND s.period_start_day BETWEEN v.variant_start AND v.variant_end
    AND s.diff_enc_note_days BETWEEN -30 AND 30;

CREATE TABLE covid_symptom__meta_date AS
SELECT
    min(start_date) AS min_date,
    max(end_date) AS max_date
FROM covid_symptom__study_period;
