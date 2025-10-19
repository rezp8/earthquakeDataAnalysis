-- محاسبه تعداد کل زلزله ها به تفکیک ماه و منطقه 1
SELECT 
    month,
    region,
    COUNT(*) AS total_quakes
FROM earthquakes
GROUP BY month, region
ORDER BY month, total_quakes DESC;

-- محاسبه میانگین بزرگی در هر منطقه و منبع 2
SELECT 
    region,
    source,
    ROUND(AVG(magnitude), 2) AS avg_magnitude,
    COUNT(*) AS total_quakes
FROM earthquakes
WHERE magnitude IS NOT NULL
GROUP BY region, source
ORDER BY avg_magnitude DESC;

-- استخراج ده زلزله شدید اخیر 3
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

-- محاسبه بیشترین و کمترین عمق در هر منطقه 4
SELECT 
    region,
    MIN(depth) AS min_depth,
    MAX(depth) AS max_depth
FROM earthquakes
WHERE depth IS NOT NULL
GROUP BY region
ORDER BY max_depth DESC;

-- حذف داده های خارج از محدوده یا مشکوک 5
CREATE TABLE suspicious_quakes AS
SELECT * FROM earthquakes
WHERE
    latitude NOT BETWEEN 20 AND 50
    OR longitude NOT BETWEEN 120 AND 155
    OR depth < 0
    OR depth > 700
    OR magnitude < 0
    OR magnitude > 10;
	-- حالا از جدول اصلی حذفشون کن
DELETE FROM earthquakes
WHERE id IN (SELECT id FROM suspicious_quakes);    


-- نسخه select
SELECT *
FROM earthquakes
WHERE
    latitude NOT BETWEEN 20 AND 50
    OR longitude NOT BETWEEN 120 AND 155
    OR depth < 0
    OR depth > 700
    OR magnitude < 0
    OR magnitude > 10;
    
-- به روز رسانی داده های ناقص 6


-- تعریف شاخص برای ستون های پر جستوجو 7
ALTER TABLE earthquakes ADD INDEX idx_source (source);
SHOW INDEXES FROM earthquakes;


------------------------------------------------------------------

-- مصور سازی داده ها

-- توزیع بزرگی زلزله ها در هر شهر
SELECT CASE
    WHEN magnitude < 3 THEN '[0,3)'
    WHEN magnitude < 4 THEN '[3,4)'
    WHEN magnitude < 5 THEN '[4,5)'
    WHEN magnitude < 6 THEN '[5,6)'
    WHEN magnitude < 7 THEN '[6,7)'
    ELSE '[7,+)'
  END AS mag_range,
  COUNT(*) AS quake_count
FROM earthquakes
WHERE magnitude IS NOT NULL
GROUP BY mag_range
ORDER BY mag_range;
	-- به تفکیک هر شهر
SELECT region, magnitude
FROM earthquakes
WHERE magnitude IS NOT NULL;
    
SELECT
  region,
  CASE
    WHEN magnitude < 3 THEN '[0,3)'
    WHEN magnitude < 4 THEN '[3,4)'
    WHEN magnitude < 5 THEN '[4,5)'
    WHEN magnitude < 6 THEN '[5,6)'
    WHEN magnitude < 7 THEN '[6,7)'
    ELSE '[7,+)'
  END AS mag_range,
  COUNT(*) AS quake_count
FROM earthquakes
WHERE magnitude IS NOT NULL
GROUP BY region, mag_range
ORDER BY region, mag_range;
	-- به تفکیک منبع
SELECT source, magnitude
FROM earthquakes
WHERE magnitude IS NOT NULL;
    
SELECT
  source,
  CASE
    WHEN magnitude < 3 THEN '[0,3)'
    WHEN magnitude < 4 THEN '[3,4)'
    WHEN magnitude < 5 THEN '[4,5)'
    WHEN magnitude < 6 THEN '[5,6)'
    WHEN magnitude < 7 THEN '[6,7)'
    ELSE '[7,+)'
  END AS mag_range,
  COUNT(*) AS quake_count
FROM earthquakes
WHERE magnitude IS NOT NULL
GROUP BY source, mag_range
ORDER BY source, mag_range;

-- روند زمانی شمارش زلزله ها و میانگین بزرگی زلزله ها به ازای هر هفته یا هر روز
SELECT DATE(time) AS day,  -- تاریخ روز
    COUNT(*) AS total_quakes, -- تعداد زلزله‌های آن روز
    ROUND(AVG(magnitude), 2) AS avg_magnitude -- میانگین بزرگی زلزله‌ها
FROM earthquakes
WHERE magnitude IS NOT NULL
GROUP BY day
ORDER BY day;

-- بزرگی عمق زلزله یا بزرگی در برابر زمان (زلزله قوی تر معمولا در چه عمق یا چه زمانی اتفاق میوفته)
SELECT depth, magnitude, region, source
FROM earthquakes
WHERE depth IS NOT NULL AND magnitude IS NOT NULL
ORDER BY magnitude DESC;
	-- بزرگی در برابر زمان
SELECT time, magnitude, region, source
FROM earthquakes
WHERE magnitude IS NOT NULL
ORDER BY time;

-- مقایسه توزیع بزرگی با عمق زلزله (ایا زلزله های قوی تر در عمق بیشتری اتفاق میوفتن؟)
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

SELECT depth, magnitude
FROM earthquakes
WHERE depth IS NOT NULL
	AND magnitude IS NOT NULL
ORDER BY depth;


-- نقشه حرارتی توزیع زلزله ها با استفاده طول و عرض جغرافیایی
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

-- نقشه حرارتی زلزله های رخ داده با استفاده از فاصله کانونی زلزله تا توکیو
SELECT	
	FLOOR(dist_to_Tokyo / 50) * 50 AS distance_range,
	COUNT(*) AS quake_count,
	ROUND(AVG(magnitude), 2) AS avg_magnitude,
	ROUND(AVG(depth), 1) AS avg_depth
FROM earthquakes
WHERE dist_to_Tokyo IS NOT NULL
GROUP BY distance_range
ORDER BY distance_range;

------------------------------------------------------------------
-- نتیجه گیری و تحلیل نهایی

-- داده اینکه زلزله های شدید معمولا در چ عمقی رخ میدهند؟ 2
	-- ایا زلزله های قوی سطحی هستن یا در اعماق زیاد اتفاق میوفتند؟
SELECT
  CASE
    WHEN depth < 70 THEN 'Shallow (0–70 km)'
    WHEN depth < 300 THEN 'Intermediate (70–300 km)'
    WHEN depth <= 700 THEN 'Deep (300–700 km)'
    ELSE 'Out of range'
  END AS depth_zone,
  
  COUNT(*) AS quake_count, -- تعداد زلزله‌ها در هر بازه عمق
  ROUND(AVG(magnitude), 2) AS avg_magnitude, -- میانگین بزرگی زلزله‌ها
  MAX(magnitude) AS max_magnitude -- بزرگ‌ترین زلزله در هر بازه
FROM earthquakes
WHERE magnitude >= 5 -- فقط زلزله‌های شدید (۵ ریشتر به بالا)
  AND depth IS NOT NULL -- حذف مقادیر خالی
GROUP BY depth_zone
ORDER BY FIELD(depth_zone,
  'Shallow (0–70 km)',
  'Intermediate (70–300 km)',
  'Deep (300–700 km)',
  'Out of range');
  

-- رتبه بندی شدید ترین زلزله ها(عمق کم و شدت زیاد) 3
SELECT
  id, `time`, region, source, magnitude, depth
FROM earthquakes
WHERE magnitude IS NOT NULL
  AND depth IS NOT NULL
  AND depth >= 0 -- عمق منفی حذف
  AND depth < 70 -- سطحی (Shallow)
  AND magnitude >= 5 -- شدید
ORDER BY magnitude DESC, depth ASC
LIMIT 20; -- ۲۰ رخداد خطرناک‌تر

-- مقایسه تعداد زلزله های بزرگ در هر منبع 4
	-- (کدام منبع بیشترین زلزله های قوی را دارد)
SELECT 
  source,
  COUNT(*) AS large_quakes,
  ROUND(AVG(magnitude), 2) AS avg_magnitude,
  MAX(magnitude) AS max_magnitude
FROM earthquakes
WHERE magnitude >= 5
GROUP BY source
ORDER BY large_quakes DESC;
--------------------------------------------------
SELECT
  source,
  CASE
    WHEN magnitude < 4 THEN '[0–4)'
    WHEN magnitude < 5 THEN '[4–5)'
    WHEN magnitude < 6 THEN '[5–6)'
    WHEN magnitude < 7 THEN '[6–7)'
    ELSE '[7,+)'
  END AS mag_range,
  COUNT(*) AS quake_count
FROM earthquakes
WHERE magnitude IS NOT NULL
GROUP BY source, mag_range
ORDER BY source, mag_range;


--









