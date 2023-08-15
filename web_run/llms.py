import os
import sys
import json
import random
import tiktoken
token_enc = tiktoken.get_encoding("cl100k_base")
import torch
import openai
from langchain import PromptTemplate, OpenAI, LLMChain
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from web_run.config import OPENAI_API_KEY

OPENAI_CHAT_MODELS = ["gpt-3.5-turbo","gpt-3.5-turbo-16k","gpt-3.5-turbo-16k-0613"]
OPENAI_LLM_MODELS = ["text-davinci-003","text-ada-001"]
FASTCHAT_MODELS = ["vicuna-7b"]

    
class langchain_openai_chatllm:
    def __init__(self, llm_name):
        openai.api_key = OPENAI_API_KEY
        self.llm_name = llm_name
        human_template="{prompt}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        self.chat_prompt = ChatPromptTemplate.from_messages([human_message_prompt])
   
    def run(self, prompt, temperature=1, stop=['\n'], max_tokens=128):
        chat = ChatOpenAI(model=self.llm_name, temperature=temperature, stop=stop, max_tokens=max_tokens)
        self.chain = LLMChain(llm=chat, prompt=self.chat_prompt)
        return self.chain.run(prompt)
        
class langchain_openai_llm:
    def __init__(self, llm_name):
        openai.api_key = OPENAI_API_KEY
        self.prompt_temp = PromptTemplate(
            input_variables=["prompt"], template="{prompt}"
        )
        self.llm_name = llm_name
        
    def run(self, prompt, temperature=0.9, stop=['\n'], max_tokens=128):
        llm = OpenAI(model=self.llm_name, temperature=temperature, stop=['\n'], max_tokens=max_tokens)
        chain = LLMChain(llm=llm, prompt=self.prompt_temp)
        return chain.run(prompt)


class langchain_fastchat_llm:
    def __init__(self, llm_name):
        openai.api_key = "EMPTY" # Not support yet
        openai.api_base = "http://localhost:8000/v1"
        self.prompt_temp = PromptTemplate(
            input_variables=["prompt"], template="{prompt}"
        )
        self.llm_name = llm_name
        
    def run(self, prompt, temperature=0.9, stop=['\n'], max_tokens=128):
        llm = OpenAI(model=self.llm_name, temperature=temperature, stop=['\n'], max_tokens=max_tokens)
        chain = LLMChain(llm=llm, prompt=self.prompt_temp)
        return chain.run(prompt)

def get_llm_backend(llm_name):
    if llm_name in OPENAI_CHAT_MODELS:
        return langchain_openai_chatllm(llm_name)
    elif llm_name in OPENAI_LLM_MODELS:
        return langchain_openai_llm(llm_name)
    else:
        return langchain_fastchat_llm(llm_name)
    
if __name__ == "__main__":    
    # prompt = "The world is"
    # llm_name = "Salesforce/xgen-7b-4k-base"
    # llm_name = "mpt-30b-instruct"
    # llm_name = "longchat-7b-16k"
    llm_name = "gpt-3.5-turbo"
    # llm = vicuna_llm
    # llm = fast_llm(llm_name).run
    # llm = langchain_llm(llm_name).run
    llm = openai_chatllm(llm_name).run
    # llm = longchat_llm
    one_shot = """
Instruction: 
Find me machine wash men's t-shirts with long sleeve with color: country, and size: xx-large,
and price lower than 30.00 dollars
Action: 
search[men's t-shirts with long sleeve]


Observation: 
[ Back to Search ]
Page 1 (Total results: 50)
[ Next > ]

[ B09Q67H373 ]
JSPOYOU 2022 Newly T-Shirt for Mens Funny 3D Graphics Pattern Crewneck Short Sleeve Tees Big 
and Tall Summer Casual Comfy Top
$1.99 to $8.99

[ B09S3BN15C ]
Mens Linen Shirt,Men's Striped Shirts Casual Short Sleeve Button Down Shirts Regular Fit 
Hawaiian Shirts Beach Tees Tops
$3.78 to $11.38

[ B09Q8RD8YN ]
Bungo Stray Anime Dogs Anime Character, Long Sleeve, Sweatshirt, Hoodie, T shirt
$19.99

[ B09KLQLLT2 ]
Long Sleeve Superhero T Shirt Tank Top Mens Compression Shirt Men Workout Fitness Gym Shirt
$19.99

[ B00O30JLDK ]
Legendary Whitetails Men's Non-Typical Long Sleeve T-Shirt
$10.52 to $40.5

[ B09HGFV91W ]
ZHDD Tops for Mens, Men's Knight Punk Vintage Style Long Sleeve Asymmetric Hem Cowl Neck Teen
Boys Gothic Pullover
$4.98 to $7.99
Action:
think[I am simulating the action of clicking on that product to get more information about it such as the available colors, sizes, and the exact price. Based on the results, I should select the item [B00O30JLDK] as it seems to fit your criteria: a long sleeve men's t-shirt that might be under $30. However, I need to verify these details including the color, size, and final price. After the "click", I'll be able to provide more detailed information on this particular product. Therefore, my next action should be click[B00O30JLDK].]

Observation:
OK
Action:
click[B00O30JLDK]


Observation:
[ Back to Search ]
[ < Prev ]
color
  [ army ]
  [ big game field camo ]
  [ black ]
  [ cardinal ]
  [ charcoal heather ]
  [ inferno ]
  [ mossy oak bottomland ]
  [ mossy oak country ]
  [ mossy oak country dna ]
  [ mossy oak coyote ]
  [ slate ]
  [ swamp ]
  [ turkey ]
  [ flag ]
  [ country ]
  [ fish ]
size
  [ small ]
  [ medium ]
  [ large ]
  [ large tall ]
  [ x-large ]
  [ x-large tall ]
  [ xx-large ]
  [ xx-large big tall ]
  [ 3x-large big ]
  [ 3x-large big tall ]
  [ 4x-large big ]
  [ 4x-large big tall ]
  [ 5x-large big ]
Legendary Whitetails Men's Non-Typical Long Sleeve T-Shirt
Price: $10.52 to $40.5
Rating: N.A.
[ Description ]
[ Features ]
[ Reviews ]
[ Buy Now ]


Action:
think[The "Legendary Whitetails Men's Non-Typical Long Sleeve T-Shirt" is available in a variety of colors, including the requested color "country". It is also available in the requested size, "xx-large". However, the price range for this item is from $10.52 to $40.5. This suggests that depending on the specific color and size selection, the price could potentially exceed the specified budget of $30.]
Observation:
OK


Action:
click[country]
Observation:
You have clicked country.


Action:
click[xx-large]
Observation:
You have clicked xx-large.


Action:
click[Buy Now]
"""
    
    instruction = "i want to find decorative, multi-colored vinyl dots for my living room windows. the size should be 17.7 inches by 23.6 inches, and price lower than 90.00 dollars"
    prompt = f"{one_shot}\n\nInstruction:\n{instruction}\n\nActions:\n"
    token_len = len(token_enc.encode(prompt))
    print(token_len)
    a = llm(prompt, 0.8, ["\n"])
    # a = llm(prompt)
    print(a)
