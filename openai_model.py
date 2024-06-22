from openai import OpenAI
import time


class OpenAIModel:
    def __init__(self, api_key: str, assistant_id: str):
        self.client = OpenAI(api_key=api_key)
        self.assistant_id = assistant_id
        self.thread_id = self.client.beta.threads.create().id
        self.run = None

    def create_assistant(self):
        self.client.beta.assistants.create(
            model="gpt-3.5-turbo",
            name="Dilligi AI Bot"
        )
    def submit_message(self, message: str):
        self.client.beta.threads.messages.create(
            thread_id=self.thread_id, role="user", content=message
        )
        self.run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
        )

        return self.run

    def get_list(self):
        return self.client.beta.threads.messages.list(thread_id=self.thread_id, order="desc")

    def get_reply(self) -> str:
        while self.run.status == "queued" or self.run.status == "in_progress":
            self.run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread_id,
                run_id=self.run.id,
            )
            time.sleep(0.5)
        res = self.get_list()
        return res.data[0].content[0].text.value

    def get_speech(self, message: str):
        res = self.client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=message
        )

        return res

    def get_text(self, voice_path: str):
        res = self.client.audio.transcriptions.create(
            file=open(voice_path, 'rb'),
            model="whisper-1"
        )

        return res
