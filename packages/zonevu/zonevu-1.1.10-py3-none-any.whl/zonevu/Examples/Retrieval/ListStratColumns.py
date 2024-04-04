from ...Zonevu import Zonevu


def main_list_stratcolumns(zonevu: Zonevu):
    strat_svc = zonevu.strat_service

    print('Strat Columns:')
    stratcolumn_entries = strat_svc.get_stratcolumns()
    for entry in stratcolumn_entries:
        print('%s (%s)' % (entry.name, entry.id))

    if len(stratcolumn_entries) > 0:
        entry = stratcolumn_entries[0]
        stratcolumn = strat_svc.find_stratcolumn(entry.id)

    # Find a named strat column
    permian_strat_col = strat_svc.get_first_named("Permian")
    found_permian = permian_strat_col is not None

    print("Execution was successful")
