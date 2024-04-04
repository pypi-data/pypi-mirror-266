from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError
from ...Services.Storage import Storage


def main(zonevu: Zonevu, storage: Storage, stratcolumn_name: str) -> None:
    """
    Write or update a named well from a ZoneVu account to user storage.
    :param zonevu: Zonevu client instance
    :param storage: User storage to save strat column to
    :param stratcolumn_name: Name of well to retrieve and save
    """
    print('Save a stratcolumn to storage')
    # Find stratcolumn with that name
    strat_svc = zonevu.strat_service
    stratcolumn = strat_svc.find_stratcolumn(6)
    if stratcolumn is None:
        raise ZonevuError.local('Could not find the stratcolumn "%s"' % stratcolumn_name)

    stratcolumn.save(storage)                          # Save stratcolumn to storage outside ZoneVu

