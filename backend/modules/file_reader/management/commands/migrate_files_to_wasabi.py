"""
Management command to migrate local files to Wasabi S3 storage.

Usage:
    python manage.py migrate_files_to_wasabi
    python manage.py migrate_files_to_wasabi --dry-run
"""

import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from modules.file_reader.models import File


class Command(BaseCommand):
    help = "Migrate local files to Wasabi S3 storage"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be migrated without actually migrating",
        )
        parser.add_argument(
            "--delete-local",
            action="store_true",
            help="Delete local files after successful migration",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        delete_local = options["delete_local"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No files will be migrated"))
        if delete_local:
            self.stdout.write(self.style.WARNING("DELETE LOCAL - Local files will be deleted after migration"))

        # Check if Wasabi is configured
        if not settings.WASABI_ACCESS_KEY or not settings.WASABI_SECRET_KEY:
            self.stdout.write(
                self.style.ERROR("Wasabi credentials not configured. Set WASABI_ACCESS_KEY and WASABI_SECRET_KEY.")
            )
            return

        # Get all files
        files = File.objects.all()
        total = files.count()
        migrated = 0
        skipped = 0
        errors = 0

        self.stdout.write(f"Found {total} files to process")

        for file_obj in files:
            try:
                file_field = file_obj.raw_file

                if not file_field:
                    self.stdout.write(f"  [{file_obj.id}] No file attached - skipping")
                    skipped += 1
                    continue

                file_name = file_field.name

                # Build local file path - check multiple possible locations
                local_path = None
                possible_paths = [
                    os.path.join(settings.BASE_DIR, file_name),
                    os.path.join(settings.MEDIA_ROOT, file_name),
                    os.path.join(settings.BASE_DIR, "media", file_name),
                    os.path.join("/app", file_name),
                    os.path.join("/app/media", file_name),
                ]

                for path in possible_paths:
                    if os.path.exists(path):
                        local_path = path
                        break

                if not local_path:
                    # No local file found - either already migrated or missing
                    self.stdout.write(
                        self.style.WARNING(f"  [{file_obj.id}] {file_name} - no local file found (may already be on S3)")
                    )
                    skipped += 1
                    continue

                if dry_run:
                    self.stdout.write(f"  [{file_obj.id}] {file_name} - would migrate")
                    migrated += 1
                    continue

                # Read local file and save to S3
                with open(local_path, "rb") as f:
                    content = f.read()

                # Get just the filename without path
                base_name = os.path.basename(file_name)

                # Save to S3 storage
                file_field.save(base_name, ContentFile(content), save=True)

                self.stdout.write(self.style.SUCCESS(f"  [{file_obj.id}] {file_name} - migrated successfully"))

                # Delete local file if requested
                if delete_local and os.path.exists(local_path):
                    os.remove(local_path)
                    self.stdout.write(f"  [{file_obj.id}] Local file deleted: {local_path}")

                migrated += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  [{file_obj.id}] Error: {str(e)}"))
                errors += 1

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Migration complete:"))
        self.stdout.write(f"  Total: {total}")
        self.stdout.write(f"  Migrated: {migrated}")
        self.stdout.write(f"  Skipped: {skipped}")
        self.stdout.write(f"  Errors: {errors}")

        if dry_run:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("This was a dry run. Run without --dry-run to actually migrate."))

