from ..DataModels.Wells.NoteCategory import NoteCategory
from ..DataModels.Wells.Note import Note
from ..DataModels.Wells.Wellbore import Wellbore
from .Client import Client


class NoteService:
    client: Client

    def __init__(self, c: Client):
        self.client = c

    def get_notes(self, wellbore: Wellbore) -> list[Note]:
        url = "notes/%s" % wellbore.id
        items = self.client.get_list(url)
        notes = [Note.from_dict(w) for w in items]
        return notes

    def load_notes(self, wellbore: Wellbore) -> list[Note]:
        notes = self.get_notes(wellbore)
        wellbore.notes = []
        for note in notes:
            wellbore.notes.append(note)
        return notes

    def add_note(self, wellbore: Wellbore, note: Note):
        url = "note/add/%s" % wellbore.id
        saved_note = self.client.post_return_dict(url, note.to_dict())
        note.id = saved_note["id"]
        # TODO: test this method

    def add_notes(self, wellbore: Wellbore, notes: list[Note]) -> None:
        url = "notes/add/%s" % wellbore.id
        data = [s.to_dict() for s in notes]
        saved_notes = self.client.post_return_list(url, data)
        for (note, saved_note) in zip(notes, saved_notes):
            note.copy_ids_from(saved_note)

    def delete_note(self, note: Note) -> None:
        # Deletes a specified note
        url = "note/delete/%s" % note.id
        self.client.delete(url)
        # TODO: test this method

    def delete_notes(self, wellbore: Wellbore) -> None:
        # Deletes all notes for a specified wellbore
        url = "notes/delete/%s" % wellbore.id
        self.client.delete(url)
        # TODO: test this method

    def get_categories(self) -> list[NoteCategory]:
        url = "notes/categories"
        items = self.client.get_list(url)
        categories = [NoteCategory.from_dict(w) for w in items]
        return categories

    # def add_category(self, category: NoteCategory):
    #     url = "notes/category/add/%s"
    #     saved_category = self.client.post(url, category.to_dict())
    #     category.copy_ids_from(saved_category)
    #     # TODO: implement this method on SERVER
    #
    # def delete_category(self, category: NoteCategory) -> None:
    #     # Deletes a specified note category
    #     url = "notes/category/delete/%s" % category.id
    #     self.client.delete(url)
    #     # TODO: implement this method on SERVER

