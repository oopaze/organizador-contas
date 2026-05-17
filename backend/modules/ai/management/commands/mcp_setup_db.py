import psycopg2
from psycopg2 import sql
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Create the read-only Postgres role for the MCP server and grant "
        "SELECT-only privileges. Requires superuser DB credentials."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--admin-user",
            default="postgres",
            help="Superuser to connect as (default: postgres)",
        )
        parser.add_argument(
            "--admin-password",
            required=True,
            help="Password for the admin user",
        )

    def handle(self, *args, **opts):
        role = settings.MCP_DATABASE_USER
        password = settings.MCP_DATABASE_PASSWORD
        if not role:
            raise CommandError("MCP_DATABASE_USER must be set in .env")
        if not password:
            raise CommandError("MCP_DATABASE_PASSWORD must be set in .env")

        conn = psycopg2.connect(
            host=settings.DATABASES["default"]["HOST"],
            port=settings.DATABASES["default"]["PORT"],
            dbname=settings.DATABASES["default"]["NAME"],
            user=opts["admin_user"],
            password=opts["admin_password"],
        )
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                role_ident = sql.Identifier(role)
                self._run(cur, sql.SQL(
                    "DROP ROLE IF EXISTS {role}"
                ).format(role=role_ident))
                self._run(cur, sql.SQL(
                    "CREATE ROLE {role} WITH LOGIN PASSWORD %s"
                ).format(role=role_ident), [password])
                for stmt in [
                    "REVOKE ALL ON ALL TABLES IN SCHEMA public FROM {role}",
                    "REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM {role}",
                    "REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM {role}",
                    "REVOKE CREATE ON SCHEMA public FROM {role}",
                    "REVOKE CREATE ON DATABASE "
                    + settings.DATABASES["default"]["NAME"]
                    + " FROM {role}",
                    "GRANT USAGE ON SCHEMA public TO {role}",
                    "GRANT SELECT ON ALL TABLES IN SCHEMA public TO {role}",
                    "ALTER DEFAULT PRIVILEGES IN SCHEMA public "
                    "GRANT SELECT ON TABLES TO {role}",
                ]:
                    self._run(cur, sql.SQL(stmt).format(role=role_ident))
        finally:
            conn.close()

        self.stdout.write(self.style.SUCCESS(
            f"Role {role} created/reset with SELECT-only privileges."
        ))

    def _run(self, cur, statement, params=None):
        self.stdout.write(f"  > {statement.as_string(cur)}")
        cur.execute(statement, params or [])
