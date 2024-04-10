"""
You need to access various services via HTTP as a client. For example,
downloading or interacting with a REST-based API.
"""

from urllib import request, parse
import requests


def example_1():
    """For very simple requests"""
    # Base URL being accessed
    url = "http://httpbin.org/"

    # Dictionary of query parameters (if any)
    params = {"name1": "value1", "name2": "value2"}

    # Encode the query string
    query_string = parse.urlencode(params)

    # Make GET request
    response = request.urlopen(f"{url}get?{query_string}")
    print(response.read().decode("utf8"))

    # Make POST request
    response = request.urlopen(f"{url}post", query_string.encode("ascii"))
    print(response.read().decode("utf8"))

    # With headers
    headers = {"User-agent": "nunya/biznis", "Spam": "eggs"}
    req = request.Request(f"{url}post", query_string.encode("ascii"), headers=headers)
    response = request.urlopen(req)
    print(response.read().decode("utf8"))


def example_2():
    """For anything more complicated than the previous example, use requests."""
    url = "http://httpbin.org/"

    params = {"name1": "value1", "name2": "value2"}

    headers = {"User-agent": "nunya/biznis", "Spam": "eggs"}

    response = requests.post(f"{url}post", data=params, headers=headers)
    print(response)
    print(response.status_code)
    print(response.json())


def example_3():
    response = requests.head("http://python.org/index.html")
    print(response)
    print(response.headers)


def example_4():
    url = "http://httpbin.org/"
    response1 = requests.get(url)
    response2 = requests.get(url, cookies=response1.cookies)
    print(response1)
    print(response2)


def main():
    # example_1()
    # example_2()
    # example_3()
    # example_4()
    pass


if __name__ == "__main__":
    main()
