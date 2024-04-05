""" Utility classes for verifying/generating covid sql definitions"""

from cumulus_library.schema.columns import Coding, Vocab
from cumulus_library.library.schema.typesystem import Period
from cumulus_library.library.schema.valueset import (
    ValueSet,
    ObservationInterpretationDetection,
)


class CovidDiagnosis(Coding):
    """
    COVID19 diagnosis is either coded (positive) or unknown.
    Lacking a coded diagnosis does not strictly imply no covid.
    """

    positive = ("Positive", "COVID Diagnosis recorded")
    none = ("NONE", "No COVID recorded")


class CovidPCR(Coding):
    """defininition for ICD PCR tests"""

    positive = (ObservationInterpretationDetection.positive.value, "Positive COVID PCR")
    negative = (ObservationInterpretationDetection.negative.value, "Negative COVID PCR")
    indeterminate = (
        ObservationInterpretationDetection.negative.value,
        "Indeterminate: COVID PCR performed but no pos/neg value",
    )
    none = ("NONE", "No COVID PCR result found")

    def __init__(self, code, display):
        super().__init__(code, display, ValueSet.ObservationInterpretation.url)


class CovidSymptom(Coding):
    """definition for ICD covid symptoms"""

    C0027424 = "Congestion or runny nose"
    C1260880 = "Congestion or runny nose"
    C0010200 = "Cough"
    C0850149 = "Cough"
    C0239134 = "Cough"
    C0011991 = "Diarrhea"
    C0015672 = "Fatigue"
    C0231218 = "Fatigue"
    C0085593 = "Fever or chills"
    C0015967 = "Fever or chills"
    C0085594 = "Fever or chills"
    C0018681 = "Headache"
    C0231528 = "Muscle or body aches"
    C0281856 = "Muscle or body aches"
    C0027497 = "Nausea or vomiting"
    C0042963 = "Nausea or vomiting"
    C0027498 = "Nausea or vomiting"
    C0003126 = "Loss of taste or smell"
    C1332239 = "Loss of taste or smell"
    C0013404 = "Dyspnea"
    C0242429 = "Sore throat"

    def __init__(self, display):
        super().__init__(self.name, display, Vocab.UMLS.url)


class CovidVariantEra(Coding):
    """
    -- Variant eras are defined using COVID-19 data for Massachusetts from CoVariant [16].
    -- Pre-Delta era was defined as March 1, 2020 to June 20, 2021
    -- Delta era as June 21, 2021 to December 19, 2021
    -- Omicron era as December 20, 2021 onwards.
    """

    before_covid = Period("2016-01-01", "2021-02-28").as_json()
    before_delta = Period("2020-03-01", "2021-06-20").as_json()
    delta = Period("2021-06-20", "2021-12-19").as_json()
    omicron = Period("2021-12-20").as_json()
