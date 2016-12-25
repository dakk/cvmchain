from klein import Klein

app = Klein()

with app.subroute("/block") as app:
    @app.route("/height/:height")
    def getBlockByHeight (request):
        return b"These stairs lead to the lair of beasts."

    @app.route("/:hash")
    def getBlock (request):
        return b"These stairs lead to an ancient crypt."
        

with app.subroute("/transaction") as app:
    @app.route("/:hash")
    def getBlockByHash (request):
        return b"These stairs lead to the lair of beasts."


app.run("localhost", 8080)