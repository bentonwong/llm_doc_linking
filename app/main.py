import threading
import uvicorn
from fastapi import FastAPI
from app.api import router as api_router
from app.ui import demo

app = FastAPI(title="Legal Brief Matcher")
app.include_router(api_router)

def start_gradio():
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=False,
        prevent_thread_lock=True  # 👈 critical for Render
    )

threading.Thread(target=start_gradio).start()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
