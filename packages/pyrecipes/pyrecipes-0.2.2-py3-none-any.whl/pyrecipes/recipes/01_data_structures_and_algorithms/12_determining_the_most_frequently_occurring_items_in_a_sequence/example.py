"""
You have a sequence of items and you'd like to determine the most frequently
occurring items in the sequence.
"""

from collections import Counter


def main():
    words = [
        "look",
        "into",
        "my",
        "eyes",
        "look",
        "into",
        "my",
        "eyes",
        "the",
        "eyes",
        "the",
        "eyes",
        "the",
        "eyes",
        "not",
        "around",
        "the",
        "eyes",
        "don't",
        "look",
        "around",
        "the",
        "eyes",
        "not",
        "around",
        "the",
        "eyes",
        "look",
        "into",
        "the",
        "eyes",
        "my",
        "eyes",
        "you'r",
        "under",
    ]

    word_counts = Counter(words)
    top_three = word_counts.most_common(3)

    print(f"\nwords: {words}", end="\n\n")
    print(f"word counter: {word_counts}", end="\n\n")
    print(f"top three: {top_three}")


if __name__ == "__main__":
    main()
