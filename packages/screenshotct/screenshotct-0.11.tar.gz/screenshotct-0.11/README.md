# Screenshot with ctypes

## Tested against Windows 10 / Python 3.11 / Anaconda

### pip install screenshotct

```PY
import cv2
from screenshotct import take_screenshot
import time
from ctypes_window_info import get_window_infos

for q in get_window_infos():
    print(q)

# hwnd
ir = take_screenshot(
    hwnd=2100816,
    crop=(0, 0, 0, 100),
    show_fps=True,
    brg_to_rgb=False,
    ignore_exceptions=True,
    client=True,
)

# first screen
# ir = take_screenshot(
#     hwnd='0',
#     crop=(0, 0, 0, 100),
#     show_fps=True,
#     brg_to_rgb=False,
#     ignore_exceptions=True,
#     client=True,
# )

# all screens
# ir = take_screenshot(
#     hwnd="all",
#     crop=(0, 0, 0, 100),
#     show_fps=True,
#     brg_to_rgb=False,
#     ignore_exceptions=True,
#     client=True,
# )

fps = 0
last_time = time.time()
for _ in range(1000):
    try:
        pic = next(ir)
        fps += 1
        cv2.imshow("pic", pic[0])
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    except Exception as e:
        print(e)
print(f"\n\n\n{fps / (time.time() - last_time)}\n")
cv2.destroyAllWindows()
```