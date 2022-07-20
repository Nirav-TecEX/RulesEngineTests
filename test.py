class Temp:
    def __init__(self):
        self.__age = ""

    @property
    def age(self):
        print("GETTING")
        return self.__age
    @age.setter
    def age(self, name):
        print("SETTING")
        self.__age = name
    
    def abc(self):
        print(self.age)

    def b(self):
        self.age = 'nirav'
        print(self.age)

temp = Temp()

temp.abc()

temp.b()

