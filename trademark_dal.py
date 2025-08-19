import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
import fitz
import base64
import json
import re
from fastapi import HTTPException
from pydantic import SecretStr

class TrademarkExtractor:
    def __init__(self, groq_api_key: str):
        self.model = ChatGroq(
            temperature=0.1,
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            api_key=SecretStr(groq_api_key),
        )
        self.model2 = ChatGroq(
            temperature=0.1,
            model="llama-3.3-70b-versatile",
            api_key=SecretStr(groq_api_key),
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

 
