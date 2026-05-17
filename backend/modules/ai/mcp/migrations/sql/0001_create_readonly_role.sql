-- Reference file. The Python command `mcp_setup_db` reproduces these
-- statements via psycopg with safe identifier/literal binding. Do not
-- execute this file directly.

CREATE ROLE poupix_mcp_ro WITH LOGIN PASSWORD '<set-by-command>';

REVOKE ALL ON ALL TABLES IN SCHEMA public FROM poupix_mcp_ro;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM poupix_mcp_ro;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM poupix_mcp_ro;
REVOKE CREATE ON SCHEMA public FROM poupix_mcp_ro;
REVOKE CREATE ON DATABASE poupix FROM poupix_mcp_ro;

GRANT USAGE ON SCHEMA public TO poupix_mcp_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO poupix_mcp_ro;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT ON TABLES TO poupix_mcp_ro;
