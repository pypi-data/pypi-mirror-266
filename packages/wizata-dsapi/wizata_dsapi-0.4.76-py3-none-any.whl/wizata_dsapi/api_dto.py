class ApiDto:

    def api_id(self) -> str:
        """
        return current object id on Web API format.
        """
        pass

    def endpoint(self) -> str:
        """
        return endpoint name in Web API (<0.4)
        """
        pass

    def to_json(self, target: str = None):
        """
        transform current object into a dict that could be JSONIFY.
        :target: by default - None. Can be 'backend-create' or 'backend-update' in order to JSONIFY only backend fields.
        :return: dumpable dict.
        """
        pass

    def from_json(self, obj):
        """
        load the object from a dict originating of a JSON format.
        :param obj: object to load information from.
        """
        pass

    @classmethod
    def route(cls):
        """
        Endpoint name in Web API (v0.4+).
        """
        pass

    @classmethod
    def from_dict(cls, data):
        """
        Init object instance from dict (v0.4+)
        """
        pass

    @classmethod
    def get_type(cls):
        """
        Return type of get format json by default - override with either pickle, dill, ...
        """
        return "json"
