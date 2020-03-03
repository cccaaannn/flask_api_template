def get_doom_days():
    import requests
    from bs4 import BeautifulSoup

    a = requests.get("https://www.watchisup.com/countdown/videogames/doom-eternal-br-release-date-2019-11-22-00-00").text

    s = BeautifulSoup(a, "html.parser")

    for i in s.findAll("li"):
        if('How many days until "Doom: Eternal" release date?' in i.text):
            v = (i.text.split("\n")[2])
    return v
