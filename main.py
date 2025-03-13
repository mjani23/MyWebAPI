
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import openai
import os
app = FastAPI()
templates = Jinja2Templates(directory="templates")
ConvoHistory = []

# Load OpenAI key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key is missing!")

openai.api_key = api_key  
client = openai.OpenAI() 


@app.get("/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/ask-openai", response_class=HTMLResponse)
async def ask_openai(prompt: str = Form(...)):
    global ConvoHistory  

    # Clear conversation history
    if prompt.lower() == "clear history":
        ConvoHistory = []  
        return HTMLResponse(content=f"""
            <textarea id="input-box" 
            class="box" 
            name="prompt" 
            placeholder="Communications..." 
            required data-cleared="false"></textarea>
        """)

    try:
        # Append user message to history
        ConvoHistory.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=ConvoHistory  
        )

        # Log the response
        ai_response = response.choices[0].message.content  
        ConvoHistory.append({"role": "assistant", "content": ai_response})

        print("OpenAI Response:", ai_response)  

        #return the updated response
        return HTMLResponse(content=f"""
            <textarea id="input-box" 
            class="box" 
            name="prompt" 
            required data-cleared="false">{ai_response}</textarea>
        """)
    except Exception as e:
        print("Error:", str(e)) 
        raise HTTPException(status_code=500, detail=str(e))

#Reference: OpenAI API documentation (https://platform.openai.com/docs/)
#http://127.0.0.1:8000/docs 


"""
Commands: 
source myenv/bin/activate
uvicorn main:app --reload

python3 test.py

kill -9 $(lsof -t -i :8000)


CTRL + C  # Stop Uvicorn server
deactivate #close virtual env 
"""

