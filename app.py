"""
2048 Web — Flask + Flask-SocketIO backend
Run:  python app.py
Then open:  http://localhost:5050
"""

import os

from flask import Flask
from flask_socketio import SocketIO, emit

from game_logic import new_game, step

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "2048-secret-change-in-prod")

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    manage_session=False,
)

# In-memory store: session_id → game state
GAMES: dict[str, dict] = {}


# ── routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    from flask import render_template
    return render_template("index.html")


# ── socket events ─────────────────────────────────────────────────────────────

@socketio.on("connect")
def on_connect():
    sid = _get_sid()
    state = new_game()
    GAMES[sid] = state
    emit("state", _serialize(state))


@socketio.on("move")
def on_move(data):
    direction = data.get("direction")
    if direction not in ("left", "right", "up", "down"):
        return
    sid = _get_sid()
    state = GAMES.get(sid)
    if not state:
        state = new_game()
        GAMES[sid] = state

    step(state, direction)
    emit("state", _serialize(state))


@socketio.on("restart")
def on_restart():
    sid = _get_sid()
    state = new_game()
    GAMES[sid] = state
    emit("state", _serialize(state))


@socketio.on("keep_playing")
def on_keep_playing():
    sid = _get_sid()
    state = GAMES.get(sid)
    if state and state.get("won"):
        state["keep_playing"] = True
        emit("state", _serialize(state))


@socketio.on("disconnect")
def on_disconnect():
    sid = _get_sid()
    GAMES.pop(sid, None)


# ── helpers ───────────────────────────────────────────────────────────────────

def _get_sid():
    from flask import request
    return request.sid


def _serialize(state: dict) -> dict:
    return {
        "grid":         state["grid"],
        "score":        state["score"],
        "best":         state["best"],
        "won":          state["won"],
        "over":         state["over"],
        "keep_playing": state["keep_playing"],
    }


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"▶  2048 running at  http://0.0.0.0:{port}")
    socketio.run(app, host="0.0.0.0", port=port, debug=False)

