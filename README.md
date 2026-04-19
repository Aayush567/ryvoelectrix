# Ryvo Electrix Corporate Website

Welcome to the official source code for **Ryvo Electrix**, a premium, visually stunning e-mobility showcase site featuring high-end glassmorphic UI, dynamic components (booking modals, responsive product sliders), and clean-masked navigation.

## 🚀 How to Run the Project

This project leverages a lightweight Custom FastAPI backend purely to provide modern, extension-free URLs (e.g. mapping `ryvoelectrix.com/about` to serve `about.html`) directly natively without the need for complex rewrite engines. 

Follow these steps to spin up the local development server:

### 1. Activate the Virtual Environment
Ensure that you are operating inside the main project directory (`/home/aayush/Antigrav/`) where the Python environment is set up.

```bash
# Activate your local python virtual environment
source venv/bin/activate
```

### 2. Install Required Dependencies
If you haven't already installed the Python dependencies required for the backend router, install them via pip:

```bash
pip install fastapi uvicorn


```

### 3. Start the Server
Run the FastAPI ASGI server using `uvicorn`. Notice how we point straight to the `main.py` routing framework located inside this directory string (`ryvoelectrix`):

```bash
uvicorn ryvoelectrix.main:app --port 8001 --reload
```
*(Tip: We use `--reload` so that any changes you make to the HTML or CSS immediately live-update upon page refresh!)*

### 4. View the App ✨
Open your browser and navigate to:
**👉 [http://localhost:8001](http://localhost:8001)**

---

## 🛠 Project Structure

- **`main.py`**: The dynamic FastAPI routing interceptor. It overrides default routing natively by returning the `.html` strings directly without appending the ugly `.html` extensions.
- **`index.html`**: The main landing page with the horizontal sliding "hero" showcase.
- **`products.html`**: The complete lineup with integrated test-ride modal hooks.
- **`styles.css`**: The core styling engine using rich, dark, edge-to-edge transparent gradients.
- **`script.js`**: Contains the logic controlling the slider translation bounds, mobile navigation toggle logic, and the central popup modal triggers. 
- **`assets/`**: Houses all 3D vehicle renderings and downloaded vendor promotional images.

## ⚡ Core Features

- **Book Test Ride Mechanism**: A purely client-side modal triggered by `.openTestRideModal()`. If called from underneath a specific product instance, the select-list natively auto-populates.
- **SEO Optimized Architecture**: The FastAPI implementation ensures navigation strings are clean and highly performant. 
- **Dynamic CSS Integration**: Uses `lucide` vector graphics natively and pure flex/grid mechanics across all browser ratios.



super user - admin
password - ryvo123