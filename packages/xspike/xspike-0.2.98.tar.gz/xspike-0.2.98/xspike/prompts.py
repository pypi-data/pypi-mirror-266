class Llama2Prompt:
    def __init__(self):
        self.user_start_token = "<s>[INST]"
        self.bot_start_token = "[/INST]"
        self.eos_token = "</s>"
        self.sys_prompt = (
            "<s>[INST] <<SYS>> You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. "
            "Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal data. "
            "Please ensure that your responses are socially unbiased and positive in nature. "
            "If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct."
            "If you don't know the answer to a question, please don't share false information.<</SYS>>"
        )

    def build_input(self, history=[], user_input=""):
        input_str = self.sys_prompt
        for idx, turn in enumerate(history):
            user_perfix = self.user_start_token if idx != 0 else ""
            bot_perfix = self.bot_start_token
            if turn["speaker"] == "user":
                input_str += user_perfix + turn["text"]
            else:
                input_str += bot_perfix + turn["text"] + self.eos_token
        user_perfix = self.user_start_token if len(history) != 0 else ""
        input_str += user_perfix + user_input + self.bot_start_token
        return input_str


class VicunaPrompt:
    def __init__(self):
        self.user_start_token = "USER:"
        self.bot_start_token = "ASSISTANT:"
        self.eos_token = "</s>"
        self.sys_prompt = (
            "A chat between a curious user and an artificial intelligence assistant."
            "The assistant gives helpful, detailed, and polite answers to the user's questions according to the context and related knowledge."
        )

    def build_input(self, history=[], user_input=""):
        input_str = self.sys_prompt
        for idx, turn in enumerate(history):
            user_perfix = self.user_start_token
            bot_perfix = self.bot_start_token
            if turn["speaker"] == "user":
                input_str += user_perfix + turn["text"]
            else:
                input_str += bot_perfix + turn["text"] + self.eos_token
        input_str += self.user_start_token + user_input + self.bot_start_token
        return input_str



class MistralPrompt:
    def __init__(self):
        self.user_start_token = "[INST]"
        self.bot_start_token = "[/INST]"
        self.eos_token = "</s>"
        self.sys_prompt = (
            ""
        )

    def build_input(self, history=[], user_input=""):
        input_str = self.sys_prompt
        for idx, turn in enumerate(history):
            user_perfix = self.user_start_token
            bot_perfix = self.bot_start_token
            if turn["speaker"] == "user":
                input_str += user_perfix + turn["text"]
            else:
                input_str += bot_perfix + turn["text"] + self.eos_token
        input_str += self.user_start_token + user_input + self.bot_start_token
        return "<s>" + input_str



PROMPT_DICT = {"llama2": Llama2Prompt(), "vicuna": VicunaPrompt(), "mistral": MistralPrompt()}
