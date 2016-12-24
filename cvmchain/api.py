from klein import Klein

app = Klein()

with app.subroute("/branch") as app:
    @app.route("/lair")
    def lair(request):
        return b"These stairs lead to the lair of beasts."

    @app.route("/crypt")
    def crypt(request):
        return b"These stairs lead to an ancient crypt."

    @app.route("/swamp")
    def swamp(request):
        return b"A stair to a swampy wasteland."

app.run("localhost", 8080)