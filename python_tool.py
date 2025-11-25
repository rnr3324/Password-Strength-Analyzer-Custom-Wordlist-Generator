#!/usr/bin/env python3
"""
Password Strength Analyzer + Custom Wordlist Generator
Single-file tool: CLI + optional Tkinter GUI
"""

import argparse
import itertools
import os
import sys

try:
    from zxcvbn import zxcvbn
except Exception as e:
    print("zxcvbn import failed. Install with: pip install zxcvbn  (or zxcvbn-python)")
    raise

# ---------------------------
# Password analysis
# ---------------------------
def analyze_password(password):
    """Return the zxcvbn result dict for a password."""
    if not password:
        return None
    return zxcvbn(password)

def pretty_print_analysis(result):
    if not result:
        print("No password provided.")
        return
    print("Score (0-4):", result["score"])
    print("Entropy:", round(result.get("entropy", 0), 2))
    print("Crack time (display):", result["crack_times_display"]["offline_fast_hashing_1e10_per_second"])
    if result.get("feedback"):
        print("Suggestions:", " | ".join(result["feedback"].get("suggestions", [])))
        warning = result["feedback"].get("warning")
        if warning:
            print("Warning:", warning)

# ---------------------------
# Wordlist generation helpers
# ---------------------------
LEET_MAP = {
    "a": ["a", "@", "4"],
    "b": ["b", "8"],
    "e": ["e", "3"],
    "i": ["i", "1", "!"],
    "l": ["l", "1", "7"],
    "o": ["o", "0"],
    "s": ["s", "5", "$"],
    "t": ["t", "7"],
    "g": ["g", "9"],
}

COMMON_APPEND = ["", "123", "1234", "2023", "2024", "!", "@", "#", "007"]

def leetspeak_variants(word, max_variants=200):
    """Generate leetspeak substitutions for a word, limit result count."""
    if not word:
        return []
    pools = []
    for ch in word.lower():
        pools.append(LEET_MAP.get(ch, [ch]))
    # create combinations (cartesian product)
    combos = itertools.product(*pools)
    results = []
    for i, tup in enumerate(combos):
        results.append("".join(tup))
        if i+1 >= max_variants:
            break
    return list(dict.fromkeys(results))  # remove duplicates while preserving order

def capitalize_variants(word):
    """Return capitalization variants: lower, title, upper, random-like."""
    s = word
    return list(dict.fromkeys([s.lower(), s.title(), s.upper(), s.capitalize()]))

def build_base_words(user_inputs):
    """Collect base words from user input dict and simple cleanups."""
    words = set()
    for v in user_inputs.values():
        if not v:
            continue
        # if it's a multi-word string split and add parts
        for part in str(v).split():
            part = part.strip()
            if part:
                words.add(part)
    return list(words)

def add_common_patterns(words):
    """Append and prepend common patterns to each word."""
    out = set()
    for w in words:
        for ext in COMMON_APPEND:
            out.add(w + ext)
            out.add(ext + w)
    return list(out)

def generate_wordlist(user_inputs, max_per_base=500):
    """
    Generate a list of candidate words from user inputs.
    user_inputs: dict with keys like name, dob, pet, fav, numbers
    """
    base_words = build_base_words(user_inputs)
    generated = set()

    # 1) For each base word add capitalization and leet variants
    for base in base_words:
        # capitalization variants
        for cap in capitalize_variants(base):
            generated.add(cap)
        # leet variants (lower-case results from leetspeak_variants)
        for l in leetspeak_variants(base, max_variants=200):
            generated.add(l)
            # also add capitalization of leet variants
            for cap in capitalize_variants(l):
                generated.add(cap)

    # 2) Combine base words with each other (pairwise concatenations)
    for a, b in itertools.permutations(base_words, 2):
        generated.add(a + b)
        generated.add(b + a)

    # 3) Append/prepend common patterns to generated words
    with_patterns = set(add_common_patterns(list(generated)))

    # 4) Add numeric-only patterns from user inputs (like DOB variants)
    for key in ("dob", "birthyear", "year", "numbers", "phone"):
        if key in user_inputs and user_inputs[key]:
            val = str(user_inputs[key])
            with_patterns.add(val)
            # common slices
            if len(val) >= 4:
                with_patterns.add(val[-2:])  # last two digits
                with_patterns.add(val[-4:])  # last four digits

    # limit size if huge
    final_list = list(with_patterns)
    if len(final_list) > max_per_base:
        final_list = final_list[:max_per_base]

    # ensure uniqueness and return
    return list(dict.fromkeys(final_list))

# ---------------------------
# Export
# ---------------------------
def export_wordlist(wordlist, filename="custom_wordlist.txt"):
    if not wordlist:
        print("No words to export.")
        return
    with open(filename, "w", encoding="utf-8") as f:
        for w in wordlist:
            f.write(w + "\n")
    print(f"Exported {len(wordlist)} entries to {filename}")

# ---------------------------
# CLI handling
# ---------------------------
def cli_main(args):
    # Collect user inputs
    user_inputs = {
        "name": args.name or "",
        "dob": args.dob or "",
        "pet": args.pet or "",
        "fav": args.fav or "",
        "numbers": args.numbers or "",
        "phone": args.phone or "",
    }

    # Password analysis if provided
    if args.password:
        print("\n=== Password Analysis ===")
        res = analyze_password(args.password)
        pretty_print_analysis(res)

    # Generate wordlist if requested
    if args.generate or args.name or args.pet or args.fav or args.dob or args.numbers or args.phone:
        print("\n=== Generating Wordlist ===")
        wordlist = generate_wordlist(user_inputs, max_per_base=args.max_words)
        print(f"Generated {len(wordlist)} candidate words.")
        if args.show:
            print("\n--- Sample words ---")
            for i, w in enumerate(wordlist[:min(50, len(wordlist))], 1):
                print(f"{i}. {w}")
        export_wordlist(wordlist, args.output)

# ---------------------------
# Simple Tkinter GUI
# ---------------------------
def run_gui():
    try:
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox
    except Exception:
        print("tkinter not available on this system.")
        return

    def on_analyze():
        pwd = pwd_entry.get()
        if not pwd:
            messagebox.showinfo("Info", "Enter a password to analyze.")
            return
        res = analyze_password(pwd)
        score_str = str(res["score"]) if res else "N/A"
        entropy_str = str(round(res.get("entropy", 0), 2)) if res else "N/A"
        crack = res["crack_times_display"]["offline_fast_hashing_1e10_per_second"] if res else "N/A"
        score_label.config(text=f"Score: {score_str}  Entropy: {entropy_str}")
        crack_label.config(text=f"Crack (est): {crack}")
        # color bar simple mapping
        color = {0: "#ff4d4d", 1: "#ff944d", 2: "#ffdb4d", 3: "#a3ff4d", 4: "#4dff88"}.get(res["score"], "#ddd")
        meter.config(bg=color)

    def on_generate():
        ui = {
            "name": name_entry.get(),
            "dob": dob_entry.get(),
            "pet": pet_entry.get(),
            "fav": fav_entry.get(),
            "numbers": numbers_entry.get(),
            "phone": phone_entry.get(),
        }
        words = generate_wordlist(ui, max_per_base=2000)
        messagebox.showinfo("Generated", f"Generated {len(words)} words. Choose file to save.")
        fpath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files","*.txt")], title="Save wordlist as")
        if fpath:
            export_wordlist(words, fpath)

    root = tk.Tk()
    root.title("Password Analyzer & Wordlist Generator")

    frm = ttk.Frame(root, padding=12)
    frm.grid(row=0, column=0, sticky="nsew")

    ttk.Label(frm, text="Password:").grid(row=0, column=0, sticky="w")
    pwd_entry = ttk.Entry(frm, width=30, show="*")
    pwd_entry.grid(row=0, column=1, sticky="w")
    ttk.Button(frm, text="Analyze", command=on_analyze).grid(row=0, column=2, padx=6)

    score_label = ttk.Label(frm, text="Score: N/A")
    score_label.grid(row=1, column=1, sticky="w")
    crack_label = ttk.Label(frm, text="Crack (est): N/A")
    crack_label.grid(row=2, column=1, sticky="w")

    meter = tk.Frame(frm, width=200, height=15, bg="#eee")
    meter.grid(row=1, column=2, rowspan=2, padx=6)

    # User inputs for wordlist
    ttk.Label(frm, text="Name:").grid(row=3, column=0, sticky="w")
    name_entry = ttk.Entry(frm, width=25); name_entry.grid(row=3, column=1, sticky="w")
    ttk.Label(frm, text="DOB/Year:").grid(row=4, column=0, sticky="w")
    dob_entry = ttk.Entry(frm, width=25); dob_entry.grid(row=4, column=1, sticky="w")
    ttk.Label(frm, text="Pet name:").grid(row=5, column=0, sticky="w")
    pet_entry = ttk.Entry(frm, width=25); pet_entry.grid(row=5, column=1, sticky="w")
    ttk.Label(frm, text="Favorite word:").grid(row=6, column=0, sticky="w")
    fav_entry = ttk.Entry(frm, width=25); fav_entry.grid(row=6, column=1, sticky="w")
    ttk.Label(frm, text="Other numbers:").grid(row=7, column=0, sticky="w")
    numbers_entry = ttk.Entry(frm, width=25); numbers_entry.grid(row=7, column=1, sticky="w")
    ttk.Label(frm, text="Phone last digits:").grid(row=8, column=0, sticky="w")
    phone_entry = ttk.Entry(frm, width=25); phone_entry.grid(row=8, column=1, sticky="w")

    ttk.Button(frm, text="Generate Wordlist & Save", command=on_generate).grid(row=9, column=1, pady=8)

    root.mainloop()

# ---------------------------
# Entrypoint
# ---------------------------
def main():
    parser = argparse.ArgumentParser(description="Password Analyzer & Custom Wordlist Generator")
    parser.add_argument("--password", "-p", help="Password to analyze")
    parser.add_argument("--name", help="Name (for wordlist)")
    parser.add_argument("--dob", help="DOB or birth year")
    parser.add_argument("--pet", help="Pet name")
    parser.add_argument("--fav", help="Favorite word")
    parser.add_argument("--numbers", help="Other numbers (lucky etc.)")
    parser.add_argument("--phone", help="Phone last digits")
    parser.add_argument("--generate", "-g", action="store_true", help="Generate wordlist from provided inputs")
    parser.add_argument("--output", "-o", default="custom_wordlist.txt", help="Output .txt filename")
    parser.add_argument("--show", action="store_true", help="Show sample generated words")
    parser.add_argument("--max-words", type=int, default=1000, help="Max words to generate (limit)")
    parser.add_argument("--gui", action="store_true", help="Launch Tkinter GUI")
    args = parser.parse_args()

    if args.gui:
        run_gui()
        return

    # run CLI flow
    cli_main(args)

if __name__ == "__main__":
    main()
