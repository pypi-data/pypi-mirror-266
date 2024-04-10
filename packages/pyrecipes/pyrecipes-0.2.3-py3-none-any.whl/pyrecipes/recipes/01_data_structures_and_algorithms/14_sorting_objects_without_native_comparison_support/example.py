"""
You want to sort objects of the same class, but they don't natively
support comparison operations.
"""

from operator import attrgetter


class User:
    def __init__(self, user_id):
        self.user_id = user_id

    def __repr__(self):
        return f"User({self.user_id})"


def main():
    users = [User(12), User(23), User(2), User(99)]
    print(f"Users: {users}\n")

    print("Sorted using lambda:")
    print(sorted(users, key=lambda u: u.user_id), end="\n\n")

    print("Sorted using attrgetter:")
    print(sorted(users, key=attrgetter("user_id")))


if __name__ == "__main__":
    main()
