## Installation

### Install dependencies
```bash
brew install poetry
brew install direnv
poetry install
```

### Setup environment
```bash
cp .envrc.sample .envrc
```
- Modify `.envrc` to add your DEEPGRAM_API_KEY
- Ensure you have a working `google-crerdentials.json` file in the root directory

```bash
direnv allow .
```

### Run the app
```bash
poetry run python main.py
```

Then just select google or deepgram and Speak! 🎤
