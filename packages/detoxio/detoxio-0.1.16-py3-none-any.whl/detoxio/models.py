# Description: Common data models for the SDK

# Data class representing a generated prompt
class LLMPrompt:
    def __init__(self, content: str, role="user"):
        self.role = role
        self.content = content

    def text(self):
        return self.content

# Data class representing a prompt response from an LLM model
class LLMResponse:
    def __init__(self, content: str, skip_evaluation: bool = False):
        self.content = content
        self.skip_evaluation = skip_evaluation

    def skip(self):
        """
        Skip evaluation of this response
        """
        self.skip_evaluation = True

    def is_skipped(self):
        """
        Check if the evaluation of this response is skipped
        """
        return self.skip_evaluation

# Data class representing the result of a prompt and response
# evaluation for security vulnerabilities
class LLMScanResult:
    def __init__(self):
        self.results = []

    # Store the raw protobuf response from the API for
    # rendering into various forms
    def add_raw_result(self, response):
        self.results.append(response)

    def __iter__(self):
        return iter(self.results)

