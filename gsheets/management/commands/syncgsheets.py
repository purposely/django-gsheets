from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.apps import apps
from gsheets import mixins


class Command(BaseCommand):
    help = 'Finds all models mixing in a Sheet syncing mixin and executes the sync'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--apppath',
            help='Find django apps nested under a relative path (path should be delineated with \'.\' instead of \'\\\')',
        )

    def handle(self, *args, **options):
        for model in self.find_syncable_models(options['apppath']):
            if issubclass(model, mixins.SheetSyncableMixin):
                model.sync_sheet()
            elif issubclass(model, mixins.SheetPullableMixin):
                model.pull_sheet()
            elif issubclass(model, mixins.SheetPushableMixin):
                model.push_to_sheet()
            else:
                raise CommandError(f'model {model} doesnt subclass a viable mixin for sync')

            self.stdout.write(self.style.SUCCESS(f'Successfully synced model {model}'))

        self.stdout.write(self.style.SUCCESS('Successfully finished sync'))

    def find_syncable_models(self, app_path):
        app_models = []
        for app in settings.INSTALLED_APPS:
            try:
                models = apps.get_app_config(app).get_models()
            except LookupError:
                if app_path:
                    try:
                        if app_path[-1] != '.':
                            app_path += '.'
                        app_name = app.split(app_path)[1]
                        models = apps.get_app_config(app_name).get_models()
                    except LookupError:
                        continue
                else:
                    continue

            app_models += [m for m in models if issubclass(m, mixins.BaseGoogleSheetMixin)]

        self.stdout.write(f'found {len(app_models)} syncable models')

        return app_models