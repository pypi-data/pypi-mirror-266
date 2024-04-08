from html_text_color.create_colored import from_text, from_ids
from transformers import AutoTokenizer


def test_single():
    tokens = ["I", "▁am", "▁a", "▁sentence", "."]
    numbers = [1, 2, 3, 4, 5]

    html = from_text(tokens, numbers, color_order="b")
    with open("test_outputs/test_single.html", "w") as f:
        f.write(html)


def test_multiple():
    tokens = [
        ["I", "▁am", "▁a", "▁sentence", "."],
        ["I", "▁am", "▁another", "▁sentence", "."],
    ]
    numbers = [
        [[1, 0, 5], [2, 0, 2], [3, 0, 3], [4, 0, 4], [5, 0, 5]],
        [[5, 0, 0], [4, 2, 0], [3, 4, 0], [2, 6, 0], [1, 8, 0]],
    ]

    html = from_text(tokens, numbers)
    with open("test_outputs/test_multiple.html", "w") as f:
        f.write(html)


def test_tokens():
    model_name = "gpt2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    ids = tokenizer.encode("I am a sentence.")
    numbers = [1, 2, 3, 4, 5]

    html = from_ids(ids, tokenizer, numbers)
    with open("test_outputs/test_tokens.html", "w") as f:
        f.write(html)


if __name__ == "__main__":
    test_single()
    test_multiple()
    test_tokens()
