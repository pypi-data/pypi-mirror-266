import json
import requests
from typing import List
from typing import Dict, Any
from base64 import b64encode 

from flexstack.models.image import ImageGeneration
from flexstack.models.audio import AudioGeneration
from flexstack.models.llm import TextGeneration
from flexstack.models.info import FlexstackInfo


class FlexStackAPI:
    """A Python wrapper for interacting with the FlexStack API.

    Attributes:
        base_url (str): The base URL for the FlexStack API.
        headers (dict): The headers to include credential. Will be updated after login.
    """
    
    def __init__(self, api_endpoint: str = "https://api.flexstack.ai/v1") -> None:
        """Initialize the FlexStackAPI with an API key.
        
        Args:
            api_key: A valid API key as a string.
        """
        self.base_url = api_endpoint
        self.image_tool = ImageGeneration(self.base_url)
        self.audio_tool = AudioGeneration(self.base_url)
        self.text_tool = TextGeneration(self.base_url)
        self.info = FlexstackInfo(self.base_url)

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Obtain Token via Basic Auth.
        
        Args:
            refresh_token: The refresh token as a string.
        
        Returns:
            A dictionary with the new token information.
        """
        url = f"{self.base_url}/user/login"
        # Authorization token: we need to base 64 encode it 
        # and then decode it to acsii as python 3 stores it as a byte string
        def basic_auth(username, password):
            token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
            return f'Basic {token}'

        #then connect
        headers = { 'Authorization' : basic_auth(username, password) }        
        response = requests.post(url, headers= headers)

        # obtain the token
        token = response.json()["data"]["access_token"]
        self.headers = {'Authorization' :  'Bearer ' + token}
        
        return response.json()

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh the API token using a refresh token.
        
        Args:
            refresh_token: The refresh token as a string.
        
        Returns:
            A dictionary with the new token information.
        """
        url = f"{self.base_url}/user/refresh_token"
        form = {"refresh_token": refresh_token}
        response = requests.post(url, data=form, headers=self.headers)
        return response.json()        

    def get_user_profile(self) -> Dict[str, Any]:
        """Retrieve the user's profile information.
        
        Returns:
            A dictionary containing the user's profile information.
        """
        url = f"{self.base_url}/user/me"
        response = requests.post(url, headers=self.headers)
        return response.json()

    def get_task_history(self) -> Dict[str, Any]:
        """Retrieve the user's task history.
        
        Returns:
            A dictionary containing the user's task history.
        """
        url = f"{self.base_url}/user/history"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_all_models(self):
        """Get all models"""
        return self.info.get_all_models(headers=self.headers)

    def get_models(self, task: str):
        """Get models of a task
        
        Args:
            task (str): Task name
        """
        return self.info.get_models(task=task, headers=self.headers)
    

    # IMAGE BLOCK ===============================
    def create_sdxl_task(self, prompt: str, rotation: str = "square", steps: int = 50, negative_prompt: str = "", enhance_prompt: bool = False) -> Dict[str, Any]:
        """Create an SDXL-turbo image task with a prompt and configuration.
        
        Args:
            prompt: Description of the image to be generated.
            rotation: Image rotation preference.
            steps: Number of generation steps.
            negative_prompt: Negative aspects to avoid in the image.
        
        Returns:
            A dictionary with the task creation response.
        """
        return self.image_tool.create_sdxl_task(
            prompt=prompt, 
            rotation=rotation, 
            steps=steps, 
            negative_prompt=negative_prompt, 
            enhance_prompt=enhance_prompt, 
            headers=self.headers
        )

    def create_sd_task(self, prompt: str, rotation: str = "square", steps: int = 50, negative_prompt: str = "", enhance_prompt: bool = False) -> Dict[str, Any]:
        """Create an SD1.5 image task with a prompt and configuration.
        
        Args:
            prompt: Description of the image to be generated.
            rotation: Image rotation preference.
            steps: Number of generation steps.
            negative_prompt: Negative aspects to avoid in the image.
        
        Returns:
            A dictionary with the task creation response.
        """
        return self.image_tool.create_sd_task(
            prompt=prompt, 
            rotation=rotation, 
            steps=steps, 
            negative_prompt=negative_prompt, 
            enhance_prompt=enhance_prompt, 
            headers=self.headers
        )
    
    def get_result_sd_task(self, task_id: str) -> Dict[str, Any]:
        """Retrieve the result of a previously submitted SD task.
        
        Args:
            task_id: The unique identifier of the SD task.
        
        Returns:
            A dictionary containing the result of the task.
        """
        return self.image_tool.get_result_sd_task(
            task_id=task_id, 
            headers=self.headers
        )
    
    def get_result_sdxl_task(self, task_id: str) -> Dict[str, Any]:
        """Retrieve the result of a previously submitted SDXL Turbo task.
        
        Args:
            task_id: The unique identifier of the SDXL Turbo task.
        
        Returns:
            A dictionary containing the result of the task.
        """
        return self.image_tool.get_result_sdxl_task(
            task_id=task_id, 
            headers=self.headers
        )
    
    def create_lora_trainer_task(self, prompt: str, images: List[str]) -> Dict[str, Any]:
        """Create a LORA training task with the given prompt and images.

        Args:
            prompt: The text prompt for fine-tuning.
            images: A list of URLs pointing to images for fine-tuning.

        Returns:
            A dictionary containing the task ID and other response data.
        """
        return self.image_tool.create_lora_trainer_task(
            prompt=prompt, 
            images=images, 
            headers=self.headers
        )
    
    def get_result_lora_trainer_task(self, task_id: str) -> Dict[str, Any]:
        """Retrieve the result of a previously submitted LoRA Trainer task.
        
        Args:
            task_id: The unique identifier of the LoRA task.
        
        Returns:
            A dictionary containing the result of the task.
        """
        return self.image_tool.get_result_lora_trainer_task(
            task_id=task_id, 
            headers=self.headers
        )

    def get_lora_types(self):
        """Get LORA types
        
        Returns:
            A dictionary containing the LORA types
        """
        return self.info.get_lora_types(headers=self.headers)
    
    def get_lora_cates(self):
        """Get LORA categories

        Returns:
            A dictionary containing the LORA categories
        """  
        return self.info.get_lora_cates(headers=self.headers)  

    def get_lora_models(self, type: str = None, cate: str = None):
        """Get LORA models
        
        Args:
            type (str): Type of LoRA model
            cate (str): Category of LoRA model
        
        Returns:
            A dictionary containing the LORA models
        
        """
        return self.info.get_lora_models(type=type, cate=cate, headers=self.headers)

    def create_txt2img(
        self,
        prompt: str,
        model: str = "sdxl-lightning",
        lora: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 8,
        seed: int = -1,
        negative_prompt: str = "",
        enhance_prompt: bool = False,
    ) -> Dict[str, Any]:
        """Create an text to image generation task with a prompt and configuration.

        Args:
            prompt (str): Description of the image to be generated.
            model (str): The type of model to be used. Default is "sdxl-lightning".
            lora (str): Optional parameter for LORA model.
            width (int): Width of the image. Default is 1024.
            height (int): Height of the image. Default is 1024.
            steps (int): Number of steps for image generation. Default is 8.
            seed (int): Random seed for image generation
            negative_prompt (str): Prompt for generating negative examples.
            enhance_prompt (bool): Whether to enhance the prompt or not. Default is False.

        Returns:
            A dictionary with the task creation response.
        """
        return self.image_tool.create_txt2img(
            prompt=prompt, 
            model=model, 
            lora=lora, 
            width=width, 
            height=height, 
            steps=steps, 
            seed=seed, 
            negative_prompt=negative_prompt, 
            enhance_prompt=enhance_prompt, 
            headers=self.headers
        )
    
    def result_txt2img(self, task_id: str):
        """Get result of text to image generation with task_id

        Args:
            task_id (str): The unique identifier of the text-to-image generation task.

        Returns:
            A dictionary with detail response.
        """
        return self.image_tool.result_txt2img(
            task_id=task_id, 
            headers=self.headers
        )

    def create_txt2vid(
        self,
        prompt: str,
        model: str = "damo-text-to-video",
        width: int = 256,
        height: int = 256,
        fps: int = 8,
        num_frames: int = 16,
        steps: int = 25,
        seed: int = -1,
        negative_prompt: str = "",
        enhance_prompt: bool = False,
    ) -> Dict[str, Any]:
        """Create an text to video generation task with a prompt and configuration.

        Args:
            prompt (str): Description of the video to be generated.
            model (str): The type of model to be used. Default is "modelscope-txt2vid"".
            width (int): Width of the image. Default is 512.
            height (int): Height of the image. Default is 512.
            fps (int): Number of frames per second.
            num_frames (int): Number of frames in the video.
            steps (int): Number of steps for video generation. Default is 8.
            seed (int): Random seed for video generation
            negative_prompt (str): Prompt for generating negative examples.
            enhance_prompt (bool): Whether to enhance the prompt or not. Default is False.

        Returns:
            A dictionary with the task creation response.
        """
        return self.image_tool.create_txt2vid(
            prompt=prompt, 
            model=model, 
            width=width, 
            height=height, 
            fps=fps, 
            num_frames=num_frames, 
            steps=steps, 
            seed=seed, 
            negative_prompt=negative_prompt, 
            enhance_prompt=enhance_prompt, 
            headers=self.headers
        )

    def result_txt2vid(self, task_id: str):
        """Get result of text to video generation with task_id

        Args:
            task_id (str): Unique task ID of the text-to-video generation task.

        Returns:
            A dictionary with detail response.
        """
        return self.image_tool.result_txt2vid(
            task_id=task_id, 
            headers=self.headers
        )
    
    # TEXT BLOCK ===============================
    def text_generation(
        self, 
        messages: list,
        model: str = "gemma-7b",
        temperature: float = 0.7,
        top_k: int = 50,
        top_p: float = 0.95,
        max_tokens: int = 256,
    ) -> Dict[str, Any]:
        """Generate text with messages input.

        Args:
            messages (list): The list of messages prompt for generation.
            model (str): The type of model to be used. Default is "gemma-7b".
            temperature (float): Temperature for generation. Default is 0.7.
            top_k (int): Top-k for generation. Default is 50.
            top_p (float): Top-p for generation. Default is 0.95.
            max_tokens (int): Max tokens for generation. Default is 256.
        
        Returns:
            A dictionary with the generated text.
        """
        
        return self.text_tool.text_generation(
            messages=messages, 
            model=model, 
            temperature=temperature, 
            top_k=top_k, 
            top_p=top_p, 
            max_tokens=max_tokens, 
            headers=self.headers
        )

    def generate_text_stream(
        self, 
        messages: list,
        model: str = "gemma-7b",
        temperature: float = 0.7,
        top_k: int = 50,
        top_p: float = 0.95,
        max_tokens: int = 256
    ):
        
        """Generate text with messages input in streaming.

        Args:
            messages (list): The list of messages prompt for generation.
            model (str): The type of model to be used. Default is "gemma-7b".
            temperature (float): Temperature for generation. Default is 0.7.
            top_k (int): Top-k for generation. Default is 50.
            top_p (float): Top-p for generation. Default is 0.95.
            max_tokens (int): Max tokens for generation. Default is 256.
        
        Returns:
            A dictionary with the generated text.
        """

        self.text_tool.generate_text_stream(
            messages=messages, 
            model=model, 
            temperature=temperature, 
            top_k=top_k, 
            top_p=top_p, 
            max_tokens=max_tokens, 
            headers=self.headers
        )

    def create_text_embedding(self, text: str, model: str="mistral"):
        """Create text embedding

        Args:
            text (str): The text for embedding.
            model (str): The type of model to be used. Default is "mistral".

        Returns:
            A dictionary with the generated embedding.
        """
        return self.text_tool.create_text_embedding(
            text=text, 
            model=model, 
            headers=self.headers
        )

    def result_text_embedding(self, task_id: str):
        """Get result of text embedding with task_id

        Args:
            task_id (str): Unique task ID of the text embedding task.

        Returns:
            A dictionary with detail response.
        """
        return self.text_tool.result_text_embedding(
            task_id=task_id, 
            headers=self.headers
        )
    
    # AUDIO BLOCK ===============================
    def create_txt2audio(
        self, 
        prompt: str,
        model: str = "musicgen",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate audio with prompt.

        Args:
            prompt (str): The prompt for generation.
            model (str): The type of model to be used. Default is "musicgen".
            **kwargs: Additional keyword arguments for the model.
        
        Returns:
            A dictionary with the generated audio.
        """
        return self.audio_tool.create_txt2audio(
            prompt=prompt, 
            model=model, 
            headers=self.headers,
            **kwargs
        )
    
    def result_txt2audio(self, task_id: str):
        """Get result of text to audio generation with task_id

        Args:
            task_id (str): Unique task ID of the text-to-audio generation task.

        Returns:
            A dictionary with detail response.
        """
        return self.audio_tool.result_txt2audio(
            task_id=task_id, 
            headers=self.headers
        )
    
    # FEEDBACK BLOCK ===============================
    def submit_feedback(self, task_id: str, rating: float, feedback: str) -> Dict[str, Any]:
        """Submit feedback for a completed task.

        Args:
            task_id: The unique identifier of the task.
            rating: A numeric rating value for the task outcome.
            feedback: Textual feedback about the task.

        Returns:
            A dictionary indicating the status of the feedback submission.
        """
        url = f"{self.base_url}/ai/feedback"
        payload = {"task_id": task_id, "rating": rating, "feedback": feedback}
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()
