from __future__ import annotations

import os
import queue
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from .config import APP_NAME, APP_VERSION
from .converter import LibreOfficeConverter
from .manager import ConversionManager
from .models import FileStatus, QueueItem
from .settings import SessionSettings
from .worker import ConversionWorker

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD

    DND_AVAILABLE = True
except ImportError:
    DND_FILES = ""
    TkinterDnD = None
    DND_AVAILABLE = False


TREE_STATUS_COLORS = {
    FileStatus.PENDING: "#cbd5e1",
    FileStatus.CONVERTING: "#93c5fd",
    FileStatus.DONE: "#86efac",
    FileStatus.FAILED: "#fca5a5",
}


if TkinterDnD:

    class DnDCTk(ctk.CTk, TkinterDnD.DnDWrapper):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            try:
                self.TkdndVersion = TkinterDnD._require(self)
            except tk.TclError:
                self.TkdndVersion = None

else:

    class DnDCTk(ctk.CTk):
        pass


class App(DnDCTk):
    def __init__(self) -> None:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        super().__init__()
        self.title(f"{APP_NAME} {APP_VERSION}")
        self.geometry("1040x750")
        self.resizable(False, False)
        self._center_window(1040, 750)
        self.main_window = MainWindow(self)
        self.main_window.pack(fill="both", expand=True)

    def _center_window(self, width: int, height: int) -> None:
        self.update_idletasks()
        x = max((self.winfo_screenwidth() - width) // 2, 0)
        y = max((self.winfo_screenheight() - height) // 2, 0)
        self.geometry(f"{width}x{height}+{x}+{y}")


class DropZone(ctk.CTkFrame):
    def __init__(self, master, on_drop_paths, on_select_files, on_select_folder) -> None:
        super().__init__(master, corner_radius=22, border_width=1, border_color="#2d3a50", fg_color="#182235")
        self.on_drop_paths = on_drop_paths
        self.on_select_files = on_select_files
        self.on_select_folder = on_select_folder
        self.is_compact = False

        self.grid_columnconfigure(0, weight=1)
        self.step_label = ctk.CTkLabel(
            self,
            text="Step 1  Add files",
            text_color="#93c5fd",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.step_label.grid(row=0, column=0, padx=24, pady=(16, 4), sticky="w")

        self.title_label = ctk.CTkLabel(
            self,
            text="Add PowerPoint files",
            font=ctk.CTkFont(size=21, weight="bold"),
        )
        self.title_label.grid(row=1, column=0, padx=24, pady=(0, 4), sticky="ew")

        self.helper_label = ctk.CTkLabel(
            self,
            text="Drop files or folders here, or choose them manually.",
            text_color="#cbd5e1",
            font=ctk.CTkFont(size=14),
        )
        self.helper_label.grid(row=2, column=0, padx=24, pady=(0, 12), sticky="ew")

        self.actions = ctk.CTkFrame(self, fg_color="transparent")
        self.actions.grid(row=3, column=0, padx=24, pady=(0, 14))
        ctk.CTkButton(
            self.actions,
            text="Select PowerPoint Files",
            width=220,
            height=38,
            font=ctk.CTkFont(weight="bold"),
            command=self.on_select_files,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
        ).grid(row=0, column=0, padx=(0, 10))
        ctk.CTkButton(
            self.actions,
            text="Select Folder",
            width=140,
            height=38,
            command=self.on_select_folder,
            fg_color="#1f2937",
            hover_color="#334155",
        ).grid(row=0, column=1)

        self.note_label = ctk.CTkLabel(
            self,
            text="PDF keeps static slide visuals, but not animations, transitions, audio, or video interactivity.",
            text_color="#b6c2d2",
            wraplength=760,
        )

        if not self._enable_drop_target():
            self.helper_label.configure(
                text="Drag-and-drop is unavailable. Use Select Files or Select Folder."
            )

    def _enable_drop_target(self) -> bool:
        if not DND_AVAILABLE:
            return False
        try:
            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<Drop>>", self._handle_drop)
            for child in (self.step_label, self.title_label, self.helper_label, self.note_label):
                child.drop_target_register(DND_FILES)
                child.dnd_bind("<<Drop>>", self._handle_drop)
        except tk.TclError:
            return False
        return True

    def set_compact(self, compact: bool) -> None:
        if self.is_compact == compact:
            return
        self.is_compact = compact
        if compact:
            self.title_label.configure(text="Add more PowerPoint files", font=ctk.CTkFont(size=18, weight="bold"))
            self.helper_label.configure(text="Drop files here or use the buttons below.", text_color="#cbd5e1")
            self.step_label.grid_configure(pady=(12, 2))
            self.title_label.grid_configure(pady=(0, 4))
            self.helper_label.grid_configure(pady=(0, 8))
            self.actions.grid_configure(pady=(0, 12))
        else:
            self.title_label.configure(
                text="Add PowerPoint files",
                font=ctk.CTkFont(size=21, weight="bold"),
            )
            self.helper_label.configure(text="Drop files or folders here, or choose them manually.", text_color="#cbd5e1")
            self.step_label.grid_configure(pady=(16, 4))
            self.title_label.grid_configure(pady=(0, 4))
            self.helper_label.grid_configure(pady=(0, 12))
            self.actions.grid_configure(pady=(0, 12))

    def _handle_drop(self, event) -> None:
        paths = [Path(value) for value in self.tk.splitlist(event.data)]
        self.on_drop_paths(paths)


class MainWindow(ctk.CTkFrame):
    def __init__(self, master: App) -> None:
        super().__init__(master, corner_radius=0, fg_color="#0b1020")
        self.master = master
        self.settings = SessionSettings()
        self.manager = ConversionManager()
        self.converter = LibreOfficeConverter()
        self.worker: ConversionWorker | None = None
        self.event_queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self.selected_ids: set[str] = set()

        self.high_quality_var = tk.BooleanVar(value=False)
        self.open_output_var = tk.BooleanVar(value=False)
        self.file_count_var = tk.StringVar(value="0 files queued")
        self.summary_var = tk.StringVar(value="Ready")
        self.logs_visible = False
        self.progress_visible = False

        self._style_treeview()
        self._build_layout()
        self._build_context_menu()
        self._update_action_states()
        self.after(250, self._process_worker_events)

    def _style_treeview(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "SlideDrop.Treeview",
            background="#182235",
            fieldbackground="#182235",
            foreground="#e5edf7",
            borderwidth=0,
            rowheight=34,
            font=("Segoe UI", 10),
        )
        style.configure(
            "SlideDrop.Treeview.Heading",
            background="#202b40",
            foreground="#d8e4f3",
            borderwidth=0,
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "SlideDrop.Treeview",
            background=[("selected", "#263c66")],
            foreground=[("selected", "#f8fbff")],
        )

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=56, pady=(16, 6), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="SlideDrop",
            font=ctk.CTkFont(size=30, weight="bold"),
        ).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            header,
            text="Convert PowerPoint files to PDF locally with LibreOffice.",
            text_color="#cbd5e1",
        ).grid(row=1, column=0, sticky="ew", pady=(2, 0))

        self.drop_zone = DropZone(self, self.add_paths, self.select_files, self.select_folder)
        self.drop_zone.grid(row=1, column=0, padx=56, pady=(4, 10), sticky="ew")

        self.list_panel = ctk.CTkFrame(
            self,
            corner_radius=18,
            fg_color="#182235",
            border_width=1,
            border_color="#263244",
        )
        self.list_panel.grid(row=2, column=0, padx=56, pady=8, sticky="nsew")
        self.list_panel.grid_columnconfigure(0, weight=1)
        self.list_panel.grid_rowconfigure(2, weight=1)

        queue_header = ctk.CTkFrame(self.list_panel, fg_color="transparent")
        queue_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        queue_header.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            queue_header,
            text="Step 2  Review queue",
            text_color="#93c5fd",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(queue_header, textvariable=self.file_count_var, text_color="#cbd5e1").grid(
            row=0, column=1, padx=12, sticky="w"
        )
        self.remove_button = ctk.CTkButton(
            queue_header,
            text="Remove Selected",
            width=126,
            command=self.remove_selected,
            fg_color="#1f2937",
            hover_color="#334155",
        )
        self.remove_button.grid(row=0, column=2, padx=(8, 6))
        self.clear_button = ctk.CTkButton(
            queue_header,
            text="Clear List",
            width=90,
            command=self.clear_list,
            fg_color="#1f2937",
            hover_color="#334155",
        )
        self.clear_button.grid(row=0, column=3)

        self.queue_body = ctk.CTkFrame(self.list_panel, fg_color="#141d2e", corner_radius=14)
        self.queue_body.grid(row=2, column=0, padx=16, pady=(0, 16), sticky="nsew")
        self.queue_body.grid_columnconfigure(0, weight=1)
        self.queue_body.grid_rowconfigure(0, weight=1)

        self.empty_queue_frame = ctk.CTkFrame(self.queue_body, fg_color="transparent")
        self.empty_queue_frame.grid(row=0, column=0, sticky="nsew")
        self.empty_queue_frame.grid_columnconfigure(0, weight=1)
        self.empty_queue_frame.grid_rowconfigure(0, weight=1)
        self.empty_queue_frame.grid_rowconfigure(4, weight=1)
        ctk.CTkLabel(
            self.empty_queue_frame,
            text="Ready for files",
            text_color="#3b82f6",
            font=ctk.CTkFont(size=17, weight="bold"),
        ).grid(row=1, column=0, pady=(0, 4), sticky="s")
        ctk.CTkLabel(
            self.empty_queue_frame,
            text="No files added yet",
            text_color="#b6c2d2",
            font=ctk.CTkFont(size=14),
        ).grid(row=2, column=0, pady=(0, 2))
        ctk.CTkLabel(
            self.empty_queue_frame,
            text="Use Select PowerPoint Files above to begin.",
            text_color="#94a3b8",
        ).grid(row=3, column=0, pady=(0, 0), sticky="n")

        self.tree_frame = ctk.CTkFrame(self.queue_body, fg_color="transparent")
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.queue_tree = ttk.Treeview(
            self.tree_frame,
            columns=("selected", "file", "folder", "status"),
            show="headings",
            selectmode="extended",
            style="SlideDrop.Treeview",
        )
        self.queue_tree.heading("selected", text="")
        self.queue_tree.heading("file", text="File name")
        self.queue_tree.heading("folder", text="Folder")
        self.queue_tree.heading("status", text="Status")
        self.queue_tree.column("selected", width=44, minwidth=44, stretch=False, anchor="center")
        self.queue_tree.column("file", width=280, minwidth=180, stretch=True, anchor="w")
        self.queue_tree.column("folder", width=320, minwidth=160, stretch=True, anchor="w")
        self.queue_tree.column("status", width=110, minwidth=90, stretch=False, anchor="center")
        self.queue_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.queue_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.queue_tree.configure(yscrollcommand=scrollbar.set)
        self.queue_tree.bind("<Button-1>", self._handle_tree_click)
        self.queue_tree.bind("<Double-Button-1>", self._handle_tree_double_click)
        self.queue_tree.bind("<Button-3>", self._handle_tree_context_menu)
        for status, color in TREE_STATUS_COLORS.items():
            self.queue_tree.tag_configure(status.value, foreground=color)
        self.queue_tree.tag_configure("checked", background="#223657")

        convert_card = ctk.CTkFrame(
            self,
            corner_radius=18,
            fg_color="#182235",
            border_width=1,
            border_color="#263244",
        )
        convert_card.grid(row=3, column=0, padx=56, pady=(8, 10), sticky="ew")
        convert_card.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(
            convert_card,
            text="Step 3  Convert",
            text_color="#93c5fd",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")
        ctk.CTkLabel(convert_card, textvariable=self.summary_var, text_color="#cbd5e1").grid(
            row=0, column=1, padx=8, pady=(12, 4), sticky="w"
        )
        self.progress = ctk.CTkProgressBar(convert_card)
        self.progress.grid(row=1, column=0, columnspan=2, padx=16, pady=(4, 12), sticky="ew")
        self.progress.set(0)
        self.progress.grid_remove()
        options = ctk.CTkFrame(convert_card, fg_color="transparent")
        options.grid(row=2, column=0, columnspan=2, padx=16, pady=(0, 12), sticky="ew")
        options.grid_columnconfigure(2, weight=1)
        ctk.CTkCheckBox(
            options,
            text="High Quality PDF (experimental)",
            variable=self.high_quality_var,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            border_color="#3b82f6",
            checkmark_color="#ffffff",
        ).grid(row=0, column=0, padx=(0, 16), sticky="w")
        ctk.CTkCheckBox(
            options,
            text="Open output when finished",
            variable=self.open_output_var,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            border_color="#3b82f6",
            checkmark_color="#ffffff",
        ).grid(row=0, column=1, sticky="w")
        self.convert_button = ctk.CTkButton(
            options,
            text="Convert to PDF",
            width=180,
            height=40,
            command=self.start_conversion,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            font=ctk.CTkFont(weight="bold"),
        )
        self.convert_button.grid(row=0, column=3, sticky="e")

        self.success_card = ctk.CTkFrame(self, corner_radius=14, fg_color="#052e1a")
        self.success_card.grid(row=4, column=0, padx=56, pady=(0, 8), sticky="ew")
        self.success_card.grid_columnconfigure(0, weight=1)
        self.success_label = ctk.CTkLabel(self.success_card, text="", text_color="#dcfce7")
        self.success_label.grid(row=0, column=0, padx=14, pady=10, sticky="w")
        ctk.CTkButton(
            self.success_card,
            text="Open Output Folder",
            width=150,
            command=self.open_output_folder,
            fg_color="#166534",
            hover_color="#15803d",
        ).grid(row=0, column=1, padx=14, pady=10)
        self.success_card.grid_remove()

        details_bar = ctk.CTkFrame(self, fg_color="transparent")
        details_bar.grid(row=5, column=0, padx=56, pady=(4, 18), sticky="ew")
        details_bar.grid_columnconfigure(1, weight=1)
        self.details_button = ctk.CTkButton(
            details_bar,
            text="Show logs",
            width=100,
            command=self.toggle_logs,
            fg_color="#1f2937",
            hover_color="#334155",
        )
        self.details_button.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            details_bar,
            text="PDF keeps static slide visuals, but not animations, transitions, audio, or video interactivity.",
            text_color="#94a3b8",
        ).grid(
            row=0, column=1, padx=10, sticky="w"
        )

        self.log_box = ctk.CTkTextbox(self, height=140)
        self.log_box.grid(row=6, column=0, padx=56, pady=(0, 24), sticky="ew")
        self.log_box.grid_remove()
        self.log("SlideDrop ready.")
        if not DND_AVAILABLE:
            self.log("Drag-and-drop package is unavailable. Manual selection still works.")

    def _build_context_menu(self) -> None:
        self.context_menu = tk.Menu(self, tearoff=False)
        self.context_menu.add_command(label="Open Source File", command=self.open_selected_source)
        self.context_menu.add_command(label="Open PDF", command=self.open_selected_pdf)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Remove from Queue", command=self.remove_selected)

    def toggle_logs(self) -> None:
        self.logs_visible = not self.logs_visible
        if self.logs_visible:
            self.log_box.grid()
            self.details_button.configure(text="Hide logs")
        else:
            self.log_box.grid_remove()
            self.details_button.configure(text="Show logs")

    def select_files(self) -> None:
        initialdir = str(self.settings.last_used_folder) if self.settings.last_used_folder else None
        files = filedialog.askopenfilenames(
            title="Select PowerPoint files",
            initialdir=initialdir,
            filetypes=[("PowerPoint files", "*.ppt *.pptx"), ("All files", "*.*")],
        )
        if files:
            self.settings.last_used_folder = Path(files[0]).parent
            self.add_paths([Path(file) for file in files])

    def select_folder(self) -> None:
        initialdir = str(self.settings.last_used_folder) if self.settings.last_used_folder else None
        folder = filedialog.askdirectory(title="Select a folder to scan", initialdir=initialdir)
        if folder:
            self.settings.last_used_folder = Path(folder)
            self.add_paths([Path(folder)])

    def add_paths(self, paths: list[Path]) -> None:
        added = self.manager.add_paths(paths)
        for item in added:
            self._add_row(item)
        if added:
            self.log(f"Added {len(added)} file(s).")
        else:
            self.log("No new PowerPoint files found.")
        self._update_counts()
        self._update_empty_state()
        self.drop_zone.set_compact(bool(self.manager.items))

    def _add_row(self, item: QueueItem) -> None:
        self.queue_tree.insert(
            "",
            "end",
            iid=item.item_id,
            values=("[ ]", item.file_name, self._display_folder(item.source_path.parent), item.status.value),
            tags=(item.status.value,),
        )
        self._update_row_status(item)

    def _display_folder(self, folder: Path) -> str:
        parent = str(folder)
        if len(parent) <= 54:
            return parent
        return f"...{parent[-51:]}"

    def _toggle_row_selection(self, item_id: str) -> None:
        if not self.queue_tree.exists(item_id):
            return
        if item_id in self.selected_ids:
            self.selected_ids.remove(item_id)
        else:
            self.selected_ids.add(item_id)
        self._refresh_selection_styles()

    def _handle_tree_click(self, event) -> None:
        item_id = self.queue_tree.identify_row(event.y)
        if not item_id:
            return
        self.queue_tree.selection_set(item_id)
        column = self.queue_tree.identify_column(event.x)
        if column in {"#1", "#2"}:
            self._toggle_row_selection(item_id)
            return "break"
        return None

    def _handle_tree_double_click(self, event) -> None:
        item_id = self.queue_tree.identify_row(event.y)
        if item_id:
            self.open_pdf_by_id(item_id)

    def _handle_tree_context_menu(self, event) -> None:
        item_id = self.queue_tree.identify_row(event.y)
        if not item_id:
            return
        self.selected_ids = {item_id}
        self.queue_tree.selection_set(item_id)
        self._refresh_selection_styles()
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def _refresh_selection_styles(self) -> None:
        for item_id in self.queue_tree.get_children():
            item = next((queued for queued in self.manager.items if queued.item_id == item_id), None)
            if item is None:
                continue
            selected = item_id in self.selected_ids
            tags = [item.status.value]
            if selected:
                tags.append("checked")
            self.queue_tree.item(item_id, values=("[x]" if selected else "[ ]", item.file_name, self._display_folder(item.source_path.parent), item.status.value), tags=tuple(tags))
        self._update_action_states()

    def _update_row_status(self, item: QueueItem) -> None:
        if not self.queue_tree.exists(item.item_id):
            return
        selected = item.item_id in self.selected_ids
        tags = [item.status.value]
        if selected:
            tags.append("checked")
        self.queue_tree.item(
            item.item_id,
            values=("[x]" if selected else "[ ]", item.file_name, self._display_folder(item.source_path.parent), item.status.value),
            tags=tuple(tags),
        )

    def start_conversion(self) -> None:
        if self.worker and self.worker.is_running:
            messagebox.showinfo(APP_NAME, "A conversion is already running.")
            return

        items = self.manager.convertable_items()
        if not items:
            messagebox.showinfo(APP_NAME, "Add PowerPoint files before converting.")
            return

        valid, message = self.converter.validate()
        if not valid:
            messagebox.showerror(APP_NAME, message)
            self.log(message)
            return

        proceed = messagebox.askokcancel(
            APP_NAME,
            "Missing fonts on this PC may cause layout changes or font substitution in the PDF.\n\n"
            "PDF output is static and does not preserve animations, transitions, audio, or video interactivity.\n\n"
            "Continue conversion?",
        )
        if not proceed:
            self.log("Conversion cancelled before start.")
            return

        self.settings.high_quality_pdf = self.high_quality_var.get()
        self.settings.open_output_when_finished = self.open_output_var.get()
        if self.settings.high_quality_pdf:
            self.log("High Quality PDF is experimental in v1; using the reliable LibreOffice default export path.")

        self._show_progress()
        self.progress.set(0)
        self.summary_var.set("Converting...")
        self.success_card.grid_remove()
        self._update_action_states(is_converting=True)
        self.worker = ConversionWorker(
            items=items,
            converter=self.converter,
            high_quality=self.settings.high_quality_pdf,
            on_progress=lambda item, current, total: self.event_queue.put(("progress", (item, current, total))),
            on_log=lambda text: self.event_queue.put(("log", text)),
            on_done=lambda success, failed: self.event_queue.put(("done", (success, failed))),
        )
        self.worker.start()

    def _process_worker_events(self) -> None:
        try:
            while True:
                event, payload = self.event_queue.get_nowait()
                if event == "progress":
                    item, current, total = payload
                    self._update_row_status(item)
                    self.progress.set(current / total if total else 0)
                elif event == "log":
                    self.log(str(payload))
                elif event == "done":
                    success, failed = payload
                    self.summary_var.set(f"Done: {success} succeeded, {failed} failed")
                    self.log(f"Batch complete. Success: {success}. Failed: {failed}.")
                    self.progress.set(1)
                    if success:
                        self.success_label.configure(text=f"Conversion complete: {success} PDF file(s) created.")
                        self.success_card.grid()
                    self._update_counts()
                    self._update_action_states(is_converting=False)
                    if self.settings.open_output_when_finished:
                        self.open_output_folder()
        except queue.Empty:
            pass
        delay_ms = 80 if self.worker and self.worker.is_running else 250
        self.after(delay_ms, self._process_worker_events)

    def remove_selected(self) -> None:
        if not self.selected_ids:
            return
        removed = self.manager.remove_ids(self.selected_ids)
        for item in removed:
            if self.queue_tree.exists(item.item_id):
                self.queue_tree.delete(item.item_id)
        self.selected_ids.clear()
        self._update_counts()
        self._update_empty_state()
        self.drop_zone.set_compact(bool(self.manager.items))
        self._update_action_states()
        self.log(f"Removed {len(removed)} file(s).")

    def clear_list(self) -> None:
        if self.worker and self.worker.is_running:
            messagebox.showinfo(APP_NAME, "Wait for the current conversion to finish before clearing.")
            return
        self.manager.clear()
        for item_id in self.queue_tree.get_children():
            self.queue_tree.delete(item_id)
        self.selected_ids.clear()
        self.progress.set(0)
        self._hide_progress()
        self.summary_var.set("Ready")
        self.success_card.grid_remove()
        self._update_counts()
        self._update_empty_state()
        self.drop_zone.set_compact(False)
        self._update_action_states()
        self.log("Queue cleared.")

    def _update_counts(self) -> None:
        total = len(self.manager.items)
        done = sum(1 for item in self.manager.items if item.status == FileStatus.DONE)
        failed = sum(1 for item in self.manager.items if item.status == FileStatus.FAILED)
        self.file_count_var.set(f"{total} file{'s' if total != 1 else ''} queued")
        if total:
            self.summary_var.set(f"{done} done, {failed} failed")
        else:
            self.summary_var.set("Ready")
        self._update_action_states()

    def _update_action_states(self, is_converting: bool | None = None) -> None:
        if is_converting is None:
            is_converting = self.worker is not None and self.worker.is_running
        has_items = bool(self.manager.items)
        has_selection = bool(self.selected_ids)
        has_convertable = bool(self.manager.convertable_items())

        if hasattr(self, "convert_button"):
            self.convert_button.configure(state="disabled" if is_converting or not has_convertable else "normal")
        if hasattr(self, "remove_button"):
            self.remove_button.configure(state="disabled" if is_converting or not has_selection else "normal")
        if hasattr(self, "clear_button"):
            self.clear_button.configure(state="disabled" if is_converting or not has_items else "normal")

    def _update_empty_state(self) -> None:
        if self.manager.items:
            self.empty_queue_frame.grid_remove()
            self.tree_frame.grid(row=0, column=0, sticky="nsew")
        else:
            self.tree_frame.grid_remove()
            self.empty_queue_frame.grid(row=0, column=0, sticky="nsew")

    def _show_progress(self) -> None:
        if self.progress_visible:
            return
        self.progress.grid()
        self.progress_visible = True

    def _hide_progress(self) -> None:
        if not self.progress_visible:
            return
        self.progress.grid_remove()
        self.progress_visible = False

    def log(self, text: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{timestamp}] {text}\n")
        self.log_box.see("end")

    def _selected_item(self) -> QueueItem | None:
        selected_id = next(iter(self.selected_ids), None)
        if not selected_id:
            return None
        return next((item for item in self.manager.items if item.item_id == selected_id), None)

    def open_selected_source(self) -> None:
        item = self._selected_item()
        if item:
            self._open_path(item.source_path)

    def open_selected_pdf(self) -> None:
        item = self._selected_item()
        if item and item.output_pdf:
            self._open_path(item.output_pdf)

    def open_pdf_by_id(self, item_id: str) -> None:
        item = next((queued for queued in self.manager.items if queued.item_id == item_id), None)
        if item and item.output_pdf and item.output_pdf.exists():
            self._open_path(item.output_pdf)

    def open_output_folder(self) -> None:
        folder = self.manager.first_output_dir()
        if not folder:
            messagebox.showinfo(APP_NAME, "No output folder is available yet.")
            return
        folder.mkdir(parents=True, exist_ok=True)
        self._open_path(folder)

    def _open_path(self, path: Path) -> None:
        try:
            os.startfile(path)  # type: ignore[attr-defined]
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"Could not open {path}: {exc}")
