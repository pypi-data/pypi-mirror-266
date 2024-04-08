PORT=8001
/Applications/Tailscale.app/Contents/MacOS/Tailscale funnel --bg --set-path mistral $PORT
cd `dirname $0`/../src
MODEL_PATH=mistralai/Mistral-7B-Instruct-v0.2 uvicorn examples.server:app --port $PORT --reload
