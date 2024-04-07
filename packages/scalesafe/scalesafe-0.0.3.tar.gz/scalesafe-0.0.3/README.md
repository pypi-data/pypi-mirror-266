# ScaleSafe Monitoring Engine

This codebase is the open-source toolkit for integrating monitoring into an AI system, for use generally with [scalesafe.ai](scalesafe.ai). The goal is to help you log AI usage, screen responses for safety and compliance, allow convenient human-in-the-loop control and request-for-manual-review handling, support continued risk monitoring, and provide risk and compliance audits. 

> This supports the EU AI Act, New York Bill 144, and other AI regulations.


## How this works?
You can assess the safety and compliance obligations and limitations of AI system use according to your model, its properties, and where it's being used. Go to [assess.scalesafe.ai](assess.scalesafe.ai) to see the requirements. This will create an account and allow you to begin monitoring. You can find your [API key](app.scalesafe.ai/keys) in the app.

To integrate with your app, choose the appropriate monitoring class and include it with your AI system / model usage. 

```bash
pip install scalesafe
```

#### API Keys
For anything here to connect to the server, you need to set your API key. You can find your model-specific secret at [app.scalesafe.ai/models/<model>/api-keys](app.scalesafe.ai/models/<model>/api-keys). You can pass them to any function with `api_key=` or set them as an environment variable `SCALESAFE_API_KEY`. The key will look something like `sk-72cb69c4af4d406c854d135b66b67f-iy6liAQuToYDBIA1h44bfTq7Rgj1`. All monitoring, benchmarking, screening, and human-in-the-loop controls are unique to the model and its use case.

### Monitoring OpenAI Chat Example
When a synchronous AI model is being used, you just need to monitor the input and output of the model. This can be done with the `OpenAIChatMonitor` class.
```python
from scalesafe.openai import OpenAIChatMonitor
from openai import OpenAI

client = OpenAI()
monitor = OpenAIChatMonitor() # We create a monitor instance

response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=user_inputs
)

monitor.monitor(response, user_inputs) # This logs for future audits
```
Which will allow you to log and monitor the chat completions.

#### Screening Inputs and Outputs

You could also include input and output screening on model use with the `screen` parameters.
```python
from scalesafe.exceptions import UnsafeInputError, BannedOutputError

try:
    monitor.monitor(response, user_inputs, screen_inputs=True, screen_outputs=True)
except (UnsafeInputError, BannedOutputError) as e:
    print(f"Bad model usage. Error: {e}")
```

### Check Compliance Status
If want to check if the model is still compliant with the requirements (which update overtime as regulation changes), you can use the `status` method.
```python
from scalesafe.exceptions import OutOfComplianceError, HumanReviewNeededException
try:
    monitor.status()
except OutOfComplianceError as e:
    print(f"Model is out of compliance. Error: {e}")
```

### Complete Required Benchmarks
Some applications require that you complete certain benchmarks to ensure compliance. 
```python
from scalesafe.benchmarking import Benchmarker
dataset = Benchmarker('nyEmploymentScreening') # Example bias screening for employment AI in New York

for item in dataset:
    print(item)  # Process the batch here
    result = True if np.random.random() > 0.5 else False # Do some AI
    dataset.answer(result, item['id'])  # We add our responses to the buffer

dataset.post_answers() # We send them to our audit team for analysis
```

<!-- ### Human in the loop -->


## Other examples

### For OpenAI Assistants
This can be a little more complicated, as we're no longer working synchronously. We still need to monitor all the usage of the model (including start and end time). The simplest way to format this is to use the `OpenAIAssistantMonitor` class.
```python
from scalesafe.openai import OpenAIAssistantMonitor
from openai import OpenAI

client = OpenAI()
monitor = OpenAIAssistantMonitor() # We create a monitor instance

assistant = client.beta.assistants.create( # You might have created this assistant previously, and it should be supported by a risk assessment at assess.scalesafe.ai.
  name="Math Tutor",
  instructions="You are a personal math tutor. Write and run code to answer math questions.",
  tools=[{"type": "code_interpreter"}],
  model="gpt-4-turbo-preview",
)

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
)

run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="Please address the user as Jane Doe. The user has a premium account."
)

import time
while run.status in ['queued', 'in_progress', 'cancelling']:
  time.sleep(1) # Wait for 1 second
  run = client.beta.threads.runs.retrieve(
    thread_id=thread.id,
    run_id=run.id
  )

if run.status == 'completed': 
  messages = client.beta.threads.messages.list(
    thread_id=thread.id
  )
  
monitor.monitor(message, assistant, thread.id) # We pass in everything to avoid the monitor needed to call OpenAI again.
```

