# Project Setup Instructions

Follow these steps in order.

### Step 1: Open Terminal

- **Mac:** Press `Command + Space`, type `Terminal`, and press Enter.
- **Windows:** Open Start, search for `PowerShell`, and open it.

### Step 2: Install `uv`

**Mac:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 3: Download the Project

Run these commands one by one:

```bash
git clone https://github.com/tanmaypurwar7-cmyk/script.git
```

```bash
cd script
```

### Step 4: Install Dependencies

```bash
uv sync
```

Wait for it to finish.

### Step 5: Run the Project

```bash
uv run main.py
```

**Done!** Follow these steps whenever you need to set up the project for the first time.

To run it again later, open Terminal or PowerShell and enter:

```bash
cd script
uv run main.py
```

If you face any errors, send a screenshot to the project team.
