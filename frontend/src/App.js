import React, { useEffect, useMemo, useRef, useState } from "react";
import "./App.css";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Small word list for practice
const WORD_LIST = [
  "future", "matrix", "neon", "syntax", "quantum", "vector", "async", "buffer", "cipher", "delta",
  "engine", "flux", "glide", "haptic", "input", "kernel", "lambda", "macro", "node", "orbit",
  "pixel", "queue", "render", "stack", "tensor", "update", "virtual", "widget", "xenon", "yotta",
];

// Keyboard layout definition
const KEY_ROWS = [
  ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "="],
  ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "\\"],
  ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'"],
  ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/"],
  ["space"],
];

const LEFT_HAND = new Set(["`","1","2","3","4","q","w","e","r","t","a","s","d","f","g","z","x","c","v","b"]);

function useUserId() {
  const [userId, setUserId] = useState("");
  useEffect(() => {
    let id = localStorage.getItem("user_id");
    if (!id) {
      id = (typeof crypto !== "undefined" && crypto.randomUUID) ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
      localStorage.setItem("user_id", id);
    }
    setUserId(id);
  }, []);
  return userId;
}

function generateText(words = 30) {
  const list = [];
  for (let i = 0; i < words; i++) {
    list.push(WORD_LIST[Math.floor(Math.random() * WORD_LIST.length)]);
  }
  return list.join(" ");
}

function computeStats({ totalTyped, correctTyped, startTime }) {
  const elapsedMs = Date.now() - startTime;
  const minutes = Math.max(elapsedMs / 60000, 0.001);
  const wpm = (correctTyped / 5) / minutes;
  const accuracy = totalTyped === 0 ? 100 : (correctTyped / totalTyped) * 100;
  return { wpm, accuracy };
}

function App() {
  const userId = useUserId();

  const [mode, setMode] = useState("time"); // time | words | freestyle
  const [timeLimit, setTimeLimit] = useState(60); // seconds
  const [wordLimit, setWordLimit] = useState(30);

  const [target, setTarget] = useState(generateText(wordLimit));
  const [typed, setTyped] = useState("");
  const [running, setRunning] = useState(false);
  const [startTime, setStartTime] = useState(0);
  const [pressedKeys, setPressedKeys] = useState(new Set());
  const [handOffset, setHandOffset] = useState({ left: 0, right: 0 });
  const intervalRef = useRef(null);
  const [stats, setStats] = useState({ wpm: 0, accuracy: 100, consistency: 100 });
  const [history, setHistory] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);

  const totalTyped = typed.length;
  const correctTyped = useMemo(() => {
    let c = 0;
    for (let i = 0; i < typed.length; i++) {
      if (typed[i] === target[i]) c++;
    }
    return c;
  }, [typed, target]);

  const remainingTime = useMemo(() => {
    if (!running || mode !== "time") return timeLimit;
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    return Math.max(timeLimit - elapsed, 0);
  }, [running, timeLimit, startTime, mode]);

  useEffect(() => {
    // ping backend once
    axios.get(`${API}/`).catch(() => {});
    fetchHistory();
    fetchLeaderboard();
  }, [userId]);

  function onKeyDown(e) {
    if (!running) return;
    const key = e.key === " " ? "space" : e.key.toLowerCase();
    setPressedKeys(prev => new Set(prev).add(key));

    // Move hands subtly
    if (LEFT_HAND.has(key)) {
      setHandOffset(o => ({ ...o, left: Math.min(o.left + 1, 6) }));
    } else {
      setHandOffset(o => ({ ...o, right: Math.min(o.right + 1, 6) }));
    }

    // Append character (except control keys)
    if (key === "backspace") {
      setTyped(t => t.slice(0, -1));
    } else if (key.length === 1) {
      setTyped(t => t + (e.shiftKey ? key.toUpperCase() : key));
    } else if (key === "space") {
      setTyped(t => t + " ");
    }
  }

  function onKeyUp(e) {
    const key = e.key === " " ? "space" : e.key.toLowerCase();
    setPressedKeys(prev => {
      const n = new Set(prev);
      n.delete(key);
      return n;
    });
  }

  useEffect(() => {
    const handlerDown = (e) => onKeyDown(e);
    const handlerUp = (e) => onKeyUp(e);
    window.addEventListener("keydown", handlerDown);
    window.addEventListener("keyup", handlerUp);
    return () => {
      window.removeEventListener("keydown", handlerDown);
      window.removeEventListener("keyup", handlerUp);
    };
  }, [running]);

  useEffect(() => {
    if (!running) return;
    // Update live stats each 200ms
    intervalRef.current = setInterval(() => {
      const { wpm, accuracy } = computeStats({ totalTyped, correctTyped, startTime });
      // naive consistency: closer to moving average = higher
      setStats(s => {
        const newWpm = wpm;
        const consistency = Math.max(0, Math.min(100, 100 - Math.abs(newWpm - s.wpm)));
        return { wpm: newWpm, accuracy, consistency };
      });

      // compute remaining internally to avoid stale startTime/remaining at session start
      if (mode === "time" && startTime > 0) {
        const elapsedSec = Math.floor((Date.now() - startTime) / 1000);
        const rem = Math.max(timeLimit - elapsedSec, 0);
        if (rem === 0) {
          stopSession();
        }
      }

      // words mode auto-stop
      if (mode === "words") {
        const wordsTyped = typed.trim() ? typed.trim().split(/\s+/).length : 0;
        if (wordsTyped >= wordLimit) {
          stopSession();
        }
      }
    }, 200);
    return () => clearInterval(intervalRef.current);
  }, [running, totalTyped, correctTyped, startTime, mode, timeLimit, wordLimit, typed]);

  function startSession() {
    setTyped("");
    setStats({ wpm: 0, accuracy: 100, consistency: 100 });
    setStartTime(Date.now());
    setRunning(true);
    if (mode !== "freestyle") {
      setTarget(generateText(wordLimit));
    }
  }

  async function stopSession() {
    setRunning(false);
    const end = Date.now();
    const { wpm, accuracy } = computeStats({ totalTyped, correctTyped, startTime });
    const payload = {
      user_id: userId,
      mode,
      duration_seconds: Math.round((end - startTime) / 1000),
      words_count: typed.trim() ? typed.trim().split(/\s+/).length : 0,
      wpm: Number(wpm.toFixed(2)),
      accuracy: Number(accuracy.toFixed(2)),
      consistency: Number(stats.consistency.toFixed(2)),
      started_at: new Date(startTime).toISOString(),
      ended_at: new Date(end).toISOString(),
      raw_typed: typed,
      target_text: target,
    };
    try {
      await axios.post(`${API}/sessions`, payload);
      fetchHistory();
      fetchLeaderboard();
    } catch (e) {
      console.error("Failed to save session", e);
    }
  }

  async function fetchHistory() {
    try {
      const { data } = await axios.get(`${API}/sessions`, { params: { user_id: userId } });
      setHistory(data);
    } catch (e) {
      // ignore
    }
  }

  async function fetchLeaderboard() {
    try {
      const { data } = await axios.get(`${API}/leaderboard`);
      setLeaderboard(data);
    } catch (e) {
      // ignore
    }
  }

  const caretIndex = typed.length;

  return (
    <div className="page">
      <nav className="topbar">
        <div className="brand">NeoType 3D</div>
        <div className="controls">
          <select value={mode} onChange={e => setMode(e.target.value)}>
            <option value="time">Time (60s)</option>
            <option value="words">Words ({wordLimit})</option>
            <option value="freestyle">Freestyle</option>
          </select>
          {mode === "time" && <span className="pill">{remainingTime}s</span>}
          {mode === "words" && <input className="pill" type="number" min={10} max={100} value={wordLimit} onChange={e => setWordLimit(Number(e.target.value))} />}
          {!running ? (
            <button className="btn" onClick={startSession}>Start</button>
          ) : (
            <button className="btn danger" onClick={stopSession}>Stop</button>
          )}
        </div>
      </nav>

      <div className="scene">
        <div className="monitor">
          <div className="screen">
            <div className="target">
              {target.split("").map((ch, idx) => {
                const typedCh = typed[idx];
                const status = typedCh == null ? "pending" : (typedCh === ch ? "ok" : "bad");
                return <span key={idx} className={`ch ${status}`}>{ch}</span>;
              })}
              <span className="caret" style={{ left: `${(caretIndex % 60) * 0.9}ch`, top: `${Math.floor(caretIndex / 60) * 1.4}em` }} />
            </div>
          </div>
          <div className="stand" />
        </div>

        <div className="keyboard">
          {KEY_ROWS.map((row, rIdx) => (
            <div className="key-row" key={rIdx}>
              {row.map(k => <Key key={k} label={k} pressed={pressedKeys.has(k)} />)}
            </div>
          ))}
        </div>

        <div className="hands">
          <div className="hand left" style={{ transform: `translate3d(${handOffset.left * 2}px, 0, 0)` }} />
          <div className="hand right" style={{ transform: `translate3d(${handOffset.right * -2}px, 0, 0)` }} />
        </div>
      </div>

      <section className="stats">
        <div className="card">
          <div className="stat">
            <div className="label">WPM</div>
            <div className="value">{stats.wpm.toFixed(1)}</div>
          </div>
          <div className="stat">
            <div className="label">Accuracy</div>
            <div className="value">{stats.accuracy.toFixed(0)}%</div>
          </div>
          <div className="stat">
            <div className="label">Consistency</div>
            <div className="value">{stats.consistency.toFixed(0)}</div>
          </div>
        </div>

        <div className="columns">
          <div className="card">
            <h3>Your Sessions</h3>
            <ul className="list">
              {history.slice(0, 8).map(s => (
                <li key={s.id}>{new Date(s.created_at).toLocaleDateString()} — {s.wpm} wpm, {s.accuracy}%</li>
              ))}
            </ul>
          </div>
          <div className="card">
            <h3>Leaderboard</h3>
            <ol className="list">
              {leaderboard.slice(0, 8).map((s, i) => (
                <li key={`${s.user_id}-${i}`}>{s.wpm} wpm — {String(s.user_id).slice(0,6)}...</li>
              ))}
            </ol>
          </div>
        </div>
      </section>

      <footer className="footer">
        Built with React + FastAPI + Mongo • Dark 3D UI • No cookies or trackers
      </footer>
    </div>
  );
}

function Key({ label, pressed }) {
  const display = label === "space" ? "" : label.length === 1 ? label.toUpperCase() : label;
  const style = { transform: pressed ? "translateZ(0px) translateY(2px)" : "translateZ(8px)" };
  const wide = label === "space" ? " wide" : "";
  return (
    <div className={`key${wide}`} style={style}>
      <div className="keycap">{display}</div>
    </div>
  );
}

export default App;