import os
import sys
import json
import random
import argparse
from concurrent.futures import ThreadPoolExecutor
import time

from web_run.web_env import webshopEnv
from web_run.llms import get_llm_backend, OPENAI_CHAT_MODELS, OPENAI_LLM_MODELS
from web_run.multi_agent_arch import SearchAgent, ClickAgent, ControlAgent
import web_run.agent_arch as agent_arch
from web_run.utils import session_save, get_instruction, get_env_botton
from web_run.evaluate import get_file_sess_idx
from web_run.config import available_agent_names

parser = argparse.ArgumentParser(description='Parsing the input of agents, llms and llm context length.')
parser.add_argument("--agent_name", type=str, help="Name of the agent.", default="React")
parser.add_argument("--llm_name", type=str, help="Name of the llm", default="gpt-3.5-turbo")
parser.add_argument("--max_context_len", type=int, help="Maximum context length", default=1700)
args = parser.parse_args()
agent_name = args.agent_name
llm_name = args.llm_name
max_context_len = args.max_context_len

assert agent_name in available_agent_names, f"Invalid agent name. Allowed values are {available_agent_names}"

def run_one_session(idx, max_steps=50):
    env = webshopEnv()
    llm_backend = get_llm_backend(llm_name)
    llm = llm_backend.run
    if agent_name in ["React_Webrun_Agent"]:
        agent = agent_arch.ReactAgent(llm, max_context_len)
    elif agent_name in ["Zeroshot_Webrun_Agent"]:
        agent = agent_arch.ZeroshotAgent(llm, max_context_len)
    elif agent_name in ["ZeroshotThink_Webrun_Agent"]:
        agent = agent_arch.ZeroshotThinkAgent(llm, max_context_len)
    elif agent_name in ["Planner_Webrun_Agent"]:
        agent = agent_arch.PlannerAgent(llm, max_context_len)
    elif agent_name in ["PlannerReact_Webrun_Agent"]:
        agent = agent_arch.PlannerReactAgent(llm, max_context_len)
    elif agent_name in ["Search_Click_Controller_Webrun_Agent","Search_Click_Control_Webrun_Agent"]:
        search_agent = SearchAgent(llm, max_context_len)
        click_agent = ClickAgent(llm, max_context_len)
        agent = ControlAgent([search_agent, click_agent])

    saving_path = f"./execution_data/{agent.type}_{llm_name}_batch.json"
    actions = []
    observations = []
    retrieved_items = []
    hulluci = 0
    # reset the environments
    action = 'reset'
    idx = f"fixed_{idx}"
    done = False
    observation, reward, done, asins, buttons = env.step(idx, action)
    env_bottons = get_env_botton(buttons)
    actions.append(action)
    observations.append(observation)
    retrieved_items.append(asins)
    inst = get_instruction(observation)
    agent.new_session(idx, inst)
    
    # start planning
    if agent_name in ["PlannerReact_Webrun_Agent", "Planner_Webrun_Agent"]:
        action = 'planning'
        agent.planning()
        agent.stop = ["\n"]
        observation = agent.plan
    
    # start interaction
    for step in range(max_steps):
        actions.append(action)
        observations.append(observation)
        retrieved_items.append(asins)
        if not done:
            action = agent.forward(observation, env_bottons).lstrip(' ') 
            # print(observation)
            print(action)
            if "No response" in action: # running too many sessions, end this session
                done = True
                # session_save(idx, actions, observations, retrieved_items, saving_path)
                return 0.0
            try:
                observation, reward, done, asins, buttons = env.step(idx, action)
                if "Buy Now" in action:
                    print(observation, reward, done, asins, buttons)
                env_bottons = get_env_botton(buttons)
            except AssertionError:
                observation = 'Invalid action!'
                hulluci += 1
            if hulluci > 3:
                reward = 0.0
                done = True
            if "handle_exception" in observation: # running too many sessions, end this session
                done = True
                session_save(idx, actions, observations, retrieved_items, saving_path)
                return 0.0
        else:
            time.sleep(1)
            session_save(idx, actions, observations, retrieved_items, saving_path)
            print("saved!")
            return reward
    session_save(idx, actions, observations, retrieved_items, saving_path)
    return 0.0

def run_episodes(session_list):
    work_num = 4
    if len(session_list) > work_num and not llm_name in (OPENAI_CHAT_MODELS + OPENAI_LLM_MODELS):
        with ThreadPoolExecutor(max_workers=work_num) as executor:
            # executor.map will return a list of tuples in the same order as idxs[:10]
            results = list(executor.map(run_one_session, session_list))
            # print(sum(results)/len(results))
            print("Done the session running!")
    else:
        for sid in session_list:
            run_one_session(sid)

file_name = f"./execution_data/webrun/{agent_name}_{llm_name}_batch.json"
if os.path.exists(file_name):
    executed_sess = get_file_sess_idx(file_name)
    session_list = [j for j in range(900) if j not in executed_sess]
    run_episodes(session_list)
else:
    run_episodes(list(range(0, 900)))


