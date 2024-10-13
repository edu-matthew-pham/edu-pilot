import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from typing import Optional, Any
import asyncio

from core.ui.base import ProjectStage, UIBase, UIClosedError, UISource, UserInput
from core.log import get_logger

log = get_logger(__name__)

class TkinterUI(UIBase):
    def __init__(self):
        self.root = None
        self.output_text = None
        self.input_text = None
        self.submit_button = None
        self.progress_bar = None
        self.user_input = None
        self.input_event = asyncio.Event()

    async def start(self) -> bool:
        log.debug("Starting Tkinter UI")
        self.root = tk.Tk()
        self.root.title("Edu-Pilot")
        self.root.geometry("800x600")

        # Reduced height of the output console
        self.output_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=80, height=20)
        self.output_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Multi-line, wrapping input field
        self.input_text = tk.Text(self.root, wrap=tk.WORD, width=80, height=5)
        self.input_text.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        # Bind the Enter key to submit_input, but allow Shift+Enter for new lines
        self.input_text.bind("<Return>", self.handle_return)
        self.input_text.bind("<Shift-Return>", lambda e: "break")

        self.submit_button = tk.Button(self.root, text="Submit", command=self.submit_input)
        self.submit_button.pack(pady=(0, 10))

        self.progress_bar = ttk.Progressbar(self.root, orient='horizontal', length=300, mode='determinate')
        self.progress_bar.pack(pady=(0, 10))

        return True

    def handle_return(self, event):
        self.submit_input()
        return "break"  # Prevents the default behavior of inserting a newline

    async def stop(self):
        log.debug("Stopping Tkinter UI")
        if self.root:
            self.root.quit()

    async def send_stream_chunk(
        self, chunk: Optional[str], *, source: Optional[UISource] = None, project_state_id: Optional[str] = None
    ):
        if chunk is None:
            self.output_text.insert(tk.END, "\n")
        else:
            self.output_text.insert(tk.END, chunk)
        self.output_text.see(tk.END)

    async def send_message(
        self, message: str, *, source: Optional[UISource] = None, project_state_id: Optional[str] = None
    ):
        if source:
            self.output_text.insert(tk.END, f"[{source.display_name}] {message}\n")
        else:
            self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)

    async def send_key_expired(self, message: Optional[str] = None):
        if message:
            await self.send_message(message)
        messagebox.showwarning("Key Expired", "Your API key has expired.")

    async def send_app_finished(
        self,
        app_id: Optional[str] = None,
        app_name: Optional[str] = None,
        folder_name: Optional[str] = None,
    ):
        message = f"Application finished: {app_name or app_id} in folder {folder_name}"
        await self.send_message(message)

    async def send_feature_finished(
        self,
        app_id: Optional[str] = None,
        app_name: Optional[str] = None,
        folder_name: Optional[str] = None,
    ):
        message = f"Feature finished for app: {app_name or app_id} in folder {folder_name}"
        await self.send_message(message)

    async def ask_question(
        self,
        question: str,
        *,
        buttons: Optional[dict[str, str]] = None,
        default: Optional[str] = None,
        buttons_only: bool = False,
        allow_empty: bool = False,
        hint: Optional[str] = None,
        initial_text: Optional[str] = None,
        source: Optional[UISource] = None,
        project_state_id: Optional[str] = None,
    ) -> UserInput:
        await self.send_message(question, source=source)
        
        if buttons:
            for k, v in buttons.items():
                default_str = " (default)" if k == default else ""
                await self.send_message(f"  [{k}]: {v}{default_str}")

        if initial_text:
            self.input_text.insert(tk.END, initial_text)

        self.input_event.clear()
        await self.input_event.wait()

        choice = self.user_input.strip()
        self.user_input = None

        if not choice and default:
            choice = default

        if buttons and choice in buttons:
            return UserInput(button=choice, text=None)
        if buttons_only:
            await self.send_message("Please choose one of available options")
            return await self.ask_question(question, buttons=buttons, default=default, buttons_only=True, source=source)
        if choice or allow_empty:
            return UserInput(button=None, text=choice)
        await self.send_message("Please provide a valid input")
        return await self.ask_question(question, buttons=buttons, default=default, allow_empty=allow_empty, source=source)

    async def send_progress(self, progress: float, *, project_state_id: Optional[str] = None):
        self.progress_bar['value'] = progress * 100

    async def send_project_stage(self, stage: ProjectStage, *, project_state_id: Optional[str] = None):
        await self.send_message(f"Project stage: {stage.display_name}")

    async def send_task_list(self, tasks: list[str], *, project_state_id: Optional[str] = None):
        await self.send_message("Task list:")
        for task in tasks:
            await self.send_message(f"- {task}")

    async def send_file_diff(self, file_path: str, diff: str, *, project_state_id: Optional[str] = None):
        await self.send_message(f"File diff for {file_path}:")
        await self.send_message(diff)

    async def send_file_content(self, file_path: str, content: str, *, project_state_id: Optional[str] = None):
        await self.send_message(f"File content for {file_path}:")
        await self.send_message(content)

    async def send_command_executed(self, command: str, output: str, *, project_state_id: Optional[str] = None):
        await self.send_message(f"Command executed: {command}")
        await self.send_message(f"Output: {output}")

    def submit_input(self):
        self.user_input = self.input_text.get("1.0", tk.END).strip()
        self.input_text.delete("1.0", tk.END)
        self.input_event.set()

    def update(self):
        if self.root:
            self.root.update()
        else:
            log.warning("Attempted to update Tkinter UI before initialization")

'''
if __name__ == "__main__":
    async def main():
        ui = TkinterUI()
        await ui.start()
        await ui.send_message("Welcome to Edu-Pilot!")
        response = await ui.ask_question("What's your name?")
        await ui.send_message(f"Hello, {response.text}!")
        await ui.send_progress(0.5)
        await ui.send_project_stage(ProjectStage.DEVELOPMENT)
        await asyncio.sleep(5)
        await ui.stop()

    asyncio.run(main())
'''
