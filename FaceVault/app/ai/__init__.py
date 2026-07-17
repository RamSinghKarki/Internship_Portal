import cv2

# Silence OpenCV's internal backend warnings (cosmetic, per-model-load).
try:
    cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)
except AttributeError:
    pass
