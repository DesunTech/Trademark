import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
import fitz
import base64
import json
import re
from fastapi import HTTPException


class TrademarkExtractor:
    def __init__(self, groq_api_key: str):
        self.model = ChatGroq(
            temperature=0.1,
            groq_api_key=groq_api_key,
            model_name="meta-llama/llama-4-scout-17b-16e-instruct",
        )
        self.model2 = ChatGroq(
            temperature=0.1,
            groq_api_key=groq_api_key,
            model_name="llama-3.3-70b-versatile",
        )

        self.text_extract_prompt_template = ChatPromptTemplate.from_messages([
            ("system", "Extract all text content from this trademark document exactly as it appears.\n      Maintain the original layout and formatting as much as possible.\n      Pay special attention to:\n      1. Company/applicant names and addresses\n      2. Trademark names and logos\n      3. Registration dates and numbers\n      4. Business categories and descriptions\n      5. Contact information and legal details"),

            ("human",
                [
                    {"type":"text", "text": "Extract all text from this trademark document with high accuracy:"},
                    {"type": "image_url", "image_url": {"url": "{image_url}"}}
                ])
        ])

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """
You are an expert trademark data extraction assistant. You must return ONLY a valid JSON object with no additional text, formatting, or explanations.

CRITICAL RULES:
1. Return ONLY the JSON object - no markdown, no code blocks, no explanations
2. Ensure all JSON syntax is correct - no trailing commas, proper quotes, valid structure
3. Use consistent field names throughout
4. All string values must be properly quoted
5. Do not include any comments or extra text

Extract the following trademark information from the document:

BASIC DETAILS:
- Trademark name/title
- Registration number or application number
- Registration date or application date

COMPANY/APPLICANT INFORMATION:
- Company/applicant name
- Full address including city, state, country
- Business type or firm type

TRADEMARK DETAILS:
- "text_in_logo": Extract ONLY the company name as it appears within the logo/trademark itself. This should be the stylized text that forms the visual brand identity. Look for text that is designed as part of the logo graphics, often in special fonts, colors, or styling. If no text is visible in the logo design, return empty string.
- "logo_description": Provide a brief 5-8 word visual description of what the logo looks like (e.g., "red circle with white text", "geometric blue triangular design", "stylized bird with wings spread", "minimalist black and white lines")
- Business category or classification
- Description of goods/services

CONTACT/LEGAL INFORMATION:
- Contact person or legal representative
- Phone, email, website if available
- Legal status or registration status

IMPORTANT DISTINCTION:
- "name": Company/applicant legal name (from application forms)
- "text_in_logo": Only the text that appears AS PART OF the logo design itself (stylized company name within the trademark symbol)

Return the JSON in this exact structure:

{{
  "name": "string",
  "address": "string", 
  "city": "string",
  "firm_type": "string",
  "date": "string",
  "text_in_logo": "string",
  "logo_description": "string",
  "registration_number": "string",
  "business_category": "string",
  "contact_person": "string",
  "phone": "string",
  "email": "string",
  "website": "string",
  "legal_status": "string",
  "description": "string",
  "state": "string",
  "country": "string"
}}

IMPORTANT: Return ONLY the JSON object. Ensure all syntax is valid JSON.
"""),
            ("human", "Extract trademark data from this text and return structured JSON:\n{text}")
        ])

    def clean_json_response(self, response: str) -> str:
        """Clean the response to extract pure JSON"""
        # Remove markdown code blocks
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*$', '', response)
        response = response.strip()
        
        # Try to find JSON object boundaries
        start_idx = response.find('{')
        if start_idx != -1:
            # Find the last closing brace
            brace_count = 0
            end_idx = -1
            for i in range(start_idx, len(response)):
                if response[i] == '{':
                    brace_count += 1
                elif response[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i
                        break
            
            if end_idx != -1:
                response = response[start_idx:end_idx + 1]
        
        return response

    def classify_document(self, text: str) -> str:
        """Classify if the document is a trademark document"""
        lower_text = text.lower()
        trademark_patterns = [
            "trademark", "trade mark", "registered trademark", "™", "®", 
            "patent", "copyright", "intellectual property", "brand",
            "logo", "service mark", "certification mark", "collective mark",
            "registration", "application", "申请", "商标", "ट्रेडमार्क",
            "marca registrada", "marque déposée", "marchio registrato"
        ]
        
        for pattern in trademark_patterns:
            if pattern in lower_text:
                return "trademark"
        
        # Check for common trademark document indicators
        if (
            ("registration" in lower_text and ("number" in lower_text or "no" in lower_text)) or
            ("application" in lower_text and ("filed" in lower_text or "date" in lower_text)) or
            ("mark" in lower_text and ("owner" in lower_text or "applicant" in lower_text))
        ):
            return "trademark"
        
        return "trademark"  # Default assumption for this use case

    def extract_trademark_data_from_text(self, text: str):
        try:
            # Get raw response from model
            chain = self.prompt_template | self.model2
            response = chain.invoke(
                {"text": text},
                config={"return_token_usage": True}
            )
            
            # Clean the response to extract pure JSON
            clean_response = self.clean_json_response(response.content)

            # Parse JSON manually with better error handling
            try:
                parsed_data = json.loads(clean_response)
                return parsed_data
            except json.JSONDecodeError as json_error:
                raise HTTPException(status_code=500, detail=f"JSON parsing error: {str(json_error)}")
                
        except Exception as e:
            print(f"Error processing text: {e}")
            raise HTTPException(status_code=500, detail="Internal processing error")

    def extract_from_pdf_bytes(self, pdf_bytes: bytes):
        """Extract trademark data from PDF bytes"""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        if doc.page_count == 0:
            raise ValueError("No pages found in PDF")
        
        all_trademarks = []
        
        # Process each page as it may contain separate trademark data
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            base64_image = base64.b64encode(img_bytes).decode("utf-8")
            
            trademark_data = self.extract_from_base64_image(base64_image)
            if trademark_data and trademark_data.get("text"):
                # Extract structured data from the text
                structured_data = self.extract_trademark_data_from_text(trademark_data["text"])
                structured_data["page_number"] = page_num + 1
                all_trademarks.append(structured_data)
        
        doc.close()
        return all_trademarks

    def extract_from_base64_image(self, base64_image: str):
        """Extract text from base64 image"""
        try:
            chain = (
                self.text_extract_prompt_template 
                | self.model 
                | {"text": StrOutputParser(), "metadata": lambda x: x}
            )
            result = chain.invoke(
                {"image_url": f"data:image/png;base64,{base64_image}"},
                config={"return_token_usage": True}
            )
            
            return {"text": result["text"]}
            
        except Exception as e:
            print(f"Error processing base64 image: {e}")
            raise 