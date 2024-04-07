# This is the code to make scalesafe seamlessly work with OpenAI API useage of AI models.

from .generic import GenericMonitor


class OpenAIChatMonitor(GenericMonitor):
    """This is a monitor object to help to manage the compliance of OpenAI Chat API useage."""

    def __init__(self, api_key=None, location=None):
        super().__init__(api_key, location)

    def monitor(self, response, messages, api_key=None):
        """
        response: ChatCompletion - This is the response from the OpenAI chat API.
        """

        data = {
            "model_version": response.model,
            "model_start_time": response.created,
            "model_end_time": response.created,
            "model_inputs": messages,
            "model_outputs": response.choices[0].message.content,
            "openai_response_id": response.id,
        }

        return super().monitor(data, api_key)

    def wrapper(client, model, messages, api_key=None, **kwargs):
        """This is a wrapper around the OpenAI chat completions.create method to monitor the useage."""
        monitor = OpenAIChatMonitor()
        response = client.chat.completions.create(
            model=model, messages=messages, **kwargs
        )
        monitor.monitor(response, messages, api_key)
        return response


class OpenAIAssistantMonitor(GenericMonitor):
    """This is a monitor object to help to manage the compliance of OpenAI Assistant API useage."""

    def __init__(self, api_key=None, location=None):
        super().__init__(api_key, location)

    def monitor(self, run, messages, api_key=None):
        """
        response: AssistantCompletion - This is the response from the OpenAI assistant API.
        """
        assert messages.data[0].assistant_id == run.assistant_id
        data = {
          "model_version": run.assistant_id,
          "model_start_time": run.created_at,
          "model_end_time": run.completed_at if run.completed_at else run.cancelled_at,
          "model_inputs": {'instructions': run.instructions},
          "thread_id": run.thread_id,
          "model_outputs": [c.text.value for c in messages.data[0].content],
        }
        return super().monitor(data, api_key)
