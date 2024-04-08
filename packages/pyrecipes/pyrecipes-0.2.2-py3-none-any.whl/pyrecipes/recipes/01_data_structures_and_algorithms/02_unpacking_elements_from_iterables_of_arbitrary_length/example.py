"""
You need to unpack N elements from an iterable, but the iterable may
be longer than N elements, causing 'too many values to unpack' exception
"""


def drop_first_last(grades):
    assert len(grades) >= 3, "expect grades to be of length at least 3"
    _, *middle, _ = grades
    return sum(middle) / len(middle)


def main():
    grades = [30, 60, 74, 76, 78, 90]
    print("grades:", grades)
    print("avg:", drop_first_last(grades))

    record = ("Dave", "dave@example.com", "777-555-1212", "847-555-1212")
    print("record:", record)
    name, email, *phone_numbers = record
    print("name:", name)
    print("email:", email)
    print("phone numbers:", phone_numbers)


if __name__ == "__main__":
    main()
