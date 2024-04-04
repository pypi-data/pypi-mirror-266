from ...Zonevu import Zonevu


def main_get_delete_code(zonevu: Zonevu) -> None:
    """
    Calling this method will cause ZoneVu server to generate a 6-digit delete authorization code and send it to
    the user using the user's current notification settings.
    :param zonevu:
    :return:
    """
    print('Generate delete code')
    company_svc = zonevu.company_service
    company_svc.get_delete_authorization()
    print('Delete code sent to caller')

