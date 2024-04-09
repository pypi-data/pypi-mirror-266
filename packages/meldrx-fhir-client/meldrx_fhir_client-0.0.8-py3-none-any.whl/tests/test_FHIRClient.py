import unittest
import time
import json
from meldrx_fhir_client.FHIRClient import FHIRClient

class TestFHIRClient(unittest.TestCase):

    #
    # Tests the full CRUDS workflow.
    # Uses the SMART-Health-IT FHIR server.
    # Looks for a hard-coded patient named "Gerardo Botello"
    #
    def test_SmartHealthIT_CRUDS(self):
        base_url = "https://launch.smarthealthit.org/v/r4/fhir"
        fhirClient = FHIRClient.for_no_auth(base_url)

        # Search for a patient...
        searchPatients = fhirClient.search_resource("Patient", { 'family': 'botello', 'given': 'gerardo' })
        self.assertEqual(searchPatients['resourceType'], 'Bundle')
        self.assertGreaterEqual(searchPatients['total'], 1)

        # Grab the patient ID from the search results and read that patient...
        patientId = searchPatients['entry'][0]['resource']['id']
        readPatient = fhirClient.read_resource("Patient", patientId)
        self.assertEqual(readPatient['resourceType'], 'Patient')
        self.assertEqual(readPatient['id'], patientId)
        self.assertEqual(readPatient['name'][0]['family'], 'Botello')

        # Create an observation for this patient...
        observation = TestFHIRClient.__create_observation(patientId)
        createObservation = fhirClient.create_resource("Observation", observation)
        self.assertEqual(createObservation['resourceType'], 'Observation')
        self.assertIsNotNone(createObservation['id'])

        # Update the observation...
        observationId = createObservation['id']
        createObservation['valueQuantity']['value'] = 73
        updateObservation = fhirClient.update_resource("Observation", observationId, createObservation)
        self.assertEqual(updateObservation['resourceType'], 'Observation')
        observation = fhirClient.read_resource("Observation", observationId)
        self.assertEqual(observation['valueQuantity']['value'], 73)

        # Delete the observation...
        deleteObservation = fhirClient.delete_resource("Observation", observationId)
        self.assertEqual(deleteObservation['resourceType'], 'OperationOutcome')
        self.assertEqual(deleteObservation['issue'][0]['severity'], 'information')

    @staticmethod
    def __create_observation(patientId):
        return {
            "resourceType": "Observation",
            "status": "final",
            "subject": {
                "reference": "Patient/" + patientId
            },
            "valueQuantity": {
                "value": 72,
                "unit": "in",
                "system": "http://unitsofmeasure.org",
            }
        }

if __name__ == '__main__':
    unittest.main()