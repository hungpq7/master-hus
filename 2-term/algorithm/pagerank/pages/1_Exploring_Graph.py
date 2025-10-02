import streamlit as st  

# ---------- Nodes ----------
# Dict keyed by node id with attributes.
NODES = {
    "A": {"name": "TechBlog",     "topics": ["Tech"],                 "is_spam": False},
    "B": {"name": "TechForum",    "topics": ["Tech"],                 "is_spam": False},
    "C": {"name": "SearchEngine", "topics": ["Tech","Sports"],        "is_spam": False},
    "D": {"name": "SportsNews",   "topics": ["Sports"],               "is_spam": False},
    "E": {"name": "SportsForum",  "topics": ["Sports"],               "is_spam": False},
    "F": {"name": "CookingBlog",  "topics": ["Cooking"],              "is_spam": False},
    "G": {"name": "CheapPills",   "topics": [],                       "is_spam": True},
    "H": {"name": "Casino",       "topics": [],                       "is_spam": True},
    "I": {"name": "University",   "topics": ["Tech"],                 "is_spam": False},
    "J": {"name": "Wikipedia",    "topics": ["Tech","Sports","Cooking"], "is_spam": False},
}

# ---------- Edges (directed) ----------
# Each edge is (source, target, weight). For vanilla PR, ignore weight; for WPR use it.
EDGES = [
    ("A","B",5), ("A","C",2), ("A","J",1),
    ("B","A",3), ("B","C",2), ("B","G",1),
    ("C","A",2), ("C","D",2), ("C","J",4), ("C","I",3),
    ("D","E",4), ("D","C",1), ("D","J",2),
    ("E","D",2), ("E","C",1), ("E","H",1),
    ("F","C",1), ("F","J",3),
    ("G","C",1), ("G","H",2), ("G","A",1),
    ("H","G",2), ("H","C",1),
    ("I","C",3), ("I","J",5),
    ("J","A",2), ("J","D",2), ("J","F",1), ("J","I",3),
]

# ---------- Topic-Sensitive teleport distributions (sum to 1 per topic) ----------
TOPIC_TELEPORT = {
    "Tech":    {"A":0.25, "B":0.25, "C":0.20, "I":0.15, "J":0.15},
    "Sports":  {"D":0.35, "E":0.25, "C":0.20, "J":0.20},
    "Cooking": {"F":0.60, "J":0.40},
    # Optional catch-all:
    "General": {"J":0.50, "C":0.30, "I":0.20},
}

# ---------- Personalized PageRank seeds (sum to 1 per user) ----------
PPR_SEEDS = {
    "alex": {"A":0.5, "B":0.5},      # Tech-inclined
    "sam":  {"D":0.5, "E":0.5},      # Sports-inclined
}

# ---------- TrustRank ----------
# Good/whitelist seeds; ground truth spam labels are in NODES[*]["is_spam"] (G,H=True)
TRUSTRANK_GOOD_SEEDS = ["I", "J", "D"]


st.write(NODES)