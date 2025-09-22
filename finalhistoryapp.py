import time
import json
import textwrap
from threading import Thread
from queue import Queue, Empty

import torch
import clip
from PIL import Image
import cv2
import wikipedia
import streamlit as st

# ---------- CONFIG ----------
LANDMARKS_JSON = "landmarks.json"   # path to your JSON file
MODEL_NAME = "ViT-B/32"             # CLIP model
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
THROTTLE_SEC = 2.0                  # seconds between CLIP inferences
SIMILARITY_THRESHOLD = 22.0         # higher threshold = stricter detection
FONT = cv2.FONT_HERSHEY_SIMPLEX
# ----------------------------

def load_landmarks(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    names = list(data.keys())
    descs = data  # dict name->desc
    return names, descs

def wrap_text(text, width=40):
    return "\n".join(textwrap.wrap(text, width=width))

def overlay_multiline_text(frame, text, x, y, line_height=20, font_scale=0.6, thickness=1):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        y_pos = y + i * line_height
        cv2.putText(frame, line, (x, y_pos), FONT, font_scale, (255,255,255), thickness+2, cv2.LINE_AA)
        cv2.putText(frame, line, (x, y_pos), FONT, font_scale, (0,120,180), thickness, cv2.LINE_AA)

def clip_worker(in_q: Queue, out_q: Queue, model, preprocess, text_embeddings, landmark_names, device):
    while True:
        item = in_q.get()
        if item is None:
            break
        pil_img = item
        try:
            image_input = preprocess(pil_img).unsqueeze(0).to(device)
            with torch.no_grad():
                image_emb = model.encode_image(image_input)
                image_emb = image_emb / image_emb.norm(dim=-1, keepdim=True)
                text_emb_norm = text_embeddings / text_embeddings.norm(dim=-1, keepdim=True)
                sims = (100.0 * image_emb @ text_emb_norm.T).squeeze(0)
                top_val, top_idx = sims.topk(1)
                score = top_val.item()
                name = landmark_names[top_idx.item()]
                out_q.put((name, score))
        except Exception:
            out_q.put((None, None))

# ---------------- FUNCTION ----------------
def clip_landmark_detector():
    #st.title("🗺️ Live CLIP Landmark Detector")
    #st.markdown("Detect landmarks from webcam using CLIP + Streamlit.")
    st.markdown("<h1 style='text-align:center; color:#2c3e50;'>🗺️ Live CLIP Landmark Detector</h1>", unsafe_allow_html=True)



    start_button = st.button("Start Webcam")
    if not start_button:
        st.info("👆 Click the button above to start the webcam.")
        st.stop()

    stframe = st.empty()
    st.info("📷 Starting webcam... Please wait...")

    # Load landmarks data
    landmark_names, landmark_descs = load_landmarks(LANDMARKS_JSON)

    # Load CLIP model
    model, preprocess = clip.load(MODEL_NAME, device=DEVICE)
    model.eval()

    with torch.no_grad():
        text_tokens = clip.tokenize(landmark_names).to(DEVICE)
        text_embeddings = model.encode_text(text_tokens)

    in_q = Queue(maxsize=1)
    out_q = Queue(maxsize=1)

    worker = Thread(target=clip_worker, args=(in_q, out_q, model, preprocess, text_embeddings, landmark_names, DEVICE), daemon=True)
    worker.start()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("❌ Could not open webcam.")
        return

    # Clear waiting message
    st.empty()

    last_infer_time = 0
    last_detected = None
    last_score = 0.0
    wiki_cache = {}
    show_wiki = True

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue

        now = time.time()
        if now - last_infer_time >= THROTTLE_SEC:
            last_infer_time = now
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb)
            try:
                in_q.put_nowait(pil_img)
            except:
                pass

        try:
            detected_name, score = out_q.get_nowait()
            if detected_name is not None:
                if score >= SIMILARITY_THRESHOLD:
                    last_detected = detected_name
                    last_score = score
                    if show_wiki and detected_name not in wiki_cache:
                        try:
                            summary = wikipedia.summary(detected_name, sentences=2)
                        except Exception:
                            summary = landmark_descs.get(detected_name, "")
                        wiki_cache[detected_name] = summary
                else:
                    last_detected = None
                    last_score = score
        except Empty:
            pass

        # Draw overlay
        if last_detected:
            header = f"{last_detected}  [{last_score:.1f}]"
            cv2.putText(frame, header, (10, 50), FONT, 0.7, (0,255,0), 2, cv2.LINE_AA)
            desc = wiki_cache.get(last_detected, landmark_descs.get(last_detected, ""))
            if desc:
                wrapped = wrap_text(desc, width=40)
                overlay_multiline_text(frame, wrapped, 10, 90, line_height=22, font_scale=0.55, thickness=1)
        else:
            cv2.putText(frame, "No landmark detected", (10, 50), FONT, 0.7, (0,165,255), 2, cv2.LINE_AA)

        stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")

# ---------------- MAIN APP ----------------
if __name__ == "__main__":
    clip_landmark_detector()
