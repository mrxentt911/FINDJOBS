# 🧑‍💻 Job Search Tool

This is a Python tool that helps you search for jobs, extract useful contact information, and save results in a structured format.  
It supports **Google Jobs via SerpAPI** and includes a **fallback to RemoteOK** when SerpAPI is unavailable.  
A **Tkinter-based GUI** is also included to make searching and viewing results easier.

---

## 🚀 Features

- 🔍 **Search jobs** using:
  - [SerpAPI Google Jobs](https://serpapi.com/google-jobs-api)
  - RemoteOK (fallback JSON API)
- 📧 Extracts **emails** from job descriptions
- 📱 Extracts **phone numbers** (regex based)
- 📂 Saves results to **CSV** (`job_results.csv`)
- 🧹 Avoids duplicates (unique check by job title + company + location)
- 🖥️ **GUI with Tkinter**:
  - Enter search query & location
  - Display jobs in a table
  - Scrollable results
  - Save results automatically

---

## 📦 Installation

1. Clone this repository:

```bash
git clone https://github.com/your-username/FINDJOBS.git
cd job-search-tool
