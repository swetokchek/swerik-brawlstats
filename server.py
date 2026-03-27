from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

SUPERCELL_KEY = os.getenv("SUPERCELL_KEY", "ВСТАВЬ_СВОЙ_КЛЮЧ_СЮДА")

SUPERCELL_API = "https://api.brawlstars.com/v1"
BRAWLAPI_API = "https://api.brawlapi.com/v1"
STARLIST_API = "https://api.starlist.pro/v1"

HEADERS_SUPERCELL = {"Authorization": f"Bearer {SUPERCELL_KEY}"}

def get_supercell_profile(tag):
    r = requests.get(f"{SUPERCELL_API}/players/%23{tag}", headers=HEADERS_SUPERCELL, timeout=10)
    if r.status_code != 200:
        return None
    return r.json()

def get_brawlapi_profile(tag):
    r = requests.get(f"{BRAWLAPI_API}/player/{tag}", timeout=10)
    if r.status_code != 200:
        return None
    return r.json()

def get_starlist_profile(tag):
    r = requests.get(f"{STARLIST_API}/players/%23{tag}", timeout=10)
    if r.status_code != 200:
        return None
    return r.json()

@app.route("/player")
def player():
    tag = request.args.get("tag", "").replace("#", "").upper()
    if not tag:
        return jsonify({"error": "no tag"}), 400

    sc = get_supercell_profile(tag)
    ba = get_brawlapi_profile(tag)
    sl = get_starlist_profile(tag)

    if not sc:
        return jsonify({"error": "player_not_found"}), 404

    profile = {
        "tag": tag,
        "name": sc.get("name"),
        "trophies": sc.get("trophies"),
        "highestTrophies": sc.get("highestTrophies"),
        "expLevel": sc.get("expLevel"),
        "club": {
            "name": (sc.get("club") or {}).get("name"),
            "tag": (sc.get("club") or {}).get("tag"),
        }
    }

    brawlers = []
    if ba and "brawlers" in ba:
        for b in ba["brawlers"]:
            brawlers.append({
                "id": b.get("id"),
                "name": b.get("name"),
                "power": b.get("power"),
                "rank": b.get("rank"),
                "trophies": b.get("trophies"),
                "highestTrophies": b.get("highestTrophies"),
                "rarity": (b.get("rarity") or {}).get("name"),
                "class": (b.get("class") or {}).get("name"),
                "gadgets": [g.get("name") for g in b.get("gadgets", [])],
                "starPowers": [s.get("name") for s in b.get("starPowers", [])],
                "gears": [g.get("name") for g in b.get("gears", [])],
            })

    battlelog = []
    stats = {}
    modes = {}
    club = {}

    if sl:
        if "battleLog" in sl:
            for b in sl["battleLog"]:
                battlelog.append({
                    "mode": b.get("mode"),
                    "result": b.get("result"),
                    "trophies": b.get("trophiesChange"),
                    "map": (b.get("event") or {}).get("map"),
                    "time": b.get("battleTime"),
                    "rank": b.get("rank"),
                })
        if "stats" in sl:
            stats = {
                "3v3Wins": sl["stats"].get("victories3v3"),
                "soloWins": sl["stats"].get("victoriesSolo"),
                "duoWins": sl["stats"].get("victoriesDuo"),
            }
        if "modes" in sl:
            modes = sl["modes"]
        if "club" in sl:
            club = sl["club"]

    return jsonify({
        "profile": profile,
        "brawlers": brawlers,
        "battlelog": battlelog,
        "stats": stats,
        "modes": modes,
        "club": club
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)