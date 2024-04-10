import unittest
from src.DLMS_SPODES_client.services import get_client_from_csv


class TestType(unittest.TestCase):
    def test_get_from_csv(self):
        res = get_client_from_csv("конфигурация GSM.csv")
        print(res)


