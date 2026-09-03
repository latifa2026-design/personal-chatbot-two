"""
Simple Groq-powered Chatbot with a Tkinter GUI.

Reads the API key from a local .env file (variable: API_KEY) and uses the
Groq Chat Completions API to generate responses.
"""

import os
import threading

# tkinter is only needed for the desktop GUI. Import it guarded so the web
# server (web_server.py) can import this module on headless hosts like Render,
# which have no Tk build ("No module named '_tkinter'").
try:
    import tkinter as tk
    from tkinter import scrolledtext

    TK_AVAILABLE = True
except ImportError:  # pragma: no cover - headless environments only
    tk = None  # type: ignore[assignment]
    scrolledtext = None  # type: ignore[assignment]
    TK_AVAILABLE = False

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

# ---------------------------------------------------------------------------
# Research publications
# Journal name + volume number (with issue, pages, year and DOI) for every
# indexed article. Metadata was verified against Crossref records. New papers
# can be added by appending a dictionary to this list.
# ---------------------------------------------------------------------------
PUBLICATIONS = [
    {
        "authors": "Naher LAD, Begum N, Ferdousi S, Begum S, Ali T",
        "title": "Sympathetic Nerve Function Status in Postmenopausal Women",
        "journal": "Journal of the Bangladesh Society of Physiologists (JBSP)",
        "journal_short": "J Bangladesh Soc Physiol",
        "volume": 5,
        "issue": 1,
        "pages": "40-45",
        "year": 2010,
        "doi": "10.3329/jbsp.v5i1.5417",
        "url": "https://doi.org/10.3329/jbsp.v5i1.5417",
    },
    {
        "authors": "Naher LAD, Begum N, Ferdousi S",
        "title": (
            "Ovarian Hormones During Different Phases of Ovarian Cycle "
            "in Healthy Young Women"
        ),
        "journal": "Journal of the Bangladesh Society of Physiologists (JBSP)",
        "journal_short": "J Bangladesh Soc Physiol",
        "volume": 7,
        "issue": 2,
        "pages": "83-88",
        "year": 2012,
        "doi": "10.3329/jbsp.v7i2.14456",
        "url": "https://doi.org/10.3329/jbsp.v7i2.14456",
    },
    {
        "authors": "Naher LAD, Begum N, Ferdousi S",
        "title": (
            "Sympathetic Nerve Function Status and their Relationships "
            "with Ovarian Hormones in Healthy Young Women"
        ),
        "journal": "Journal of the Bangladesh Society of Physiologists (JBSP)",
        "journal_short": "J Bangladesh Soc Physiol",
        "volume": 11,
        "issue": 1,
        "pages": "13-17",
        "year": 2016,
        "doi": "10.3329/jbsp.v11i1.29704",
        "url": "https://doi.org/10.3329/jbsp.v11i1.29704",
    },
]

# ---------------------------------------------------------------------------
# MEU (Medical Education Unit) role & activities — Universal Medical College
# ---------------------------------------------------------------------------
MEU_ROLE = {
    "title": "Member Secretary & Coordinator",
    "unit": "Medical Education Unit (MEU)",
    "institution": "Universal Medical College (UMC), Dhaka, Bangladesh",
    "summary": (
        "Prof. Dr. Latifa Afrin Dill Naher serves as the Member Secretary and "
        "Coordinator of the Medical Education Unit (MEU) at Universal Medical "
        "College (UMC), Dhaka. In this role she drives faculty development and "
        "medical-education activities for the institution."
    ),
    "activities": [
        "Serves as Member Secretary & Coordinator of the MEU, plans its annual "
        "calendar and maintains the minutes, records and documentation of all "
        "MEU meetings.",
        "Organizes faculty development programs and workshops on teaching–"
        "learning methods for UMC faculty.",
        "Conducts training sessions on modern assessment techniques such as "
        "OSPE/OSCE, MCQs and structured viva-voce.",
        "Arranges medical-education seminars, CMEs and symposia on topics "
        "such as communication skills, ethics and student feedback.",
        "Facilitates orientation and mentoring of newly appointed faculty "
        "members.",
        "Supports curriculum planning and implementation aligned with the "
        "Bangladesh Medical & Dental Council (BMDC) requirements.",
        "Encourages and coordinates educational/action research by faculty "
        "and prepares the MEU annual report.",
    ],
}


def format_publications(publications=None):
    """Return a human-readable, numbered citation for each publication."""
    publications = publications or PUBLICATIONS
    lines = []
    for i, pub in enumerate(publications, start=1):
        citation = (
            f"{i}. {pub['title']}. {pub['authors']}. "
            f"{pub['journal_short']}, {pub['year']}; "
            f"{pub['volume']}({pub['issue']}): {pub['pages']}. "
            f"DOI: {pub['doi']}"
        )
        lines.append(citation)
    return "\n".join(lines)


PUBLICATIONS_TEXT = format_publications()
MEU_TEXT = "\n".join(f"- {activity}" for activity in MEU_ROLE["activities"])

PROFILE_BIO = """
Name: Prof. Dr. Latifa Afrin Dill Naher
Education:
- MBBS - Rangpur Medical College
- Postgraduation - Physiology, Bangabandhu Sheikh Mujib Medical University (BSMMU)
Current position: Professor and Head, Department of Physiology,
Universal Medical College, Dhaka, Bangladesh
Experience: More than 20 years of teaching experience in Physiology
Professional roles:
- Vice President (VP), Dhaka Division,
  Bangladesh Society of Physiologists (BSP)
- Associate Editor, Journal of the Bangladesh Society of Physiologists (JBSP)
- Former Executive Editor, Prime Medical Journal (served for about 5-6 years)
Additional duties:
- Member Secretary & Coordinator, Medical Education Unit (MEU),
  Universal Medical College (UMC), Dhaka
  Key MEU activities:
  * Coordinates the MEU and, as Member Secretary, maintains its records,
    minutes and documentation
  * Organizes faculty development programs and workshops on teaching-
    learning methods
  * Conducts training on assessment techniques (OSPE/OSCE, MCQs,
    structured viva-voce)
  * Arranges medical-education seminars, CMEs and symposia for faculty
  * Supports new-faculty orientation, mentoring, and educational research
Research & publications (journal name with volume number):
- She has published original research articles in national and
  international journals. Her indexed articles appear in the Journal of
  the Bangladesh Society of Physiologists (J Bangladesh Soc Physiol),
  for example:
  * J Bangladesh Soc Physiol, 2010; 5(1): 40-45
  * J Bangladesh Soc Physiol, 2012; 7(2): 83-88
  * J Bangladesh Soc Physiol, 2016; 11(1): 13-17
- Her published articles have received citations from other researchers
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
6. RESEARCH & PUBLICATIONS: When asked about her research work, published
   articles, or journals, use the numbered Publications list below. Always
   state the journal name AND its volume number (e.g. "Journal of the
   Bangladesh Society of Physiologists, Vol. 5, No. 1"), together with the
   issue, page range, year and DOI when relevant.
7. MEU ROLE: When asked about her Medical Education Unit duties or
   activities, mention that she is the Member Secretary & Coordinator of
   the Medical Education Unit (MEU) at Universal Medical College (UMC),
   Dhaka, and describe only the activities listed below.
8. NEVER invent or guess article titles, journal names, volume numbers,
   issue numbers, page ranges, years or DOIs that are not present in the
   lists below.

--- Research publications (journal name with volume number) ---
{PUBLICATIONS_TEXT}

--- MEU activities (Member Secretary & Coordinator, UMC) ---
{MEU_TEXT}
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
            "question, her research publications (journal name with volume "
            "number), or about her activities as Member Secretary & "
            "Coordinator of the MEU at UMC.",
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
    if not TK_AVAILABLE:
        print(
            "Tkinter is not available in this environment.\n"
            "Start the web version instead with:  python web_server.py"
        )
        return
    root = tk.Tk()
    ChatbotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

