--desc covid_symptom__nlp_results;
--id                  	string
--docref_id           	string
--encounter_id        	string
--subject_id          	string
--match               	struct<
--    begin:bigint,
--    end:bigint,
--    polarity:bigint,
--    text:string,
--    type:string,
--    conceptAttributes:array<struct<
--        code:string,
--        codingScheme:string,
--        cui:string,
--        tui:string>>>

-- ############################################################################

CREATE TABLE covid_symptom__symptom_ctakes_negation AS
WITH mention AS (
    SELECT
        t.concept,
        t.concept.cui,
        nr.match.text AS match_text,
        nr.subject_id,
        nr.encounter_id,
        nr.docref_id
    FROM covid_symptom__nlp_results AS nr,
        UNNEST(match.conceptattributes) AS t (concept)
),

covid_symptom__define_symptom_cui AS (
    SELECT DISTINCT
        cui,
        pref
    FROM covid_symptom__define_symptom
)

SELECT DISTINCT
    s.variant_era,
    s.subject_ref,
    s.encounter_ref,
    m.docref_id,
    def.pref AS symptom_display,
    s.start_date,
    s.end_date,
    s.author_week,
    s.author_month,
    s.age_group,
    s.gender,
    s.race_display,
    s.enc_class_display,
    s.ed_note,
    s.status
FROM mention AS m,
    covid_symptom__define_symptom_cui AS def,
    covid_symptom__study_period AS s
WHERE
    concept.cui = def.cui
    AND s.encounter_ref = CONCAT('Encounter/', m.encounter_id);


CREATE TABLE covid_symptom__symptom_icd10 AS
WITH temp_period AS (
    SELECT
        variant_era,
        subject_ref,
        encounter_ref,
        start_date,
        author_week,
        author_month,
        age_group,
        gender,
        race_display,
        enc_class_display AS ed_note
    FROM covid_symptom__study_period
),

icd10_list AS (
    SELECT DISTINCT
        code AS icd10_code,
        CONCAT('ICD10:', pref) AS icd10_display
    FROM covid_symptom__define_symptom WHERE code_system = 'ICD10CM'
)

SELECT DISTINCT
    temp_period.*,
    icd10_list.icd10_code,
    icd10_list.icd10_display
FROM temp_period,
    core__condition AS v,
    icd10_list
WHERE
    temp_period.encounter_ref = v.encounter_ref
    AND v.code = icd10_list.icd10_code; --noqa: RF02,LT01
