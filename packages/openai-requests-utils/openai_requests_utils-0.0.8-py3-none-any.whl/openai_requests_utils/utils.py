import json
import requests
import os
import time
from datetime import datetime
import tiktoken
import re

def read_json(filename):
    nb_retry = 0
    exception = None

    # Retry a few times if json is empty, happens sometimes if accessing it while it's being written
    while nb_retry < 5:
        try:
            with open(filename, 'r', encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from '{filename}'. File might be empty or corrupted. Exception: {e}")
            exception = e
        
        time.sleep(0.1)
        nb_retry += 1

    raise exception

# Return None when an error occured
def validate_if_oai_chunk_error(chunk):
    if chunk is not None:
        error = chunk.get("error")

        if error is not None:
            print(f"Error received from OAI: {error}")
            return error
        
    return None

def oai_call_stream(model, messages, max_response_length, timeout, temperature, top_p, frequency_penalty, presence_penalty, json_mode = False):
    start_time = time.time()

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(os.getenv("OPENAI_API_KEY")),
    }

    params = {
        "model": model,
        "messages": messages,
        "max_tokens": max_response_length, #Max nb of tokens in th response
        "stream": True 
    }

    if json_mode:
        params["response_format"] = {"type": "json_object"}

    # Only add the parameters if they are not None
    if temperature is not None:
        params["temperature"] = temperature
    if top_p is not None:
        params["top_p"] = top_p
    if frequency_penalty is not None:
        params["frequency_penalty"] = frequency_penalty
    if presence_penalty is not None:
        params["presence_penalty"] = presence_penalty

    formatted_params = json.dumps(params, ensure_ascii=False)
    encoded_params = formatted_params.encode('utf-8')

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, data=encoded_params, timeout=timeout, stream=True)

    if response.status_code != 200:
        raise Exception(f"Error in OAI call: {response.status_code} - {response.text}")

    # Dictionary to hold the log data
    oai_call_log = {
        "id": "",
        "object": "",
        "created": "",
        "model": model,
        "temperature": temperature,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty,
        "max_tokens": max_response_length,
        "timeout": timeout,
        "longest_time_between_chunks_id": 0,
        "longest_time_between_chunks": 0,
        "total_time_taken": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "response_message": "",
        "messages": messages,
        "chunks": []
    }

    role = None

    # Variable to keep track of the longest time between chunks
    longest_time_between_chunks = 0.0
    longest_time_between_chunks_id = 0
    last_chunk_time = time.time()

    chunk = None
    x = 0

    # create variables to collect the stream of chunks
    collected_chunks = []
    collected_messages = []

    # create a byte buffer to collect incoming data
    byte_buffer = b""

    is_first_byte = True
    is_first_chunk = True

    # iterate through the incoming bytes
    for byte_data in response.iter_content():
        if is_first_byte:
            is_first_byte = False
            #print(f"First byte received at time: {time.time() - start_time}")

        byte_buffer += byte_data

        # Check for the end of a completed chunk
        while b'}\n\n' in byte_buffer:
            chunk_time = (time.time() - last_chunk_time)
            total_time = time.time() - start_time  # calculate the time delay of the chunk
            last_chunk_time = time.time()

            if chunk_time > longest_time_between_chunks:
                longest_time_between_chunks = chunk_time
                longest_time_between_chunks_id = x

            # Extract the next full completed chunk from the byte buffer
            chunk_end_idx = byte_buffer.index(b'}\n\n') + 3  # +3 to include "}\n\n"
            completed_chunk = byte_buffer[:chunk_end_idx].decode('utf-8')

            # Remove "data: " prefix and decode the JSON
            json_str = completed_chunk.replace("data: ", "", 1)
            chunk = json.loads(json_str)
            byte_buffer = byte_buffer[chunk_end_idx:]

            # Validate if chunk error
            chunk_error = validate_if_oai_chunk_error(chunk)
            if chunk_error:
                raise Exception(f"Error received from OAI: {chunk_error}")

            # Extract the message
            collected_chunks.append(chunk)  # save the event response
            chunk_message = chunk['choices'][0]['delta']  # extract the message
            collected_messages.append(chunk_message.get("content", ""))  # save the message
            #print(f"Message received {total_time:.2f} sec after request, {chunk_time:.4f} sec after last chunk: {chunk_message}")  # 

            if is_first_chunk:
                role = chunk_message.get("role", None)
                is_first_chunk = False
                # print(f"First chunk received at time: {time.time() - start_time}")

            # Add the chunk data to the log
            oai_call_log["chunks"].append({
                "chunk_nb": x,
                "chunk_time": round(chunk_time, 4),
                "content": chunk_message.get("content", "")
            })
            x += 1

            # Check for the [DONE] marker
            if b"data: [DONE]\n\n" in byte_buffer:
                byte_buffer = b""
                break

    if chunk is None:
        raise Exception("No chunk received from OAI")
    
    if role is None:
        raise Exception("No role received from OAI")

    response_msg = "".join(collected_messages)
    response_msg_oai = format_msg_oai(role, response_msg)

    # Create the log file
    oai_call_log["id"] = chunk.get("id", "")
    oai_call_log["object"] = chunk.get("object", "")
    oai_call_log["created"] = chunk.get("created", "")
    oai_call_log["model"] = chunk.get("model", "")

    oai_call_log["longest_time_between_chunks_id"] = longest_time_between_chunks_id
    oai_call_log["longest_time_between_chunks"] = round(longest_time_between_chunks, 4)
    
    oai_call_log["total_time_taken"] = round(total_time, 4)
    oai_call_log["response_message"] = response_msg

    oai_call_log["prompt_tokens"] = count_tokens(messages)
    oai_call_log["completion_tokens"] = count_tokens([response_msg_oai]) 
    oai_call_log["total_tokens"] = oai_call_log["prompt_tokens"] + oai_call_log["completion_tokens"]

    #print(f"Response received from OAI in {time.time() - start_time}s, model used: {model}")

    return oai_call_log, response_msg_oai

# Send msg to openai
def send_open_ai_gpt_message(messages_arg, no_gen = None, json_mode = False):
    # create config file if it doesn't exist already
    if not os.path.exists('oai_config.json'):
        with open('oai_config.json', 'w', encoding="utf-8") as f:
            f.write('{"model": "gpt-3.5-turbo"}')

    # Decide gpt models + settings
    config = read_json('oai_config.json')
    model = config["model"]

     # Optional params
    max_response_length = config.get("max_response_length", 400)
    timeout = config.get("timeout", 10)
    temperature = config.get("temperature")
    top_p = config.get("top_p")
    presence_penalty = config.get("presence_penalty")
    frequency_penalty = config.get("frequency_penalty")
    
    # # Remove all messages with unsupported roles
    messages = [msg for msg in messages_arg if msg["role"] in ["system", "user", "assistant"] or print(f"Warning: Removed message with invalid role")]

    # Json mode require to have json present somewhere in the prompt, definitely a bug
    if json_mode and len(messages) > 0 and "json" not in messages[-1]["content"].lower():
        raise Exception("ERROR : Json mode require to have json present somewhere in the prompt. Prompt: " + messages[-1]["content"])

    response_message = None
    max_immeditate_retry = 4 # +1 for initial try
    wait_time_until_no_response_retry = 60 # Wait 60 secs before retrying if no response received
    start_time_call_oai = time.time()

    # Loop until we get a response
    while (response_message is None):
        nb_retry = 0

        while(response_message is None and nb_retry <= max_immeditate_retry):
            try:
                oai_call_log, response_message = oai_call_stream(model, messages, max_response_length, timeout, temperature, top_p, frequency_penalty, presence_penalty, json_mode)
                
            except requests.exceptions.Timeout as e:
                print(f"Took longer than {timeout} sec, retrying... Exception: {e}")
                timeout += 3
                nb_retry += 1
            except Exception as e:
                print(f"Connexion crashed: {e}")
                timeout += 2
                nb_retry += 1
            
        # Never return None, just wait until eventually get a response
        if (response_message is None):
            print(f"Max immediate retry reached, trying again in {wait_time_until_no_response_retry} secs.")
            time.sleep(wait_time_until_no_response_retry)

    # print(f"Response received from OAI in {time.time() - start_time_call_oai}s, model used: {model}")

    # Debug calls
    suffix = f"_{no_gen}" if no_gen is not None else ""

    # Create current_convo_debug directory if it doesn't exist already
    if not os.path.exists('current_convo_debug'):
        os.makedirs('current_convo_debug')

    filename = f'{datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]}{suffix}' # Filename including the nb of ms (otherwise filename might be overwritten)
    with open(f'current_convo_debug/{filename}.json', 'w', encoding="utf-8") as f:
        formatted_data = json.dumps(oai_call_log, ensure_ascii=False, indent=4)
        f.write(formatted_data)

    return response_message

def format_msg_oai(msg_type, content):
    return {"role": msg_type, "content": content}

encoding_gpt = None

def count_tokens(messages):
    global encoding_gpt
    if encoding_gpt is None:
        encoding_gpt = tiktoken.encoding_for_model("gpt-4") # Same encoding for gpt-3.5 and gpt4, doesn't matter which i use

    num_tokens = 0
    for message in messages:
        for key, value in message.items():
            num_tokens+=len(encoding_gpt.encode(value))
        # every message follows <|start|>{role/name}\n{content}<|end|>\n
        num_tokens += 4 

    # every reply is primed with <|start|>assistant<|message|>
    num_tokens += 3
    #print(f"{num_tokens} tokens")
    return num_tokens

# Return last json object contained in the response_content
def extract_json_from_response(func_name, response_content):
    try:
        # Use regular expression to find potential JSON objects
            # The regex also captures JSON content that might not have a closing brace.
        matches = re.findall(r'\{.*\}|\{.*$', response_content, re.MULTILINE | re.DOTALL) # Just need to detect everything in {} as a json object, json_mode should only output valid json (I think)
        
        if matches:
            modified_response = matches[-1]

            # Calculate number of missing closing braces and append them
            missing_closing_braces = modified_response.count('{') - modified_response.count('}')
            if missing_closing_braces > 0:
                modified_response += '}' * missing_closing_braces

            # Replace "true/false" with "false", in case the JSON object contains "true/false" as a string (error when created it)
            modified_response = re.sub(r'(?i)["\']?true/false["\']?', 'false', modified_response) 

            # Convert all instances of "True" and "False" (case insensitive) to True and False
            modified_response = re.sub(r'(?i)["\']?true["\']?', 'true', re.sub(r'(?i)["\']?false["\']?', 'false', modified_response))
            
            # Replace N/A with "N/A" if it appears after a colon and optional whitespaces, case-insensitive
            modified_response = re.sub(r'(?i)(:\s*)N/A', r'\1"N/A"', modified_response)

            # Remove trailing commas right before ] or }
            modified_response = re.sub(r',\s*([}\]])', r'\1', modified_response)

            return json.loads(modified_response)
        else:
            print(f'Error in {func_name}: No potential JSON object found in the text. {response_content}')
            return None
    except json.JSONDecodeError as e:
        print(f'Error in {func_name}: The text does not contain a valid JSON object. {response_content}. Error : {str(e)}')
        return None