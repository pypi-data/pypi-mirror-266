-- noqa: disable=LT05
CREATE OR REPLACE VIEW covid_symptom__define_dx_snomed AS SELECT * FROM (
    VALUES
    (
        'http://snomed.info/sct',
        '1017214008',
        'Viremia caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '1119302008',
        'Acute disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '119731000146105',
        'Cardiomyopathy due to disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '119741000146102',
        'Conjunctivitis due to disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '119751000146104',
        'Fever caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '119981000146107',
        'Dyspnea caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '1240521000000100',
        'Otitis media due to disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '1240531000000103',
        'Myocarditis due to disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '1240541000000107',
        'Infection of upper respiratory tract caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '1240561000000108',
        'Encephalopathy due to disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '1240581000000104',
        'Severe acute respiratory syndrome coronavirus 2 detected (finding)'
    ),
    (
        'http://snomed.info/sct',
        '138389411000119105',
        'Acute bronchitis caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '189486241000119100',
        'Asymptomatic severe acute respiratory syndrome coronavirus 2 infection (finding)'
    ),
    (
        'http://snomed.info/sct',
        '674814021000119106',
        'Acute respiratory distress syndrome due to disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '840539006',
        'Disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '866151004',
        'Lymphocytopenia due to severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '866152006',
        'Thrombocytopenia due to severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '870588003',
        'Sepsis due to disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '870589006',
        'Acute kidney injury due to disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '870590002',
        'Acute hypoxemic respiratory failure due to disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '870591003',
        'Rhabdomyolysis due to disease caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '880529761000119102',
        'Infection of lower respiratory tract caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    ),
    (
        'http://snomed.info/sct',
        '882784691000119100',
        'Pneumonia caused by severe acute respiratory syndrome coronavirus 2 (disorder)'
    )
) AS t (system, code, display); --noqa: AL05
