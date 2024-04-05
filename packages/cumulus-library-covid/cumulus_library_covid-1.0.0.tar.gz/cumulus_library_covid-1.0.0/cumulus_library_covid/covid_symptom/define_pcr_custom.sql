-- http://hl7.org/fhir/R4/v3/ObservationInterpretation/cs.html#v3-ObservationInterpretation-ObservationInterpretationDetection
--
--code=POS
--	display=Positive
--		A presence finding of the specified component / analyte, organism or clinical sign based on the established threshold of the performed test or procedure.
--code=NEG
--    display=Negative
--        An absence finding of the specified component / analyte, organism or clinical sign based on the established threshold of the performed test or procedure.

CREATE OR REPLACE VIEW covid_symptom__define_pcr_custom AS SELECT * FROM (
    VALUES
    (
        'http://cumulus.smarthealthit.org',
        'Negative',
        'Negative',
        'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation',
        'NEG',
        'Negative'
    ),
    (
        'http://cumulus.smarthealthit.org',
        'NEGATIVE',
        'NEGATIVE',
        'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation',
        'NEG',
        'Negative'
    ),
    (
        'http://cumulus.smarthealthit.org',
        'Positive',
        'Positive',
        'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation',
        'POS',
        'Positive'
    ),
    (
        'http://cumulus.smarthealthit.org',
        'POSITIVE',
        'POSITIVE',
        'http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation',
        'POS',
        'Positive'
    )
) AS t (from_system, from_code, from_display, system, code, display); --noqa: AL05
