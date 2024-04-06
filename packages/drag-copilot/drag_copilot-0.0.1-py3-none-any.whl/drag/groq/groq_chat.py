import os
import re
from abc import abstractmethod

import pandas as pd
from groq import Groq

from ..base.base import Drag


class Groq_Chat(Drag):
    def __init__(self, config=None):
        Drag.__init__(self, config=config)

        if "api_key" in config:
            self.client = Groq(api_key=config["api_key"])
        if "model" in config:
            self.model = config["model"]
        else:
            self.model = "mixtral-8x7b-32768"

    def submit_prompt(self, prompt, temperature=0.4, **kwargs) -> str:
        if prompt is None:
            raise Exception("Prompt is None")
        if len(prompt) == 0:
            raise Exception("Prompt is empty")
        
        chat_completion = self.client.chat.completions.create(
            messages=prompt,
            model=self.model,
            temperature=temperature,
        )
        llm_response = self.clear_llm_response(llm_response=chat_completion.choices[0].message.content)
        return llm_response
    
    def clear_llm_response(self, llm_response, **kwargs):
        llm_response = self.extract_llm_response_between_triple_backticks(llm_response=llm_response)
        llm_response = self.extract_characters_between_asterisks(llm_response=llm_response)
        llm_response = llm_response.replace("```", "")
        llm_response = llm_response.replace("python", "")
        llm_response = llm_response.strip()
        return llm_response
    
    def extract_llm_response_between_triple_backticks(self, llm_response):
        start_index = llm_response.find('```')
        end_index = llm_response.find('```', start_index + 3)
        if (start_index != -1 or end_index != -1) and start_index != end_index:
            return llm_response[start_index:end_index+3]
        return llm_response
        
    def extract_characters_between_asterisks(self, llm_response):
        start_index = llm_response.find("*")
        end_index = llm_response.rfind("*")
        if (start_index != -1 or end_index != -1) and start_index != end_index:
            return llm_response[start_index+2:end_index-1]
        return llm_response