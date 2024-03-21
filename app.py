import os
from pypdf import PdfReader
import pathlib
import textwrap
import google.generativeai as genai
from IPython.display import display, Audio
import gradio as gr
import boto3

genai.configure(api_key = 'YOUR_GOOGLE_API_KEY')
polly = boto3.client('polly',region_name='us-east-1',aws_access_key_id='YOUR_ACCESS_KEY',aws_secret_access_key='YOUR_SECRET_KEY')

def pdf_reader(pdf_path):
    reader = PdfReader(pdf_path) 
    text=" "
    for i in range(len(reader.pages)):
        page = reader.pages[i] 
        text += page.extract_text()
    return text

def generate_gemini_content(transcript_text,prompt):
    model=genai.GenerativeModel("gemini-pro")
    response=model.generate_content(prompt+transcript_text)
    return response.text

def main(path_pdf):
   prompt = """YOUR_PROMPT"""
   parsed_text = pdf_reader(path_pdf)
   final_text = generate_gemini_content(parsed_text,prompt)
   response = polly.synthesize_speech(Text=final_text, OutputFormat="mp3",
                                       VoiceId="Joanna")
   if "AudioStream" in response:
      with response["AudioStream"] as stream:
         output_file = "speech.mp3"
         try:
            # Open a file for writing the output as a binary stream
               with open(output_file, "wb") as file:
                  file.write(stream.read())
         except IOError as error:
            # Could not write to file, exit gracefully
            print(error)
   else:
      # The response didn't contain audio data, exit gracefully
      print("Could not stream audio")
   return final_text, output_file

input_pdf_path = gr.File(label="Upload PDF")
output_summary = gr.components.Textbox(label="Summary"), gr.Audio()

interface = gr.Interface(
    fn=main,
    inputs=input_pdf_path,
    outputs=["text", "audio"],
    title="PDF Summarizer",
    description="Provide PDF file path to get the summary.",
).launch()
