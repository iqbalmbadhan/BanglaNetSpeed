# Microsoft Store Submission Guide for Win11 Net Speed Compact
Developed by **Iqbal Mahmud** · [https://iqbalmahmud.com](https://iqbalmahmud.com)

This guide walks you step-by-step through publishing **Win11 Net Speed Compact** to the official **Microsoft Store**.

---

## 1. Prerequisites

1. **Microsoft Developer Account:**
   - Register at [Microsoft Partner Center](https://partner.microsoft.com/dashboard/registration).
   - Cost: **$19 USD** one-time registration fee for an individual account (no yearly recurring fee).
2. **Built Installer:**
   - Your Inno Setup installer: `dist\Win11NetSpeedCompact-Setup.exe` (hosted as a public GitHub release asset or on your domain).
3. **Visual Assets:**
   - App Icon: 300×300 px PNG (transparent or dark background).
   - Screenshots: 1920×1080 px or 1366×768 px PNG (found in `screenshots\`).

---

## 2. Choosing Your Submission Method

Microsoft Store supports two methods for Win32 desktop apps:

| Method | How it works | Best for |
| :--- | :--- | :--- |
| **Method A: Direct Win32 Installer (Recommended)** | Provide your GitHub Release `.exe` installer URL. The Store runs it with silent switches. Updates are managed by your GitHub releases. | Fastest to publish, no MSIX certificate needed, zero code changes. |
| **Method B: MSIX Package** | Wrap the app into an `.msix` package using the Microsoft MSIX Packaging Tool. Updates flow through the Store. | Native Windows store container install. |

*We recommend **Method A (Direct Win32 Installer)** because it works seamlessly with the Inno Setup installer and GitHub releases.*

---

## 3. Step-by-Step Submission (Method A: Win32 EXE)

### Step 1: Reserve Your Product Name
1. Log in to [Microsoft Partner Center](https://partner.microsoft.com/dashboard/apps-and-games/overview).
2. Click **New product** → **App** (or Win32 app).
3. Enter the product name: `Win11 Net Speed Compact`.
4. Click **Reserve product name**.

---

### Step 2: Package & Installer Configuration
In your app submission dashboard, go to the **Package** or **Installer** section:

1. **Installer Type:** Select `EXE (Inno Setup)`.
2. **Download URL:** Provide the direct public link to your GitHub release installer, for example:
   ```text
   https://github.com/iqbalmbadhan/Win11NetSpeedCompact/releases/download/v1.2.1/Win11NetSpeedCompact-Setup.exe
   ```
3. **Silent Install Arguments:**
   ```text
   /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
   ```
4. **Silent Uninstall Arguments:**
   ```text
   /VERYSILENT /SUPPRESSMSGBOXES /NORESTART
   ```
5. **Success Exit Codes:** `0`
6. **Architecture:** `x64` (and `x86` if compatible).

---

### Step 3: Product Properties & Age Rating
1. **Category:** `Developer tools` or `Utilities & tools`.
2. **Pricing:** `Free` (Base price: Free).
3. **Markets:** `All markets` (Worldwide).
4. **Age Rating (IARC):**
   - Click **Start questionnaire**.
   - Category: *Utility, Productivity, Communication or other*.
   - Does the app share user location? *No*.
   - Does the app allow users to interact or exchange messages? *No*.
   - Does the app contain violence or adult content? *No*.
   - Rating output: **All Ages / Everyone / PEGI 3**.

---

### Step 4: Store Listing Information

Copy and paste the following verified details into the **Store listing** tab:

- **App title:** `Win11 Net Speed Compact`
- **Short description (Under 100 characters):**
  > Lightweight, always-on-top network speed and CPU/RAM meter for the Windows 11 taskbar.
- **Description:**
  ```text
  Win11 Net Speed Compact is an ultra-lightweight, customizable network speed meter designed specifically for Windows 11. It sits unobtrusively on or near your taskbar and monitors real-time internet performance without bloat, background telemetry, or administrative privileges.

  Key Features:
  • Live download (↓) and upload (↑) speeds, refreshed twice per second.
  • Two layout options: Classic horizontal view or ultra-compact 2-row stacked format.
  • Optional stacked CPU and RAM usage percentages.
  • Interactive hover tooltips showing live upload/download speed and hardware status.
  • Dual language support: Instant switching between English and pure Bengali (বাংলা).
  • Minimal resource consumption: Sub-30MB RAM footprint built in Python & Tkinter.
  • Custom appearance: Font sizes, font weights, custom font colors, and background themes.
  • Drag to position anywhere, and resize with mouse-wheel or bottom-right grip.
  • 100% open source under the MIT License with zero outbound tracking.
  ```
- **Keywords / Search terms:**
  `net speed`, `network speed monitor`, `taskbar speed meter`, `internet speed`, `bandwidth monitor`, `ram monitor`, `cpu monitor`, `win11 speed meter`, `bangla speed meter`
- **Copyright information:** `Copyright © 2026 Iqbal Mahmud`
- **Developer website:** `https://iqbalmahmud.com`
- **Support contact URL:** `https://github.com/iqbalmbadhan/Win11NetSpeedCompact/issues`
- **Privacy policy URL:** `https://github.com/iqbalmbadhan/Win11NetSpeedCompact/blob/main/SECURITY.md`

---

### Step 5: Screenshots and Assets
1. **Desktop Screenshots:**
   - Upload `screenshots/widget-taskbar.png`
   - Upload `screenshots/widget-default.png`
   - Upload `screenshots/widget-cpu-ram.png`
   - Upload `screenshots/widget-cpu-ram-custom.png`
2. **App Tile / Logo:**
   - Upload a square icon (300×300 px PNG).

---

### Step 6: Review & Submit
1. Click **Review and submit**.
2. Certification typically takes between **24 to 48 hours**.
3. Once approved, your app will have its own official Microsoft Store URL (e.g. `https://apps.microsoft.com/detail/...`) and users can install it directly from the Windows Store!

---

## 4. Alternative: MSIX Packaging Method (Optional)

If you prefer publishing a self-contained `.msix` package:
1. Download the free **MSIX Packaging Tool** from the Microsoft Store.
2. Select **Application package** on a clean virtual machine or sandbox.
3. Select `dist\Win11NetSpeedCompact-Setup.exe` as the installer.
4. Run the installer through the tool to record registry and file changes.
5. Save the generated `.msix` file.
6. In Partner Center, select **Upload package** and drag-and-drop the `.msix` file.
