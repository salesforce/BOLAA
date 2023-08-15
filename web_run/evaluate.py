import json
import os
import re 
from collections import defaultdict
from web_run.config import available_agent_names

def get_complexity(ins_attr_file="../webshop/data/items_human_ins_new.json"):
    with open(ins_attr_file) as f:
        human_attr = json.load(f)
    complexity_dict = {}
    for asin in human_attr:
        for ins in human_attr[asin]:
            instruction = ins["instruction"]
            attribute_complexity = len(ins["instruction_attributes"])
            option_complexity = len(ins["instruction_options"])
            key = instruction.strip('.')    
            complexity_dict[key] = [attribute_complexity, option_complexity]
    return complexity_dict

def get_reward(session):
    last_session = session[-1]
    observation = last_session['observation']
    if observation.startswith('Your score'):
        tokens = observation.split(':')
        for idx, token in enumerate(tokens):
            if "Your score (min 0.0, max 1.0)" in token:
                cur_idx = idx+1
                reward = tokens[cur_idx].strip()
                return float(reward)
    return 0.0

def get_sess_ins(session):
    instruction = session[0]['instruction_text']
    return instruction

def get_sess_step(session):
    step_id = session[-1]["step_id"]
    numbers = re.findall(r'\d+', step_id)
    sess_idx, step_len = numbers
    return int(step_len)

def filter_results(file_name):
    sessions = get_file_sess(file_name)
    original = len(sessions)
    new_sessions = []
    with open(file_name + '.back', 'a') as f:
        for _, sess in enumerate(sessions):
            json.dump(sess, f)
            f.write('\n')
            saving_label = True
            for step in sess: 
                if "action" in step: # checking whether it is a action step
                    if "No response" in step["action"]: # checking whether it is No response due to LLM 
                        saving_label = False
                if "observation" in step:
                    if "Your score (min 0.0, max 1.0):" in step["observation"]:
                        saving_label = True
            if saving_label:
                new_sessions.append(sess)        
    after_filtering = len(new_sessions)
    if original - after_filtering > 0:
        print(f"{original - after_filtering} session contain No response")
    with open(file_name, 'w') as f:
        for sess in new_sessions:
            json.dump(sess, f)
            f.write('\n')

def delete_repeat(file_name):
    sessions = get_file_sess(file_name)
    idx_score = {}
    idx_ref = {}
    with open(file_name + '.repeat', 'a') as f: # only saving highest score
        for sess in sessions:
            json.dump(sess, f)
            f.write('\n')
            sess_idx = get_sess_idx(sess)
            reward = get_reward(sess)
            if sess_idx in idx_score:
                if reward < idx_score[sess_idx]:
                    continue
            idx_score[sess_idx] = reward
            idx_ref[sess_idx] = sess
    with open(file_name, 'w') as f:
        sort_idx = sorted(idx_ref.keys())
        for sess_idx in sort_idx:
            sess = idx_ref[sess_idx]
            json.dump(sess, f)
            f.write('\n')
              
def get_file_sess(file_name):
    sessions = []
    with open(file_name) as f:
        for line in f:
            session = json.loads(line)
            sessions.append(session)
    return sessions

def get_sess_idx(session):
    step_id = session[-1]["step_id"]
    numbers = re.findall(r'\d+', step_id)
    sess_idx, step_len = numbers
    return int(sess_idx)

def get_file_sess_idx(file_name):
    session_idx = []
    with open(file_name) as f:
        for line in f:
            session = json.loads(line)
            session_idx.append(get_sess_idx(session))
    return set(session_idx)

def get_goal_item(session):
    goal = session[0]
    asin = goal['asin']
    return asin 

def get_session_items(session):
    items = []
    for step in session:
        if "retrieved_items" in step:
            items += step["retrieved_items"]
    return items

def merge_sessions_by_llm(model_name, path = "./execution_data/"):
    file_list = []
    sessions = []
    for root, _, files in os.walk(path):
        for file_name in files:
            if model_name in file_name:
                file_list.append(os.path.join(root, file_name))
    for f_name in file_list:
        with open(f_name) as f:
            for line in f:
                session = json.loads(line)
                sessions.append(session)
    return sessions

def get_recall(sess):
    goal_item = get_goal_item(sess)
    retri_items = get_session_items(sess)
    if goal_item in retri_items:
        return 1
    else:
        return 0
    
def get_precision(sess):
    goal_item = get_goal_item(sess)
    retri_items = get_session_items(sess)
    if goal_item in retri_items:
        return 1/len(retri_items)
    else:
        return 0

def get_fail(sess):
    if "observation" in sess[-1]:
        if "Your score (min 0.0, max 1.0):" in sess[-1]["observation"]:
            return 0
    return 1

def get_halluci(sess):
    halluci_step_idx = []
    for step in sess:
        if "step_id" in step:
            step_id = step["step_id"]
            numbers = re.findall(r'\d+', step_id)
            sess_idx, step_idx = numbers
            if "observation" in step:
                if "Invalid action!" in step["observation"]:
                    halluci_step_idx.append(step_idx)
    return halluci_step_idx
    
def eval_complexity(sessions, complexity_dict):
    complexity = []
    for sess in sessions:
        instruction = get_sess_ins(sess)
        if instruction.find(", and price lower") > 0:
            ins_key = instruction[:instruction.find(", and price lower")]
        else:
            ins_key = instruction
        if ins_key in complexity_dict:
            attr_complexity, option_complexity = complexity_dict[ins_key]
        else:
            print("no complexity for ", ins_key)
        complexity.append(attr_complexity + option_complexity)
    return complexity

def eval_success(sessions) -> list:
    success = []
    for sess in sessions:
        r = get_reward(sess)
        if r >= 1:
            success.append(1)
        else:
            success.append(0)
    return success                

def eval_initial_halluci(sessions) -> list:
    initial_halluci = []
    for sess in sessions:
        initial_halluci.append(get_halluci(sess)[0])
    return initial_halluci

def eval_avg_halluci(sessions) -> list:
    avg_halluci = []
    for sess in sessions:
        halluci = get_halluci(sess)
        avg_halluci.append(sum(halluci)/len(halluci))
    return avg_halluci

def eval_fail(sessions) -> list:
    fail_list = [get_fail(sess) for sess in sessions]
    return fail_list

def eval_reward(sessions) -> list:
    reward = []
    for sess in sessions:
        reward.append(get_reward(sess))
    return reward

def eval_recall(sessions) -> list:
    recall = [get_recall(sess) for sess in sessions]
    return recall

def eval_precision(sessions) -> list:
    prec = [get_precision(sess) for sess in sessions]
    return prec

def y_wrt_x_rel(x, y):
    x_dict = defaultdict(list)
    for idx, c in enumerate(x):
        x_dict[c].append(y[idx])
    x_dict_y = {key:round(sum(val)/len(val), 4) for key, val in x_dict.items()}
    return x_dict_y

def get_all_eval_values(llm_name):
    agent_types = available_agent_names
    for a_type in agent_types:
        get_eval_values(llm_name, a_type)
        
def get_eval_values(llm_name, agent_type, path="./execution_data/"):
    file_name = f"{agent_type}_{llm_name}_batch.json"
    file_name = os.path.join(path, file_name)
    delete_repeat(file_name)
    session_idx = get_file_sess_idx(file_name)
    assert len(session_idx) == 900
    sessions = get_file_sess(file_name)
    # print(len(sessions))
    recalls = eval_recall(sessions)
    rewards = eval_reward(sessions)
    precisions = eval_precision(sessions)
    success = eval_success(sessions)
    fail = eval_fail(sessions)
    avg_reward = round(sum(rewards)/len(rewards), 4)
    success_rate = round(sum(success)/len(success), 4)
    fail_rate = round(sum(fail)/len(success), 4)
    avg_recall = round(sum(recalls)/len(recalls), 4)
    avg_prec = round(sum(precisions)/len(precisions), 4)
    print(f"{avg_reward}\t{success_rate}\t{fail_rate}\t{avg_recall}\t{avg_prec}")