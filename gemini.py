import os
import json
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure the API key for Google Generative AI
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    logger.error("API_KEY is not set. Please set it in the .env file.")
    raise ValueError("API_KEY is not set. Please set it in the .env file.")

genai.configure(api_key=API_KEY)

BASE_PROMPT = """You are an AI assistant with access to a dynamic knowledge base, capable of retrieving relevant information from trusted sources to provide accurate, clear, and contextually appropriate responses. Your responses must be provided in a simple JSON format unless subsections are specifically requested.

<Examples>

1. Simple Query:
User: "About abstract of Attention is all you need"
Retrieved Context: "The paper introduces the Transformer architecture..."
Response: {
    "response": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train."
}

2. Query Requesting Details:
User: "Explain the architecture of Transformer model with its components"
Retrieved Context: "The Transformer architecture consists of several key components..."
Response: {
    "response": {
        "overview": "The Transformer is a neural network architecture that relies entirely on attention mechanisms",
        "components": {
            "encoder": "Processes the input sequence through multiple layers of self-attention",
            "decoder": "Generates the output sequence using both self-attention and encoder-attention",
            "attention_layers": "Multi-head attention mechanisms that allow parallel processing"
        }
    }
}

3. Direct Question:
User: "What is the main advantage of Transformer models?"
Retrieved Context: "Transformers offer improved parallelization..."
Response: {
    "response": "The main advantage of Transformer models is their ability to process sequences in parallel, eliminating the sequential nature of traditional RNNs, which results in significantly faster training times and better performance on many language tasks."
}

Guidelines for responses:
1. For simple queries, provide a direct response in JSON format:
   {
       "response": "Your clear and concise answer here"
   }

2. Only include subsections when:
   - Explicitly requested by the user
   - The query specifically asks for multiple aspects or components
   - Complex analysis is required

Your responses must be entirely focused on the user's query, and all information provided should be 100% relevant. Avoid adding unrelated details or off-topic information. Always ensure the highest quality and accuracy in your responses by utilizing your access to external knowledge.
"""

# Model configuration
generation_config = {
    "temperature": 0.3,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
    "response_mime_type": "application/json",
}

class Gemini:
    def __init__(self):
        logger.info("Initializing the Gemini class.")
        try:
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-pro",
                generation_config=generation_config,
            )
            logger.info("Gemini model initialized successfully.")
        except Exception as e:
            logger.error("Error initializing the Gemini model: %s", str(e))
            raise ValueError(f"Initialization error: {e}")

    def respond(self, retrieved_contents: str = None, user_input: str = None, history: str = None) -> str:
        logger.info("Respond method called with user_input: %s", user_input)
        if not user_input:
            logger.warning("No user_input provided to respond method.")
            raise ValueError("User input is required.")

        PROMPT = BASE_PROMPT + (retrieved_contents or "") + user_input
        logger.debug("Constructed prompt: %s", PROMPT)

        inputs = [PROMPT]

        try:
            # Generate content using the model
            logger.info("Sending input to the generative model.")
            response = self.model.generate_content(inputs)
            logger.info("Response received from the model.")
            
            # Log the entire raw response for debugging
            logger.debug("Raw model response: %s", response)

            # Parse the response
            if response and hasattr(response, 'text'):
                logger.info("Parsing the response text.")
                return json.loads(response.text)
            else:
                logger.error("No valid response received from the model.")
                raise ValueError("No valid response received from the model.")
        except Exception as e:
            logger.error("Error generating response: %s", str(e))
            raise ValueError(f"Error generating response: {e}")
       

#     def app_prompt(self, retrieved_contents: str, user_input: str = None, history: str = None) -> str:
#         """
#         Build the prompt based on user input.

#         Args:
#             user_input (str): Text input from the user.

#         Returns:
#             str: Complete prompt with user input.
#         """
#         if user_input:
#             return f"{BASE_PROMPT + retrieved_contents}\n\nUser input: {history + user_input}"
#         return BASE_PROMPT

#     def respond(self, image_path: str = None, user_text: str = None) -> dict:
#         """
#         Generate a response based on the provided image and/or text.

#         Args:
#             image_path (str): Path to the image file.
#             user_text (str): Text input from the user.

#         Returns:
#             dict: Parsed response from the model.
#         """
#         # Build the prompt
#         prompt = self.app_prompt(user_text)
        
#         # Prepare inputs for the model
#         inputs = [prompt]

#         if image_path:
#             try:
#                 img = Image.open(image_path)
#                 inputs.append(img)
#             except Exception as e:
#                 raise ValueError(f"Failed to process the image: {e}")

#         try:
#             # Generate content using the model
#             response = self.model.generate_content(inputs)
#             print("Entire Response:",response)
#             # Parse the response
#             if response and hasattr(response, 'text'):
#                 return json.loads(response.text)
#             else:
#                 raise ValueError("No valid response received from the model.")
#         except Exception as e:
#             raise ValueError(f"Error generating response: {e}")


# # img = r"E:\API's\medicine_img.png"
# # query = "About the given image."
# # Model = Gemini()
# # response = Model.respond(image_path=img, user_text=query)
# # print("Response:",response)


