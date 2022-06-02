---
--- Creating and Populate the FVS_STANDINIT_PLOT_FT table
---
CREATE TABLE FVS_STANDINIT_PLOT_FT (
    STAND_ID VARCHAR (26),
    VARIANT VARCHAR (11),
    INV_YEAR FLOAT,
    --- The [...] are to delimit the inside incase you wanted spaces or smthg
    --- it's not really necessary
    --- see: https://stackoverflow.com/questions/9917196/meaning-of-square-brackets-in-ms-sql-table-designer
    [GROUPS] VARCHAR (200),
    ADDFILES VARCHAR (200),
    FVSKEYWORDS VARCHAR (200),
    REGION FLOAT,
    FOREST FLOAT,
    LOCATION FLOAT,
    AGE FLOAT,
    BASAL_AREA_FACTOR FLOAT,
    INV_PLOT_SIZE FLOAT,
    BRK_DBH FLOAT,
    NUM_PLOTS FLOAT,
    SAM_WT FLOAT,
    DG_TRANS FLOAT,
    DG_MEASURE FLOAT,
    SITE_SPECIES VARCHAR (8),
    SITE_INDEX FLOAT,
    STATE FLOAT --- No comma at the end !!!
);

--- Populate ID
INSERT INTO FVS_STANDINIT_PLOT_FT (STAND_ID)
SELECT DISTINCT STAND_ID
FROM FVS_PLOTINIT_PLOT_INVYEARST;

--- Remove '/' character ("n/a" => "na")
UPDATE FVS_STANDINIT_PLOT_FT
SET STAND_ID = "na"
WHERE STAND_ID = "n/a";



--- Set Average Ages
CREATE VIEW IF NOT EXISTS AVG_AGE AS
SELECT
    STAND_ID,
    ROUND(AVG(AGE)) AS AVERAGE_AGE
FROM FVS_STANDINIT_PLOT_INVYEARST
GROUP BY STAND_ID;

UPDATE FVS_STANDINIT_PLOT_FT
SET AGE = (
        SELECT
            AVERAGE_AGE
        FROM
            AVG_AGE
        WHERE
            AVG_AGE.STAND_ID = FVS_STANDINIT_PLOT_FT.STAND_ID
    );


--- Site Species
-- Step 1: Get info from STANDINIT
CREATE VIEW STANDINIT_CORES_BY_FT AS
SELECT
    STAND_ID,
    SITE_SPECIES,
    SITE_INDEX,
    COUNT(SITE_SPECIES) AS NUM_CORINGS,
    AVG(SITE_INDEX) AS AVG_SI
FROM FVS_STANDINIT_PLOT_INVYEARST
WHERE SITE_SPECIES > 1
GROUP BY
    STAND_ID,
    SITE_SPECIES
ORDER BY
    STAND_ID,
    -NUM_CORINGS;


CREATE VIEW STANDINIT_MAX_CORES_PER_FT_WITH_TIES AS
SELECT ALL_FT.*
FROM STANDINIT_CORES_BY_FT AS ALL_FT
    INNER JOIN (
        SELECT
            STAND_ID,
            MAX(NUM_CORINGS) AS MAX_CORINGS
        FROM STANDINIT_CORES_BY_FT
        GROUP BY STAND_ID
    ) AS MAX_PER_FT ON ALL_FT.STAND_ID = MAX_PER_FT.STAND_ID
    AND ALL_FT.NUM_CORINGS = MAX_PER_FT.MAX_CORINGS;


-- Tree View (used for tie breaks)

-- Count number of species per stand
CREATE VIEW TREEINIT_SPECIES_BY_FT AS
SELECT TREEINIT.STAND_ID, 
	TREEINIT.SPECIES AS SITE_SPECIES, 
	COUNT(TREEINIT.SPECIES) AS NUM_SPECIES 
FROM FVS_TREEINIT_PLOT_INVYEARST AS TREEINIT
GROUP BY TREEINIT.STAND_ID, 
	TREEINIT.SPECIES;

CREATE VIEW TREEINIT_MAX_SPECIES_PER_FT AS
SELECT STAND_ID, MAX(NUM_SPECIES) AS MAX_NUM_SPECIES
FROM TREEINIT_SPECIES_BY_FT INNER JOIN
	STANDINIT_MAX_CORES_PER_FT_WITH_TIES
USING (STAND_ID, SITE_SPECIES)
GROUP BY STAND_ID;


-- These two really can be turned into a natural join but izzz ok for now

CREATE VIEW STANDINIT_MAX_WITH_NUM_SPECIES AS
SELECT STAND_MAX.STAND_ID, STAND_MAX.SITE_SPECIES, TREE_SPECIES.NUM_SPECIES, STAND_MAX.AVG_SI
FROM STANDINIT_MAX_CORES_PER_FT_WITH_TIES AS STAND_MAX
	INNER JOIN TREEINIT_SPECIES_BY_FT AS TREE_SPECIES
ON STAND_MAX.STAND_ID = TREE_SPECIES.STAND_ID AND
	STAND_MAX.SITE_SPECIES = TREE_SPECIES.SITE_SPECIES;


CREATE VIEW STANDINIT_STAND_ID_SITE_SPECIES AS 
SELECT S.*
FROM STANDINIT_MAX_WITH_NUM_SPECIES AS S
	INNER JOIN TREEINIT_MAX_SPECIES_PER_FT AS T
ON
	S.STAND_ID = T.STAND_ID 
	AND S.NUM_SPECIES = T.MAX_NUM_SPECIES;

UPDATE FVS_STANDINIT_PLOT_FT
SET SITE_SPECIES = 
   (SELECT SITE_SPECIES 
	FROM STANDINIT_STAND_ID_SITE_SPECIES
	WHERE FVS_STANDINIT_PLOT_FT.STAND_ID = STANDINIT_STAND_ID_SITE_SPECIES.STAND_ID);

UPDATE FVS_STANDINIT_PLOT_FT
SET SITE_INDEX = 
   (SELECT AVG_SI 
	FROM STANDINIT_STAND_ID_SITE_SPECIES
	WHERE FVS_STANDINIT_PLOT_FT.STAND_ID = STANDINIT_STAND_ID_SITE_SPECIES.STAND_ID);


--
-- Fill in some more simple fields

-- Fill in num_plots
UPDATE FVS_STANDINIT_PLOT_FT
SET NUM_PLOTS = 
   (SELECT NUMBER_PLOTS 
	FROM 
	   (SELECT DISTINCT 
			STAND_ID, 
			COUNT(STAND_ID) AS NUMBER_PLOTS  
		FROM FVS_PLOTINIT_PLOT_INVYEARST
      -- FROM FVS_PLOTINIT_PLOT
		GROUP BY STAND_ID)
	WHERE STAND_ID = FVS_STANDINIT_PLOT_FT.STAND_ID);

-- Basal Area Factor
UPDATE FVS_STANDINIT_PLOT_FT
SET BASAL_AREA_FACTOR = 
   (SELECT BASAL_AREA_FACTOR 
	FROM FVS_STANDINIT_PLOT_INVYEARST
	WHERE STAND_ID = FVS_STANDINIT_PLOT_FT.STAND_ID);

-- INV_PLOT_SIZE
UPDATE FVS_STANDINIT_PLOT_FT
SET INV_PLOT_SIZE = 
   (SELECT INV_PLOT_SIZE 
	FROM FVS_STANDINIT_PLOT_INVYEARST
	WHERE STAND_ID = FVS_STANDINIT_PLOT_FT.STAND_ID);

-- BRK_DBH
UPDATE FVS_STANDINIT_PLOT_FT
SET BRK_DBH =
   (SELECT BRK_DBH 
	FROM FVS_STANDINIT_PLOT_INVYEARST
	WHERE STAND_ID = FVS_STANDINIT_PLOT_FT.STAND_ID);

-- STATE
UPDATE FVS_STANDINIT_PLOT_FT
SET STATE =
   (SELECT STATE 
	FROM FVS_STANDINIT_PLOT_INVYEARST
	WHERE STAND_ID = FVS_STANDINIT_PLOT_FT.STAND_ID);

-- VARIANT
UPDATE FVS_STANDINIT_PLOT_FT
SET VARIANT =
   (SELECT VARIANT 
	FROM FVS_STANDINIT_PLOT_INVYEARST
	WHERE STAND_ID = FVS_STANDINIT_PLOT_FT.STAND_ID);

-- DG_TRANS
UPDATE FVS_STANDINIT_PLOT_FT
SET DG_TRANS = 1.0;

-- DG_MEASURE
UPDATE FVS_STANDINIT_PLOT_FT
SET DG_MEASURE = 5.0;

-- FOREST
UPDATE FVS_STANDINIT_PLOT_FT
SET FOREST =
   (SELECT FOREST 
	FROM FVS_STANDINIT_PLOT_INVYEARST
	WHERE STAND_ID = FVS_STANDINIT_PLOT_FT.STAND_ID);

-- LOCATION
UPDATE FVS_STANDINIT_PLOT_FT
SET LOCATION =
   (SELECT LOCATION 
	FROM FVS_STANDINIT_PLOT_INVYEARST
	WHERE STAND_ID = FVS_STANDINIT_PLOT_FT.STAND_ID);

-- REGION
UPDATE FVS_STANDINIT_PLOT_FT
SET REGION =
   (SELECT REGION 
	FROM FVS_STANDINIT_PLOT_INVYEARST
	WHERE STAND_ID = FVS_STANDINIT_PLOT_FT.STAND_ID);

-- GROUPS
UPDATE FVS_STANDINIT_PLOT_FT
SET GROUPS = "All_FIA_ForestTypes";

-- INV_YEAR
UPDATE FVS_STANDINIT_PLOT_FT
SET INV_YEAR = 
   (SELECT INV_YEAR_AVG 
	FROM
	   (SELECT DISTINCT 
			STAND_ID, 
			INV_YEAR, 
			ROUND(AVG(INV_YEAR)) AS INV_YEAR_AVG 
		FROM FVS_STANDINIT_PLOT_INVYEARST   
		GROUP BY STAND_ID)_
	WHERE STAND_ID = FVS_STANDINIT_PLOT_FT.STAND_ID);







--
-- Edits to TREEINIT_INVYEARST & PLOTINIT_INVYEARST
--

UPDATE FVS_TREEINIT_PLOT_INVYEARST 
SET STAND_ID = "na"
WHERE STAND_ID = "n/a";

UPDATE FVS_PLOTINIT_PLOT_INVYEARST 
SET STAND_ID = "na"
WHERE STAND_ID = "n/a";


-- We need the STANDPLOT_ID columns to be unique, which is achieved
-- by concatenating STAND_ID to the beginning of them
UPDATE FVS_TREEINIT_PLOT_INVYEARST
SET STANDPLOT_ID = STAND_ID || '_' || STANDPLOT_ID;

UPDATE FVS_PLOTINIT_PLOT_INVYEARST
SET STANDPLOT_ID = STAND_ID || '_' || STANDPLOT_ID;




--
-- Renaming tables so FVS recognizes them
--

-- Renaming FVS_STANDINIT_PLOT_FT -> FVS_STANDINIT_PLOT
ALTER TABLE FVS_STANDINIT_PLOT
RENAME TO FVS_STANDINIT_PLOT_BU;

ALTER TABLE FVS_STANDINIT_PLOT_FT
RENAME TO FVS_STANDINIT_PLOT;

-- Renaming FVS_PLOTINIT_PLOT_INVYEARST -> FVS_PLOTINIT_PLOT
ALTER TABLE FVS_PLOTINIT_PLOT
RENAME TO FVS_PLOTINIT_PLOT_BU;

ALTER TABLE FVS_PLOTINIT_PLOT_INVYEARST
RENAME TO FVS_PLOTINIT_PLOT;

-- Renaming FVS_TREEINIT_PLOT_INVYEARST -> FVS_TREEINIT_PLOT
ALTER TABLE FVS_TREEINIT_PLOT
RENAME TO FVS_TREEINIT_PLOT_BU;

ALTER TABLE FVS_TREEINIT_PLOT_INVYEARST
RENAME TO FVS_TREEINIT_PLOT;

--ADD DATA INTO TREEVALUE BASED OFF OF CRCLASS DATA--
UPDATE FVS_TREEINIT_PLOT
SET TREEVALUE = 1 WHERE CRCLASS IN(1, 2, 3);

UPDATE FVS_TREEINIT_PLOT
SET TREEVALUE = 2 WHERE CRCLASS = 4;

UPDATE FVS_TREEINIT_PLOT
SET TREEVALUE = 3 WHERE CRCLASS = 5;







