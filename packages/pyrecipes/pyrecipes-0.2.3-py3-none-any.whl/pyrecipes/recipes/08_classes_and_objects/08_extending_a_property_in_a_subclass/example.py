"""
Within a subclass, you want to extend the functionality of a property
defined in a parent class.
"""


class Person:
    def __init__(self, name):
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError("Expected a string.")
        self._name = value

    @name.deleter
    def name(self):
        print("Cannot delete attribute.")


class SubPerson(Person):
    @property
    def name(self):
        print("getting name")
        return super().name

    @name.setter
    def name(self, value):
        print(f"setting name to {value}")
        super(SubPerson, SubPerson).name.__set__(self, value)

    @name.deleter
    def name(self):
        print("Deleting name.")
        super(SubPerson, SubPerson).name.__delete__(self)


def main():
    sub_person = SubPerson("Chris")
    print(sub_person.name)
    sub_person.name = "Bob"
    del sub_person.name


if __name__ == "__main__":
    main()
