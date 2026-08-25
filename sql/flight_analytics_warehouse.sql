-- ============================================================
-- 01 AIRLINE PERFORMANCE
-- Flight Analytics Warehouse
-- ============================================================

USE flight_analytics;


-- ============================================================
-- QUERY 1
-- Overall airline performance
-- ============================================================

SELECT
    c.carrier_code,

    COUNT(*) AS total_flights,

    SUM(f.cancelled) AS cancelled_flights,

    SUM(f.diverted) AS diverted_flights,

    SUM(
        CASE
            WHEN f.cancelled = 0
             AND f.diverted = 0
            THEN 1
            ELSE 0
        END
    ) AS completed_flights,

    ROUND(
        100.0 * SUM(f.cancelled)
        / COUNT(*),
        2
    ) AS cancellation_rate_pct,

    ROUND(
        AVG(
            CASE
                WHEN f.cancelled = 0
                 AND f.diverted = 0
                THEN f.dep_delay
            END
        ),
        2
    ) AS avg_departure_delay_minutes,

    ROUND(
        AVG(
            CASE
                WHEN f.cancelled = 0
                 AND f.diverted = 0
                THEN f.arr_delay
            END
        ),
        2
    ) AS avg_arrival_delay_minutes

FROM fact_flight f

JOIN dim_carrier c
    ON f.carrier_id = c.carrier_id

GROUP BY
    c.carrier_code

ORDER BY
    avg_arrival_delay_minutes DESC;


-- ============================================================
-- QUERY 2
-- Airline delay performance
-- Only completed, non-diverted flights
-- ============================================================

SELECT
    c.carrier_code,

    COUNT(*) AS completed_flights,

    ROUND(
        AVG(f.dep_delay),
        2
    ) AS avg_departure_delay,

    ROUND(
        AVG(f.arr_delay),
        2
    ) AS avg_arrival_delay,

    ROUND(
        AVG(
            CASE
                WHEN f.arr_delay > 0
                THEN f.arr_delay
            END
        ),
        2
    ) AS avg_delay_when_delayed,

    SUM(
        CASE
            WHEN f.arr_delay > 15
            THEN 1
            ELSE 0
        END
    ) AS delayed_over_15_min,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN f.arr_delay > 15
                THEN 1
                ELSE 0
            END
        )
        / COUNT(*),
        2
    ) AS delay_over_15_rate_pct

FROM fact_flight f

JOIN dim_carrier c
    ON f.carrier_id = c.carrier_id

WHERE
    f.cancelled = 0
    AND f.diverted = 0
    AND f.arr_delay IS NOT NULL

GROUP BY
    c.carrier_code

ORDER BY
    delay_over_15_rate_pct DESC;


-- ============================================================
-- QUERY 3
-- Primary delay drivers by airline
-- ============================================================

SELECT
    c.carrier_code,

    f.primary_delay_driver,

    COUNT(*) AS flight_count,

    ROUND(
        100.0 * COUNT(*)
        / SUM(COUNT(*))
          OVER (
              PARTITION BY f.carrier_id
          ),
        2
    ) AS percentage_of_airline_flights

FROM fact_flight f

JOIN dim_carrier c
    ON f.carrier_id = c.carrier_id

GROUP BY
    c.carrier_id,
    c.carrier_code,
    f.primary_delay_driver

ORDER BY
    c.carrier_code,
    flight_count DESC;


-- ============================================================
-- QUERY 4
-- Delay category distribution by airline
-- ============================================================

SELECT
    c.carrier_code,

    f.delay_category,

    COUNT(*) AS flight_count,

    ROUND(
        100.0 * COUNT(*)
        / SUM(COUNT(*))
          OVER (
              PARTITION BY f.carrier_id
          ),
        2
    ) AS percentage_of_airline_flights

FROM fact_flight f

JOIN dim_carrier c
    ON f.carrier_id = c.carrier_id

GROUP BY
    c.carrier_id,
    c.carrier_code,
    f.delay_category

ORDER BY
    c.carrier_code,
    flight_count DESC;


-- ============================================================
-- QUERY 5
-- Weather impact by airline
-- ============================================================

SELECT
    c.carrier_code,

    COUNT(*) AS flights_with_weather,

    SUM(
        CASE
            WHEN f.weather_severity <> 'normal'
            THEN 1
            ELSE 0
        END
    ) AS flights_with_adverse_weather,

    ROUND(
        AVG(
            CASE
                WHEN f.weather_severity <> 'unavailable'
                THEN f.arr_delay
            END
        ),
        2
    ) AS avg_arrival_delay,

    ROUND(
        AVG(
            CASE
                WHEN f.weather_severity IN (
                    'precipitation',
                    'snow',
                    'high_wind'
                )
                THEN f.arr_delay
            END
        ),
        2
    ) AS avg_arrival_delay_adverse_weather

FROM fact_flight f

JOIN dim_carrier c
    ON f.carrier_id = c.carrier_id

WHERE
    f.cancelled = 0
    AND f.diverted = 0

GROUP BY
    c.carrier_code

ORDER BY
    avg_arrival_delay_adverse_weather DESC;


-- ============================================================
-- QUERY 6
-- Rank airlines by average arrival delay
-- ============================================================

WITH airline_metrics AS (

    SELECT
        c.carrier_code,

        AVG(f.arr_delay) AS avg_arrival_delay

    FROM fact_flight f

    JOIN dim_carrier c
        ON f.carrier_id = c.carrier_id

    WHERE
        f.cancelled = 0
        AND f.diverted = 0
        AND f.arr_delay IS NOT NULL

    GROUP BY
        c.carrier_code
)

SELECT
    carrier_code,

    ROUND(
        avg_arrival_delay,
        2
    ) AS avg_arrival_delay,

    RANK() OVER (
        ORDER BY avg_arrival_delay DESC
    ) AS delay_rank

FROM airline_metrics

ORDER BY
    delay_rank;


-- ============================================================
-- QUERY 7
-- Airline cancellation performance
-- ============================================================

SELECT
    c.carrier_code,

    COUNT(*) AS total_flights,

    SUM(f.cancelled) AS cancelled_flights,

    ROUND(
        100.0 * SUM(f.cancelled)
        / COUNT(*),
        2
    ) AS cancellation_rate_pct

FROM fact_flight f

JOIN dim_carrier c
    ON f.carrier_id = c.carrier_id

GROUP BY
    c.carrier_code

ORDER BY
    cancellation_rate_pct DESC;


-- ============================================================
-- END
-- ============================================================