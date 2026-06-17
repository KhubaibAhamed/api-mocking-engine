import os
import json
import tempfile
import gradio as gr
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from fpdf import FPDF

# 1. Load the API token
load_dotenv()
hf_token = os.getenv("HF_TOKEN")
client = InferenceClient("meta-llama/Meta-Llama-3-8B-Instruct", token=hf_token)

# [SECURITY FEATURE]: Prevent massive inputs that could crash memory or exhaust API limits
MAX_INPUT_LENGTH = 5000 

system_prompt = """
You are an expert API architect. Analyze the provided Java Spring Boot code snippet.
Extract the REST API endpoint details (paths, methods, parameters) and output a valid OpenAPI 3.0 JSON specification.
Generate realistic mock data for the response based on the code context.
IMPORTANT: Return ONLY raw JSON. Do not include markdown formatting like triple backticks.
"""

def generate_mock_api(java_code):
    # [SECURITY FEATURE]: Input Size Validation
    if len(java_code) > MAX_INPUT_LENGTH:
        error_msg = f"Error: Input too large. Please keep code under {MAX_INPUT_LENGTH} characters."
        # Return error and hide the download button
        return error_msg, gr.update(visible=False)

    if not hf_token or hf_token == "your_token_here":
        return "Error: Hugging Face Token is missing from .env file.", gr.update(visible=False)
        
    try:
        response = client.chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": java_code}
            ],
            max_tokens=800,
            temperature=0.1 
        )
        
        raw_output = response.choices[0].message.content.strip()
        
        # Clean markdown formatting if AI added it (Using a trick to avoid chat cutoff)
        markdown_json = "`" * 3 + "json"
        markdown_block = "`" * 3
        
        if raw_output.startswith(markdown_json): 
            raw_output = raw_output[7:]
        if raw_output.startswith(markdown_block): 
            raw_output = raw_output[3:]
        if raw_output.endswith(markdown_block): 
            raw_output = raw_output[:-3]
            
        parsed_json = json.loads(raw_output.strip())
        formatted_json = json.dumps(parsed_json, indent=2)
        
        # Save locally for the Java server
        with open("../openapi-mock.json", "w") as f:
            f.write(formatted_json)
            
        # --- [NEW FEATURE]: Generate PDF ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Courier", size=10)
        
        # Add a nice header to the PDF
        pdf.set_font("Courier", style='B', size=14)
        pdf.cell(0, 10, txt="Intelligent API Mocking Engine - Contract", align='C')
        pdf.ln(10)
        
        # Add the JSON content
        pdf.set_font("Courier", size=9)
        for line in formatted_json.split('\n'):
            # [MEMORY/SECURITY]: Sanitize characters to prevent PDF generation crashes
            safe_line = line.encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(0, 5, txt=safe_line)
            pdf.ln(5)

        # [MEMORY MANAGEMENT]: Use a temporary file that the OS cleans up automatically
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(temp_pdf.name)
        
        # Return the JSON text, AND update the Download Button to show the new PDF
        return formatted_json, gr.update(value=temp_pdf.name, visible=True)
        
    except json.JSONDecodeError:
         return f"Error: The AI did not return valid JSON.\n\n{raw_output}", gr.update(visible=False)
    except Exception as e:
        return f"An error occurred: {str(e)}", gr.update(visible=False)

# Build the Visual Website Layout
with gr.Blocks() as web_interface:
    gr.Markdown("# Intelligent API Mocking Engine")
    gr.Markdown("Paste your backend Spring Boot code below. The AI will instantly generate a mock OpenAPI contract.")
    
    with gr.Row():
        with gr.Column():
            code_input = gr.Code(
                label="Paste Java Spring Boot Code Here", 
                lines=15,
                value="@RestController\n@RequestMapping(\"/api/products\")\npublic class ProductController {\n    @GetMapping(\"/{id}\")\n    public Product getProduct(@PathVariable String id) {\n        return new Product(id, \"Laptop\", 999.99);\n    }\n}"
            )
            submit_btn = gr.Button("Generate Mock API & PDF", variant="primary")
        
        with gr.Column():
            json_output = gr.Code(label="AI Generated OpenAPI Contract", interactive=False, lines=14)
            # [NEW FEATURE]: Hidden download button that appears after successful generation
            download_btn = gr.DownloadButton("📥 Download API Contract as PDF", visible=False)
            
    # Connect the button click to the Python function (Note: it now updates TWO outputs)
    submit_btn.click(
        fn=generate_mock_api, 
        inputs=code_input, 
        outputs=[json_output, download_btn]
    )

if __name__ == "__main__":
    # [SECURITY/MEMORY FEATURE]: Enable queuing to prevent server overload if many people click at once
    web_interface.queue(default_concurrency_limit=5)
    web_interface.launch(server_name="0.0.0.0", server_port=7860)