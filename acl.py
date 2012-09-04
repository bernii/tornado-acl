import inspect
import functools
try:
    from tornado.web import HTTPError
except ImportError:
    # Not using this with Tornado? Not a problem..
    class HTTPError(Exception):
        """ Raised when user is not allowed to use the method/class """
        def __init__(self, status_code, message):
            self.status_code = status_code
            self.message = message


class AccessControlList:
    """
    Access Control List class
    Provides all the decorator logic and provides default forbidden behaviour

    wrap_class_methods - list of methods that should be wrapped with ACL when using acl decorator on the whole class
    """
    wrap_class_methods = ["post", "get"]

    def __init__(self, check, forbidden=None):
        """ Initialize with custom ACL check function and optional forbidden handler """
        self.check = check
        self.forbidden = forbidden if forbidden else self._forbidden

    def _forbidden(self):
        """ Default method executed when user is not allowed to access the method """
        raise HTTPError(403, "You are not allowed to enter this area")

    def _check_acl(self, method, acl_list):
        """
        Check if user has right to access the resource.
        Works both on class and function objects
        """
        # Wrapper is used on the whole class
        if inspect.isclass(method):
            for name, c_method in inspect.getmembers(method, predicate=inspect.ismethod):
                if name in self.wrap_class_methods:
                    setattr(method, c_method.__name__, self._check_acl(getattr(method, c_method.__name__), acl_list))
            return method
        else:  # Wrapper is used on the method
            @functools.wraps(method)
            def wrapper(inself, *args, **kwargs):
                # Check if user is allowed to access
                has_right_to_access = self.check(inself) in acl_list
                if not has_right_to_access:
                    # Use custom forbidden handler provided by user if available
                    return inself.forbidden() if hasattr(inself, "forbidden") else self.forbidden()
                return method(inself, *args, **kwargs)
            return wrapper

    @classmethod
    def init(cls, check, forbidden=None):
        """ Initialize ACL with check anf (optional) forbidden function """
        cls.instance = AccessControlList(check, forbidden)
        return cls.instance

    @classmethod
    def get_instance(cls):
        """ Get instance of ACL class if it has been initalized (singleton) """
        if not cls.instance:
            raise Exception('AccessControlList not initialized! Use acl_init first!')
        return cls.instance


## Handy shortcut functions for ease of use and to keep the code clean


def acl_init(check, forbidden=None):
    """ Initilizer shortcut function """
    return AccessControlList.init(check, forbidden)


def acl(acl_list):
    """ Decorator shortcut function """
    # If parmeter is not a list, convert it
    if not isinstance(acl_list, list):
        acl_list = [acl_list]

    def call(f):
        return AccessControlList.get_instance()._check_acl(f, acl_list)
    return call
