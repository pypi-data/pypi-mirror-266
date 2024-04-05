from kiwipiepy import Kiwi


def fetch_kiwi() -> Kiwi:
    """
    fetch kiwi with user-defined rules
    """
    kiwi = Kiwi(model_type="sbg")  # use the better model by default
    kiwi.add_user_word(".", tag="SF", score=10)
    kiwi.add_user_word("우리말", tag="NNP", score=10)
    kiwi.add_user_word("점순이", tag="NNP", score=10)
    kiwi.add_user_word("할금할금", tag="MAG", score=10)
    kiwi.add_pre_analyzed_word(
        "벗어.", [("벗", "VV-R"), ("어", "EF"), (".", "SF")], score=10
    )
    kiwi.add_pre_analyzed_word(
        "누구신가요", [("누구", "NP"), ("이", "VCP"), ("시", "EP"), ("ᆫ가요", "EF")], score=10
    )
    return kiwi
