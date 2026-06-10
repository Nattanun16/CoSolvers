"""
Google Vision API utility — ตรวจสอบความปลอดภัยของรูปภาพก่อนบันทึก
"""
import base64
import requests
from django.conf import settings


# ระดับที่ถือว่าไม่ผ่าน
UNSAFE_LEVELS = {"LIKELY", "VERY_LIKELY"}

# ประเภทที่ตรวจสอบ และข้อความแจ้งเตือนภาษาไทย
SAFETY_CHECKS = {
    "adult":    "เนื้อหาลามกอนาจาร",
    "violence": "เนื้อหาที่มีความรุนแรง",
    "racy":     "เนื้อหาไม่เหมาะสม",
    "medical":  "เนื้อหาทางการแพทย์ที่รุนแรง",
}


def check_image_safety(image_file):
    """
    ตรวจสอบรูปภาพด้วย Google Vision API SafeSearch Detection

    Args:
        image_file: Django InMemoryUploadedFile หรือ file-like object
                    (ต้องสามารถ .read() และ .seek(0) ได้)

    Returns:
        dict:
            {
                "safe":   True | False,
                "reason": ""   | "ภาพถูกปฏิเสธ: พบ...",
                "skipped": True  # เมื่อ API key ไม่ได้ตั้งค่า — ผ่านโดยไม่ตรวจ
            }
    """
    api_key = getattr(settings, "GOOGLE_VISION_API_KEY", "")

    # ถ้ายังไม่ได้ตั้ง API key ให้ผ่านไปก่อน ไม่บล็อก user
    if not api_key or api_key.startswith("YOUR_"):
        return {"safe": True, "reason": "", "skipped": True}

    try:
        raw = image_file.read()
        image_file.seek(0)  # rewind เพื่อให้ Django บันทึกไฟล์ได้ต่อ
        image_b64 = base64.b64encode(raw).decode("utf-8")
    except Exception:
        return {"safe": True, "reason": "", "skipped": True}

    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    payload = {
        "requests": [
            {
                "image": {"content": image_b64},
                "features": [{"type": "SAFE_SEARCH_DETECTION"}],
            }
        ]
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        result = resp.json()
    except requests.RequestException:
        # ถ้า Vision API ล้มเหลว ให้ผ่านไปก่อน (ไม่บล็อก user)
        return {"safe": True, "reason": "", "skipped": True}

    annotations = (
        result.get("responses", [{}])[0].get("safeSearchAnnotation", {})
    )

    for field, label in SAFETY_CHECKS.items():
        if annotations.get(field, "UNKNOWN") in UNSAFE_LEVELS:
            return {
                "safe": False,
                "reason": f"ภาพถูกปฏิเสธ: พบ{label}",
                "skipped": False,
            }

    return {"safe": True, "reason": "", "skipped": False}
