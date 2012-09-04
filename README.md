Python (Tornado) Access Control Lists
=====================================

General use access control lists in Python originally created to be used with Tornado. Consists of easy to use decorator that you can use to restrict/grant access to certain parts of you system and an initialization function.

Story behind
------------

Let's say that some of parts of you site should be access only by certain types of users (or even certain individuals). That is where Access Control List become handy. This simple lib allows you to easilly implement ACLs on you site. It was designed to work with [Tornado](http://www.tornadoweb.org) but can easily work with any Python project as it is pretty general.

Usage
-----

You have a Tornado project where certain portion of the site should be accessible only to certain users (admin area, moderator area, partner area etc.). For example you have a Tornado application like:

```python

application = tornado.web.Application([
    (r"/", Potentium),
    (r"/lightside_hq", GalacticCity),
    (r"/darkside_hq", DeathStar),
])
```

As you can see there is some Potentium, GalacticCity (where Jedi reside), DeathStar (where Sith reside). Obviously you don't want Sith to access GalacticCity and you want to have DeathStar only for the Sith! You could write some conditionals, but let the acl decorator do the work for you:

```python

class Potentium(tornado.web.RequestHandler):
    @acl(["jedi", "sith"])  # Used on single method!
    def get(self):
        self.finish("As you can see both sides can access me! But regular people still can't. You need to have some force...")


@acl("jedi")  # ACL is used on the whole handler class!
class GalacticCity(tornado.web.RequestHandler):
    def get(self):
        self.finish("Your true wisdom is greatly appreciated.")

    def forbidden(self):
        if self.user == "sith":
            self.write("Dark side is not welcome here")
        else:
            self.write("Welcome traveller, we are afraid you cannot enter, we do not feel the force in you")


@acl(["sith"])
class DeathStar(tornado.web.RequestHandler):
    def get(self):
        self.write("Welcome to the Death Star my master!")

    def forbidden(self):
        if self.user == "jedi":
            self.write("Jedi Master, welcome to the Dark Side ]:->")
        else:
            raise HTTPError(403, "Get out of here or you will feel my Anger Force Attack!")

```

Easy! Now you know how to restrict the access to the certain areas with acl decorator. But how to indetify who is who?. Well, you have to figure out a method that works best for you. We can use an User Agent string in the Web world for example:

```python

# ACL check - we use browser user agent data to differ users (for simplicity!)
def check(self):
    user_agent = self.request.headers.get("User-Agent", "")
    # This will be quite simple, we consider
    # Chrome user as the Jedi and
    # IE user as the Sith - hey! no bad feelings!
    if user_agent.lower().find("chrome") != -1:
        self.user = "jedi"
    elif user_agent.lower().find("ie") != -1:
        self.user = "sith"
    else:
        self.user = "other"
    return self.user


# Default behaviour when user is not permitted to access the resource
def forbidden():
    raise HTTPError(403, "To enter this area you are allowed not")

# Initialize the Access Control List checker!
acl_init(check, forbidden)

```

That's it. As you can see we added pretty cool logic and it is still all readable and easy to maintain.

For a full example with annotated source check *[sample.py](https://github.com/bernii/tornado-acl/blob/master/sample.py)* file, you can run it via:

    python sample.py

Testing ![Continuous Integration status](https://secure.travis-ci.org/bernii/tornado-acl.png)
-------

Project has full unit test coverage which you can run from you shell.

    python test.py


Got some questions or suggestions? [Mail me](mailto:bkobos+ghacl@extensa.pl) directly or use the [issue tracker](https://github.com/bernii/tornado-acl/issues).

**May the Force be with you!**