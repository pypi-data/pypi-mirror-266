CREATE TABLE covid_symptom__count_dx_month AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            s.encounter_ref,
            --noqa: disable=RF03, AL02
            s."cond_month",
            s."enc_class_display",
            s."age_at_visit",
            s."ed_note",
            s."variant_era"
            --noqa: enable=RF03, AL02
        FROM covid_symptom__dx AS s
        WHERE s.status = 'finished'
    ),
    
    null_replacement AS (
        SELECT
            subject_ref,
            encounter_ref,
            coalesce(
                cast(cond_month AS varchar),
                'cumulus__none'
            ) AS cond_month,
            coalesce(
                cast(enc_class_display AS varchar),
                'cumulus__none'
            ) AS enc_class_display,
            coalesce(
                cast(age_at_visit AS varchar),
                'cumulus__none'
            ) AS age_at_visit,
            coalesce(
                cast(ed_note AS varchar),
                'cumulus__none'
            ) AS ed_note,
            coalesce(
                cast(variant_era AS varchar),
                'cumulus__none'
            ) AS variant_era
        FROM filtered_table
    ),
    secondary_powerset AS (
        SELECT
            count(DISTINCT encounter_ref) AS cnt_encounter_ref,
            "cond_month",
            "enc_class_display",
            "age_at_visit",
            "ed_note",
            "variant_era",
            concat_ws(
                '-',
                COALESCE("cond_month",''),
                COALESCE("enc_class_display",''),
                COALESCE("age_at_visit",''),
                COALESCE("ed_note",''),
                COALESCE("variant_era",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "cond_month",
            "enc_class_display",
            "age_at_visit",
            "ed_note",
            "variant_era"
            )
    ),

    powerset AS (
        SELECT
            count(DISTINCT subject_ref) AS cnt_subject_ref,
            "cond_month",
            "enc_class_display",
            "age_at_visit",
            "ed_note",
            "variant_era",
            concat_ws(
                '-',
                COALESCE("cond_month",''),
                COALESCE("enc_class_display",''),
                COALESCE("age_at_visit",''),
                COALESCE("ed_note",''),
                COALESCE("variant_era",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "cond_month",
            "enc_class_display",
            "age_at_visit",
            "ed_note",
            "variant_era"
            )
    )

    SELECT
        s.cnt_encounter_ref AS cnt,
        p."cond_month",
        p."enc_class_display",
        p."age_at_visit",
        p."ed_note",
        p."variant_era"
    FROM powerset AS p
    JOIN secondary_powerset AS s on s.id = p.id
    WHERE
        cnt_subject_ref >= 10
        
);
CREATE TABLE covid_symptom__count_dx_week AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            s.encounter_ref,
            --noqa: disable=RF03, AL02
            s."cond_week",
            s."enc_class_display",
            s."age_at_visit",
            s."ed_note",
            s."variant_era"
            --noqa: enable=RF03, AL02
        FROM covid_symptom__dx AS s
        WHERE s.status = 'finished'
    ),
    
    null_replacement AS (
        SELECT
            subject_ref,
            encounter_ref,
            coalesce(
                cast(cond_week AS varchar),
                'cumulus__none'
            ) AS cond_week,
            coalesce(
                cast(enc_class_display AS varchar),
                'cumulus__none'
            ) AS enc_class_display,
            coalesce(
                cast(age_at_visit AS varchar),
                'cumulus__none'
            ) AS age_at_visit,
            coalesce(
                cast(ed_note AS varchar),
                'cumulus__none'
            ) AS ed_note,
            coalesce(
                cast(variant_era AS varchar),
                'cumulus__none'
            ) AS variant_era
        FROM filtered_table
    ),
    secondary_powerset AS (
        SELECT
            count(DISTINCT encounter_ref) AS cnt_encounter_ref,
            "cond_week",
            "enc_class_display",
            "age_at_visit",
            "ed_note",
            "variant_era",
            concat_ws(
                '-',
                COALESCE("cond_week",''),
                COALESCE("enc_class_display",''),
                COALESCE("age_at_visit",''),
                COALESCE("ed_note",''),
                COALESCE("variant_era",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "cond_week",
            "enc_class_display",
            "age_at_visit",
            "ed_note",
            "variant_era"
            )
    ),

    powerset AS (
        SELECT
            count(DISTINCT subject_ref) AS cnt_subject_ref,
            "cond_week",
            "enc_class_display",
            "age_at_visit",
            "ed_note",
            "variant_era",
            concat_ws(
                '-',
                COALESCE("cond_week",''),
                COALESCE("enc_class_display",''),
                COALESCE("age_at_visit",''),
                COALESCE("ed_note",''),
                COALESCE("variant_era",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "cond_week",
            "enc_class_display",
            "age_at_visit",
            "ed_note",
            "variant_era"
            )
    )

    SELECT
        s.cnt_encounter_ref AS cnt,
        p."cond_week",
        p."enc_class_display",
        p."age_at_visit",
        p."ed_note",
        p."variant_era"
    FROM powerset AS p
    JOIN secondary_powerset AS s on s.id = p.id
    WHERE
        cnt_subject_ref >= 10
        
);
CREATE TABLE covid_symptom__count_study_period_month AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            s.encounter_ref,
            --noqa: disable=RF03, AL02
            s."start_month",
            s."variant_era",
            s."ed_note",
            s."gender",
            s."age_group",
            s."race_display"
            --noqa: enable=RF03, AL02
        FROM covid_symptom__study_period AS s
        WHERE s.status = 'finished'
    ),
    
    null_replacement AS (
        SELECT
            subject_ref,
            encounter_ref,
            coalesce(
                cast(start_month AS varchar),
                'cumulus__none'
            ) AS start_month,
            coalesce(
                cast(variant_era AS varchar),
                'cumulus__none'
            ) AS variant_era,
            coalesce(
                cast(ed_note AS varchar),
                'cumulus__none'
            ) AS ed_note,
            coalesce(
                cast(gender AS varchar),
                'cumulus__none'
            ) AS gender,
            coalesce(
                cast(age_group AS varchar),
                'cumulus__none'
            ) AS age_group,
            coalesce(
                cast(race_display AS varchar),
                'cumulus__none'
            ) AS race_display
        FROM filtered_table
    ),
    secondary_powerset AS (
        SELECT
            count(DISTINCT encounter_ref) AS cnt_encounter_ref,
            "start_month",
            "variant_era",
            "ed_note",
            "gender",
            "age_group",
            "race_display",
            concat_ws(
                '-',
                COALESCE("start_month",''),
                COALESCE("variant_era",''),
                COALESCE("ed_note",''),
                COALESCE("gender",''),
                COALESCE("age_group",''),
                COALESCE("race_display",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "start_month",
            "variant_era",
            "ed_note",
            "gender",
            "age_group",
            "race_display"
            )
    ),

    powerset AS (
        SELECT
            count(DISTINCT subject_ref) AS cnt_subject_ref,
            "start_month",
            "variant_era",
            "ed_note",
            "gender",
            "age_group",
            "race_display",
            concat_ws(
                '-',
                COALESCE("start_month",''),
                COALESCE("variant_era",''),
                COALESCE("ed_note",''),
                COALESCE("gender",''),
                COALESCE("age_group",''),
                COALESCE("race_display",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "start_month",
            "variant_era",
            "ed_note",
            "gender",
            "age_group",
            "race_display"
            )
    )

    SELECT
        s.cnt_encounter_ref AS cnt,
        p."start_month",
        p."variant_era",
        p."ed_note",
        p."gender",
        p."age_group",
        p."race_display"
    FROM powerset AS p
    JOIN secondary_powerset AS s on s.id = p.id
    WHERE
        cnt_subject_ref >= 10
        
);
CREATE TABLE covid_symptom__count_study_period_week AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            s.encounter_ref,
            --noqa: disable=RF03, AL02
            s."start_week",
            s."variant_era",
            s."ed_note",
            s."gender",
            s."age_group",
            s."race_display"
            --noqa: enable=RF03, AL02
        FROM covid_symptom__study_period AS s
        WHERE s.status = 'finished'
    ),
    
    null_replacement AS (
        SELECT
            subject_ref,
            encounter_ref,
            coalesce(
                cast(start_week AS varchar),
                'cumulus__none'
            ) AS start_week,
            coalesce(
                cast(variant_era AS varchar),
                'cumulus__none'
            ) AS variant_era,
            coalesce(
                cast(ed_note AS varchar),
                'cumulus__none'
            ) AS ed_note,
            coalesce(
                cast(gender AS varchar),
                'cumulus__none'
            ) AS gender,
            coalesce(
                cast(age_group AS varchar),
                'cumulus__none'
            ) AS age_group,
            coalesce(
                cast(race_display AS varchar),
                'cumulus__none'
            ) AS race_display
        FROM filtered_table
    ),
    secondary_powerset AS (
        SELECT
            count(DISTINCT encounter_ref) AS cnt_encounter_ref,
            "start_week",
            "variant_era",
            "ed_note",
            "gender",
            "age_group",
            "race_display",
            concat_ws(
                '-',
                COALESCE("start_week",''),
                COALESCE("variant_era",''),
                COALESCE("ed_note",''),
                COALESCE("gender",''),
                COALESCE("age_group",''),
                COALESCE("race_display",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "start_week",
            "variant_era",
            "ed_note",
            "gender",
            "age_group",
            "race_display"
            )
    ),

    powerset AS (
        SELECT
            count(DISTINCT subject_ref) AS cnt_subject_ref,
            "start_week",
            "variant_era",
            "ed_note",
            "gender",
            "age_group",
            "race_display",
            concat_ws(
                '-',
                COALESCE("start_week",''),
                COALESCE("variant_era",''),
                COALESCE("ed_note",''),
                COALESCE("gender",''),
                COALESCE("age_group",''),
                COALESCE("race_display",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "start_week",
            "variant_era",
            "ed_note",
            "gender",
            "age_group",
            "race_display"
            )
    )

    SELECT
        s.cnt_encounter_ref AS cnt,
        p."start_week",
        p."variant_era",
        p."ed_note",
        p."gender",
        p."age_group",
        p."race_display"
    FROM powerset AS p
    JOIN secondary_powerset AS s on s.id = p.id
    WHERE
        cnt_subject_ref >= 10
        
);
CREATE TABLE covid_symptom__count_symptom_week AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            s.encounter_ref,
            --noqa: disable=RF03, AL02
            s."author_week",
            s."symptom_display",
            s."variant_era",
            s."age_group",
            s."gender",
            s."race_display",
            s."enc_class_display",
            s."ed_note"
            --noqa: enable=RF03, AL02
        FROM covid_symptom__symptom_ctakes_negation AS s
        WHERE s.status = 'finished'
    ),
    
    null_replacement AS (
        SELECT
            subject_ref,
            encounter_ref,
            coalesce(
                cast(author_week AS varchar),
                'cumulus__none'
            ) AS author_week,
            coalesce(
                cast(symptom_display AS varchar),
                'cumulus__none'
            ) AS symptom_display,
            coalesce(
                cast(variant_era AS varchar),
                'cumulus__none'
            ) AS variant_era,
            coalesce(
                cast(age_group AS varchar),
                'cumulus__none'
            ) AS age_group,
            coalesce(
                cast(gender AS varchar),
                'cumulus__none'
            ) AS gender,
            coalesce(
                cast(race_display AS varchar),
                'cumulus__none'
            ) AS race_display,
            coalesce(
                cast(enc_class_display AS varchar),
                'cumulus__none'
            ) AS enc_class_display,
            coalesce(
                cast(ed_note AS varchar),
                'cumulus__none'
            ) AS ed_note
        FROM filtered_table
    ),
    secondary_powerset AS (
        SELECT
            count(DISTINCT encounter_ref) AS cnt_encounter_ref,
            "author_week",
            "symptom_display",
            "variant_era",
            "age_group",
            "gender",
            "race_display",
            "enc_class_display",
            "ed_note",
            concat_ws(
                '-',
                COALESCE("author_week",''),
                COALESCE("symptom_display",''),
                COALESCE("variant_era",''),
                COALESCE("age_group",''),
                COALESCE("gender",''),
                COALESCE("race_display",''),
                COALESCE("enc_class_display",''),
                COALESCE("ed_note",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "author_week",
            "symptom_display",
            "variant_era",
            "age_group",
            "gender",
            "race_display",
            "enc_class_display",
            "ed_note"
            )
    ),

    powerset AS (
        SELECT
            count(DISTINCT subject_ref) AS cnt_subject_ref,
            "author_week",
            "symptom_display",
            "variant_era",
            "age_group",
            "gender",
            "race_display",
            "enc_class_display",
            "ed_note",
            concat_ws(
                '-',
                COALESCE("author_week",''),
                COALESCE("symptom_display",''),
                COALESCE("variant_era",''),
                COALESCE("age_group",''),
                COALESCE("gender",''),
                COALESCE("race_display",''),
                COALESCE("enc_class_display",''),
                COALESCE("ed_note",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "author_week",
            "symptom_display",
            "variant_era",
            "age_group",
            "gender",
            "race_display",
            "enc_class_display",
            "ed_note"
            )
    )

    SELECT
        s.cnt_encounter_ref AS cnt,
        p."author_week",
        p."symptom_display",
        p."variant_era",
        p."age_group",
        p."gender",
        p."race_display",
        p."enc_class_display",
        p."ed_note"
    FROM powerset AS p
    JOIN secondary_powerset AS s on s.id = p.id
    WHERE 
        cnt_subject_ref >= 10
);
CREATE TABLE covid_symptom__count_symptom_month AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            s.encounter_ref,
            --noqa: disable=RF03, AL02
            s."author_month",
            s."symptom_display",
            s."variant_era",
            s."age_group",
            s."gender",
            s."race_display",
            s."enc_class_display",
            s."ed_note"
            --noqa: enable=RF03, AL02
        FROM covid_symptom__symptom_ctakes_negation AS s
        WHERE s.status = 'finished'
    ),
    
    null_replacement AS (
        SELECT
            subject_ref,
            encounter_ref,
            coalesce(
                cast(author_month AS varchar),
                'cumulus__none'
            ) AS author_month,
            coalesce(
                cast(symptom_display AS varchar),
                'cumulus__none'
            ) AS symptom_display,
            coalesce(
                cast(variant_era AS varchar),
                'cumulus__none'
            ) AS variant_era,
            coalesce(
                cast(age_group AS varchar),
                'cumulus__none'
            ) AS age_group,
            coalesce(
                cast(gender AS varchar),
                'cumulus__none'
            ) AS gender,
            coalesce(
                cast(race_display AS varchar),
                'cumulus__none'
            ) AS race_display,
            coalesce(
                cast(enc_class_display AS varchar),
                'cumulus__none'
            ) AS enc_class_display,
            coalesce(
                cast(ed_note AS varchar),
                'cumulus__none'
            ) AS ed_note
        FROM filtered_table
    ),
    secondary_powerset AS (
        SELECT
            count(DISTINCT encounter_ref) AS cnt_encounter_ref,
            "author_month",
            "symptom_display",
            "variant_era",
            "age_group",
            "gender",
            "race_display",
            "enc_class_display",
            "ed_note",
            concat_ws(
                '-',
                COALESCE("author_month",''),
                COALESCE("symptom_display",''),
                COALESCE("variant_era",''),
                COALESCE("age_group",''),
                COALESCE("gender",''),
                COALESCE("race_display",''),
                COALESCE("enc_class_display",''),
                COALESCE("ed_note",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "author_month",
            "symptom_display",
            "variant_era",
            "age_group",
            "gender",
            "race_display",
            "enc_class_display",
            "ed_note"
            )
    ),

    powerset AS (
        SELECT
            count(DISTINCT subject_ref) AS cnt_subject_ref,
            "author_month",
            "symptom_display",
            "variant_era",
            "age_group",
            "gender",
            "race_display",
            "enc_class_display",
            "ed_note",
            concat_ws(
                '-',
                COALESCE("author_month",''),
                COALESCE("symptom_display",''),
                COALESCE("variant_era",''),
                COALESCE("age_group",''),
                COALESCE("gender",''),
                COALESCE("race_display",''),
                COALESCE("enc_class_display",''),
                COALESCE("ed_note",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "author_month",
            "symptom_display",
            "variant_era",
            "age_group",
            "gender",
            "race_display",
            "enc_class_display",
            "ed_note"
            )
    )

    SELECT
        s.cnt_encounter_ref AS cnt,
        p."author_month",
        p."symptom_display",
        p."variant_era",
        p."age_group",
        p."gender",
        p."race_display",
        p."enc_class_display",
        p."ed_note"
    FROM powerset AS p
    JOIN secondary_powerset AS s on s.id = p.id
    WHERE 
        cnt_subject_ref >= 10
);
CREATE TABLE covid_symptom__count_prevalence_ed_month AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            s.encounter_ref,
            --noqa: disable=RF03, AL02
            s."author_month",
            s."covid_dx",
            s."covid_icd10",
            s."covid_pcr_result",
            s."covid_symptom",
            s."symptom_icd10_display",
            s."variant_era",
            s."age_group",
            s."enc_class_display"
            --noqa: enable=RF03, AL02
        FROM covid_symptom__prevalence_ed AS s
        WHERE s.status = 'finished'
    ),
    
    null_replacement AS (
        SELECT
            subject_ref,
            encounter_ref,
            coalesce(
                cast(author_month AS varchar),
                'cumulus__none'
            ) AS author_month,
            coalesce(
                cast(covid_dx AS varchar),
                'cumulus__none'
            ) AS covid_dx,
            coalesce(
                cast(covid_icd10 AS varchar),
                'cumulus__none'
            ) AS covid_icd10,
            coalesce(
                cast(covid_pcr_result AS varchar),
                'cumulus__none'
            ) AS covid_pcr_result,
            coalesce(
                cast(covid_symptom AS varchar),
                'cumulus__none'
            ) AS covid_symptom,
            coalesce(
                cast(symptom_icd10_display AS varchar),
                'cumulus__none'
            ) AS symptom_icd10_display,
            coalesce(
                cast(variant_era AS varchar),
                'cumulus__none'
            ) AS variant_era,
            coalesce(
                cast(age_group AS varchar),
                'cumulus__none'
            ) AS age_group,
            coalesce(
                cast(enc_class_display AS varchar),
                'cumulus__none'
            ) AS enc_class_display
        FROM filtered_table
    ),
    secondary_powerset AS (
        SELECT
            count(DISTINCT encounter_ref) AS cnt_encounter_ref,
            "author_month",
            "covid_dx",
            "covid_icd10",
            "covid_pcr_result",
            "covid_symptom",
            "symptom_icd10_display",
            "variant_era",
            "age_group",
            "enc_class_display",
            concat_ws(
                '-',
                COALESCE("author_month",''),
                COALESCE("covid_dx",''),
                COALESCE("covid_icd10",''),
                COALESCE("covid_pcr_result",''),
                COALESCE("covid_symptom",''),
                COALESCE("symptom_icd10_display",''),
                COALESCE("variant_era",''),
                COALESCE("age_group",''),
                COALESCE("enc_class_display",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "author_month",
            "covid_dx",
            "covid_icd10",
            "covid_pcr_result",
            "covid_symptom",
            "symptom_icd10_display",
            "variant_era",
            "age_group",
            "enc_class_display"
            )
    ),

    powerset AS (
        SELECT
            count(DISTINCT subject_ref) AS cnt_subject_ref,
            "author_month",
            "covid_dx",
            "covid_icd10",
            "covid_pcr_result",
            "covid_symptom",
            "symptom_icd10_display",
            "variant_era",
            "age_group",
            "enc_class_display",
            concat_ws(
                '-',
                COALESCE("author_month",''),
                COALESCE("covid_dx",''),
                COALESCE("covid_icd10",''),
                COALESCE("covid_pcr_result",''),
                COALESCE("covid_symptom",''),
                COALESCE("symptom_icd10_display",''),
                COALESCE("variant_era",''),
                COALESCE("age_group",''),
                COALESCE("enc_class_display",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "author_month",
            "covid_dx",
            "covid_icd10",
            "covid_pcr_result",
            "covid_symptom",
            "symptom_icd10_display",
            "variant_era",
            "age_group",
            "enc_class_display"
            )
    )

    SELECT
        s.cnt_encounter_ref AS cnt,
        p."author_month",
        p."covid_dx",
        p."covid_icd10",
        p."covid_pcr_result",
        p."covid_symptom",
        p."symptom_icd10_display",
        p."variant_era",
        p."age_group",
        p."enc_class_display"
    FROM powerset AS p
    JOIN secondary_powerset AS s on s.id = p.id
    WHERE 
        cnt_subject_ref >= 10
);
CREATE TABLE covid_symptom__count_prevalence_ed_week AS (
    WITH
    filtered_table AS (
        SELECT
            s.subject_ref,
            s.encounter_ref,
            --noqa: disable=RF03, AL02
            s."author_week",
            s."covid_dx",
            s."covid_icd10",
            s."covid_pcr_result",
            s."covid_symptom",
            s."symptom_icd10_display",
            s."variant_era",
            s."age_group",
            s."enc_class_display"
            --noqa: enable=RF03, AL02
        FROM covid_symptom__prevalence_ed AS s
        WHERE s.status = 'finished'
    ),
    
    null_replacement AS (
        SELECT
            subject_ref,
            encounter_ref,
            coalesce(
                cast(author_week AS varchar),
                'cumulus__none'
            ) AS author_week,
            coalesce(
                cast(covid_dx AS varchar),
                'cumulus__none'
            ) AS covid_dx,
            coalesce(
                cast(covid_icd10 AS varchar),
                'cumulus__none'
            ) AS covid_icd10,
            coalesce(
                cast(covid_pcr_result AS varchar),
                'cumulus__none'
            ) AS covid_pcr_result,
            coalesce(
                cast(covid_symptom AS varchar),
                'cumulus__none'
            ) AS covid_symptom,
            coalesce(
                cast(symptom_icd10_display AS varchar),
                'cumulus__none'
            ) AS symptom_icd10_display,
            coalesce(
                cast(variant_era AS varchar),
                'cumulus__none'
            ) AS variant_era,
            coalesce(
                cast(age_group AS varchar),
                'cumulus__none'
            ) AS age_group,
            coalesce(
                cast(enc_class_display AS varchar),
                'cumulus__none'
            ) AS enc_class_display
        FROM filtered_table
    ),
    secondary_powerset AS (
        SELECT
            count(DISTINCT encounter_ref) AS cnt_encounter_ref,
            "author_week",
            "covid_dx",
            "covid_icd10",
            "covid_pcr_result",
            "covid_symptom",
            "symptom_icd10_display",
            "variant_era",
            "age_group",
            "enc_class_display",
            concat_ws(
                '-',
                COALESCE("author_week",''),
                COALESCE("covid_dx",''),
                COALESCE("covid_icd10",''),
                COALESCE("covid_pcr_result",''),
                COALESCE("covid_symptom",''),
                COALESCE("symptom_icd10_display",''),
                COALESCE("variant_era",''),
                COALESCE("age_group",''),
                COALESCE("enc_class_display",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "author_week",
            "covid_dx",
            "covid_icd10",
            "covid_pcr_result",
            "covid_symptom",
            "symptom_icd10_display",
            "variant_era",
            "age_group",
            "enc_class_display"
            )
    ),

    powerset AS (
        SELECT
            count(DISTINCT subject_ref) AS cnt_subject_ref,
            "author_week",
            "covid_dx",
            "covid_icd10",
            "covid_pcr_result",
            "covid_symptom",
            "symptom_icd10_display",
            "variant_era",
            "age_group",
            "enc_class_display",
            concat_ws(
                '-',
                COALESCE("author_week",''),
                COALESCE("covid_dx",''),
                COALESCE("covid_icd10",''),
                COALESCE("covid_pcr_result",''),
                COALESCE("covid_symptom",''),
                COALESCE("symptom_icd10_display",''),
                COALESCE("variant_era",''),
                COALESCE("age_group",''),
                COALESCE("enc_class_display",'')
            ) AS id
        FROM null_replacement
        GROUP BY
            cube(
            "author_week",
            "covid_dx",
            "covid_icd10",
            "covid_pcr_result",
            "covid_symptom",
            "symptom_icd10_display",
            "variant_era",
            "age_group",
            "enc_class_display"
            )
    )

    SELECT
        s.cnt_encounter_ref AS cnt,
        p."author_week",
        p."covid_dx",
        p."covid_icd10",
        p."covid_pcr_result",
        p."covid_symptom",
        p."symptom_icd10_display",
        p."variant_era",
        p."age_group",
        p."enc_class_display"
    FROM powerset AS p
    JOIN secondary_powerset AS s on s.id = p.id
    WHERE 
        cnt_subject_ref >= 10
);
