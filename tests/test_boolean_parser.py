from sciseek.searchers.boolean_parser import BooleanParser, evaluate


def test_boolean_parser_parentheses():
    tree = BooleanParser("(alpha OR beta) AND NOT gamma").parse()
    assert evaluate(tree, "alpha and delta") is True
    assert evaluate(tree, "beta gamma") is False
