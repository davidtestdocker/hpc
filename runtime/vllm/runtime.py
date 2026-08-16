import json
import urllib.request

from runtime.base import Runtime


class VLLMRuntime(Runtime):
    def __init__(self, endpoint):
        # Store the vLLM server endpoint without a trailing slash
        self.endpoint = endpoint.rstrip("/")

    def initialize(self):
        # Use the models endpoint to verify that the vLLM server is reachable
        url = f"{self.endpoint}/v1/models"

        # Send an HTTP GET request to the vLLM server
        with urllib.request.urlopen(url, timeout=5) as response:
            # Treat any non-200 response as runtime initialization failure
            if response.status != 200:
                raise RuntimeError("vLLM runtime is not available")

    def run(self, request):
        # Build the OpenAI-compatible chat completion endpoint
        url = f"{self.endpoint}/v1/chat/completions"

        # Convert the Python dictionary into JSON bytes for the HTTP request body
        payload = json.dumps(request).encode("utf-8")

        # Build an HTTP POST request
        http_request = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        # Send the inference request to vLLM
        with urllib.request.urlopen(http_request, timeout=60) as response:
            # Decode the JSON response and return it as a Python dictionary
            return json.loads(response.read().decode("utf-8"))

    def get_info(self):
        # Return metadata describing this runtime
        return {
            "name": "vllm",
            "type": "llm-inference",
            "gpu_required": True,
            "endpoint": self.endpoint,
        }
