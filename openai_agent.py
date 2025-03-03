import openai
import json
from config import OPENAI_API_KEY,  GPT_MODEL


# Load the Textract JSON document
file_path = 'docs/SOP_Document_Control.json'
with open(file_path, 'r') as file:
    textract_data = json.load(file)

# Function to call OpenAI's Chat Completion API to structure the document
def chat_completion_agent(textract_data):
    # Extract all the text content from the Textract JSON blocks
    document_text = "\n".join([block['Text'] for block in textract_data['Blocks'] if block['BlockType'] == 'LINE'])
    
    # Define the system prompt for the model
    system_message = """
    You are a helpful assistant that processes document text and extracts important structured information like title, date, address, and sections.
    Based on the provided document, extract the following:
    1. The document's title
    2. The document's date
    3. The address (if available)
    4. Sections like Purpose, Scope, Responsibility, and Procedure with their respective text.
    """

    # Create the messages for the completion API
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Here is the document text: {document_text}. Please extract the information as described."}
    ]

    # Initialize the OpenAI
    client = openai.Client(api_key=OPENAI_API_KEY)  # Initialize the client
    # Call OpenAI's Chat Completion API
    response = client.chat.completions.create(
        model=GPT_MODEL,  # Use the appropriate model here (gpt-4 or gpt-3.5-turbo)
        messages=messages,
        max_tokens=500  # Adjust based on the length of the document
    )
    
    # Return the response from the model (the structured information)
    return response.choices[0].message['content']



if __name__ == "__main__":
    # Call the Chat Completion Agent
    structured_data = chat_completion_agent(textract_data)

    # Print out the structured data from the model
    print(structured_data)

    # Optionally save the output to a file
    output_path = 'docs/structured_SOP_output.json'
    with open(output_path, 'w') as json_file:
        json.dump(structured_data, json_file, indent=4)
