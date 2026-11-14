# hf_fetch.py  usage:  python hf_fetch.py <repo> [N]    (N=0 lists only; N>0 downloads N videos per folder)
import sys, os, shutil, collections
from huggingface_hub import list_repo_files, hf_hub_download

REPO = sys.argv[1] if len(sys.argv) > 1 else "marcusmball/face-anti-spoofing-dataset"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 0
EXT = (".mp4", ".avi", ".mov", ".webm", ".mkv")

files = [
    f for f in list_repo_files(REPO, repo_type="dataset") if f.lower().endswith(EXT)
]
if not files:
    print(
        "No raw video files (repo may be parquet-only). Try a TrainingDataPro repo instead."
    )
    sys.exit()

groups = collections.defaultdict(list)
for f in files:
    groups[os.path.dirname(f) or "root"].append(f)
for g, fs in sorted(groups.items()):
    print(f"{len(fs):5d} videos  {g}")

if N:
    for g, fs in groups.items():
        dst = os.path.join("data_ext", g.replace("/", "_"))
        os.makedirs(dst, exist_ok=True)
        for f in fs[:N]:
            shutil.copy(
                hf_hub_download(REPO, f, repo_type="dataset"),
                os.path.join(dst, os.path.basename(f)),
            )
        print("downloaded", min(N, len(fs)), "->", dst)
