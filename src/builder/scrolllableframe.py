import platform
import tkinter as tk
from tkinter import ttk


class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
        "<Configure>",
        lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        system = platform.system().lower()
        print(f"On platform {system}")
        if system == "darwin":
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_mac)
        elif system == "linux" or system == "linux2":
            self.canvas.bind_all("<Button-4>", self._scroll_down_linux)
            self.canvas.bind_all("<Button-5>", self._scroll_up_linux)
        else:
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_windows)
        print("Event binded")

    def _on_mousewheel_mac(self, event):
        self.canvas.yview_scroll(int(-1.0 * event.delta), "units")

    def _on_mousewheel_windows(self, event):
        self.canvas.yview_scroll(int(-1.0 * event.delta / 120.0), "units")

    # See alessandro's comment on the accepted answer
    # https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar
    # event.delta comes up as 0 on linux
    def _scroll_up_linux(self, event):
        self.canvas.yview_scroll(1, "units")

    def _scroll_down_linux(self, event):
        self.canvas.yview_scroll(-1, "units")







#
# Usage Example
#
if __name__ == "__main__":
    root = tk.Tk()

    frame = ScrollableFrame(root)

    for i in range(50):
        btn = tk.Button(frame.scrollable_frame, text=f"{i+1}")
        btn.pack()

    frame.pack()
    root.mainloop()

