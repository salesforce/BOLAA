import random
import re
import json 
import time
import os
import tiktoken
import web_run.pre_prompt as pre_prompt
from web_run.utils import get_query
from web_run.llms import token_enc


class BaseAgent(object):
    def __init__(self, llm, context_len=2000):
        self.type = "Base_Webrun_Agent"
        self.life_label = time.time()
        self.name = f"{self.type}_{self.life_label}"
        self.task = {}
        self.actions = {}
        self.observations = {}
        self.item_recall = {}
        self.llm = llm
        self.context_len = context_len
        self.cur_session = 0
        
    def new_session(self, idx, task):
        self.cur_session = idx
        self.task[idx] = task
        self.actions[idx] = ['reset']
        self.observations[idx] = []
        self.item_recall[idx] = []
        
    def llm_layer(self, prompt):
        return self.llm(prompt)
    
    def get_history(self, session=None):
        if not session:
            session = self.cur_session
        history = ""
        for idx in range(1, len(self.actions[session])):
            history += f"Action: {self.actions[session][idx]}\n"
            history += f"Observation: {self.observations[session][idx]}\n\n"
        return history
    
    def save(self, path):
        file_name = os.path.join(path, self.name+'_'+str(self.life_label))
        with open(file_name, 'a') as f:
            f.write(f"session_idx:{self.cur_session}\n")
            history = self.get_history(self.cur_session)
            f.write(history)
            f.write('\n')
    
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
    
    def prompt_layer(self):
        raise NotImplementedError
    
    def forward(self, observation, available_actions=None):
        raise NotImplementedError


class ReactAgent(BaseAgent):
    def __init__(self, llm, context_len=2000):
        super().__init__(llm, context_len)
        self.type = "React_Webrun_Agent"
        self.name = f"{self.type}_{self.life_label}"
        
    def prompt_layer(self):
        one_shot = pre_prompt.oneshot
        prompt = f"{one_shot}{self.observations[self.cur_session][0]}\n\nAction:"
        if len(self.actions[self.cur_session]) > 1:
            initial_prompt = f"{one_shot}{self.observations[self.cur_session][0]}\n\n"
            history = self.get_history()
            remain_context_space = (self.context_len - len(token_enc.encode(initial_prompt)))*3
            history = history[-int(remain_context_space):]
            prompt = f"{initial_prompt}{history}\n\nAction:"
        return prompt
  
    def forward(self, observation, available_actions=None):
        self.observations[self.cur_session].append(observation)
        prompt = self.prompt_layer()
        action = self.llm_layer(prompt)
        self.actions[self.cur_session].append(action)
        return action
            
class ZeroshotAgent(BaseAgent):
    def __init__(self, llm, context_len=2000, temperature=0.9, stop=['\n']):
        super().__init__(llm, context_len)
        self.type = "Zeroshot_Webrun_Agent"
        self.life_label = time.time()
        self.name = f"{self.type}_{self.life_label}"
        self.temperature = temperature
        self.stop = stop
   
    def llm_layer(self, prompt):
        return self.llm(prompt, temperature=self.temperature, stop=self.stop)
   
    def avai_action_prompt(self, available_actions):
        if 'search' in available_actions:
            return "{search}"
        elif 'click' in available_actions:
            actions = available_actions['click']
            ac_string = "\t".join(actions)
            return f"click: [{ac_string}]"
    
    def prompt_layer(self, available_actions):
        zeroshot = pre_prompt.zeroshot
        actions_prompt = f"current available action is {self.avai_action_prompt(available_actions)[-3000:]}"
        prompt = f"{zeroshot}{self.observations[self.cur_session][0]}{actions_prompt}\n\nAction:"
        if len(self.actions[self.cur_session]) > 1:
            initial_prompt = f"{zeroshot}{self.observations[self.cur_session][0]}\n\n"
            history = self.get_history()
            remain_context_space = (self.context_len - len(token_enc.encode(f"{initial_prompt}{actions_prompt}")))*3
            history = history[-int(remain_context_space):]
            prompt = f"{initial_prompt}{history}{actions_prompt}\n\nAction:"
        return prompt

    def forward(self, observation, available_actions=None):
        self.observations[self.cur_session].append(observation)
        prompt = self.prompt_layer(available_actions)
        action = self.llm_layer(prompt).lstrip()
        action = self.action_parser(action, available_actions)
        self.actions[self.cur_session].append(action)
        return action
            
class ZeroshotThinkAgent(BaseAgent):
    def __init__(self, llm, context_len=2000, temperature=0.9, stop=['\n']):
        super().__init__(llm, context_len)
        self.type = "ZeroshotThink_Webrun_Agent"
        self.life_label = time.time()
        self.name = f"{self.type}_{self.life_label}"
        self.temperature = temperature
        self.stop = stop
  
    def llm_layer(self, prompt, temperature=0.8, stop=['\n']):
        return self.llm(prompt, temperature=self.temperature, stop=self.stop)
    
    def avai_action_prompt(self, available_actions):
        if 'search' in available_actions:
            return "{search}"
        elif 'click' in available_actions:
            actions = available_actions['click']
            ac_string = "\t".join(actions)
            return f"click: [{ac_string}]"
        
    def prompt_layer(self, available_actions):
        zeroshot = pre_prompt.zeroshot_think
        actions_prompt = f"current available action is {self.avai_action_prompt(available_actions)[-3000:]}"
        prompt = f"{zeroshot}{self.observations[self.cur_session][0]}{actions_prompt}\n\nAction:"
        if len(self.actions[self.cur_session]) > 1:
            initial_prompt = f"{zeroshot}{self.observations[self.cur_session][0]}\n\n"
            history = self.get_history()
            remain_context_space = (self.context_len - len(token_enc.encode(initial_prompt+actions_prompt)))*3
            history = history[-int(remain_context_space):]
            prompt = f"{initial_prompt}{history}{actions_prompt}\n\nAction:"
        return prompt

    def forward(self, observation, available_actions=None):
        self.observations[self.cur_session].append(observation)
        prompt = self.prompt_layer(available_actions)
        action = self.llm_layer(prompt, temperature=self.temperature, stop=self.stop).lstrip()
        action = self.action_parser(action, available_actions)
        self.actions[self.cur_session].append(action)
        return action
            
class PlannerAgent(BaseAgent):
    def __init__(self, llm, context_len=2000, temperature=0.9, stop=['\n']):
        super().__init__(llm, context_len)
        self.type = "Planner_Webrun_Agent"
        self.name = f"{self.type}_{self.life_label}"
        self.temperature = temperature
        self.stop = stop
        self.max_plan_token_len = 256
        self.plan = None
        
    def planning(self):
        plan_prompt = f"{pre_prompt.plan}\n\nInstruction: {self.task[self.cur_session]}\nPlan:"
        self.plan = self.llm(plan_prompt, temperature=self.temperature, stop=["\n"], 
                             max_tokens=self.max_plan_token_len)
 
    def llm_layer(self, prompt):
        return self.llm(prompt, temperature=self.temperature, stop=self.stop)

    def prompt_layer(self, available_actions):
        oneshot = pre_prompt.oneshot_plan 
        prompt = f"{oneshot}\n\nInstruction: {self.task[self.cur_session]}\nPlan: {self.plan}\n\nAction:"
        if len(self.actions[self.cur_session]) > 1:
            initial_prompt = f"{oneshot}\n\nInstruction: {self.task[self.cur_session]}\nPlan: {self.plan}\n\n"
            history = self.get_history()
            remain_context_space = (self.context_len - len(token_enc.encode(initial_prompt)))*3
            history = history[-remain_context_space:]
            prompt = f"{initial_prompt}{history}Action:"
        return prompt
 
    def forward(self, observation, available_actions=None):
        self.observations[self.cur_session].append(observation)
        prompt = self.prompt_layer(available_actions)
        action = self.llm_layer(prompt).lstrip(' ')
        action = self.action_parser(action, available_actions)
        self.actions[self.cur_session].append(action)
        return action

class PlannerReactAgent(PlannerAgent):
    def __init__(self, llm, context_len=2000, temperature=0.9, stop=['\n']):
        super().__init__(llm, context_len, temperature, stop)
        self.type = "PlannerReact_Webrun_Agent"
        self.name = f"{self.type}_{self.life_label}"
        
    def planning(self):
        plan_prompt = f"{pre_prompt.plan_react}\n\nInstruction: {self.task[self.cur_session]}\nPlan:"
        self.plan = self.llm(plan_prompt, temperature=self.temperature, stop=["\n"], 
                             max_tokens=self.max_plan_token_len)
        
    def prompt_layer(self, available_actions=None):
        oneshot = pre_prompt.oneshot_plan_react 
        prompt = f"{oneshot}\n\nInstruction: {self.task[self.cur_session]}\nPlan: {self.plan}\n\nAction:"
        if len(self.actions[self.cur_session]) > 1:
            initial_prompt = f"{oneshot}\n\nInstruction: {self.task[self.cur_session]}\nPlan: {self.plan}\n\n"
            history = self.get_history()
            remain_context_space = (self.context_len - len(token_enc.encode(initial_prompt)))*3
            history = history[-remain_context_space:]
            prompt = f"{initial_prompt}{history}Action:"
        return prompt
 
    def forward(self, observation, available_actions=None):
        self.observations[self.cur_session].append(observation)
        prompt = self.prompt_layer(available_actions)
        action = self.llm_layer(prompt).lstrip(' ')
        action = self.action_parser(action, available_actions)
        self.actions[self.cur_session].append(action)
        return action