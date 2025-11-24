 Modular CV Project - Nicolas J. Aguilar

## 📁 File Structure

```
RL_current/
├── main-refactored.tex          ← Main file with version toggles
├── Nico.jpg                      ← Your photo
├── setup/
│   ├── preamble.tex             ← Package imports, colors, formatting
│   └── macros.tex               ← Custom commands (\work, \education, \badge, etc.)
├── sections/
│   ├── header.tex               ← Name, title, contact info
│   ├── sidebar.tex              ← Skills & Languages badges
│   ├── achievements-faang.tex   ← FAANG version achievements
│   ├── achievements-startup.tex ← Startup version achievements
│   ├── achievements-climate.tex ← Climate version achievements
│   ├── experience-amazon.tex    ← Amazon SDE role
│   ├── experience-inedit.tex    ← Inèdit data engineer role
│   └── education.tex            ← M.Sc. Environmental Economics
└── badges/                       ← Badge images (if using PNG badges)
```

---

## 🎯 How to Toggle Between 3 Versions

Open `main-refactored.tex` and edit lines 10-27:

### **Version 1: FAANG** (Amazon + AWS focus)
```latex
\FAANGtrue
% \Startupfalse
% \Climatefalse
```

**Includes:**
- Amazon SDE + Inèdit experiences
- Achievements: Last-mile delivery, AWS microservices, automation

---

### **Version 2: Startup** (Inèdit + automation focus)
```latex
% \FAANGfalse
\Startuptrue
% \Climatefalse
```

**Includes:**
- Inèdit experience only
- Achievements: 80% time savings, Dockerized pipeline, Python suite

---

### **Version 3: Climate** (Inèdit + carbon + ARIMA focus)
```latex
% \FAANGfalse
% \Startupfalse
\Climatetrue
```

**Includes:**
- Inèdit experience only
- Achievements: ARIMA models, carbon footprint, R-based climate modeling

---

## 🛠️ Customization Guide

### Adding a New Section
1. Create `sections/new-section.tex`
2. Add `\input{sections/new-section.tex}` in `main-refactored.tex`

### Creating a 4th Version
1. In `main-refactored.tex`, add:
   ```latex
   \newif\ifCustom
   \Customtrue  % Activate this version
   ```

2. In the document body:
   ```latex
   \ifCustom
       \input{sections/achievements-custom.tex}
   \fi
   ```

### Editing Contact Info
Edit [sections/header.tex](sections/header.tex):
```latex
\name{Your Name}{}
\email{your.email@example.com}
\phone{+XX XXX XXX XXX}
\address{Your City, Country}
\github{https://github.com/}{yourusername}
```

### Modifying Skills/Languages
Edit [sections/sidebar.tex](sections/sidebar.tex):
```latex
\badge{Python} \badge{React} \badge{Go}
```

---

## 📦 Package Dependencies

All packages are loaded in [setup/preamble.tex](setup/preamble.tex):

- **Formatting**: `babel`, `geometry`, `sectsty`, `enumitem`
- **Fonts**: `Archivo`, `fontenc`
- **Graphics**: `fontawesome5`, `graphicx`, `tcolorbox`, `xcolor`, `tikz`
- **Misc**: `hyperref`

---

## 🚀 Building the CV

### On Overleaf:
1. Upload all files maintaining the folder structure
2. Set **Main document** to `main-refactored.tex`
3. Compile with **pdfLaTeX**

### Locally (TeXLive/MiKTeX):
```bash
pdflatex main-refactored.tex
```

---

## 🎨 Custom Macros Reference

Defined in [setup/macros.tex](setup/macros.tex):

| Macro | Usage | Example |
|-------|-------|---------|
| `\name{First}{Last}` | Display name | `\name{Nicolas J. Aguilar}{}` |
| `\email{addr}` | Email with icon | `\email{nicolas@example.com}` |
| `\phone{num}` | Phone with icon | `\phone{+34 634 089 567}` |
| `\address{loc}` | Location with icon | `\address{Barcelona, Spain}` |
| `\github{url}{user}` | GitHub link | `\github{https://github.com/}{nijordia}` |
| `\badge{text}` | Skill badge | `\badge{Python}` |
| `\work{title}{dates}{company}{desc}` | Work experience | See experience files |
| `\education{degree}{dates}{school}{desc}` | Education entry | See education.tex |

---

## 📋 Checklist for .zip Upload to Overleaf

```
✅ main-refactored.tex
✅ Nico.jpg
✅ setup/preamble.tex
✅ setup/macros.tex
✅ sections/header.tex
✅ sections/sidebar.tex
✅ sections/achievements-faang.tex
✅ sections/achievements-startup.tex
✅ sections/achievements-climate.tex
✅ sections/experience-amazon.tex
✅ sections/experience-inedit.tex
✅ sections/education.tex
✅ badges/ (optional, if using PNG badges)
```

---

## 🔄 Version Control Workflow

**Recommended approach:**

1. **Keep one main.tex file** with version toggles (current approach)
2. **Or create 3 separate files:**
   ```
   main-faang.tex      → \FAANGtrue
   main-startup.tex    → \Startuptrue
   main-climate.tex    → \Climatetrue
   ```
   All three would `\input` the same sections conditionally.

---

## 📝 Notes

- **Colors** are defined in [setup/preamble.tex](setup/preamble.tex): `title` (#333F50), `backdrop` (#f2f2f2)
- **Page margins** are tight (7mm) for a compact CV layout
- **Photo** must be named `Nico.jpg` or update the path in [sections/header.tex](sections/header.tex)
- All `.tex` files use UTF-8 encoding

---

## 🐛 Troubleshooting

**Issue: "Missing \item" error**
→ Make sure `enumitem` package is loaded in [setup/preamble.tex](setup/preamble.tex)

**Issue: Font not found (Archivo)**
→ On Overleaf: works by default
→ Locally: Install Archivo font or comment out `\usepackage{Archivo}` in [setup/preamble.tex](setup/preamble.tex)

**Issue: Photo not displaying**
→ Check `Nico.jpg` is in the root directory
→ Verify the path in [sections/header.tex](sections/header.tex):
```latex
\includegraphics[width=3.5cm, height=3.5cm, keepaspectratio]{Nico.jpg}
```

---

## 📧 Contact

**Nicolas J. Aguilar**
nicolasjordi.aguilar@gmail.com
https://github.com/nijordia

---

**Generated**: 2025-11-13
**LaTeX Distribution**: Tested on Overleaf (TeXLive 2024)
