// Pure-JS Live ASL Hand Sign Interpreter (powered by exported model.p -> model.json)
import {
  FilesetResolver,
  HandLandmarker,
  DrawingUtils,
} from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@1.2.2/vision_bundle.mjs";

const MEDIAPIPE_WASM_URL =
  "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@1.2.2/wasm";
const HAND_MODEL_URL =
  "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task";

const SMOOTHING_WINDOW = 8;
const MIN_CONFIDENCE = 0.35;
const TRAIN_ASPECT_RATIO = 4 / 3; // 640x480 training camera aspect ratio

/**
 * Evaluates all 100 Random Forest trees from model.json on a 42-float feature vector.
 */
export function predictSign(features, model) {
  const votes = new Uint16Array(model.labels.length);
  const { trees, classOrder, labels } = model;

  for (let t = 0; t < trees.length; t++) {
    const tree = trees[t];
    let node = tree[0];
    while (Array.isArray(node)) {
      // node = [featureIndex, threshold, leftChildIdx, rightChildIdx]
      node = features[node[0]] <= node[1] ? tree[node[2]] : tree[node[3]];
    }
    votes[node]++;
  }

  // Tie-break in exact scikit-learn model.classes_ order
  let bestClass = classOrder[0];
  let maxVotes = votes[bestClass];
  for (let i = 1; i < classOrder.length; i++) {
    const cls = classOrder[i];
    if (votes[cls] > maxVotes) {
      maxVotes = votes[cls];
      bestClass = cls;
    }
  }

  return {
    classId: bestClass,
    letter: labels[bestClass],
    confidence: maxVotes / trees.length,
  };
}

/**
 * Extracts the exact 42 normalized coordinates expected by model.p:
 * [x0 - minX, y0 - minY, ..., x20 - minX, y20 - minY]
 */
export function extractFeatures(landmarks, aspectScale = 1, mirrorLeftHand = false) {
  const features = new Float32Array(42);
  const xs = new Float32Array(21);
  const ys = new Float32Array(21);
  let minX = Infinity;
  let minY = Infinity;

  for (let i = 0; i < 21; i++) {
    const rawX = mirrorLeftHand ? 1 - landmarks[i].x : landmarks[i].x;
    const x = rawX * aspectScale;
    const y = landmarks[i].y;
    xs[i] = x;
    ys[i] = y;
    if (x < minX) minX = x;
    if (y < minY) minY = y;
  }

  for (let i = 0; i < 21; i++) {
    features[i * 2] = xs[i] - minX;
    features[i * 2 + 1] = ys[i] - minY;
  }

  return features;
}

/**
 * Attaches live webcam sign interpretation to DOM elements.
 */
export function createSignInterpreter({
  videoEl,
  canvasEl,
  toggleBtn,
  letterEl,
  confidenceEl,
  statusEl,
  leftHandCheckbox = null,
  modelUrl = "./model.json",
  inlineModel = null,
}) {
  const ctx = canvasEl.getContext("2d");
  const drawingUtils = new DrawingUtils(ctx);

  let model = inlineModel;
  let handLandmarker = null;
  let stream = null;
  let rafId = null;
  let running = false;
  let lastVideoTime = -1;
  const history = [];

  function setStatus(msg, allowOpenNewTab = false) {
    if (!statusEl) return;
    statusEl.textContent = msg;
    if (allowOpenNewTab && window.self !== window.top) {
      const link = document.createElement("a");
      link.href = window.location.href;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = " (Open in new tab)";
      link.style.color = "#4ade80";
      statusEl.appendChild(link);
    }
  }

  async function initModels() {
    if (model && handLandmarker) return;
    setStatus("Loading hand tracker & sign model…");

    const [loadedModel, vision] = await Promise.all([
      model ? Promise.resolve(model) : fetch(modelUrl).then((r) => {
        if (!r.ok) throw new Error(`Failed to load ${modelUrl} (${r.status})`);
        return r.json();
      }),
      FilesetResolver.forVisionTasks(MEDIAPIPE_WASM_URL),
    ]);
    model = loadedModel;

    const baseOpts = {
      runningMode: "VIDEO",
      numHands: 1, // Prevents 84-feature crash when 2 hands enter frame
      minHandDetectionConfidence: 0.3,
      minHandPresenceConfidence: 0.3,
      minTrackingConfidence: 0.3,
    };

    try {
      handLandmarker = await HandLandmarker.createFromOptions(vision, {
        ...baseOpts,
        baseOptions: { modelAssetPath: HAND_MODEL_URL, delegate: "GPU" },
      });
    } catch {
      handLandmarker = await HandLandmarker.createFromOptions(vision, {
        ...baseOpts,
        baseOptions: { modelAssetPath: HAND_MODEL_URL, delegate: "CPU" },
      });
    }
  }

  function smoothPrediction(raw) {
    if (raw.confidence < MIN_CONFIDENCE) return null;
    history.push(raw);
    if (history.length > SMOOTHING_WINDOW) history.shift();

    const counts = new Map();
    for (const item of history) {
      counts.set(item.letter, (counts.get(item.letter) || 0) + 1);
    }

    let winner = raw.letter;
    let bestCount = 0;
    for (const [ltr, count] of counts) {
      if (count > bestCount) {
        bestCount = count;
        winner = ltr;
      }
    }

    const matching = history.filter((h) => h.letter === winner);
    const avgConfidence =
      matching.reduce((sum, h) => sum + h.confidence, 0) / matching.length;

    return { letter: winner, confidence: avgConfidence };
  }

  function drawOverlay(landmarks, prediction) {
    const W = canvasEl.width;
    const H = canvasEl.height;
    ctx.clearRect(0, 0, W, H);

    // Draw hand skeleton
    drawingUtils.drawConnectors(landmarks, HandLandmarker.HAND_CONNECTIONS, {
      color: "#22c55e",
      lineWidth: 3,
    });
    drawingUtils.drawLandmarks(landmarks, {
      color: "#ffffff",
      fillColor: "#16a34a",
      lineWidth: 1.5,
      radius: 4,
    });

    // Compute bounding box in pixel space
    let minX = 1, minY = 1, maxX = 0, maxY = 0;
    for (const lm of landmarks) {
      if (lm.x < minX) minX = lm.x;
      if (lm.y < minY) minY = lm.y;
      if (lm.x > maxX) maxX = lm.x;
      if (lm.y > maxY) maxY = lm.y;
    }

    const pad = 12;
    const x1 = Math.max(0, minX * W - pad);
    const y1 = Math.max(0, minY * H - pad);
    const x2 = Math.min(W, maxX * W + pad);
    const y2 = Math.min(H, maxY * H + pad);

    ctx.strokeStyle = "#22c55e";
    ctx.lineWidth = 2.5;
    ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

    if (prediction) {
      const label = `${prediction.letter}  ${Math.round(prediction.confidence * 100)}%`;
      ctx.save();
      // Counter-flip text so it reads left-to-right on a CSS scaleX(-1) canvas
      ctx.translate(x2, Math.max(28, y1 - 8));
      ctx.scale(-1, 1);
      ctx.font = "600 16px system-ui, -apple-system, sans-serif";
      const textWidth = ctx.measureText(label).width;
      ctx.fillStyle = "rgba(15, 23, 42, 0.85)";
      ctx.fillRect(0, -20, textWidth + 16, 26);
      ctx.fillStyle = "#4ade80";
      ctx.fillText(label, 8, -2);
      ctx.restore();
    }
  }

  function renderLoop() {
    if (!running) return;

    if (videoEl.readyState >= 2 && videoEl.currentTime !== lastVideoTime) {
      lastVideoTime = videoEl.currentTime;

      if (
        canvasEl.width !== videoEl.videoWidth ||
        canvasEl.height !== videoEl.videoHeight
      ) {
        canvasEl.width = videoEl.videoWidth;
        canvasEl.height = videoEl.videoHeight;
      }

      const result = handLandmarker.detectForVideo(videoEl, performance.now());

      if (result.landmarks && result.landmarks.length > 0) {
        const landmarks = result.landmarks[0];
        const aspectScale =
          videoEl.videoWidth / videoEl.videoHeight / TRAIN_ASPECT_RATIO;
        const mirrorLeft = Boolean(leftHandCheckbox && leftHandCheckbox.checked);

        const features = extractFeatures(landmarks, aspectScale, mirrorLeft);
        const rawPred = predictSign(features, model);
        const smoothed = smoothPrediction(rawPred);

        drawOverlay(landmarks, smoothed);

        if (smoothed) {
          if (letterEl) letterEl.textContent = smoothed.letter;
          if (confidenceEl) {
            confidenceEl.textContent = `${Math.round(smoothed.confidence * 100)}%`;
          }
        }
      } else {
        history.length = 0;
        ctx.clearRect(0, 0, canvasEl.width, canvasEl.height);
        if (letterEl) letterEl.textContent = "—";
        if (confidenceEl) confidenceEl.textContent = "No hand";
      }
    }

    rafId = requestAnimationFrame(renderLoop);
  }

  async function start() {
    if (running) return;
    if (toggleBtn) toggleBtn.disabled = true;

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("Camera requires HTTPS or http://localhost");
      }
      await initModels();
      setStatus("Requesting camera access…");

      stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "user",
          width: { ideal: 640 },
          height: { ideal: 480 },
        },
        audio: false,
      });

      videoEl.srcObject = stream;
      await videoEl.play();

      running = true;
      lastVideoTime = -1;
      history.length = 0;
      if (toggleBtn) {
        toggleBtn.textContent = "Stop Camera";
        toggleBtn.disabled = false;
      }
      setStatus("Live — show an ASL hand sign (A–Y)");
      rafId = requestAnimationFrame(renderLoop);
    } catch (err) {
      const isPermErr =
        err && (err.name === "NotAllowedError" || err.name === "SecurityError");
      setStatus(
        isPermErr && window.self !== window.top
          ? "Camera blocked inside embedded preview"
          : `Error: ${err.message || "Unable to access camera"}`,
        isPermErr
      );
      if (toggleBtn) toggleBtn.disabled = false;
    }
  }

  function stop() {
    running = false;
    if (rafId) cancelAnimationFrame(rafId);
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      stream = null;
    }
    videoEl.srcObject = null;
    ctx.clearRect(0, 0, canvasEl.width, canvasEl.height);
    history.length = 0;
    if (letterEl) letterEl.textContent = "—";
    if (confidenceEl) confidenceEl.textContent = "0%";
    if (toggleBtn) toggleBtn.textContent = "Start Live Demo";
    setStatus("Camera off");
  }

  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => (running ? stop() : start()));
  }

  window.addEventListener("pagehide", stop);

  return { start, stop };
}
