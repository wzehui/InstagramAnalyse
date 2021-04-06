import openai

def detect_language(phase):
    OPENAI_API_KEY = 'sk-vNN45jeT8PUGFAKr1gbAniV4oy9W8XiNnvX3ZWBr'
    openai.api_key = OPENAI_API_KEY
    ans = openai.Answer.create(
        model="curie",
        documents=["ar", "de", "en", "ja", "ko", "nl", "ru"],
        question="What language is contained in this phase {}".format(phase),
        examples_context="This phase is written in German.",
        examples=[["What language is contained in this phase '🌹❤️😘   es ist "
                   "was es ist sagt die liebe❣' ","de"],
                  ["What language is contained in this phase 'sildipi thank "
                "you so much🙏🙏'", "en"]
                ],
        max_tokens=5,
        stop=["\n", "<|endoftext|>"]
      )
    return ans

