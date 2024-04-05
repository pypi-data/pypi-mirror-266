CREATE OR REPLACE VIEW covid_symptom__define_pcr_negative AS SELECT * FROM (
    VALUES
    ('http://snomed.info/sct', '131194007', 'Non-Reactive (qualifier value)'),
    (
        'http://snomed.info/sct',
        '168230009',
        'Sample direct microscopy no organism seen (finding)'
    ),
    ('http://snomed.info/sct', '17621005', 'Normal (qualifier value)'),
    ('http://snomed.info/sct', '23506009', 'Normal flora (finding)'),
    ('http://snomed.info/sct', '260385009', 'Negative (qualifier value)'),
    ('http://snomed.info/sct', '260389003', 'No reaction (qualifier value)'),
    ('http://snomed.info/sct', '260394003', 'Normal limits (qualifier value)'),
    ('http://snomed.info/sct', '260395002', 'Normal range (qualifier value)'),
    ('http://snomed.info/sct', '260415000', 'Not detected (qualifier value)'),
    ('http://snomed.info/sct', '264868006', 'No growth (qualifier value)'),
    ('http://snomed.info/sct', '264887000', 'Not isolated (qualifier value)'),
    ('http://snomed.info/sct', '2667000', 'Absent (qualifier value)'),
    ('http://snomed.info/sct', '272519000', 'Absence findings (qualifier value)'),
    ('http://snomed.info/sct', '27863008', 'No organisms seen (finding)'),
    ('http://snomed.info/sct', '280413001', 'Normal result (qualifier value)'),
    ('http://snomed.info/sct', '281297005', 'Analyte not detected (qualifier value)'),
    ('http://snomed.info/sct', '371928007', 'Not significant (qualifier value)'),
    ('http://snomed.info/sct', '373067005', 'No (qualifier value)'),
    (
        'http://snomed.info/sct',
        '435151000124100',
        'No acid fast organisms seen (finding)'
    ),
    (
        'http://snomed.info/sct',
        '444991000124106',
        'Repeatedly non-reactive (qualifier value)'
    ),
    (
        'http://snomed.info/sct',
        '449501000124109',
        'Within defined limits (qualifier value)'
    ),
    ('http://snomed.info/sct', '47492008', 'Not seen (qualifier value)')
) AS t (system, code, display); --noqa: AL05
