-- noqa: disable=LT05
CREATE OR REPLACE VIEW covid_symptom__define_pcr AS SELECT * FROM (
    VALUES
    (
        'http://loinc.org',
        '94309-2',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Unspecified specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94500-6',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Respiratory specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94565-9',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Nasopharynx by NAA with non-probe detection'
    ),
    (
        'http://loinc.org',
        '94660-8',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Serum or Plasma by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94759-8',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Nasopharynx by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94819-0',
        'SARS-CoV-2 (COVID-19) RNA [Log #/volume] (viral load) in Unspecified specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94822-4',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Saliva (oral fluid) by Sequencing'
    ),
    (
        'http://loinc.org',
        '94845-5',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Saliva (oral fluid) by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '95406-5',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Nose by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '95424-8',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Respiratory specimen by Sequencing'
    ),
    (
        'http://loinc.org',
        '95608-6',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Respiratory specimen by NAA with non-probe detection'
    ),
    (
        'http://loinc.org',
        '94307-6',
        'SARS-CoV-2 (COVID-19) N gene [Presence] in Specimen by Nucleic acid amplification using CDC primer-probe set N1'
    ),
    (
        'http://loinc.org',
        '94308-4',
        'SARS-CoV-2 (COVID-19) N gene [Presence] in Specimen by Nucleic acid amplification using CDC primer-probe set N2'
    ),
    (
        'http://loinc.org',
        '94309-2',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94314-2',
        'SARS-CoV-2 (COVID-19) RdRp gene [Presence] in Specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94316-7',
        'SARS-CoV-2 (COVID-19) N gene [Presence] in Specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94500-6',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Respiratory specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94533-7',
        'SARS-CoV-2 (COVID-19) N gene [Presence] in Respiratory specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94534-5',
        'SARS-CoV-2 (COVID-19) RdRp gene [Presence] in Respiratory specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94559-2',
        'SARS-CoV-2 (COVID-19) ORF1ab region [Presence] in Respiratory specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94565-9',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Nasopharynx by NAA with non-probe detection'
    ),
    (
        'http://loinc.org',
        '94639-2',
        'SARS-CoV-2 (COVID-19) ORF1ab region [Presence] in Specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94640-0',
        'SARS-CoV-2 (COVID-19) S gene [Presence] in Respiratory specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94641-8',
        'SARS-CoV-2 (COVID-19) S gene [Presence] in Specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94660-8',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Serum or Plasma by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94756-4',
        'SARS-CoV-2 (COVID-19) N gene [Presence] in Respiratory specimen by Nucleic acid amplification using CDC primer-probe set N1'
    ),
    (
        'http://loinc.org',
        '94757-2',
        'SARS-CoV-2 (COVID-19) N gene [Presence] in Respiratory specimen by Nucleic acid amplification using CDC primer-probe set N2'
    ),
    (
        'http://loinc.org',
        '94759-8',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Nasopharynx by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94766-3',
        'SARS-CoV-2 (COVID-19) N gene [Presence] in Serum or Plasma by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94767-1',
        'SARS-CoV-2 (COVID-19) S gene [Presence] in Serum or Plasma by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '94845-5',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Saliva (oral fluid) by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '95406-5',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Nose by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '95409-9',
        'SARS-CoV-2 (COVID-19) N gene [Presence] in Nose by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '95425-5',
        'SARS-CoV-2 (COVID-19) N gene [Presence] in Saliva (oral fluid) by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '95608-6',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Respiratory specimen by NAA with non-probe detection'
    ),
    (
        'http://loinc.org',
        '95824-9',
        'SARS-CoV-2 (COVID-19) ORF1ab region [Presence] in Saliva (oral fluid) by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '96091-4',
        'SARS-CoV-2 (COVID-19) RdRp gene [Presence] in Saliva (oral fluid) by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '96120-1',
        'SARS-CoV-2 (COVID-19) RdRp gene [Presence] in Lower respiratory specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '96123-5',
        'SARS-CoV-2 (COVID-19) RdRp gene [Presence] in Upper respiratory specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '96448-6',
        'SARS-CoV-2 (COVID-19) N gene [Presence] in Saliva (oral fluid) by Nucleic acid amplification using CDC primer-probe set N1'
    ),
    (
        'http://loinc.org',
        '96763-8',
        'SARS-CoV-2 (COVID-19) E gene [Presence] in Respiratory specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '96765-3',
        'SARS-CoV-2 (COVID-19) S gene [Presence] in Saliva (oral fluid) by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '96797-6',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Oropharyngeal wash by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '96829-7',
        'SARS-CoV-2 (COVID-19) RNA [Presence] in Specimen from Donor by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '96957-6',
        'SARS-CoV-2 (COVID-19) M gene [Presence] in Upper respiratory specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '96958-4',
        'SARS-CoV-2 (COVID-19) N gene [Presence] in Saliva (oral fluid) by Nucleic acid amplification using CDC primer-probe set N2'
    ),
    (
        'http://loinc.org',
        '96986-5',
        'SARS-CoV-2 (COVID-19) N gene [Presence] in Nose by NAA with non-probe detection'
    ),
    (
        'http://loinc.org',
        '97098-8',
        'SARS-CoV-2 (COVID-19) Nsp2 gene [Presence] in Upper respiratory specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '98131-6',
        'SARS-CoV-2 (COVID-19) ORF1b region [Presence] in Respiratory specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '98132-4',
        'SARS-CoV-2 (COVID-19) ORF1a region [Presence] in Respiratory specimen by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '98493-0',
        'SARS-CoV-2 (COVID-19) ORF1b region [Presence] in Saliva (oral fluid) by NAA with probe detection'
    ),
    (
        'http://loinc.org',
        '98494-8',
        'SARS-CoV-2 (COVID-19) ORF1a region [Presence] in Saliva (oral fluid) by NAA with probe detection'
    )
) AS t (system, code, display); --noqa: AL05
