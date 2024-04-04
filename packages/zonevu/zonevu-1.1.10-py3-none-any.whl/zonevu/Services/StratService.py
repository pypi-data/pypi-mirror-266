from ..DataModels.Strat.StratColumn import StratColumn
from .Client import Client
from typing import Optional


class StratService:
    client: Client

    def __init__(self, c: Client):
        self.client = c

    def get_stratcolumns(self, match_token: Optional[str] = None) -> list[StratColumn]:
        url = "stratcolumns"
        if match_token is not None:
            url += "/%s" % match_token
        items = self.client.get_list(url)
        cols = [StratColumn.from_dict(w) for w in items]
        return cols

    def get_first_named(self, name: str) -> Optional[StratColumn]:
        """
        Get first project with the specified name, populate it, and return it.
        :param name: name of strat column to get
        :return:
        """
        strat_col_entries = self.get_stratcolumns(name)
        if len(strat_col_entries) == 0:
            return None
        strat_col_entry = strat_col_entries[0]
        strat_col = self.find_stratcolumn(strat_col_entry.id)
        return strat_col

    def find_stratcolumn(self, column_id: int) -> StratColumn:
        url = "stratcolumn/%s" % column_id
        item = self.client.get(url)
        col = StratColumn.from_dict(item)
        return col

    def add_stratcolumn(self, col: StratColumn) -> None:
        url = "stratcolumn/add"
        item = self.client.post(url, col.to_dict())
        server_survey = StratColumn.from_dict(item)
        col.copy_ids_from(server_survey)


