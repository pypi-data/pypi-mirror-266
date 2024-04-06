# MODULO, del paquete HACK4u

class Courses:

    def __init__(self, name, duration, link):

        self.name = name
        self.duration = duration
        self.link =  link

    def __repr__(self): # Es como el __str__ pero podemos visualizar los elementos si iterar con con un for, los itera ya el podemos elegir con courses[1]

        return f"{self.name} [{self.duration}] horas, link: {self.link}"


courses = [

    Courses("Introducción a Linux", 15, "https://hack4u.io/"),
    Courses("Personalización de Linux", 3, "https://hack4u.io/"),
    Courses("Introducción al Hacking", 53, "https://hack4u.io/")
]


def list_courses():
    for course in courses:
        print(course)

def search_name(name):
    for course in courses:
        if course.name == name:
            return f"[+] {course}"
    return None