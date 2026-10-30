from app.validation import check_tweets, parse_json

STYLES = ["engaging"] * 3 + ["promotional"] * 2 + ["witty"] * 3 + ["informative"] * 2


def make(n=10, length=50):
    return {"tweets": [{"style": STYLES[i % 10], "text": f"{i} " + "x" * length} for i in range(n)]}


def test_parse_json_with_fences():
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_parse_json_with_stray_text():
    assert parse_json('Here you go: {"a": 1} thanks') == {"a": 1}


def test_valid_tweets_pass():
    tweets, problem = check_tweets(make())
    assert problem is None and len(tweets) == 10


def test_wrong_count_fails():
    assert check_tweets(make(9))[1] is not None


def test_too_long_fails():
    assert "280" in check_tweets(make(length=300))[1]


def test_style_mix_enforced():
    data = make()
    data["tweets"][0]["style"] = "witty"
    assert "mix" in check_tweets(data)[1].lower()
