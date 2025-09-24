import time
import json
import textwrap
from queue import Queue, Empty
from threading import Thread

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
    st.markdown("<h1 style='text-align:center; color:#2c3e50;'>🗺️ CLIP Landmark Detector</h1>", unsafe_allow_html=True)
    st.info("Upload an image of a landmark to detect it.")

    # Load landmarks data
    landmark_names, landmark_descs = load_landmarks(LANDMARKS_JSON)

    # Load CLIP model
    model, preprocess = clip.load(MODEL_NAME, device=DEVICE)
    model.eval()
    with torch.no_grad():
        text_tokens = clip.tokenize(landmark_names).to(DEVICE)
        text_embeddings = model.encode_text(text_tokens)

    # Queues and worker
    in_q = Queue(maxsize=1)
    out_q = Queue(maxsize=1)
    worker = Thread(target=clip_worker, args=(in_q, out_q, model, preprocess, text_embeddings, landmark_names, DEVICE), daemon=True)
    worker.start()

    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Send image to CLIP worker
        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        try:
            in_q.put_nowait(pil_img)
        except:
            pass

        try:
            detected_name, score = out_q.get(timeout=5)
            if detected_name and score >= SIMILARITY_THRESHOLD:
                header = f"{detected_name}  [{score:.1f}]"
                cv2.putText(frame, header, (10, 50), FONT, 0.7, (0,255,0), 2, cv2.LINE_AA)
                try:
                    summary = wikipedia.summary(detected_name, sentences=2)
                except Exception:
                    summary = landmark_descs.get(detected_name, "")
                wrapped = wrap_text(summary, width=40)
                overlay_multiline_text(frame, wrapped, 10, 90, line_height=22, font_scale=0.55, thickness=1)
            else:
                cv2.putText(frame, "No landmark detected", (10, 50), FONT, 0.7, (0,165,255), 2, cv2.LINE_AA)
        except Empty:
            cv2.putText(frame, "Processing...", (10, 50), FONT, 0.7, (255,255,0), 2, cv2.LINE_AA)

        st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB")

# ---------------- MAIN APP ----------------
if __name__ == "__main__":
    clip_landmark_detector()
