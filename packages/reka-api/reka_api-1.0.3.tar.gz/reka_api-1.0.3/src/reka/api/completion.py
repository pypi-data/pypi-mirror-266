"""Completion-related server interactions."""

from typing import List, Optional, cast

import reka.api.driver as driver


def completion(
    prompt: str,
    model_name: str = "default",
    request_output_len: Optional[int] = None,
    temperature: Optional[float] = None,
    random_seed: Optional[int] = None,
    runtime_top_k: Optional[int] = None,
    runtime_top_p: Optional[float] = None,
    frequency_penalty: Optional[float] = None,
    presence_penalty: Optional[float] = None,
    length_penalty: Optional[float] = None,
    stop_words: Optional[List[str]] = None,
) -> str:
    """Request a text completion in synchronous mode.

    Example usage:
    ```python
    import reka
    reka.API_KEY = "APIKEY"

    result = reka.completion("What is the capital of the UK?")
    print(completion)  # "The capital of the United Kingdom is London. ..."
    ```

    Args:
        prompt: string.

        model_name: Name of model.
        request_output_len: Completion length in tokens.
        temperature: Softmax temperature, higher is more diverse.
        random_seed: Seed to obtain different results.
        runtime_top_k: Keep only k top tokens when sampling.
        runtime_top_p: Keep only top p quantile when sampling.
        frequency_penalty: Penalize repetition. 0 means no penalty.
        presence_penalty: Penalize repetition. 0 means no penalty.
        length_penalty: Penalize short answers. 1 means no penalty.
        stop_words: Optional list of words on which to stop generation.

    Returns:
        model completion.
    """
    json_dict = {
        key: value
        for key, value in [
            ("prompts", [prompt]),
            ("model_name", model_name),
            ("request_output_len", request_output_len),
            ("temperature", temperature),
            ("random_seed", random_seed),
            ("runtime_top_k", runtime_top_k),
            ("runtime_top_p", runtime_top_p),
            ("frequency_penalty", frequency_penalty),
            ("presence_penalty", presence_penalty),
            ("length_penalty", length_penalty),
            ("stop_words", stop_words or []),
        ]
        if value is not None
    }

    response = driver.make_request(
        method="post",
        endpoint="completion",
        headers={"Content-Type": "application/json"},
        json=json_dict,
    )

    return cast(str, response["text"][0])
