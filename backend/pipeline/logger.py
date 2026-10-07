import pandas as pd
import config

# class to collect excluded and fixed record with explanation for each
class RecordLogger:

    def __init__(self):
        self.frames = []
        self.counts = []


    def log(self, rows, reason, action="excluded"):
        if rows.empty:
            return
        logged = rows.copy()
        logged["reason"] = reason
        logged["action"] = action
        self.frames.append(logged)
        self.counts.append((reason, action, len(rows)))


    def print_summary(self, total_rows):
        print("\n ======CLEANING SUMMARY======")
        print(f"{'Reason':<40}{'Action':<10}{'Rows':>10}{'%':>9}")
        for reason, action, count in sorted(self.counts, key=lambda c: -c[2]):
            pct = count / total_rows * 100
            print(f"{reason:<40}{action:<10}{count:>10,}{pct:>8.2f}%")

        excluded = sum(c for _, a, c in self.counts if a == "excluded")
        print(f"\n Total Excluded : {excluded:,} of {total_rows:,}")
        print( f"({excluded/ total_rows * 100:.2f}%)")

    def save(self):
        config.LOGS_DIR.mkdir(parents = True, exist_ok=True)
        if self.frames:
            log_df = pd.concat(self.frames, ignore_index=True)
            log_df.to_csv(config.EXCLUDED_LOG, index=False)
        print(f"\n Log saved to {config.EXCLUDED_LOG}")