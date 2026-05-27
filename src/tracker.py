import json
from pathlib import Path
from datetime import datetime

class Tracker:
    def __init__(self, output_dir: Path):
        self.file = output_dir / ".processed.json"
        self.data = self._load()

    def _load(self):
        if self.file.exists():
            return json.loads(self.file.read_text())
        return {"processed": []}

    def is_processed(self, url: str) -> bool:
        return any(it["url"] == url for it in self.data["processed"])

    def mark_processed(self, url: str, title: str, date: str, daily_file: str, script_file: str):
        self.data["processed"].append({
            "url": url,
            "title": title,
            "date": date,
            "daily_file": daily_file,
            "script_file": script_file,
            "processed_at": datetime.now().isoformat(),
        })
        self._save()

    def _save(self):
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.write_text(json.dumps(self.data, indent=2))

    def get_by_week(self) -> dict[str, list]:
        weeks = {}
        for it in self.data["processed"]:
            dt = datetime.strptime(it["date"], "%Y-%m-%d")
            iso = dt.isocalendar()
            key = f"{iso[0]}-W{iso[1]:02d}"
            if key not in weeks:
                weeks[key] = []
            weeks[key].append(it)
        return weeks
