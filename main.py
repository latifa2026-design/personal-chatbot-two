"""
Simple Groq-powered Chatbot with a Tkinter GUI.

Reads the API key from a local .env file (variable: API_KEY) and uses the
Groq Chat Completions API to generate responses.
"""

import os
import threading
import tkinter as tk
from tkinter import scrolledtext

from dotenv import load_dotenv
from groq import Groq

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
load_dotenv()  # loads variables from the .env file into the environment

API_KEY = os.getenv("API_KEY")
MODEL_NAME = "openai/gpt-oss-120b"  # a current, fast Groq-hosted model

if not API_KEY:
    raise RuntimeError(
        "API_KEY not found. Make sure a .env file exists next to main.py "
        "with a line like: API_KEY=your_key_here"
    )

client = Groq(api_key=API_KEY)

# ---------------------------------------------------------------------------
# Profile / persona information
# ---------------------------------------------------------------------------
PROFILE_NAME = "Prof. Dr. Latifa Afrin Dill Naher"
PROFILE_TITLE = "Physiology Teaching Assistant"

PROFILE_BIO = """
Name: Prof. Dr. Latifa Afrin Dill Naher
Education:
- MBBS - Rangpur Medical College
- Postgraduation - Physiology, Bangabandhu Sheikh Mujib Medical University (BSMMU)
Current position: Professor and Head, Department of Physiology,
Universal Medical College, Dhaka, Bangladesh
Experience: More than 20 years of teaching experience in Physiology
Professional role: Vice President (VP), Dhaka Division,
Bangladesh Society of Physiologists (BSP)
Current goal: Expanding teaching skills by learning and applying AI in
medical education.
""".strip()

SYSTEM_PROMPT = f"""
You are the personal AI teaching assistant of {PROFILE_NAME}, built to help
her extend her Physiology teaching using AI.

Here is her profile, use it whenever asked about her background,
credentials, or achievements, and answer such questions accurately and
respectfully in third person:

{PROFILE_BIO}

Your responsibilities:
1. When asked about {PROFILE_NAME} (her education, career, experience,
   or professional roles), answer using ONLY the profile information above.
2. When asked Physiology questions (concepts, mechanisms, exam questions,
   teaching material, MCQs, case discussions, etc.), answer as a
   knowledgeable Physiology teaching assistant - clear, accurate, and
   suitable for medical students and teaching purposes.
3. When asked general questions about teaching methods, AI tools for
   education, or how to use AI in medical teaching, give practical,
   supportive advice.
4. Keep a professional, warm, and encouraging tone, appropriate for an
   academic environment.
5. If a question is outside Physiology/medical education/her profile,
   answer helpfully as a general assistant.
""".strip()

# Conversation history sent to the model on every request so it has context.
conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------
class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{PROFILE_NAME} - {PROFILE_TITLE}")
        self.root.geometry("560x640")
        self.root.minsize(420, 420)

        # Header banner with name/title
        header = tk.Frame(root, bg="#0b3d91")
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text=PROFILE_NAME,
            bg="#0b3d91",
            fg="white",
            font=("Segoe UI", 13, "bold"),
            anchor="w",
            pady=6,
            padx=12,
        ).pack(fill=tk.X)
        tk.Label(
            header,
            text=f"{PROFILE_TITLE} | Physiology, Universal Medical College, Dhaka",
            bg="#0b3d91",
            fg="#d6e4ff",
            font=("Segoe UI", 9),
            anchor="w",
            pady=6,
            padx=12,
        ).pack(fill=tk.X)

        # Chat display area
        self.chat_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state="disabled", font=("Segoe UI", 10)
        )
        self.chat_area.pack(padx=10, pady=(10, 5), fill=tk.BOTH, expand=True)
        self.chat_area.tag_config("user", foreground="#1a73e8")
        self.chat_area.tag_config("bot", foreground="#188038")
        self.chat_area.tag_config("error", foreground="#d93025")

        # Input area (entry + send button)
        input_frame = tk.Frame(root)
        input_frame.pack(padx=10, pady=(0, 10), fill=tk.X)

        self.user_input = tk.Entry(input_frame, font=("Segoe UI", 11))
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.user_input.bind("<Return>", self.on_send)
        self.user_input.focus()

        self.send_button = tk.Button(
            input_frame, text="Send", width=10, command=self.on_send
        )
        self.send_button.pack(side=tk.RIGHT)

        self._append_message(
            "Bot",
            "Welcome! I am the AI teaching assistant for Prof. Dr. Latifa Afrin "
            "Dill Naher. Ask me a Physiology question, a teaching-related "
            "question, or about her academic background.",
            "bot",
        )

    # -- UI helpers -----------------------------------------------------
    def _append_message(self, sender, message, tag):
        self.chat_area.configure(state="normal")
        self.chat_area.insert(tk.END, f"{sender}: {message}\n\n", tag)
        self.chat_area.configure(state="disabled")
        self.chat_area.see(tk.END)

    def _set_inputs_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.user_input.configure(state=state)
        self.send_button.configure(state=state)

    # -- Event handlers ---------------------------------------------------
    def on_send(self, event=None):
        message = self.user_input.get().strip()
        if not message:
            return

        self.user_input.delete(0, tk.END)
        self._append_message("You", message, "user")
        conversation_history.append({"role": "user", "content": message})

        self._set_inputs_enabled(False)
        threading.Thread(target=self._get_bot_reply, daemon=True).start()

    def _get_bot_reply(self):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=conversation_history,
            )
            reply = response.choices[0].message.content
            conversation_history.append({"role": "assistant", "content": reply})
            self.root.after(0, lambda: self._append_message("Bot", reply, "bot"))
        except Exception as exc:  # noqa: BLE001
            error_text = f"Error: {exc}"
            self.root.after(0, lambda: self._append_message("Bot", error_text, "error"))
        finally:
            self.root.after(0, lambda: self._set_inputs_enabled(True))
            self.root.after(0, self.user_input.focus)


def main():
    root = tk.Tk()
    ChatbotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

