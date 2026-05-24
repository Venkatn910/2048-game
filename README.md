# 2048 Web — Deploy & Run Guide

## Files

```
2048_web/
├── app.py           ← Flask + SocketIO server (port 5050)
├── game_logic.py    ← Pure game engine (unchanged from terminal version)
├── templates/
│   └── index.html   ← Full game UI (HTML + CSS + JS, no build step)
├── requirements.txt ← Python deps
├── 2048.service     ← systemd unit (EC2 auto-start)
└── README.md        ← This file
```

---

## Run locally (any machine)

```bash
# 1. Create virtualenv & install deps
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Start the server
python app.py

# 3. Open in browser
#    http://localhost:5050
```

---

## Deploy on AWS EC2

### Step 1 — Launch EC2

- AMI: **Amazon Linux 2023** (or Ubuntu 22.04)
- Instance type: **t3.micro** (free tier)
- Security Group — add an **inbound rule**:
  - Type: Custom TCP
  - Port: **5050**
  - Source: `0.0.0.0/0` (anywhere)

### Step 2 — SSH in & install

```bash
ssh -i your-key.pem ec2-user@YOUR_EC2_IP

# update & install python
sudo dnf update -y                          # Amazon Linux 2023
sudo dnf install -y python3 python3-pip git

# clone / upload your files to ~/2048_web
mkdir ~/2048_web && cd ~/2048_web
# (copy files via scp or git clone)
```

### Step 3 — Install Python deps

```bash
cd ~/2048_web
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4 — Run the server

```bash
python app.py
# ▶  2048 running at  http://0.0.0.0:5050
```

Open your browser at:
```
http://YOUR_EC2_PUBLIC_IP:5050
```

---

## Auto-start on reboot (systemd)

```bash
# copy the service file
sudo cp 2048.service /etc/systemd/system/

# edit WorkingDirectory and User if needed (default: ec2-user)
sudo nano /etc/systemd/system/2048.service

# enable and start
sudo systemctl daemon-reload
sudo systemctl enable 2048
sudo systemctl start  2048

# check status
sudo systemctl status 2048
```

After this, the game restarts automatically if your instance reboots.

---

## Upload files from your laptop

```bash
# scp method
scp -i your-key.pem -r ./2048_web ec2-user@YOUR_EC2_IP:~/

# rsync method (faster for updates)
rsync -avz -e "ssh -i your-key.pem" ./2048_web/ ec2-user@YOUR_EC2_IP:~/2048_web/
```

---

## How it works — architecture

```
Browser (any device)
  │  HTTP GET /          → Flask serves index.html
  │  WebSocket (WS)      → Flask-SocketIO handles events
  │
  │  Events sent by browser:
  │    move   { direction: "left"|"right"|"up"|"down" }
  │    restart
  │    keep_playing
  │
  │  Events sent by server:
  │    state  { grid, score, best, won, over, keep_playing }
  │
app.py  (Flask + SocketIO)
  └── game_logic.py  (pure Python, zero I/O)
        apply_move() / add_random_tile() / has_won() / is_game_over()
```

- `game_logic.py` is **identical** to the terminal version — pure functions only.
- `app.py` keeps one game state dict per connected WebSocket session.
- The browser re-renders the grid on every `state` event — no page reloads.

---

## Controls

| Input | Action |
|---|---|
| Arrow keys | Move |
| WASD / hjkl | Move |
| Swipe (mobile) | Move |
| New Game button | Restart |
| Keep Playing button | Continue after 2048 |

---

## Environment variables

| Var | Default | Description |
|---|---|---|
| `PORT` | `5050` | Port to listen on |
| `SECRET_KEY` | `2048-secret-change-in-prod` | Flask session secret — **change in production** |

```bash
PORT=8080 SECRET_KEY=mysecret python app.py
```
