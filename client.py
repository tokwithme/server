class Client():
    def __init__(self):
        self._id = None
        self._gender = None
        self._other_gender = None

    @property
    def id(self):
        return self._id

    @property
    def self_gender(self):
        return self._gender

    @property
    def other_gender(self):
        return self._other_gender

    def join(self, client_id, self_gender, other_gender):
        self._id = client_id
        self._gender = self_gender
        self._other_gender = other_gender

    def leave(self):
        self._id = None
        self._gender = None
        self._other_gender = None
