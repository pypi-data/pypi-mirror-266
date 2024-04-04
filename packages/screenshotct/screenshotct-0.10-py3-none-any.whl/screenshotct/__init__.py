import ctypes as ct
import ctypes.wintypes as wintypes
import numpy as np
import time
import re
from getmonitorresolution import get_monitors_resolution

allmoni, gera = get_monitors_resolution()
monwidth = gera["width_all_monitors"]
monheight = gera["height_all_monitors"]
max_monitor_width = gera["max_monitor_width"]
min_monitor_width = gera["min_monitor_width"]
max_monitor_height = gera["max_monitor_height"]
min_monitor_height = gera["min_monitor_height"]
windll = ct.LibraryLoader(ct.WinDLL)
windll.shcore.SetProcessDpiAwareness()


HGDI_ERROR = wintypes.HANDLE(-1).value
GHND = 0x0042
GMEM_FIXED = 0x0000
GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0040
DIB_RGB_COLORS = 0
SRCCOPY = 0x00CC0020
BI_RGB = 0


class BITMAP(ct.Structure):
    _fields_ = (
        ("bmType", wintypes.LONG),
        ("bmWidth", wintypes.LONG),
        ("bmHeight", wintypes.LONG),
        ("bmWidthBytes", wintypes.LONG),
        ("bmPlanes", wintypes.WORD),
        ("bmBitsPixel", wintypes.WORD),
        ("bmBits", wintypes.LPVOID),
    )


class BITMAPFILEHEADER(ct.Structure):
    _pack_ = 2
    _fields_ = (
        ("bfType", wintypes.WORD),
        ("bfSize", wintypes.DWORD),
        ("bfReserved1", wintypes.WORD),
        ("bfReserved2", wintypes.WORD),
        ("bfOffBits", wintypes.DWORD),
    )


class BITMAPINFOHEADER(ct.Structure):
    _fields_ = (
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.biSize = ct.sizeof(self)


class RGBQUAD(ct.Structure):
    _fields_ = (
        ("rgbBlue", wintypes.BYTE),
        ("rgbGreen", wintypes.BYTE),
        ("rgbRed", wintypes.BYTE),
        ("rgbReserved", wintypes.BYTE),
    )


class BITMAPINFO(ct.Structure):
    _fields_ = (("bmiHeader", BITMAPINFOHEADER), ("bmiColors", RGBQUAD * 1))


class RECT(wintypes.RECT):
    def __eq__(self, other):
        return bytes(self) == bytes(other)


LPBITMAPINFO = ct.POINTER(BITMAPINFO)
SIZE_T = ct.c_size_t

kernel32 = windll.kernel32
GlobalAlloc = kernel32.GlobalAlloc
GlobalAlloc.argtypes = wintypes.UINT, SIZE_T
GlobalAlloc.restype = wintypes.HGLOBAL
GlobalLock = kernel32.GlobalLock
GlobalLock.argtypes = (wintypes.HGLOBAL,)
GlobalLock.restype = wintypes.LPVOID
GlobalFree = kernel32.GlobalFree
GlobalFree.argtypes = (wintypes.HGLOBAL,)
GlobalFree.restype = wintypes.HGLOBAL
GlobalUnlock = kernel32.GlobalUnlock
GlobalUnlock.argtypes = (wintypes.HGLOBAL,)
GlobalUnlock.restype = wintypes.BOOL
user32 = windll.user32
GetDesktopWindow = user32.GetDesktopWindow
GetDesktopWindow.argtypes = ()
GetDesktopWindow.restype = wintypes.HWND
GetWindowDC = user32.GetWindowDC
GetWindowDC.argtypes = (wintypes.HWND,)
GetWindowDC.restype = wintypes.HDC
GetWindowRect = user32.GetWindowRect
GetWindowRect.argtypes = wintypes.HWND, wintypes.LPRECT
GetWindowRect.restype = wintypes.BOOL
ReleaseDC = user32.ReleaseDC
ReleaseDC.argtypes = wintypes.HWND, wintypes.HDC
ReleaseDC.restype = ct.c_int
GetClientRect = user32.GetClientRect
gdi32 = windll.gdi32
CreateCompatibleDC = gdi32.CreateCompatibleDC
CreateCompatibleDC.argtypes = (wintypes.HDC,)
CreateCompatibleDC.restype = wintypes.HDC
CreateCompatibleBitmap = gdi32.CreateCompatibleBitmap
CreateCompatibleBitmap.argtypes = wintypes.HDC, ct.c_int, ct.c_int
CreateCompatibleBitmap.restype = wintypes.HBITMAP
SelectObject = gdi32.SelectObject
SelectObject.argtypes = wintypes.HDC, wintypes.HGDIOBJ
SelectObject.restype = wintypes.HGDIOBJ
BitBlt = gdi32.BitBlt
BitBlt.argtypes = (
    wintypes.HDC,
    ct.c_int,
    ct.c_int,
    ct.c_int,
    ct.c_int,
    wintypes.HDC,
    ct.c_int,
    ct.c_int,
    wintypes.DWORD,
)
BitBlt.restype = wintypes.BOOL
CreateDCW = windll.gdi32.CreateDCW
DeleteDC = gdi32.DeleteDC
DeleteDC.argtypes = (wintypes.HDC,)
DeleteDC.restype = wintypes.BOOL
DeleteObject = gdi32.DeleteObject
DeleteObject.argtypes = (wintypes.HGDIOBJ,)
DeleteObject.restype = wintypes.BOOL
GetObject = gdi32.GetObjectW
GetObject.argtypes = wintypes.HANDLE, ct.c_int, wintypes.LPVOID
GetObject.restype = ct.c_int
GetDIBits = gdi32.GetDIBits
GetDIBits.argtypes = wintypes.HDC, wintypes.HBITMAP, wintypes.UINT, wintypes.UINT, wintypes.LPVOID, LPBITMAPINFO, wintypes.UINT
GetDIBits.restype = ct.c_int


def take_screenshot(
    hwnd=0,
    crop=(0, 0, 0, 0),
    show_fps=False,
    brg_to_rgb=False,
    ignore_exceptions=True,
    client=False,
):
    r = RECT()

    if isinstance(hwnd, int):
        wDC = GetWindowDC(hwnd)
        if client:
            GetClientRect(hwnd, ct.byref(r))
        else:
            GetWindowRect(hwnd, ct.byref(r))
    elif isinstance(hwnd, str):
        if hwnd == "all":
            wDC = CreateDCW("DISPLAY", None, None, None)
            r.right = monwidth
            r.left = 0
            r.top = 0
            r.bottom = max_monitor_height
        if re.match(r"^\d+$", hwnd):
            monitor = int(hwnd)
            wDC = CreateDCW(allmoni[monitor]["DeviceName"], None, None, None)
            r.right = allmoni[monitor]["width"]
            r.left = 0
            r.top = 0
            r.bottom = allmoni[monitor]["height"]
    cDC = CreateCompatibleDC(wDC)
    y0: int = crop[1]
    x1: int = crop[2]
    x0: int = crop[0]
    y1: int = crop[3]
    a = np.array([], dtype=np.uint8)
    dataBitMap = CreateCompatibleBitmap(wDC, r.right, r.bottom)

    def saveBitmap(
        w,
        h,
        wDC,
        dataBitMap,
    ):
        nonlocal a
        bmpScreen = BITMAP()
        GetObject(dataBitMap, ct.sizeof(BITMAP), ct.byref(bmpScreen))
        bi = BITMAPINFOHEADER()
        bi.biSize = ct.sizeof(bi)
        bi.biWidth = bmpScreen.bmWidth
        bi.biHeight = -bmpScreen.bmHeight
        bi.biPlanes = 1
        bi.biBitCount = 32
        bi.biCompression = BI_RGB
        dwBmpSize = (
            ((bmpScreen.bmWidth * bi.biBitCount + 31) // 32) * 4 * bmpScreen.bmHeight
        )
        hDIB = GlobalAlloc(GHND, dwBmpSize)
        try:
            lpbitmap = GlobalLock(hDIB)
            try:
                GetDIBits(
                    wDC,
                    dataBitMap,
                    0,
                    bmpScreen.bmHeight,
                    lpbitmap,
                    ct.cast(ct.byref(bi), LPBITMAPINFO),
                    DIB_RGB_COLORS,
                )
                imi = ct.string_at(lpbitmap, dwBmpSize)
                a = np.frombuffer(imi, dtype=np.uint8).reshape((h, w, 4))[..., :3]
            finally:
                GlobalUnlock(hDIB)
        finally:
            GlobalFree(hDIB)

    def screenshot():
        nonlocal a, dataBitMap, r
        winrec = (-1, -1, -1, -1)
        new_offset_left = -1
        new_offset_top = -1
        new_w = -1
        new_h = -1
        new_end_x = -1
        new_end_y = -1
        if isinstance(hwnd, int):
            old_right = r.right
            old_left = r.left
            old_top = r.top
            old_bottom = r.bottom
            if client:
                GetClientRect(hwnd, ct.byref(r))
            else:
                GetWindowRect(hwnd, ct.byref(r))
            if (
                old_right != r.right
                or old_left != r.left
                or old_top != r.top
                or old_bottom != r.bottom
            ):
                try:
                    DeleteObject(dataBitMap)
                except Exception:
                    pass
                dataBitMap = CreateCompatibleBitmap(wDC, r.right, r.bottom)
        width = r.right - r.left
        height = r.bottom - r.top
        offset_y = r.top
        offset_x = r.left
        try:
            orig = SelectObject(cDC, dataBitMap)
            try:
                BitBlt(cDC, 0, 0, width, height, wDC, 0, 0, SRCCOPY)
                saveBitmap(
                    width,
                    height,
                    wDC,
                    dataBitMap,
                )
                new_h = a.shape[0] - y0 - y1
                new_w = a.shape[1] - x0 - x1
                new_offset_top = offset_y + y0
                new_offset_left = offset_x + x0
                new_end_x = new_offset_left + new_w
                new_end_y = new_offset_top + new_h
                if sum(crop) != 0:
                    a = a[y0:new_end_y, x0:new_end_x]
                winrec = (r.left, r.top, r.right, r.bottom)
            finally:
                try:
                    SelectObject(cDC, orig)
                except Exception:
                    pass
        finally:
            pass
        return [
            winrec,
            new_offset_left,
            new_offset_top,
            new_w,
            new_h,
            new_end_x,
            new_end_y,
        ]

    try:
        while True:
            try:
                if show_fps:
                    loop_time = time.time()

                resus = screenshot()
                yield [a, *resus]

                if show_fps:
                    print(
                        "FPS {}            ".format(1 / (time.time() - loop_time)),
                        end="\r",
                    )

            except Exception as e:
                if not ignore_exceptions:
                    raise e
                else:
                    print(e)
    except KeyboardInterrupt:
        try:
            time.sleep(1)
        except:
            pass

    finally:
        try:
            DeleteObject(dataBitMap)
        except Exception:
            pass
        try:
            DeleteDC(cDC)
        except Exception:
            pass
        try:
            ReleaseDC(hwnd, wDC)
        except Exception:
            pass

    return [np.array([], dtype=np.uint8), (-1, -1, -1, -1), -1, -1, -1, -1]


__all__ = ["take_screenshot"]
