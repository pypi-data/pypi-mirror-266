
import requests
import os, json

class Benchmarker:
    """
    A class to interact with the ScaleSafe benchmarking API. This will allow you to stream a benchmarking dataset and submit answers to the server for auditing and compliance reporting.

    :param benchmark: The benchmark ID to fetch data from.
    :param batch_size: The number of items to fetch in each batch.
    :param api_key: The API key for authentication, if required.
    """

    def __init__(self, benchmark, batch_size=10, api_key=None):
        self.benchmark = benchmark
        self.batch_size = batch_size
        self.last_doc_id = None
        self.data_buffer = []  # Buffer to hold fetched items
        self.is_finished = False
        self.api_key = api_key if api_key else os.getenv("SCALESAFE_API_KEY")
        self.answer_buffer = []

    def get_api_key(self, api_key):
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("SCALESAFE_API_KEY")
            if not self.api_key:
                raise ValueError("API key not provided or set in environment variables. Get one at app.scalesafe.com/models/<model>/api-keys.")

    def fetch_next_batch(self):
        """Fetch the next batch of data from the server and refill the buffer."""
        if self.is_finished:
            return

        params = {
            'benchmark': self.benchmark,
            'batchSize': self.batch_size,
        }

        headers = {
            'Authorization': f'Bearer {self.api_key}'  # Set the Authorization header with the Bearer token
        }

        if self.last_doc_id:
            params['lastDocId'] = self.last_doc_id

        response = requests.get('https://get-benchmark-datum-zc6tu6qxxa-uc.a.run.app', params=params, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error fetching data: {response.json().get('error', '')}")

        data = response.json()

        if not data.get('data'):
            self.is_finished = True
            return

        self.data_buffer.extend(data['data'])
        self.last_doc_id = data.get('nextLastDocId')

        if self.last_doc_id is None:
            self.is_finished = True

    def __iter__(self):
        return self

    def __next__(self):
        if not self.data_buffer and not self.is_finished:
            self.fetch_next_batch()

        if not self.data_buffer:
            raise StopIteration
        
        return self.data_buffer.pop(0)  # Return and remove the first element from the buffer
    

    def answer(self, output, id):
        """Answer the question with the given output."""
        if type(id) is not str:
            raise ValueError("ID must be a string.")
        if type(output) is dict:
            self.answer_buffer.append({'id': id, 'output': output})
        if type(output) is bool:
            self.answer_buffer.append({'id': id, 'output': 'true' if output else 'false'})
        elif type(output) is not str:
            raise ValueError("Output should be a string or a dictionary.")
        else:
            self.answer_buffer.append({'id': id, 'output': output})


    def post_answers(self, submit_batch_size=100):
        """
        Posts responses to the server in batches.

        
        :param submit_batch_size: The number of responses to send in each batch.
        :param api_key: The API key for authentication, if required.
        """
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        total_batches = (len(self.answer_buffer) + submit_batch_size - 1) // submit_batch_size  # Calculate the total number of batches

        for i in range(total_batches):
            batch = self.answer_buffer[i*submit_batch_size : (i+1)*submit_batch_size]
            data = {
                'benchmark': self.benchmark,
                'data': batch
            }

            response = requests.post('https://post-benchmark-response-zc6tu6qxxa-uc.a.run.app', json=data, headers=headers)
            if response.status_code != 200:
                print(f"Error posting batch {i+1}: {response.json().get('error', 'Unknown error')}")
            

        print("Answers uploaded successfully.")