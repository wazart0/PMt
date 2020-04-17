-- Directional hypergraph engine implementation
-- https://www.slideshare.net/quipo/rdbms-in-the-social-networks-age/36-Nodes_and_Edges_nodesCREATE_TABLE
-- Caching ideas:
--  * check if edges table changed if not then use nodes from cache (do not search again)



CREATE TABLE nodes (
    id SERIAL PRIMARY KEY,
    -- Custom fields:
    node_type INTEGER
);

CREATE TABLE edges (
    source_node INTEGER NOT NULL REFERENCES nodes(id) ON UPDATE CASCADE ON DELETE CASCADE,
    target_node INTEGER NOT NULL REFERENCES nodes(id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (source_node, target_node),
    -- Custom fields:
    -- hierarchy BOOLEAN, -- if this required?
    -- dependency_type INTEGER, -- cannot remind why
    -- privileges_dependency BOOLEAN, -- can't remind why
    cost_dependency BOOLEAN,
    time_dependency BOOLEAN
);

ALTER TABLE edges ADD CONSTRAINT no_self_loops CHECK (source_node <> target_node);

SELECT * FROM edges WHERE source_node = 2;