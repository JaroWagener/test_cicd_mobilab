-- Apache AGE Schema Setup for exo_graph
-- This script creates vertex and edge labels for the exo_graph database

-- Load AGE extension and set search path
LOAD 'age';
SET search_path = ag_catalog, "$user", public;

-- Create graph if it doesn't exist (handle existing graph gracefully)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'exo_graph') THEN
        PERFORM create_graph('exo_graph');
    END IF;
END
$$;

-- Create vertex labels (nodes) - each in its own transaction block to handle existing labels
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'Aim') THEN
        PERFORM create_vlabel('exo_graph', 'Aim');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'AimType') THEN
        PERFORM create_vlabel('exo_graph', 'AimType');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'Dof') THEN
        PERFORM create_vlabel('exo_graph', 'Dof');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'Exo') THEN
        PERFORM create_vlabel('exo_graph', 'Exo');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'ExoProperty') THEN
        PERFORM create_vlabel('exo_graph', 'ExoProperty');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'JointT') THEN
        PERFORM create_vlabel('exo_graph', 'JointT');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'Part') THEN
        PERFORM create_vlabel('exo_graph', 'Part');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'StructureKinematicName') THEN
        PERFORM create_vlabel('exo_graph', 'StructureKinematicName');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'StructureKinematicNameType') THEN
        PERFORM create_vlabel('exo_graph', 'StructureKinematicNameType');
    END IF;
END $$;

-- Create edge labels (relationships)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'ASSISTS_IN') THEN
        PERFORM create_elabel('exo_graph', 'ASSISTS_IN');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'DOESNT_GO_WITH') THEN
        PERFORM create_elabel('exo_graph', 'DOESNT_GO_WITH');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'GIVES_POSTURAL_SUPPORT_IN') THEN
        PERFORM create_elabel('exo_graph', 'GIVES_POSTURAL_SUPPORT_IN');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'GIVES_RESISTANCE_IN') THEN
        PERFORM create_elabel('exo_graph', 'GIVES_RESISTANCE_IN');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'HAS_AIM') THEN
        PERFORM create_elabel('exo_graph', 'HAS_AIM');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'HAS_AIM_SKN') THEN
        PERFORM create_elabel('exo_graph', 'HAS_AIM_SKN');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'HAS_AIMTYPE') THEN
        PERFORM create_elabel('exo_graph', 'HAS_AIMTYPE');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'HAS_AS_MAIN_DOF') THEN
        PERFORM create_elabel('exo_graph', 'HAS_AS_MAIN_DOF');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'HAS_DOF') THEN
        PERFORM create_elabel('exo_graph', 'HAS_DOF');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'HAS_PROPERTY') THEN
        PERFORM create_elabel('exo_graph', 'HAS_PROPERTY');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'HAS_SKNTYPE') THEN
        PERFORM create_elabel('exo_graph', 'HAS_SKNTYPE');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'IS_CONNECTED_WITH') THEN
        PERFORM create_elabel('exo_graph', 'IS_CONNECTED_WITH');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'LIMITS_IN') THEN
        PERFORM create_elabel('exo_graph', 'LIMITS_IN');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'TRANSFERS_FORCES_FROM') THEN
        PERFORM create_elabel('exo_graph', 'TRANSFERS_FORCES_FROM');
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM ag_catalog.ag_label WHERE name = 'TRANSFERS_FORCES_TO') THEN
        PERFORM create_elabel('exo_graph', 'TRANSFERS_FORCES_TO');
    END IF;
END $$;
