import unittest
from acl import acl, acl_init, HTTPError

"""
If it has no tests you can't tell if it is working... right?

Testing if ACL lists and all the features work correctly.
Engagnig Star Wars unit testing...
"""


class AclWrapperTests(unittest.TestCase):
    """ ACL wrapper test suite """
    def setUp(self):
        def check(self):
            self.user = self.who_am_i
            return self.user

        def default_forbidden():
            return "this is default 403"

        acl_init(check, default_forbidden)

        @acl(["jedi", "sith"])
        class TheEndOfTheGalaxyPub(object):
            def get(self):
                return "Yeah, it's working"

            def forbidden(self):
                if self.user == "pony":
                    return "No ponies allowed here!"
                raise Exception(44)
        self.test1 = TheEndOfTheGalaxyPub()

        @acl(["sith"])
        class DeathStar(object):
            def get(self):
                return "Yeah, it's working and you are using the Dark Force!"
        self.test2 = DeathStar()

    def test_allowed(self):
        # First ACL element
        self.test1.who_am_i = "jedi"
        self.assertEqual(self.test1.get(), "Yeah, it's working")
        # Second ACL element
        self.test1.who_am_i = "sith"
        self.assertEqual(self.test1.get(), "Yeah, it's working")

    def test_custom_forbidden(self):
        # Test custom forbidden handler
        self.test1.who_am_i = "pony"
        self.assertEqual(self.test1.get(), "No ponies allowed here!")
        # Test conditional
        self.test1.who_am_i = "dontknow"
        try:
            self.test1.get()
        except Exception as e:
            self.assertEqual(e.args[0], 44)

    def test_default_forbidden(self):
        # Test the default forbidden handler passed to acl_init function
        self.test2.who_am_i = "britney"
        self.assertEqual(self.test2.get(), "this is default 403")


class AclWrapperSecondTests(unittest.TestCase):
    """ Second wrapper test suite - different wrapper ACL configuration """
    def setUp(self):
        def check(self):
            return False

        acl_init(check)

        @acl(True)
        class BlackHole(object):
            def get(self):
                return "Yeah, it's working"
        self.test1 = BlackHole()

    def test_forbidden(self):
        try:
            self.test1.get()
        except HTTPError as e:
            self.assertEqual(e.status_code, 403)

if __name__ == '__main__':
    unittest.main()
