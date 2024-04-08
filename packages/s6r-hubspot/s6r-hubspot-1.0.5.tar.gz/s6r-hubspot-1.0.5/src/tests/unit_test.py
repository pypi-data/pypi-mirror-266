import unittest
import time
import os
import sys
sys.path.append("..")

from src.s6r_hubspot import HubspotConnection


# Method or group of method not tested yet
# - files/folder methods
# - _read() need to uniformize read() and _read()
# - token methods (can't make these function work without public app)

class TestHubspotMethod(unittest.TestCase):
    def setUp(self):
        self.token = os.environ.get('HUBSPOT_TOKEN', '')
        self.connection = HubspotConnection(token=self.token)
        self.email = 'contact@scalizer.fr'
        self.domain = 'scalizer.fr'
        self.contact_id = 0
        self.company_id = 0

    def test_object(self):
        self.create()
        self.get_all()
        self.update()
        self.read()
        time.sleep(10)  # need to wait to find contact in search
        self.search()
        self.archive('contacts', self.contact_id)
        self.archive('companies', self.company_id)

    def create(self):
        firstname = 'Morgane'
        lastname = 'Goujon'
        contact_create = self.connection.create('contacts', [
            {'properties': {'lastname': lastname, 'firstname': firstname, 'email': self.email}}])
        self.contact_id = contact_create[0]['id']
        self.assertEqual(contact_create[0]['properties']['hs_object_source'], 'INTEGRATION')
        self.assertEqual(contact_create[0]['properties']['email'], self.email)
        self.assertEqual(contact_create[0]['properties']['lastname'], lastname)
        self.assertEqual(contact_create[0]['properties']['firstname'], firstname)

        company_create = self.connection.create('companies',
                                                [{'properties': {'name': 'Scalizer', 'domain': self.domain}}])
        self.company_id = company_create[0]['id']
        self.assertEqual(company_create[0]['properties']['hs_object_source'], 'INTEGRATION')
        self.assertEqual(company_create[0]['properties']['domain'], self.domain)
        self.assertEqual(company_create[0]['properties']['name'], 'Scalizer')

        self.connection.create_association('contacts', 'companies', [
            {"from": {"id": self.contact_id}, "to": {"id": company_create[0]['id']},
             "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 1}]}])

    def read(self):
        contact = self.connection.read('contacts', [self.contact_id], ['lastname', 'firstname', 'email'],
                                       associations=['companies'])
        contact_read_email = self.connection.read('contacts', [self.email], ['lastname', 'firstname', 'email'],
                                                  propertiesWithHistory=['firstname'], associations=['companies'],
                                                  props_name="email")
        self.assertEqual(contact[0]['properties']['email'], self.email)
        self.assertEqual(contact_read_email[0]['properties']['email'], self.email)
        self.assertEqual(contact_read_email[0]['id'], contact[0]['id'])
        self.assertEqual(contact_read_email[0]['_companies'][0]['id'], contact[0]['_companies'][0]['id'])
        self.assertEqual(contact[0]['_companies'][0]['id'], int(self.company_id))
        self.assertTrue(len(contact_read_email[0]['propertiesWithHistory']['firstname']) == 2)
        self.assertTrue(all([x['value'] in ['Morgane', 'Morgane1'] for x in
                             contact_read_email[0]['propertiesWithHistory']['firstname']]))

    def search(self):
        contact = self.connection.search('contacts',
                                         filters=[{"value": "Goujon", "propertyName": "lastname", "operator": "EQ"}],
                                         properties=['email', 'lastname', 'firstname'], load_associations=True)
        self.assertTrue(len(contact) == 1)

    def update(self):
        contact_update = self.connection.update('contacts', [
            {'id': self.contact_id, 'properties': {'firstname': 'Morgane1', 'zip': '44000', 'phone': '0625849532'}}])
        self.assertEqual(contact_update[0]['properties']['zip'], '44000')
        self.assertEqual(contact_update[0]['properties']['phone'], '0625849532')

    def archive(self, model, object_id):
        self.connection.archive(model, [object_id])
        obj = self.connection.read(model, [object_id], [])
        self.assertFalse(obj)

    def get_all(self):
        companies = self.connection.get_all('companies', ['name'])
        self.assertTrue(len(companies) == 1)
        self.assertEqual(companies[0]['properties']['name'], 'Scalizer')

    def test_owners(self):
        owners = self.connection.get_owners()
        owner = owners[0]
        owner_from_get_owner = self.connection.get_owner(owner['id'])
        self.assertEqual(owner['email'], owner_from_get_owner['email'])

    def test_pipeline_stage(self):
        pipelines = self.connection.get_pipelines('deals')
        pipeline = self.connection.get_pipeline('deals', pipelines[0]['id'])
        self.assertEqual(pipelines[0]['label'], pipeline['label'])

        stage = self.connection.get_stage('deals', pipelines[0]['id'], 'closedwon')
        self.assertEqual(stage['id'], 'closedwon')

    def test_properties(self):
        search_email = self.connection._search_properties('contacts', 'emails')
        self.assertTrue(search_email)
        search_property_1 = self.connection._search_properties('contacts', 'property_1')
        self.assertFalse(search_property_1)
        property_1 = {"inputs": [{"label": "Property 1", "name": "property_1", "type": "number", "fieldType": "number",
                                  "groupName": "contactinformation"}]}
        self.connection._create_properties('contacts', property_1)
        search_property_1 = self.connection._search_properties('contacts', 'property_1')
        self.assertTrue(search_property_1)
        self.connection._archive_properties('contacts', 'property_1')
        search_property_1 = self.connection._search_properties('contacts', 'property_1')
        self.assertFalse(search_property_1)

    def test_label_association(self):
        labels = self.connection.get_association_label('contacts', 'deals')
        self.assertTrue(len(labels['results']) == 1)

    def clear_objects(self, model):
        objects = self.connection.search(model, filters=[])
        if objects:
            self.connection.archive(model, [o['id'] for o in objects])

    def tearDown(self):
        for model in ['companies', 'contacts', 'deals']:
            self.clear_objects(model)


if __name__ == '__main__':
    unittest.main()
