import openai
from dotenv import find_dotenv, load_dotenv
import time
import logging
import json

load_dotenv()

class OpenAssist:
    def __init__(self):
        self.client = openai.OpenAI()
        self.thread_id = None
        self.assistant_id = None
        
        # Load thread and assistant IDs from file if available
        self.load_ids()
        
        if self.assistant_id is None:
            self.create_assistant()
            
        if self.thread_id is None:
            self.create_thread()
        
    def load_ids(self):
        try:
            with open("ids.json", "r") as file:
                data = json.load(file)
                self.thread_id = data.get("thread_id")
                self.assistant_id = data.get("assistant_id")
        except FileNotFoundError:
            logging.info("No IDs file found.")
    
    def save_ids(self):
        data = {
            "thread_id": self.thread_id,
            "assistant_id": self.assistant_id
        }
        with open("ids.json", "w") as file:
            json.dump(data, file)
    
    def create_assistant(self):
        assistant = self.client.beta.assistants.create(model="gpt-3.5-turbo-16k")
        self.assistant_id = assistant.id
        self.save_ids()
    
    def create_thread(self):
        thread = self.client.beta.threads.create()
        self.thread_id = thread.id
        self.save_ids()
    
    def create_message(self, message_content):
        message = self.client.beta.threads.messages.create(
            thread_id=self.thread_id, role="user", content=message_content
        )
        return message
    
    def add_message_to_thread(self, role, content):
        if self.thread_id:
            self.client.beta.threads.messages.create(
                thread_id=self.thread_id,
                role=role,
                content=content
            )  

    def run_assistant(self):
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
        )
        return run
    
    def wait_for_run_completion(self, run_id, sleep_interval=5):
        while True:
            try:
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread_id, run_id=run_id
                )
                if run.completed_at:
                    messages = self.client.beta.threads.messages.list(thread_id=self.thread_id)
                    summary = []
                    last_message = messages.data[0]
                    response = last_message.content[0].text.value
                    summary.append(response)
                    self.summary = "\n".join(summary)
                    print(f"Assistant Response: {response}")
                    break
            except Exception as e:
                logging.error(f"An error occurred while retrieving the run: {e}")
                break
            logging.info("Waiting for run to complete...")
            time.sleep(sleep_interval)
            
    def get_summary(self):
        return self.summary 

    def get_previous_response(self):
        # Get previous response from the last completed run
        try:
            messages = self.client.beta.threads.messages.list(thread_id=self.thread_id)
            response = messages.data[0].content[0].text.value
            return response
        except Exception as e:
            logging.error(f"An error occurred while retrieving the previous response: {e}")
            return ""    
     

def main():
    open_assist = OpenAssist()
      
    message_content = input("Enter your message: ")
    
    open_assist.create_message(message_content)
    
    open_assist.add_message_to_thread(role="user", content=message_content)
    
    run = open_assist.run_assistant()
    
    open_assist.wait_for_run_completion(run.id)
    
    open_assist.get_previous_response()

if __name__ == "__main__":
    main()
