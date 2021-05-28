from tests import BaseTestCase


class IndexTest(BaseTestCase):
    """
    Test that index is accessible
    """

    def test_connectorsGet(self):
        with self.client:
            result = self.client.get("/connectors")
            self.assertEqual(result.status_code, 200)
    def test_connectorsPost(self):
        #####
    