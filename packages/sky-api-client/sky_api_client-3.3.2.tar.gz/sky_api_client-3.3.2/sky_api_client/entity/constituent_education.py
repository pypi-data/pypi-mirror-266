import re

import six
from sky_api_client.entity.base import Entity
from sky_api_client.entity.education import EducationCustomField
from sky_api_client.entity.registry import EntityRegistry
from sky_api_client.common.tasks.asyncio import BulkTaskExecutor


def slugify_underscore(name):
    """Return slug for the given name i.e. replace any non alphanumeric character with underscore."""
    if name is None or not isinstance(name, six.text_type):
        return None

    name = name.strip().lower()
    # Any non word characters (letters, digits, and underscores) are replaced by '-'
    name = re.sub(r'\W+', '_', name)
    # Removing any trailing or leading dash
    name = re.sub(r'^[-_]|[-_]$', '', name)
    # Replace multiple continuous hipens with one
    name = re.sub('[-_]+', '_', name)
    return name


@EntityRegistry.register('constituent_education')
class ConstituentEducation(Entity):
    LIST_URL = '/constituent/v1/constituents/{id}/educations'

    def list(self, id=None, parent_id=None, params=None):
        data = super().list(id=id, parent_id=parent_id, params=params)

        pull_education_custom_fields = params.pop('pull_education_custom_fields', False)
        if not pull_education_custom_fields:
            return data

        self.add_custom_fields_async(data)

        return data

    def add_custom_fields(self, education):
        education_custom_fields = EducationCustomField(self._api).custom_fields(education_id=education['id'])
        custom_fields = {}
        for custom_field in education_custom_fields:
            default_value = []
            field_value = custom_fields.setdefault(slugify_underscore(custom_field['category']), default_value)
            field_value.append(custom_field['value'])

        for key, value in custom_fields.items():
            education[key] = value if len(value) > 1 else value[0]

    def add_custom_fields_async(self, data):
        task_list = []
        for education in data.get('value', []):
            task_list.append(((self.add_custom_fields, education), {}))

        return BulkTaskExecutor.execute_sync(
            {
                'task_list': task_list,
            }
        )
