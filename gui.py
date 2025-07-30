import customtkinter as ctk
import queue
import logging

class QueueHandler(logging.Handler):
    """Class to send logging records to a queue."""
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(self.format(record))

class AppGUI(ctk.CTk):
    def __init__(self, log_queue):
        super().__init__()

        self.log_queue = log_queue

        # ---- Window Setup ----
        self.title("HobbitTrash AI Control Panel")
        self.geometry("800x600")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # ---- Main Layout ----
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.dashboard_tab = self.tab_view.add("Dashboard")
        # self.settings_tab = self.tab_view.add("Settings") # To be implemented later
        # self.memory_tab = self.tab_view.add("Memory Manager") # To be implemented later

        # ---- Dashboard Tab Content ----
        self.dashboard_tab.grid_columnconfigure(0, weight=1)
        self.dashboard_tab.grid_rowconfigure(1, weight=1)

        # -- Controls Frame --
        self.controls_frame = ctk.CTkFrame(self.dashboard_tab)
        self.controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.controls_frame.grid_columnconfigure(2, weight=1) # Push status to the right

        self.start_stop_button = ctk.CTkButton(self.controls_frame, text="Start AI", command=self.toggle_ai_state, width=120)
        self.start_stop_button.grid(row=0, column=0, padx=10, pady=10)

        self.status_label = ctk.CTkLabel(self.controls_frame, text="Status: OFFLINE", text_color="red", font=ctk.CTkFont(weight="bold"))
        self.status_label.grid(row=0, column=2, padx=10, pady=10, sticky="e")

        # -- Log View --
        self.log_textbox = ctk.CTkTextbox(self.dashboard_tab, state="disabled", wrap="word")
        self.log_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # ---- Start Polling for Logs ----
        self.after(100, self.poll_log_queue)

    def set_callbacks(self, start_callback, stop_callback):
        """Sets the callback functions for the Start/Stop button."""
        self.start_callback = start_callback
        self.stop_callback = stop_callback

    def toggle_ai_state(self):
        logging.info("Start/Stop button pressed.")
        current_text = self.start_stop_button.cget("text")

        if current_text == "Start AI":
            if self.start_callback:
                self.start_callback()
                self.start_stop_button.configure(text="Stop AI")
                # The bot thread itself will update the status label
        else:
            if self.stop_callback:
                self.stop_callback()
                self.start_stop_button.configure(text="Start AI")
                self.update_status("OFFLINE", "red")

    def update_status(self, text, color):
        self.status_label.configure(text=f"Status: {text}", text_color=color)

    def poll_log_queue(self):
        """Periodically check the queue for new log messages."""
        while True:
            try:
                record = self.log_queue.get(block=False)
                self.log_textbox.configure(state="normal")
                self.log_textbox.insert("end", record + "\n")
                self.log_textbox.see("end") # Scroll to the bottom
                self.log_textbox.configure(state="disabled")
            except queue.Empty:
                break
        self.after(100, self.poll_log_queue)

if __name__ == '__main__':
    # This block is for testing the GUI directly
    log_queue = queue.Queue()

    # Set up logging to go to the queue
    logging.basicConfig(level=logging.INFO)
    queue_handler = QueueHandler(log_queue)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    queue_handler.setFormatter(formatter)
    logging.getLogger().addHandler(queue_handler)

    app = AppGUI(log_queue)

    # Simulate some log messages
    logging.info("GUI started.")
    logging.warning("This is a test warning.")
    logging.error("This is a test error.")

    app.mainloop()
