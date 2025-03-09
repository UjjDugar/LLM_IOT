from openai import OpenAI
import os, csv
from datetime import datetime

class GPT: 

    def __init__(self, model_name):
        self.model_name = model_name
        pass

    def get_response(
            self, 
            prompt,
            system_prompt="You are a helpful assistant", 
            api_key = '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',
            logging=False):

        if self.model_name == 'test':
            return 'testing text'

        client = OpenAI(api_key=api_key)

        completion = client.chat.completions.create(
        model=self.model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        )

        result = completion.choices[0].message.content

        if logging:
            # Log prompt, result, timestamp, and model used
            log_file = 'LLM_logging.csv'
            file_exists = os.path.isfile(log_file)

            with open(log_file, mode='a', newline='') as file:
                writer = csv.writer(file)

                # Write header if file does not exist
                if not file_exists:
                    writer.writerow(["Timestamp", "Model Name", "Prompt", "Response"])

                # Write the log entry
                writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.model_name, prompt, result.replace('\n', ' ')])

        return result
    
if __name__ == "__main__":
    gpt = GPT(model_name="gpt-3.5-turbo")
    with open('prompt_start.txt', 'r') as f:
        prompt_start = f.read()
    prompt = prompt_start + input('Enter a prompt: ')
    with open('api_key.txt', 'r') as f:
        api_key = f.read()
    print(gpt.get_response(prompt, api_key=api_key))