"""Helper utilities in migrations"""
from django.core.management import call_command
from django.core.serializers import base, python


def load_fixture_base(file_name: str, app_label: str, apps, _schema_editor):
    """Function to define load_fixure in migration file.
    You need to define a wrapper function to load fixture in migration process like following

    def load_fixture(apps, schema_editor):
      return load_fixture_base(<fixture-file-name.json>, <your app name>, apps, schema_editor)

    refer the second answer to this question.
    https://stackoverflow.com/questions/25960850/loading-initial-data-with-django-1-7-and-data
    -migrations
    """

    # Save the old _get_model() function
    old_get_model = python._get_model

    # Define new _get_model() function here, which utilizes the apps argument to
    # get the historical version of a model. This piece of code is directly stolen
    # from django.core.serializers.python._get_model, unchanged. However, here it
    # has a different context, specifically, the apps variable.
    def _get_model(model_identifier):
        try:
            return apps.get_model(model_identifier)
        except (LookupError, TypeError) as err:
            raise base.DeserializationError(
                "Invalid model identifier: '%s'" % model_identifier) from err

    # Replace the _get_model() function on the module, so loaddata can utilize it.
    python._get_model = _get_model

    try:
        # Call loaddata command
        call_command('loaddata', file_name, app_label=app_label)
    finally:
        # Restore old _get_model() function
        python._get_model = old_get_model
