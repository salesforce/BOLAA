import json 
import re

def obser_parser(observation, instruction_text):
    obs = observation.encode().decode("unicode-escape").encode("latin1").decode("utf-8")
    # obs = obs.replace("[SEP]",'|')
    obs = obs.replace("[button]","[")
    obs = obs.replace("[button_]","]")
    if obs.startswith('Instruction:'):
        obs = obs.replace(instruction_text,"")
        obs = obs.replace('Instruction:',"")
    if obs.startswith('You have clicked'):
        obs = obs.split('\n')[0]
    obs = obs.lstrip()
    return obs

def instruction_parser(ins):
    ins = ins.encode().decode("unicode-escape").encode("latin1").decode("utf-8")
    ins = ins[13:].lstrip()
    return ins

def get_instruction(obs):
    obs = obs.split('\n')
    for idx, ob in enumerate(obs):
        if "Instruction:" in ob:
            return obs[idx+1].strip()

def get_buttons(obs):
  pattern = r"\[(.*?)\]"
  matches = re.findall(pattern, obs)
  return matches

def get_query(search):
  pattern = r"\[(.*?)\]"
  matches = re.findall(pattern, search)
  if matches:
    return matches[0]
  else:
    return search.replace('search', '')

def get_actions(obs):
  if "[Search]" in obs:
    avai_actions = {'search':[]}
  else:
    avai_actions = {'click':get_buttons(obs)}
  return avai_actions

def get_env_botton(bottons):
  if "Search" in bottons:
    avai_actions = {'search':[]}
  else:
    avai_actions = {'click':bottons}
  return avai_actions

def session_save(session_idx, actions, observations, retrieved_items, file_path):
  save_dict_list = []
  for idx in range(len(actions)):
    save_dict =  {"step_id": f"session_{session_idx}_step_{idx}", "action": actions[idx], "observation":observations[idx], "retrieved_items": retrieved_items[idx]}
    save_dict_list.append(save_dict)
  # get goal
  goal_file_name = f"./webshop/user_session_logs/mturk/{session_idx}.jsonl"
  with open(goal_file_name) as f:
    for line in f:
      page = json.loads(line)
      break
    goal = page["goal"]
  # saving
  save_dict_list = [goal] + save_dict_list
  with open(file_path, 'a') as f:
    json.dump(save_dict_list, f)
    f.write('\n')