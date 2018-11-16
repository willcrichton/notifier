# notifier

Utility for receiving push notifications from Esper on your laptop. Currently only supports OS X.

## Setup

```
brew install terminal-notifier tmux
git clone https://github.com/scanner-research/notifier
cd notifier
pip3 install -r requirements.txt
```

## Usage

Use tmux to start a session. Then run:

```
python3 listener.py <GCE node name>
```
