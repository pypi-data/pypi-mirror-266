from ..DataModels.Completions.FracEntry import FracEntry
from ..DataModels.Completions.Frac import Frac
from ..DataModels.Wells.Wellbore import Wellbore
from .Client import Client, ZonevuError
from typing import Tuple, Union, Dict, Optional, Any, List
from strenum import StrEnum


class StageUpdateMethodEnum(StrEnum):
    Preserve = 'Preserve'           # Preserve existing stages, but append new stages
    Merge = 'Merge'                 # Merge overlapping stages
    Overwrite = 'Overwrite'         # Overwrite existing overlapping stages
    Bypass = 'Bypass'               # Do not update stages


class CompletionsService:
    client: Client

    def __init__(self, c: Client):
        self.client = c

    def get_fracs(self, wellbore_id: int) -> List[FracEntry]:
        """
        Gets a list of fracs for the specified wellbore.
        :param wellbore_id: System id of wellbore
        :return: a list of frac catalog entries
        """
        url = "completions/fracs/%s" % wellbore_id
        items = self.client.get_list(url)
        frac_entries = [FracEntry.from_dict(w) for w in items]
        return frac_entries

    def find_frac(self, frac_id: int) -> Frac:
        url = "completions/frac/%s" % frac_id
        item = self.client.get(url)
        frac = Frac.from_dict(item)
        return frac

    def load_fracs(self, wellbore: Wellbore) -> List[Frac]:
        frac_entries = self.get_fracs(wellbore.id)
        wellbore.fracs = []
        for frac_entry in frac_entries:
            try:
                frac = self.find_frac(frac_entry.id)
                wellbore.fracs.append(frac)
            except ZonevuError as frac_err:
                print('Could not load frac "%s" because %s' % frac_err.message)
            except Exception as frac_err2:
                print('Could not load frac "%s" because %s' % frac_err2)
        return wellbore.fracs

    def add_frac(self, wellbore: Wellbore, frac: Frac) -> None:
        """
        Adds a survey to a wellbore. Updates the passed in survey with zonevu ids.
        @param wellbore: Zonevu id of wellbore to which survey will be added.
        @param frac: Frac object
        @return: Throw a ZonevuError if method fails
        """
        url = "completions/frac/add/%s" % wellbore.id
        item = self.client.post(url, frac.to_dict())
        server_frac = Frac.from_dict(item)
        frac.copy_ids_from(server_frac)

    def delete_frac(self, frac: Frac, delete_code: str) -> None:
        url = "completions/frac/delete/%s" % frac.id
        self.client.delete(url, {"deletecode": delete_code})

    def update_frac(self, frac: Frac, frac_update: bool, stage_update: StageUpdateMethodEnum = StageUpdateMethodEnum.Bypass) -> None:
        """
        Updates a frac and/or its stages.
        @param frac: Frac object
        @param frac_update:  which method to use for updating frac
        @param stage_update: which method to use for updating frac stages
        @return: Throw a ZonevuError if method fails
        """
        url = "completions/frac/update/%s" % frac.id
        item = self.client.patch(url, frac.to_dict(), True, {'fracupdate': frac_update, 'stageupdate': stage_update})
        server_frac = Frac.from_dict(item)
        frac.copy_ids_from(server_frac)
