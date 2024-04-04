import copy
from ...Zonevu import Zonevu
from ...Services.Error import ZonevuError


# Phase I - Get a strat column to copy
def main_copy_stratcol(zonevu: Zonevu, strat_col_name: str):
    """
    This script will locate a strat column in ZoneVu, and make a copy.
    :param zonevu: Zonevu instance
    :param strat_col_name: Name of stratigraphic column to work with
    """
    print('Making a copy of a strat column in ZoneVu')
    strat_svc = zonevu.strat_service  # Get reference to ZoneVu WebAPI strat service service

    strat_cols = strat_svc.get_stratcolumns()
    strat_col_entry = next((s for s in strat_cols if s.name == strat_col_name), None)
    if strat_col_entry is None:
        print('Could not find strat column with the name "%s"' % strat_col_name)
        return

    # Find the strat column to copy
    strat_column = strat_svc.find_stratcolumn(strat_col_entry.id)

    print("Strat Column ID = %s:" % strat_column.id)
    print("   Num formations = %d:" % len(strat_column.formations))
    print()

    do_copy = True

    if do_copy:
        # Phase II - Delete Copy if it exists
        stratcol_copy_name = '%s-Copy' % strat_column.name        # The copied strat column will be called this
        print("The copied strat column will be named '%s'." % stratcol_copy_name)
        existing_copy = next((item for item in strat_cols if item.name == stratcol_copy_name), None)
        if existing_copy is not None:
            print("There was an existing strat column named '%s'. Go delete it in ZoneVu first." % stratcol_copy_name)
            return

        # Phase III - Make a copy of the strat column
        try:
            stratcol_copy = copy.deepcopy(strat_column)      # Make a local copy of strat column including stations.
            stratcol_copy.name = stratcol_copy_name             # Name the copy
            strat_svc.add_stratcolumn(stratcol_copy)    # Add strat column to ZoneVu
            print("Copy process was successful")
        except ZonevuError as copy_err:
            print("Could not copy strat column because %s" % copy_err.message)
            raise copy_err

        print("Execution was successful")



