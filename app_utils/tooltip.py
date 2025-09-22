#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具提示元件
提供滑鼠懸停時的說明功能
"""

import tkinter as tk


class ToolTip:
    """工具提示類別"""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)

    def on_enter(self, event=None):
        """滑鼠移入時顯示提示"""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # 更現代化的工具提示樣式
        label = tk.Label(self.tooltip_window, text=self.text,
                         background="#f8f9fa", foreground="#333333",
                         relief="solid", borderwidth=1,
                         font=("Segoe UI", 9), wraplength=350, justify="left",
                         padx=12, pady=8)
        label.pack()

    def on_leave(self, event=None):
        """滑鼠移出時隱藏提示"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
