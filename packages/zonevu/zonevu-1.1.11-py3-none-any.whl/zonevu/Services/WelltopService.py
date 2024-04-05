from ..DataModels.Wells.Welltop import Welltop
from ..DataModels.Wells.Wellbore import Wellbore
from .Client import Client
from .Error import ZonevuError


class WelltopService:
    client: Client

    def __init__(self, c: Client):
        self.client = c

    def get_welltops(self, wellbore: Wellbore) -> list[Welltop]:
        url = "welltops/%s" % wellbore.id
        items = self.client.get_list(url)
        tops = [Welltop.from_dict(w) for w in items]
        return tops

    def load_welltops(self, wellbore: Wellbore) -> list[Welltop]:
        tops = self.get_welltops(wellbore)
        wellbore.tops = []
        for top in tops:
            wellbore.tops.append(top)
        return tops

    def add_top(self, wellbore: Wellbore, top: Welltop):
        raise ZonevuError.local('add_top not implemented')
        # url = "welltop/add/%s" % wellbore.id
        # saved_top = self.client.post(url, top.to_dict())
        # top.copy_ids_from(saved_top)
        # TODO: implement this method on SERVER and CLIENT

    def add_tops(self, wellbore: Wellbore, tops: list[Welltop]) -> None:
        # Copy survey ids
        for top in tops:
            if top.survey:
                top.survey_id = top.survey.id

        url = "welltops/add/%s" % wellbore.id
        data = [s.to_dict() for s in tops]
        items = self.client.post_return_list(url, data)
        saved_tops = [Welltop.from_dict(w) for w in items]
        for (top, saved_top) in zip(tops, saved_tops):
            top.copy_ids_from(saved_top)

    def delete_top(self, top: Welltop) -> None:
        url = "welltop/delete/%s" % top.id
        self.client.delete(url)
        # TODO: implement this method on SERVER - deletes a specified top

    def delete_tops(self, wellbore: Wellbore) -> None:
        url = "welltops/delete/%s" % wellbore.id
        self.client.delete(url)
        # TODO: implement this method on SERVER - deletes all tops on a specified wellbore

