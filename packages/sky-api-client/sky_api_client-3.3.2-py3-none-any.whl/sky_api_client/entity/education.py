from sky_api_client.entity.base import Entity
from sky_api_client.entity.registry import EntityRegistry
from sky_api_client.exceptions.exception import MethodNotDefined


@EntityRegistry.register('education')
class Education(Entity):
    LIST_URL = '/constituent/v1/educations/'
    CREATE_URL = '/constituent/v1/educations/'
    GET_URL = '/constituent/v1/constituents/educations/{id}'
    UPDATE_URL = '/constituent/v1/educations/{id}'
    DELETE_URL = '/constituent/v1/educations/{id}'
    SUBJECTS_URL = '/constituent/v1/educations/subjects'
    DEGREES_URL = '/constituent/v1/educations/degrees'

    def subjects(self):
        if self.SUBJECTS_URL:
            return self._api.request(method='GET', path=self.SUBJECTS_URL).get('value', [])
        raise MethodNotDefined('subjects')

    def degrees(self):
        if self.DEGREES_URL:
            return self._api.request(method='GET', path=self.DEGREES_URL).get('value', [])
        raise MethodNotDefined('degrees')


@EntityRegistry.register('education_custom_field')
class EducationCustomField(Entity):
    LIST_URL = 'constituent/v1/educations/customfields/categories/details?limit=5000'
    CREATE_URL = 'constituent/v1/educations/customfields'
    DELETE_URL = 'constituent/v1/educations/customfields/{custom_field_id}'
    UPDATE_URL = 'constituent/v1/educations/customfields/{custom_field_id}'
    CUSTOM_FIELDS_URL = 'constituent/v1/educations/{education_id}/customfields'
    CUSTOM_FIELD_CATEGORIES_CODE_TABLE_URL = 'constituent/v1/educations/customfields/categories/values?category_name={}'

    def list(self, id=None, parent_id=None, params=None, all=False):
        data = super().list(id=id, parent_id=parent_id, params=params)
        if not all:
            return data
        count = data['count']
        while count > 5000:
            params['offset'] = params.get('offset', 0) + 5000
            data['value'] += super().list(id=id, parent_id=parent_id, params=params)['value']
            count -= 5000
        return data

    def custom_fields(self, education_id):
        if self.CUSTOM_FIELDS_URL:
            return self._api.request(method='GET', path=self.CUSTOM_FIELDS_URL.format(education_id=education_id)).get(
                'value', []
            )
        raise MethodNotDefined('custom_fields')

    def custom_field_categories_code_table(self, category_name):
        if self.CUSTOM_FIELD_CATEGORIES_CODE_TABLE_URL:
            return self._api.request(
                method='GET', path=self.CUSTOM_FIELD_CATEGORIES_CODE_TABLE_URL.format(category_name)
            ).get('value', [])
        raise MethodNotDefined('custom_field_categories_code_table')
