class DataProvider:
    """
    Interface commune des fournisseurs de données externes.

    Exemples futurs :
    - Notion
    - Airtable
    - Supabase
    - Sigma API
    """

    provider_key = None

    def configuration(self):
        raise NotImplementedError

    def validate(self):
        raise NotImplementedError

    def list_resources(self):
        raise NotImplementedError

    def pull(self, resource):
        raise NotImplementedError

    def push(self, resource, records):
        raise NotImplementedError

    def snapshot(self):
        return {
            "provider": self.provider_key,
            "configuration": self.configuration(),
            "validation": self.validate(),
        }
