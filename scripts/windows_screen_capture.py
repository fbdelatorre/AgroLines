"""Native Windows desktop pixels only. No widget rendering or image composition."""

import ctypes
import os
from ctypes import wintypes as W


class Rect(ctypes.Structure):
    _fields_ = [(name, W.LONG) for name in ("left", "top", "right", "bottom")]


class Monitor(ctypes.Structure):
    _fields_ = [("size", W.DWORD), ("bounds", Rect), ("work", Rect), ("flags", W.DWORD)]


class BitmapInfo(ctypes.Structure):
    _fields_ = [
        ("size", W.DWORD),
        ("width", W.LONG),
        ("height", W.LONG),
        ("planes", W.WORD),
        ("bit_count", W.WORD),
        ("compression", W.DWORD),
        ("size_image", W.DWORD),
        ("xppm", W.LONG),
        ("yppm", W.LONG),
        ("colors_used", W.DWORD),
        ("colors_important", W.DWORD),
    ]


class NativeDesktop:
    def __init__(self):
        self.user = ctypes.WinDLL("user32", use_last_error=True)
        self.gdi = ctypes.WinDLL("gdi32", use_last_error=True)
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.wts = ctypes.WinDLL("wtsapi32", use_last_error=True)
        signatures = [
            (self.kernel, "ProcessIdToSessionId", [W.DWORD, ctypes.POINTER(W.DWORD)], W.BOOL),
            (self.kernel, "GetCurrentThreadId", [], W.DWORD),
            (self.user, "OpenInputDesktop", [W.DWORD, W.BOOL, W.DWORD], W.HANDLE),
            (self.user, "CloseDesktop", [W.HANDLE], W.BOOL),
            (self.user, "GetThreadDesktop", [W.DWORD], W.HANDLE),
            (
                self.user,
                "GetUserObjectInformationW",
                [W.HANDLE, ctypes.c_int, W.LPVOID, W.DWORD, ctypes.POINTER(W.DWORD)],
                W.BOOL,
            ),
            (self.user, "GetForegroundWindow", [], W.HWND),
            (self.user, "GetWindowThreadProcessId", [W.HWND, ctypes.POINTER(W.DWORD)], W.DWORD),
            (self.user, "GetWindowRect", [W.HWND, ctypes.POINTER(Rect)], W.BOOL),
            (self.user, "IsWindowVisible", [W.HWND], W.BOOL),
            (self.user, "IsIconic", [W.HWND], W.BOOL),
            (self.user, "MonitorFromWindow", [W.HWND, W.DWORD], W.HANDLE),
            (self.user, "GetMonitorInfoW", [W.HANDLE, ctypes.POINTER(Monitor)], W.BOOL),
            (self.user, "GetWindowTextW", [W.HWND, W.LPWSTR, ctypes.c_int], ctypes.c_int),
            (self.user, "PostMessageW", [W.HWND, W.UINT, W.WPARAM, W.LPARAM], W.BOOL),
            (self.user, "GetDC", [W.HWND], W.HDC),
            (self.user, "ReleaseDC", [W.HWND, W.HDC], ctypes.c_int),
            (self.gdi, "CreateCompatibleDC", [W.HDC], W.HDC),
            (self.gdi, "CreateCompatibleBitmap", [W.HDC, ctypes.c_int, ctypes.c_int], W.HANDLE),
            (self.gdi, "SelectObject", [W.HDC, W.HANDLE], W.HANDLE),
            (
                self.gdi,
                "BitBlt",
                [
                    W.HDC,
                    ctypes.c_int,
                    ctypes.c_int,
                    ctypes.c_int,
                    ctypes.c_int,
                    W.HDC,
                    ctypes.c_int,
                    ctypes.c_int,
                    W.DWORD,
                ],
                W.BOOL,
            ),
            (
                self.gdi,
                "GetDIBits",
                [W.HDC, W.HANDLE, W.UINT, W.UINT, W.LPVOID, ctypes.POINTER(BitmapInfo), W.UINT],
                ctypes.c_int,
            ),
            (self.gdi, "DeleteObject", [W.HANDLE], W.BOOL),
            (self.gdi, "DeleteDC", [W.HDC], W.BOOL),
            (
                self.wts,
                "WTSQuerySessionInformationW",
                [
                    W.HANDLE,
                    W.DWORD,
                    ctypes.c_int,
                    ctypes.POINTER(W.LPVOID),
                    ctypes.POINTER(W.DWORD),
                ],
                W.BOOL,
            ),
            (self.wts, "WTSFreeMemory", [W.LPVOID], None),
        ]
        for library, name, arguments, result in signatures:
            function = getattr(library, name)
            function.argtypes, function.restype = arguments, result

    def desktop_name(self, handle):
        buffer = ctypes.create_unicode_buffer(256)
        needed = W.DWORD()
        if not self.user.GetUserObjectInformationW(
            handle, 2, buffer, ctypes.sizeof(buffer), ctypes.byref(needed)
        ):
            raise RuntimeError("Não foi possível verificar o desktop.")
        return buffer.value

    def readiness(self):
        session = W.DWORD()
        if not self.kernel.ProcessIdToSessionId(os.getpid(), ctypes.byref(session)):
            raise RuntimeError("Sessão Windows não verificável.")
        pointer, count = W.LPVOID(), W.DWORD()
        if not self.wts.WTSQuerySessionInformationW(
            None, session.value, 8, ctypes.byref(pointer), ctypes.byref(count)
        ):
            raise RuntimeError("Estado interativo não verificável.")
        try:
            state = ctypes.cast(pointer, ctypes.POINTER(ctypes.c_int)).contents.value
        finally:
            self.wts.WTSFreeMemory(pointer)
        desktop = self.user.OpenInputDesktop(0, False, 1)
        if not desktop:
            raise RuntimeError("Não há desktop de entrada acessível.")
        try:
            same = self.desktop_name(desktop) == self.desktop_name(
                self.user.GetThreadDesktop(self.kernel.GetCurrentThreadId())
            )
        finally:
            self.user.CloseDesktop(desktop)
        if session.value == 0 or state != 0 or not same:
            raise RuntimeError("Exigir sessão ativa e desktop de entrada do processo.")
        return {"session_id": session.value, "session_active": True, "input_desktop_matches": same}

    def foreground(self):
        handle = self.user.GetForegroundWindow()
        owner = W.DWORD()
        self.user.GetWindowThreadProcessId(handle, ctypes.byref(owner))
        title = ctypes.create_unicode_buffer(256)
        self.user.GetWindowTextW(handle, title, len(title))
        return handle, owner.value, title.value

    def capture(self, main_handle, output):
        from PySide6.QtGui import QImage

        readiness = self.readiness()
        foreground, owner, _ = self.foreground()
        if owner != os.getpid() or not self.user.IsWindowVisible(main_handle):
            raise RuntimeError("AgroLines não está visível/em primeiro plano.")
        if self.user.IsIconic(main_handle):
            raise RuntimeError("Janela minimizada.")
        rect = Rect()
        if not self.user.GetWindowRect(main_handle, ctypes.byref(rect)):
            raise RuntimeError("Janela nativa não verificável.")
        monitor = Monitor(size=ctypes.sizeof(Monitor))
        if not self.user.GetMonitorInfoW(
            self.user.MonitorFromWindow(main_handle, 2), ctypes.byref(monitor)
        ):
            raise RuntimeError("Monitor não verificável.")
        bounds = monitor.bounds
        if (
            rect.left < bounds.left
            or rect.top < bounds.top
            or rect.right > bounds.right
            or rect.bottom > bounds.bottom
        ):
            raise RuntimeError("Janela fora dos limites do monitor.")
        width, height = rect.right - rect.left, rect.bottom - rect.top
        if width < 1366 or height < 768:
            raise RuntimeError(f"Resolução real insuficiente: {width} × {height}.")
        screen = self.user.GetDC(None)
        memory = self.gdi.CreateCompatibleDC(screen)
        bitmap = self.gdi.CreateCompatibleBitmap(screen, width, height)
        if not screen or not memory or not bitmap:
            raise RuntimeError("Captura GDI indisponível.")
        old = self.gdi.SelectObject(memory, bitmap)
        try:
            if not self.gdi.BitBlt(
                memory, 0, 0, width, height, screen, rect.left, rect.top, 0x00CC0020 | 0x40000000
            ):
                raise RuntimeError("Captura real de tela falhou.")
            self.gdi.SelectObject(memory, old)
            info = BitmapInfo(
                size=ctypes.sizeof(BitmapInfo), width=width, height=-height, planes=1, bit_count=32
            )
            buffer = ctypes.create_string_buffer(width * height * 4)
            if (
                self.gdi.GetDIBits(screen, bitmap, 0, height, buffer, ctypes.byref(info), 0)
                != height
            ):
                raise RuntimeError("Pixels de tela incompletos.")
            image = QImage(buffer.raw, width, height, width * 4, QImage.Format_RGB32).copy()
            colors = {
                image.pixel(x, y)
                for x in range(0, width, max(width // 30, 1))
                for y in range(0, height, max(height // 30, 1))
            }
            if len(colors) < 4 or not image.save(str(output), "PNG"):
                raise RuntimeError("Captura vazia/uniforme ou PNG inválido.")
        finally:
            self.gdi.SelectObject(memory, old)
            self.gdi.DeleteObject(bitmap)
            self.gdi.DeleteDC(memory)
            self.user.ReleaseDC(None, screen)
        if output.stat().st_size >= 50_000_000:
            raise RuntimeError("PNG excede 50 MB.")
        return {
            **readiness,
            "window_hwnd": int(main_handle),
            "foreground_hwnd": int(foreground),
            "process_id": owner,
            "width": width,
            "height": height,
            "bytes": output.stat().st_size,
            "method": "Windows desktop GDI BitBlt/GetDIBits",
        }
