SELECT
    id,
    place,
    title,
    mag,
    TO_TIMESTAMP(time / 1000) AT TIME ZONE 'UTC' AS formatted_time,
    latitude,
    longitude,
    CASE
        WHEN mag >= 5 THEN 'Major'
        ELSE 'Minor'
    END AS category
FROM {{ ref('earthquakes') }}
