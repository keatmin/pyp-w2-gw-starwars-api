from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError
import six

api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        
        for key, value in six.iteritems(json_data):
            setattr(self, key, value) 

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        
        json_data = getattr(api_client, 'get_{}'.format(cls.RESOURCE_NAME))(resource_id)
        return cls(json_data)
        

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        method_name = "{}QuerySet".format(cls.RESOURCE_NAME.title())
        return eval(method_name)()


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self):
        self.curr_page = 0
        self.curr_elem = 0
        self.objects = []
        self.total_count = getattr(api_client, 'get_{}'.format(self.RESOURCE_NAME))(**{'page': self.curr_page})['count']

    def __iter__(self):
        return self.__class__() 

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        
        while True:
            if self.curr_elem + 1 > len(self.objects):
            # need to request a new page
                try:
                    self._get_next_page()
                except SWAPIClientError:
                    raise StopIteration()
            elem = self.objects[self.curr_elem]
            self.curr_elem += 1
            return elem
        
     
    def _get_next_page(self): 
        self.curr_page += 1
        method = getattr(api_client, 'get_{}'.format(self.RESOURCE_NAME))
        json_data = method(**{'page': self.curr_page})
         
        Model = eval(self.RESOURCE_NAME.title())
        for resource_data in json_data['results']:
            self.objects.append(Model(resource_data))

    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        return self.total_count
        
    

class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
