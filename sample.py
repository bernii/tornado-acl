import tornado.ioloop
import tornado.web
from tornado.web import HTTPError
from acl import acl, acl_init
# Please refer to http://en.wikipedia.org/wiki/Jedi if something seems unclear. True wisdom you will find there ;)


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


class StartPoint(tornado.web.RequestHandler):
    def get(self):
        self.finish(
            "Welcome <b>" + check(self) + "</b>" +
            "<h1>Everyone can acess this area</h1>Choose a place to go: " +
            "<ul><li><a href='/potentium'>Potentium (Sith & Jedi)</a></li>" +
            "<li><a href='/lightside_hq'>GalacticCity (Jedi only)</a></li>" +
            "<li><a href='/darkside_hq'> DeathStar (Sith only)</a></li>" +
            "</ul>")


# Let's say all Force users can access it freely
class Potentium(tornado.web.RequestHandler):
    @acl(["jedi", "sith"])  # Used on single method!
    def get(self):
        self.finish("As you can see both sides can access me! But regular people still can't")


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


application = tornado.web.Application([
    (r"/", StartPoint),
    (r"/potentium", Potentium),
    (r"/lightside_hq", GalacticCity),
    (r"/darkside_hq", DeathStar),
], debug=True)  # <- turn the debug on so you can easily see the custom 403 messages

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
