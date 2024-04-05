CREATE OR REPLACE VIEW covid_symptom__define_pcr_positive AS SELECT * FROM (
    VALUES
    ('http://snomed.info/sct', '10828004', 'Positive (qualifier value)'),
    ('http://snomed.info/sct', '11214006', 'Reactive (qualifier value)'),
    ('http://snomed.info/sct', '117006002', 'Weakly-reactive (qualifier value)'),
    ('http://snomed.info/sct', '260347006', 'Present + out of ++++ (qualifier value)'),
    ('http://snomed.info/sct', '260348001', 'Present ++ out of ++++ (qualifier value)'),
    (
        'http://snomed.info/sct',
        '260349009',
        'Present +++ out of ++++ (qualifier value)'
    ),
    (
        'http://snomed.info/sct',
        '260350009',
        'Present ++++ out of ++++ (qualifier value)'
    ),
    ('http://snomed.info/sct', '260351008', 'Just noticeable (qualifier value)'),
    ('http://snomed.info/sct', '260373001', 'Detected (qualifier value)'),
    ('http://snomed.info/sct', '260405006', 'Trace (qualifier value)'),
    ('http://snomed.info/sct', '260408008', 'Weakly positive (qualifier value)'),
    ('http://snomed.info/sct', '260411009', 'Presence findings (qualifier value)'),
    ('http://snomed.info/sct', '263654008', 'Abnormal (qualifier value)'),
    ('http://snomed.info/sct', '263776006', 'Heavy growth (qualifier value)'),
    ('http://snomed.info/sct', '263812008', 'Moderate growth (qualifier value)'),
    ('http://snomed.info/sct', '280415008', 'Abnormal result (qualifier value)'),
    ('http://snomed.info/sct', '373066001', 'Yes (qualifier value)'),
    ('http://snomed.info/sct', '410515003', 'Known present (qualifier value)'),
    ('http://snomed.info/sct', '410591008', 'Definitely present (qualifier value)'),
    ('http://snomed.info/sct', '410592001', 'Probably present (qualifier value)'),
    ('http://snomed.info/sct', '410605003', 'Confirmed present (qualifier value)'),
    ('http://snomed.info/sct', '43261007', 'Abnormal presence of (qualifier value)'),
    (
        'http://snomed.info/sct',
        '441517005',
        'Present two plus out of three plus (qualifier value)'
    ),
    (
        'http://snomed.info/sct',
        '441521003',
        'Present three plus out of three plus (qualifier value)'
    ),
    (
        'http://snomed.info/sct',
        '441614007',
        'Present one plus out of three plus (qualifier value)'
    ),
    ('http://snomed.info/sct', '46651001', 'Isolated (qualifier value)'),
    ('http://snomed.info/sct', '52101004', 'Present (qualifier value)'),
    ('http://snomed.info/sct', '61620004', 'True positive (qualifier value)'),
    ('http://snomed.info/sct', '7882003', 'Identified (qualifier value)'),
    ('http://snomed.info/sct', '89292003', 'Rare (qualifier value)')
) AS t (system, code, display); --noqa: AL05
