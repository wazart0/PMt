-- Directional hypergraph engine implementation
-- https://www.slideshare.net/quipo/rdbms-in-the-social-networks-age/36-Nodes_and_Edges_vertexsCREATE_TABLE
-- Caching ideas:
--  * check if edges table changed if not then use vertexs from cache (do not search again)



CREATE TABLE vertexs (
    id SERIAL PRIMARY KEY,
    -- Custom fields:
    vertex_type INTEGER
);

CREATE TABLE edges (
    source_vertex INTEGER NOT NULL REFERENCES vertexs(id) ON UPDATE CASCADE ON DELETE CASCADE,
    target_vertex INTEGER NOT NULL REFERENCES vertexs(id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (source_vertex, target_vertex),
    -- Custom fields:
    -- hierarchy BOOLEAN, -- if this required?
    -- dependency_type INTEGER, -- cannot remind why
    -- privileges_dependency BOOLEAN, -- can't remind why
    cost_dependency BOOLEAN,
    time_dependency BOOLEAN
);

ALTER TABLE edges ADD CONSTRAINT no_self_loops CHECK (source_vertex <> target_vertex);

SELECT * FROM edges WHERE source_vertex = 2;