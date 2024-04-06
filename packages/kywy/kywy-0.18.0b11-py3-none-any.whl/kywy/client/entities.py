import json


class KawaEntities:

    def __init__(self, kawa_client):
        self._k = kawa_client
        self._entity_kind = None

    def entities_of_kind(self, entity_kind):
        self._entity_kind = entity_kind
        return self

    def conversations(self):
        self._entity_kind = 'conversations'
        return self

    def perimeters(self):
        self._entity_kind = 'perimeters'
        return self

    def attributes(self):
        self._entity_kind = 'attributes'
        return self

    def data_categories(self):
        self._entity_kind = 'data-categories'
        return self

    def data_providers(self):
        self._entity_kind = 'data-providers'
        return self

    def datasources(self):
        self._entity_kind = 'datasources'
        return self

    def dashboards(self):
        self._entity_kind = 'dashboards'
        return self

    def sheets(self):
        self._entity_kind = 'sheets'
        return self

    def views(self):
        self._entity_kind = 'extended-views'
        return self

    def principals(self):
        self._entity_kind = 'principals'
        return self

    def workspaces(self):
        self._entity_kind = 'workspaces'
        return self

    def script_runners(self):
        self._entity_kind = 'script-runners'
        return self

    def secrets(self):
        self._entity_kind = 'secret'
        return self

    def python_private_joins(self):
        self._entity_kind = 'python-private-joins'
        return self

    def list_entities(self):
        return self._k.get('{}/backoffice/{}'.format(self._k.kawa_api_url, self._entity_kind.lower()))

    def get_entity_by_id(self, id):
        return self._k.get('{}/backoffice/{}/{}'.format(self._k.kawa_api_url, self._entity_kind.lower(), id))

    def list_entity_names(self):
        return [e.get('displayInformation').get('displayName') for e in self.list_entities()]

    def get_datasource_schema(self, datasource_id=None):
        return self._k.get('{}/backoffice/datasources/{}/schema'.format(self._k.kawa_api_url, datasource_id))

    def get_sheet_schema(self, sheet_id=None):
        return (self._k
                .get('{}/backoffice/sheets/{}/schema'.format(self._k.kawa_api_url, sheet_id))
                .get('schema'))

    def get_entity(self, entity_id_or_name=None):
        if not entity_id_or_name:
            return None

        entity_id_or_name = str(entity_id_or_name)

        if self._entity_kind == 'attributes':
            # Attributes are saved in upper case so if we want to search for some,
            # we need to translate the searched for name to upper case as well.
            entity_name = entity_id_or_name.upper()

        for entity in self.list_entities():
            candidate_name = entity.get('displayInformation').get('displayName')
            candidate_id = entity.get('id')
            if candidate_name == entity_id_or_name or candidate_id == entity_id_or_name:
                return entity

        return None

    def get_entity_id(self, entity_name):
        entity = self.get_entity(entity_name)
        if entity:
            return entity.get('id')

    def find_first_entity_by_attribute(self, attribute, value):
        for entity in self.list_entities():
            if entity.get(attribute) == value:
                return entity

    def find_entities_by_attribute(self, attribute, value_list):
        res = []
        value_set = set(value_list)
        for entity in self.list_entities():
            if entity.get(attribute) in value_set:
                res.append(entity)
        return res
