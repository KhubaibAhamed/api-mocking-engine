import os
import json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# 1. Load the HF_TOKEN from the .env file
load_dotenv()
hf_token = os.getenv("HF_TOKEN")

if not hf_token or hf_token == "your_token_here":
    print("Error: Valid HF_TOKEN not found. Please add your actual token to the .env file.")
    exit()

# 2. Initialize the Hugging Face Client
# We are using Meta's Llama 3 8B model, which is excellent at coding tasks and JSON generation.
client = InferenceClient("meta-llama/Meta-Llama-3-8B-Instruct", token=hf_token)

# 3. Dummy Java Spring Boot Controller snippet (This is what a user would paste in)
java_code = """
@RestController
@RequestMapping("/api/users")
public class UserController {
    @GetMapping("/{id}")
    public User getUserById(@PathVariable String id) {
        // Returns user details
        return new User(id, "Jane Doe", "jane.doe@example.com");
    }
}
"""

# 4. The Prompt instructing the AI exactly what we want
system_prompt = """
You are an expert API architect. Analyze the provided Java Spring Boot code snippet.
Extract the REST API endpoint details (paths, methods, parameters) and output a valid OpenAPI 3.0 JSON specification.
Generate realistic mock data for the response based on the code context.
IMPORTANT: Return ONLY raw JSON. Do not include markdown formatting like ```json or any conversational text.
"""

print("Analyzing Java code and generating mock API contract via Hugging Face...")

try:
    # 5. Call the Hugging Face API
    response = client.chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": java_code}
        ],
        max_tokens=800,
        temperature=0.1 # Low temperature for more deterministic, structured output
    )
    
    # Extract the text content from the AI's response
    raw_output = response.choices[0].message.content.strip()
    
    # 6. Clean up output (In case the AI adds markdown backticks despite our instructions)
    if raw_output.startswith("```json"):
        raw_output = raw_output[7:]
    if raw_output.startswith("```"):
         raw_output = raw_output[3:]
    if raw_output.endswith("```"):
        raw_output = raw_output[:-3]
        
    raw_output = raw_output.strip()

    # 7. Validate JSON and save it to a file
    parsed_json = json.loads(raw_output)
    
    # Save the file to the parent directory so the Java server can find it later
    with open("../openapi-mock.json", "w") as f:
        json.dump(parsed_json, f, indent=2)
        
    print("Success! OpenAPI contract saved to 'openapi-mock.json' in the root directory.")

except json.JSONDecodeError:
    print("Error: The AI did not return valid JSON. Here is what it returned instead:")
    print(raw_output)
except Exception as e:
    print(f"An error occurred: {e}")