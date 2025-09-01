import re
import requests
import csv
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

API_KEY = "a8bcb5567f9d2cd9071e331cb0948c0bd2e62eb9bad8fb73c7504bf8e3e5d79f"
CSV_FILE = "job_results.csv"


def search_jobs_serpapi(query="remote software developer jobs", location="Worldwide"):
    """Search jobs using SerpAPI"""
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_jobs",
        "q": query,
        "location": location,
        "hl": "en",
        "api_key": API_KEY
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
    except Exception as e:
        print("❌ Error calling SerpAPI:", e)
        return []

    jobs = []
    if "jobs_results" in data:
        for job in data["jobs_results"]:
            description = job.get("description") or ""
            emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", description)
            phones = re.findall(r"\+?\d[\d\-\s]{7,}\d", description)  # Phone regex

            job_info = {
                "date": datetime.today().strftime("%Y-%m-%d"),
                "title": job.get("title"),
                "company": job.get("company_name"),
                "location": job.get("location"),
                "via": job.get("via"),
                "emails": ", ".join(emails) if emails else "Not provided",
                "phones": ", ".join(phones) if phones else "Not provided",
                "description": description[:150] + "..." if len(description) > 150 else description,
            }
            jobs.append(job_info)
    return jobs


def search_jobs_remoteok(query="developer"):
    """Fallback: Scrape jobs from RemoteOK (JSON feed)"""
    url = "https://remoteok.com/api"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        jobs_data = response.json()
    except Exception as e:
        print("❌ Error fetching RemoteOK:", e)
        return []

    jobs = []
    for job in jobs_data[1:]:
        description = job.get("description") or ""
        emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", description)
        phones = re.findall(r"\+?\d[\d\-\s]{7,}\d", description)

        job_info = {
            "date": datetime.today().strftime("%Y-%m-%d"),
            "title": job.get("position"),
            "company": job.get("company"),
            "location": job.get("location") or "Remote",
            "via": "RemoteOK",
            "emails": ", ".join(emails) if emails else "Not provided",
            "phones": ", ".join(phones) if phones else "Not provided",
            "description": description[:150] + "..." if len(description) > 150 else description,
        }
        jobs.append(job_info)
    return jobs


def load_existing_jobs(filename=CSV_FILE):
    """Load already saved jobs to avoid duplicates"""
    existing = set()
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = (row["title"], row["company"], row["location"])
                existing.add(key)
    except FileNotFoundError:
        pass
    return existing


def save_to_csv(jobs, filename=CSV_FILE):
    """Append unique job listings to CSV file with date"""
    fieldnames = ["date", "title", "company", "location", "via", "emails", "phones", "description"]

    existing = load_existing_jobs(filename)
    new_jobs = [job for job in jobs if (job["title"], job["company"], job["location"]) not in existing]

    if not new_jobs:
        print("⚠️ No new jobs to add (all duplicates).")
        return

    try:
        file_exists = False
        try:
            with open(filename, "r", encoding="utf-8"):
                file_exists = True
        except FileNotFoundError:
            file_exists = False

        with open(filename, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for job in new_jobs:
                writer.writerow(job)

        print(f"✅ Added {len(new_jobs)} new jobs to {filename}")
    except Exception as e:
        print("❌ Error saving CSV:", e)


# ---------------- GUI ---------------- #
class JobSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Search Tool")

        # Input fields
        tk.Label(root, text="Search Query:").grid(row=0, column=0, padx=5, pady=5)
        self.query_entry = tk.Entry(root, width=40)
        self.query_entry.insert(0, "remote software developer jobs")
        self.query_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Location:").grid(row=1, column=0, padx=5, pady=5)
        self.location_entry = tk.Entry(root, width=40)
        self.location_entry.insert(0, "Worldwide")
        self.location_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(root, text="Search Jobs", command=self.on_search).grid(row=2, column=0, columnspan=2, pady=10)

        # Treeview (results table)
        columns = ("title", "company", "location", "via", "emails", "phones", "description")
        self.tree = ttk.Treeview(root, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=150, anchor="w")

        self.tree.grid(row=3, column=0, columnspan=2, sticky="nsew")

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        scrollbar_y.grid(row=3, column=2, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_x = ttk.Scrollbar(root, orient="horizontal", command=self.tree.xview)
        scrollbar_x.grid(row=4, column=0, columnspan=2, sticky="ew")
        self.tree.configure(xscrollcommand=scrollbar_x.set)

        root.grid_rowconfigure(3, weight=1)
        root.grid_columnconfigure(1, weight=1)

    def on_search(self):
        query = self.query_entry.get().strip()
        location = self.location_entry.get().strip()

        jobs = search_jobs_serpapi(query, location)
        if not jobs:
            print("⚠️ No jobs from SerpAPI, falling back to RemoteOK...")
            jobs = search_jobs_remoteok(query)

        if not jobs:
            messagebox.showinfo("Job Search", "No jobs found.")
            return

        # Save jobs
        save_to_csv(jobs)

        # Clear old results
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insert new results
        for job in jobs:
            self.tree.insert("", "end", values=(
                job["title"], job["company"], job["location"], job["via"], job["emails"], job["phones"], job["description"]
            ))

        messagebox.showinfo("Job Search", f"Found {len(jobs)} jobs. Results displayed & saved to job_results.csv.")


if __name__ == "__main__":
    root = tk.Tk()
    app = JobSearchApp(root)
    root.mainloop()