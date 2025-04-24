![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![React](https://img.shields.io/badge/Frontend-React%2FTS-blue?logo=react)
![TailwindCSS](https://img.shields.io/badge/Styling-TailwindCSS-38b2ac?logo=tailwindcss)
![Chart.js](https://img.shields.io/badge/Charts-Chart.js-orange?logo=chartdotjs)
![License](https://img.shields.io/badge/License-MIT-green)


# 🧠 Brain Activity Monitor

> Because watching your brain make decisions is more fun than actually making them.



## 🎥 Demo Video

Because seeing is believing, and this project deserves screen time.


https://github.com/user-attachments/assets/650ec8ad-1145-41b0-9669-baf298b6ee6a



## 📖 Overview

**Brain Activity Monitor** is a real-time web application that visualizes live or simulated brain activity using EEG (electroencephalogram) data. It does more than just look cool—it shows which side of your brain is working harder (logic vs. creativity), tracks your eye movements, and even detects when you blink. Basically, your brain has never looked this flashy.

This solo-built system runs both with real EEG datasets or in simulation mode for those without a headset lying around. It also integrates webcam-based eye tracking, because who doesn't want their browser to know where they're looking?



## ✨ Features

- 🧠 **Hemisphere Dominance Detection**  
  Logical vs. creative brain activity in real-time
- 👁 **Eye Position + Blink Tracking**  
  Visualizes attention and fatigue with a simple webcam
- 📈 **Live EEG Data Visualization**  
  Use real CSV-formatted EEG data—or just simulate it
- 🧪 **Brain State Analysis**  
  Decodes whether you're in "left brain," "right brain," or "neutral" mode
- 💻 **Sleek Web Interface**  
  Built with React + Tailwind, responsive on all devices



## ⚙️ How It Works

The backend (Python) does the heavy lifting—processing EEG signals or simulating them if you're in demo mode. It exposes a REST API with endpoints for brain state analysis, eye tracking, device connection, and more.

The frontend (React + TypeScript) takes that data and turns it into sleek, animated brain visuals.



## 🔌 API Endpoints

| Endpoint              | What it Does                        |
|-----------------------|-------------------------------------|
| `/api/status`         | Checks if the backend is alive      |
| `/api/data`           | Streams EEG data in real-time       |
| `/api/mental_state`   | Returns current brain state         |
| `/api/connect`        | Starts EEG or simulated session     |
| `/api/disconnect`     | Stops session                       |



## 🚀 Setup & Usage

### 📦 Requirements

- Python 3.8+
- Node.js
- Web browser (with WebGL)

### 🧠 Backend

```bash
cd backend
pip install -r requirements.txt
python standalone.py
```

### 🎨 Frontend

```bash
cd frontend
npm install
npm run dev
```

Now open `http://localhost:5173` in your browser.



## 🧪 Simulation Mode

Don’t have EEG data? No stress.

```bash
cd frontend
npm run simulate
```


## 📁 Using Your Own EEG Data

Drop your CSV file in the `data/` directory and name it `mentalstate.csv`.  
Required columns:

- `timestamp`
- EEG channels (e.g., F3, F4, C3, C4, etc.)
- `label`: like `left`, `right`, or `neutral`

Need to convert your dataset? Use the helper scripts in `/backend/utils`.



## 🔍 Recommended Datasets

- [BCI Competition](http://www.bbci.de/competition/)
- [EEGMMIDB on PhysioNet](https://physionet.org/)
- [OpenBCI Sample Sets](https://docs.openbci.com/)
- [NeuroTechX EEG Notebooks](https://github.com/NeuroTechX/eeg-notebooks)



## 🧰 Troubleshooting

- **Backend not responding?** It should be on port 5000. Check your terminal.
- **Missing dependencies?** Run `pip install -r requirements.txt`.
- **CSV not working?** Make sure it follows the correct format (timestamp, channels, label).



## 📬 Contact

📧 If you run into any issues, have suggestions, or just want to nerd out about brains and code—feel free to reach out at [Anushka](mailto:anushkeaa@gmail.com)



## 📄 License

This project is licensed under the MIT License.  
Copy it, fork it, break it, remix it—just don’t forget to give credit.
