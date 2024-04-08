"""
Your program has become and unreadable mess of hardcoded slice indices and you want to clean it up.
"""

#         0123456789012345678901234567890123456789012345678901234567890
record = "....................100          .......513.25      ........."


def example_1():
    print(f'\n{"=" * 50}\nExample 1\n{"=" * 50}')
    print(f"Record: {record}\n")
    print(
        "parsing the record with the hardcoded slices [20:32] and [40:48] to find the product..."
    )
    qty = int(record[20:32])
    value = float(record[40:48])
    print(f"Qty: {qty}")
    print(f"Value: {value}")
    print(f"Total: {qty * value}")


def example_2():
    print(f'\n{"=" * 50}\nExample 2\n{"=" * 50}')
    print(f"Record: {record}\n")
    print("parsing the record with the named slices to find the product...\n")
    qty = slice(20, 32)
    value = slice(40, 48)
    total = int(record[qty]) * float(record[value])

    print(f"Qty: {qty}")
    print(f"Value: {value}")
    print(f"Total: {total}")


def main():
    example_1()
    example_2()


if __name__ == "__main__":
    main()
