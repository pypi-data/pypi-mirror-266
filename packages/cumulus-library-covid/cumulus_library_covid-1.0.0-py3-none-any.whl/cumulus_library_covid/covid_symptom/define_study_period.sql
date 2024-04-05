-- ############################################################################
-- COVID19 Study Period for Variant Eras
--
-- Variant eras are defined using COVID-19 data for Massachusetts from CoVariant [16].
-- Pre-Delta era was defined as March 1, 2020 to June 20, 2021
-- Delta era as June 21, 2021 to December 19, 2021
-- Omicron era as December 20, 2021 onwards.

CREATE OR REPLACE VIEW covid_symptom__define_period AS
SELECT
    t.variant_era,
    t.variant_start,
    t.variant_end
FROM (
    VALUES
    ('before-delta', date('2020-03-01'), date('2021-06-20')),
    ('delta', date('2021-06-21'), date('2021-12-19')),
    ('omicron', date('2021-12-20'), date('2022-06-01'))
)
    AS t (variant_era, variant_start, variant_end);
