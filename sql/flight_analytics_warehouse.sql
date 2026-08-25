USE flight_analytics;

-- 1. Airline Performance

SELECT
    c.carrier_code,

    COUNT(*) AS total_flights,

    SUM(f.cancelled) AS cancelled_flights,

    ROUND(
        100.0 * SUM(f.cancelled) / COUNT(*),
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
    
 
 
 -- 2. Airport Performance
    
USE flight_analytics;

SELECT
    a.airport_code,
    a.airport_name,

    COUNT(*) AS completed_departures,

    ROUND(
        AVG(f.dep_delay),
        2
    ) AS avg_departure_delay_minutes,

    SUM(
        CASE
            WHEN f.dep_delay > 15
            THEN 1
            ELSE 0
        END
    ) AS delayed_over_15_min,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN f.dep_delay > 15
                THEN 1
                ELSE 0
            END
        )
        / COUNT(*),
        2
    ) AS delay_over_15_rate_pct

FROM fact_flight f

JOIN dim_airport a
    ON f.origin_airport_id = a.airport_id

WHERE
    f.cancelled = 0
    AND f.diverted = 0
    AND f.dep_delay IS NOT NULL

GROUP BY
    a.airport_id,
    a.airport_code,
    a.airport_name

HAVING
    COUNT(*) >= 100

ORDER BY
    avg_departure_delay_minutes DESC

LIMIT 20;    


-- 3. Weather Impact
USE flight_analytics;

SELECT
    f.weather_severity,

    COUNT(*) AS flights,

    ROUND(
        AVG(f.arr_delay),
        2
    ) AS avg_arrival_delay_minutes,

    ROUND(
        AVG(f.dep_delay),
        2
    ) AS avg_departure_delay_minutes

FROM fact_flight f

WHERE
    f.cancelled = 0
    AND f.diverted = 0
    AND f.weather_severity <> 'unavailable'

GROUP BY
    f.weather_severity

ORDER BY
    avg_arrival_delay_minutes DESC;

-- 4. Route Performance
USE flight_analytics;

SELECT
    origin.airport_code AS origin,
    destination.airport_code AS destination,

    COUNT(*) AS completed_flights,

    ROUND(
        AVG(f.dep_delay),
        2
    ) AS avg_departure_delay_minutes,

    ROUND(
        AVG(f.arr_delay),
        2
    ) AS avg_arrival_delay_minutes

FROM fact_flight f

JOIN dim_airport origin
    ON f.origin_airport_id = origin.airport_id

JOIN dim_airport destination
    ON f.destination_airport_id = destination.airport_id

WHERE
    f.cancelled = 0
    AND f.diverted = 0
    AND f.dep_delay IS NOT NULL
    AND f.arr_delay IS NOT NULL

GROUP BY
    origin.airport_code,
    destination.airport_code

HAVING
    COUNT(*) >= 100

ORDER BY
    avg_arrival_delay_minutes DESC

LIMIT 20;
