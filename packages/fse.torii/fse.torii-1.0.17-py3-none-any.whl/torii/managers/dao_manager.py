from torii.dao.business_object_dao import BusinessObjectDao


class DaoManager:
    """
    The manager for all data access objects (DAOs).

    All DAOs should be mapped to the 'services' dictionary, where the Key is the
    first element in the REST API path and the value the uninitialized DAO class.
    """

    services = {
        'bo': BusinessObjectDao,
    }

    def __init__(self, torii):
        self._torii = torii
        self._logger = self._torii.logger

        for key, bo in self.services.items():
            # Check if bo is a class and not an instance
            if isinstance(bo, type):
                self.services[key] = bo(torii)

    def run_service(self, intent: str, path: str, params=None, json=None, data=None, files=None, timeout=None):
        """
        Runs the intended service corresponding to the given intent and path.
        Passes the defined arguments to the service.

        :param intent: The Http method (GET, POST, PUT, DELETE or PATCH).
        :param path: The REST API path (ex.: bo/{boClass}/page).
        :param params: Optional keyword argument.
        :param json: Optional argument.
        :param data: Optional argument.
        :param files: Optional argument.
        :param timeout: Optional argument.
        :returns: The class method if exists, otherwise None.
        """

        if not self._torii.properties['use_python_dao']:
            return None

        self._logger.info(f"Using Direct DAO (use_python_dao={self._torii.properties['use_python_dao']})")

        path = path.split('/')
        service = path.pop(0)

        if service not in self.services:
            return None

        args = [intent, '/'.join(path)]
        if json: args.append(json)
        if data: args.append(data)
        if files: args.append(files)
        if timeout: args.append(timeout)
        kwargs = params or {}

        try:
            return self.services[service].init(*args, **kwargs)
        except Exception as e:
            self._logger.info('Error in DAO Manager run_service:', e)
            raise e
