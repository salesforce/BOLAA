"""
 Copyright (c) 2023, salesforce.com, inc.
 All rights reserved.
 SPDX-License-Identifier: Apache License 2.0
 For full license text, see the LICENSE file in the repo root or https://www.apache.org/licenses/LICENSE-2.0
"""

import time
import os
import web_run.pre_prompt as pre_prompt
from web_run.utils import get_query
from web_run.llms import token_enc


control_dict = {"Search_Webrun_Agent":"search",
                "Think_Webrun_Agent":"think",
                "Click_Webrun_Agent":"click"}
        
class ClickAgent:
    def __init__(self, llm, context_len=2000):
        self.type = "Click_Webrun_Agent"
        self.life_label = time.time()
        self.name = f"{self.type}_{self.life_label}"
        self.llm = llm 
        self.context_len = context_len
        self.task = None
    
    def action_parser(self, text, available_actions):
        nor_text = text.strip().lower()
        if nor_text.startswith('search'):
            query = get_query(nor_text)
            return f"search[{query}]"
        if nor_text.startswith('click'):
            if 'click' in available_actions:
                for a in available_actions['click']:
                    if a.lower() in nor_text:
                        return f"click[{a}]"
        return text
    
    def avai_action_prompt(self, available_actions):
        if 'search' in available_actions:
            return "{search}"
        elif 'click' in available_actions:
            actions = available_actions['click']
            ac_string = "\t".join(actions)
            return f"click:[{ac_string}]"
    
    def prompt_layer(self, control_prompt, available_actions):
        one_shot = pre_prompt.click
        initial = f"Instruction:\n{self.task}"
        actions_prompt = f"current available action is {self.avai_action_prompt(available_actions)[:3000]}"
        remain_context_space = (self.context_len - len(token_enc.encode(initial+one_shot+actions_prompt)))*3
        prompt = f"{one_shot}\n{initial}\n{control_prompt[-int(remain_context_space):]}\n{actions_prompt}\n\nAction:"
        if len(token_enc.encode(prompt)) > self.context_len:
            print("this prompt may be over context length requirements:")
            print("---------\n")
            print(prompt)
            print("\n---------")
        return prompt
    
    def llm_layer(self, prompt):
        return self.llm(prompt)
    
    def forward(self, control_prompt, available_actions):
        prompt = self.prompt_layer(control_prompt, available_actions)
        action = self.llm_layer(prompt).lstrip(' ')
        action = self.action_parser(action, available_actions)
        return action

class SearchAgent:
    def __init__(self, llm, context_len=2000):
        self.type = "Search_Webrun_Agent"
        self.life_label = time.time()
        self.name = f"{self.type}_{self.life_label}"
        self.llm = llm 
        self.context_len = context_len
        self.task = None
    
    def action_parser(self, text, available_actions):
        nor_text = text.strip().lower()
        if nor_text.startswith('search'):
            query = get_query(nor_text)
            return f"search[{query}]"
        return text
        
    def prompt_layer(self, control_prompt, available_actions):
        one_shot = pre_prompt.search
        remain_context_space = (self.context_len - len(token_enc.encode(one_shot)))*3
        prompt = f"{one_shot}{control_prompt[-int(remain_context_space):]}\n\nAction:"
        if len(token_enc.encode(prompt)) > self.context_len:
            print("this prompt may be over context length requirements:")
            print("---------\n")
            print(prompt)
            print("\n---------")
        return prompt
    
    def llm_layer(self, prompt):
        return self.llm(prompt)
    
    def forward(self, control_prompt, available_actions):
        prompt = self.prompt_layer(control_prompt, available_actions)
        action = self.llm_layer(prompt).lstrip(' ')
        action = self.action_parser(action, available_actions)
        return action
    
class ThinkAgent:
    def __init__(self, llm, context_len=2000):
        self.type = "Think_Webrun_Agent"
        self.name = f"{self.type}_{self.life_label}"
        self.llm = llm 
        self.context_len = context_len
        self.task = None
    
    def action_parser(self, text):
        nor_text = text.strip().lower()
        if nor_text.startswith('think'):
            query = get_query(nor_text)
            return f"think[{query}]"
        return text
        
    def prompt_layer(self, agent, available_actions):
        one_shot = pre_prompt.click
        prompt = f"{one_shot}{self.observations[self.cur_session][0]}\n\nAction:"
        actions_prompt = f"current available action is {self.avai_action_prompt(available_actions)}"
        prompt = f"\n\nAction:"
        return prompt
    
    
    def llm_layer(self, prompt):
        return self.llm(prompt)
    
    def forward(self, control_prompt, available_actions):
        prompt = self.prompt_layer(control_prompt, available_actions)
        action = self.llm_layer(prompt).lstrip(' ')
        action = self.action_parser(action, available_actions)
        return action
    
class ControlAgent:
    def __init__(self, agents):
        self.type = "Search_Click_Control_Webrun_Agent"
        self.agents = agents
        self.task = {}
        self.actions = {}
        self.observations = {}
        self.agent_calls = {} # saving the agents types in sessions
        self.item_recall = {}
        self.cur_session = 0
        self.agents = agents
        self.control_dict = control_dict
        
    def new_session(self, idx, task):
        self.cur_session = idx
        self.task[idx] = task
        self.actions[idx] = ['reset']
        self.observations[idx] = []
        self.item_recall[idx] = []
        self.agent_calls[idx] = ["Search_Click_Controller"]
        self.task_assign(task)
    
    def task_assign(self, task):
        for agent in self.agents:
            agent.task = task

    def action_parser(self, text, available_actions):
        nor_text = text.strip().lower()
        if nor_text.startswith('search'):
            query = get_query(nor_text)
            return f"search[{query}]"
        if nor_text.startswith('click'):
            if 'click' in available_actions:
                for a in available_actions['click']:
                    if a.lower() in nor_text:
                        return f"click[{a}]"
        return text
    
    def get_agents_types(self):
        return [a.type for a in self.agents]
        
    def prompt_layer(self, agent, available_actions):
        if agent.type == "Search_Webrun_Agent":
            return self.ask_search_agent()
        if agent.type == "Click_Webrun_Agent":
            return self.ask_click_agent()
        return 0
    
    def ask_search_agent(self):
        initial = self.task[self.cur_session]
        prompt = f"Instruction:\n{initial}\n"
        search_label = False
        for idx, agent_type in enumerate(self.agent_calls[self.cur_session]):
            if agent_type == "Search_Webrun_Agent":
                search_label = True
                action = self.actions[self.cur_session][idx]
                prompt += f"You have already {action}.\n"
        if search_label:
            prompt += "Can you change your search query?"
        return prompt
    
    def ask_click_agent(self):
        prompt = ""
        for idx in range(1, len(self.actions[self.cur_session])):
            agent_type = self.agent_calls[self.cur_session][idx]
            action = self.actions[self.cur_session][idx]
            observation = self.observations[self.cur_session][idx]
            if agent_type == "Click_Webrun_Agent":
                prompt += f"\n\nAction:{action}\nObservation:{observation}"
            else:
                prompt += f"\n\n{agent_type}:{action}\nObservation:{observation}"
        return prompt
    
    def call_agent(self, observation, available_actions):
        for agent in self.agents:
            if self.control_dict[agent.type] in available_actions:
                return agent
    
    def llm_layer(self, prompt):
        return self.llm(prompt)
    
    def forward(self, observation, available_actions=None):
        self.observations[self.cur_session].append(observation)
        agent = self.call_agent(observation, available_actions)
        prompt = self.prompt_layer(agent, available_actions)
        action = agent.forward(prompt, available_actions).lstrip()
        action = self.action_parser(action, available_actions)
        self.actions[self.cur_session].append(action)
        self.agent_calls[self.cur_session].append(agent.type)
        return action