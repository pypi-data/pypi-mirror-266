import requests

class downloadpy():
    def __init__(self,fileurl,namefile) -> None:
        self.file = fileurl
        self.name = namefile

    def downloadfile(self):
        r = requests.get(self.file)

        with open(self.name, 'wb') as f: 
            f.write(r.content)