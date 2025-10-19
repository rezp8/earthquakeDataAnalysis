-- name: histogramS
SELECT 
source, magnitude
FROM earthquakes
WHERE magnitude IS NOT NULL;

-- name: Linear
SELECT DATE(time) AS day,  -- تاریخ روز
    COUNT(*) AS total_quakes, -- تعداد زلزله‌های آن روز
    ROUND(AVG(magnitude), 2) AS avg_magnitude -- میانگین بزرگی زلزله‌ها
FROM earthquakes
WHERE magnitude IS NOT NULL
GROUP BY day
ORDER BY day;

-- name: Scattering
SELECT depth, magnitude, region, source
FROM earthquakes
WHERE depth IS NOT NULL AND magnitude IS NOT NULL
ORDER BY magnitude DESC;
-- name: Scattering2
SELECT time, magnitude, region, source
FROM earthquakes
WHERE magnitude IS NOT NULL
ORDER BY time;

-- name: boxPlot
SELECT
  CASE
    WHEN depth < 70  THEN 'Shallow (0–70 km)'
    WHEN depth < 300 THEN 'Intermediate (70–300 km)'
    WHEN depth <= 700 THEN 'Deep (300–700 km)'
    ELSE 'Out of range'
  END AS depth_zone,
  magnitude
FROM earthquakes
WHERE depth IS NOT NULL
  AND magnitude IS NOT NULL
ORDER BY FIELD(depth_zone,
  'Shallow (0–70 km)', 'Intermediate (70–300 km)', 'Deep (300–700 km)', 'Out of range');
  
-- name: heatmap
SELECT 
    ROUND(latitude, 1) AS lat,
    ROUND(longitude, 1) AS lon,
    COUNT(*) AS quake_count
FROM earthquakes
WHERE latitude IS NOT NULL 
  AND longitude IS NOT NULL
GROUP BY lat, lon
ORDER BY quake_count DESC;

-- name: heatmap2
SELECT
  CASE
    WHEN latitude < 28.8 THEN 'Lat 1 (24–28.8°N)'
    WHEN latitude < 33.6 THEN 'Lat 2 (28.8–33.6°N)'
    WHEN latitude < 38.4 THEN 'Lat 3 (33.6–38.4°N)'
    ELSE 'Lat 4 (38.4–43.1°N)'
  END AS lat_range,
  CASE
    WHEN longitude < 128.5 THEN 'Lon 1 (123–128.5°E)'
    WHEN longitude < 134.0 THEN 'Lon 2 (128.5–134°E)'
    WHEN longitude < 139.5 THEN 'Lon 3 (134–139.5°E)'
    ELSE 'Lon 4 (139.5–145°E)'
  END AS lon_range,

  COUNT(*) AS quake_count
FROM earthquakes
WHERE latitude BETWEEN 24 AND 43.1
  AND longitude BETWEEN 123 AND 145
GROUP BY lat_range, lon_range
ORDER BY lat_range, lon_range;

-- name: heatmapEx
SELECT	
	FLOOR(dist_to_Tokyo / 50) * 50 AS distance_range,
	COUNT(*) AS quake_count,
	ROUND(AVG(magnitude), 2) AS avg_magnitude,
	ROUND(AVG(depth), 1) AS avg_depth
FROM earthquakes
WHERE dist_to_Tokyo IS NOT NULL
GROUP BY distance_range
ORDER BY distance_range;



-- name: quakes_by_month_region
SELECT 
    month,
    region,
    COUNT(*) AS total_quakes
FROM earthquakes
GROUP BY month, region
ORDER BY month, total_quakes DESC;

-- name: region_source_avg_magnitude
SELECT 
    region,
    source,
    ROUND(AVG(magnitude), 2) AS avg_magnitude,
    COUNT(*) AS total_quakes
FROM earthquakes
WHERE magnitude IS NOT NULL
GROUP BY region, source
ORDER BY avg_magnitude DESC;

-- name: recent_top10_quakes
SELECT 
    time,
    region,
    source,
    magnitude,
    depth
FROM earthquakes
WHERE magnitude IS NOT NULL
ORDER BY magnitude DESC, time DESC
LIMIT 10;

-- name: region_depth_extremes
SELECT 
    region,
    MIN(depth) AS min_depth,
    MAX(depth) AS max_depth
FROM earthquakes
WHERE depth IS NOT NULL
GROUP BY region
ORDER BY max_depth DESC;

-- name: filtered_outlier_removed
SELECT *
FROM earthquakes
WHERE
    latitude NOT BETWEEN 20 AND 50
    OR longitude NOT BETWEEN 120 AND 155
    OR depth < 0
    OR depth > 700
    OR magnitude < 0
    OR magnitude > 10;








