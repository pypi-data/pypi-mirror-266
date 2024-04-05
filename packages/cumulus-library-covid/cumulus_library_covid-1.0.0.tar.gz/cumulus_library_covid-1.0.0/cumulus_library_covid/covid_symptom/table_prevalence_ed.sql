CREATE TABLE covid_symptom__prevalence_ed AS
WITH study_period AS (
    SELECT DISTINCT
        encounter_ref,
        subject_ref,
        author_week,
        author_month,
        gender,
        race_display,
        age_at_visit,
        age_group,
        variant_era,
        enc_class_display,
        status
    FROM covid_symptom__study_period
    WHERE ed_note
),

join_2020 AS (
    SELECT DISTINCT
        p.status,
        p.author_week,
        p.author_month,
        p.gender,
        p.race_display,
        p.age_at_visit,
        p.age_group,
        p.variant_era,
        p.enc_class_display,
        p.subject_ref,
        p.encounter_ref,
        COALESCE(pcr.covid_pcr_result_display, 'None') AS covid_pcr_result,
        COALESCE(dx.cond_code, 'None') AS covid_icd10,
        (dx.cond_code IS NOT NULL OR pcr.covid_pcr_result_display = 'POSITIVE')
            AS covid_dx,
        COALESCE(cn.symptom_display, 'None') AS covid_symptom,
        COALESCE(icd10.icd10_display, 'None') AS symptom_icd10_display
    FROM study_period AS p
    LEFT JOIN covid_symptom__dx AS dx ON p.encounter_ref = dx.encounter_ref
    LEFT JOIN covid_symptom__pcr AS pcr ON p.encounter_ref = pcr.encounter_ref
    LEFT JOIN covid_symptom__symptom_ctakes_negation AS cn
        ON p.encounter_ref = cn.encounter_ref
    LEFT JOIN covid_symptom__symptom_icd10 AS icd10
        ON p.encounter_ref = icd10.encounter_ref
)

SELECT * FROM join_2020
ORDER BY author_week, variant_era;
