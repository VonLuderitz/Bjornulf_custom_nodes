import ollama
from ollama import Client
import logging
import hashlib
import os

class ollamaLoader:
    # _available_models = None  # Class variable to cache models
    
    # @classmethod
    # def read_host_from_file(cls, filename='ollama_ip.txt'):
    #     try:
    #         script_dir = os.path.dirname(os.path.realpath(__file__))
    #         file_path = os.path.join(script_dir, filename)
    #         print(f"Looking for file at: {file_path}")
            
    #         with open(file_path, 'r') as f:
    #             host = f.read().strip()
    #             if host:
    #                 logging.info(f"Using host from {file_path}: {host}")
    #                 return host
    #             else:
    #                 logging.warning(f"{file_path} is empty. Falling back to default hosts.")
    #     except Exception as e:
    #         logging.error(f"Failed to read host from {file_path}: {e}")
    #     return None

    # @classmethod
    # def get_available_models(cls):
    #     # Return cached models if available
    #     if cls._available_models is not None:
    #         return cls._available_models
            
    #     models = ["none"]  # Default fallback
    #     host = cls.read_host_from_file()
        
    #     def try_connect(host_url):
    #         try:
    #             client = Client(host=host_url)
    #             list_models = client.list()
    #             return [model['name'] for model in list_models['models']]
    #         except Exception as e:
    #             logging.error(f"Error fetching models from {host_url}: {e}")
    #             return None

    #     # Try user-specified host first
    #     if host:
    #         result = try_connect(host)
    #         if result:
    #             models = result

    #     # Try default hosts if necessary
    #     if models == ["none"]:
    #         for default_host in ["http://127.0.0.1:11434", "http://0.0.0.0:11434"]:
    #             result = try_connect(default_host)
    #             if result:
    #                 models = result
    #                 break
        
    #     cls._available_models = models  # Cache the results
    #     return models

    @classmethod
    def INPUT_TYPES(cls):
        default_system_prompt = (
            "Describe a specific example of an object, animal, person, or landscape based on a given general idea. "
            "Start with a clear and concise overall description in the first sentence. Then, provide a detailed depiction "
            "of its physical features, focusing on colors, size, clothing, eyes, and other distinguishing characteristics. "
            "Use commas to separate each detail and avoid listing them. Ensure each description is vivid, precise, and "
            "specific to one unique instance of the subject. Refrain from using poetic language and giving it a name.\n"
            "Example input: man\n Example output: \nAn overweight old man sitting on a bench, wearing a blue hat, "
            "yellow pants, orange jacket and black shirt, sunglasses, very long beard, very pale skin, long white hair, "
            "very large nose."
        )
        # Lazy load models only when the node is actually used
        return {
            "required": {
                "user_prompt": ("STRING", {"multiline": True}),
                "selected_model": ("STRING", {"default": "llama3.2:1b"} ),  # Default to none, will be populated when node is used
                "ollama_url": ("STRING", {"default": "http://0.0.0.0:11434"}),
                "system_prompt": ("STRING", {
                    "multiline": True,
                    "default": default_system_prompt
                }),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "keep_1min_in_vram": ("BOOLEAN", {"default": False})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("ollama_response",)
    FUNCTION = "connect_2_ollama"
    CATEGORY = "Bjornulf"

    def __init__(self):
        self.last_content_hash = None
    #     # Update available models when the node is actually instantiated
    #     self.__class__._available_models = self.get_available_models()

    def connect_2_ollama(self, user_prompt, selected_model, system_prompt, keep_1min_in_vram,ollama_url, seed):
        content_hash = hashlib.md5((user_prompt + selected_model + system_prompt).encode()).hexdigest()

        if content_hash != self.last_content_hash:
            self.last_content_hash = content_hash
        else:
            seed = None

        keep_alive_minutes = 1 if keep_1min_in_vram else 0
        # host = self.read_host_from_file()
        host = ollama_url
        
        def try_generate(host_url):
            try:
                client = Client(host=host_url)
                response = client.generate(
                    model=selected_model,
                    system=system_prompt,
                    prompt=user_prompt,
                    keep_alive=f"{keep_alive_minutes}m"
                )
                logging.info(f"Ollama response ({host_url}): {response['response']}")
                return response['response']
            except Exception as e:
                logging.error(f"Connection to {host_url} failed: {e}")
                return None

        # Try user-specified host first
        if host:
            result = try_generate(host)
            if result:
                return (result,)

        # Try default hosts
        # for default_host in ["http://127.0.0.1:11434", "http://0.0.0.0:11434"]:
        #     result = try_generate(default_host)
        #     if result:
        #         return (result,)

        logging.error("All connection attempts failed.")
        return ("Connection to Ollama failed.",)