from ...Zonevu import Zonevu


def main_confirm_delete_code(zonevu: Zonevu, delete_code: str) -> None:
    """
    This method demonstrates confirming a delete code
    :param zonevu:
    :param delete_code:
    :return:
    """
    print('Validate delete code')
    company_svc = zonevu.company_service
    ok, msg = company_svc.confirm_delete_authorization(delete_code)
    assert ok, 'The supplied delete code is not valid'
    print(msg)

