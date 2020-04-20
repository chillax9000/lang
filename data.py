import json
import os
import pymongo


data_folder_path = os.path.join(os.path.dirname(__file__), "data")
default_data_path = os.path.join(data_folder_path, "data.json")


class EntryDAO:
    def get_entry(id_):
        raise NotImplementedError

    def write_entry(self, id_, entry):
        raise NotImplementedError

    def add_entry(self, entry):
        raise NotImplementedError

    def delete_entry(self, id_):
        raise NotImplementedError


class JsonDAO(EntryDAO):
    def __init__(self, data_path=default_data_path):
        self.data_path = data_path
        self.texts = {}

        if os.path.exists(self.data_path):
            with open(self.data_path) as f:
                self.texts = json.load(f)

    def get_entry(self, id_):
        return Entry.from_dict(self.texts[id_])

    def write_entry(self, id_, entry):
        self.texts[id_] = entry.to_dict()

    def add_entry(self, entry):
        i = 0
        for i, id_int in enumerate(sorted(map(int, self.texts.keys()))):
            if i < id_int:
                self.write_entry(str(i), entry)
        new_id = str(i+1)
        self.write_entry(new_id, entry)
        return new_id

    def delete_entry(self, id_):
        del self.texts[id_]

    def commit(self):
        with open(self.data_path, "w") as f:
            json.dump(self.texts, f)


class MongoDAO(EntryDAO):
    def __init__(self, client_getter, db_name, collection_name):
        self.client = client_getter()
        self.db = getattr(self.client, db_name)
        self.texts = getattr(self.db, collection_name)

    def get_entry(self, id_):
        doc = self.texts.find_one({"_id": id_})
        if "_id" in doc:
            del doc["_id"]
        print(doc)
        return Entry.from_dict(doc)

    def write_entry(self, id_, entry):
        entry_dict = entry.do_dict()
        entry_dict["_id"] = id_
        self.texts.insert(entry_dict)

    def add_entry(self, entry):
        self.texts.insert(entry.to_dict())

    def delete_entry(self, id_):
        self.texts.find_one_and_delete({"_id": id_})


class Text:
    def __init__(self, lang, str_, tokens=None):
        self.lang = lang
        self.str = str_
        self.tokens = tokens if tokens else []

    def set_tokens(self, tokens):
        self.tokens = tokens

    def to_dict(self):
        return {"text": self.str, "tokens": self.tokens}


class Entry:
    def __init__(self, text_src):
        self.lang_src = text_src.lang
        self.text_src = text_src
        self.texts = {text_src.lang: (text_src, None)}

    @property
    def langs(self):
        return tuple(self.texts)

    @property
    def target_langs(self):
        return tuple(filter(lambda l: l != self.lang_src, self.texts))

    def add(self, text, map_=()):

        self.texts[text.lang] = (text, map_)

    def get(self, lang):
        return self.texts[lang]

    def get_text(self, lang):
        return self.get(lang)[0]

    def get_map(self, lang):
        return self.get(lang)[1]

    def set(self, lang, text=None, map_=None):
        text_old, map_old = self.texts[lang]
        self.texts[lang] = (text if text is not None else text_old,
                            map_ if map_ is not None else map_old)

    @classmethod
    def from_dict(cls, d):
        lang_src = d["info"]["src"]
        text_src = Text(lang_src, d["src"]["text"], d["src"]["tokens"])
        entry = cls(text_src)
        for lang, d_ in d.items():
            if lang not in ("info", "src"):
                entry.add(Text(lang, d_["text"], d_["tokens"]), d_["map"])
        return entry

    def to_dict(self):
        base = {"info": {"src": self.lang_src},
                "src": self.text_src.to_dict()}
        base.update({lang: {**text.to_dict(), "map": map_}
                     for lang, (text, map_) in self.texts.items() if map_ is not None})
        return base


DAO = MongoDAO(pymongo.MongoClient, "lang_db", "text")
