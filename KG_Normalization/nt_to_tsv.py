"""
Convert an N-Triples file into a tab-separated triples file (subject <TAB> predicate <TAB> object).
Inverse of tsv_to_nt.py.
"""
import argparse
import os
import re
import sys
from urllib.parse import unquote

RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

TERM = r'(<[^>]*>|_:\S+|"(?:[^"\\]|\\.)*"(?:@[A-Za-z0-9-]+|\^\^<[^>]*>)?)'
TRIPLE_RE = re.compile(rf"^\s*{TERM}\s+(<[^>]*>)\s+{TERM}\s*\.\s*$")
LITERAL_RE = re.compile(r'^"((?:[^"\\]|\\.)*)"(?:@[A-Za-z0-9-]+|\^\^<[^>]*>)?$')


def from_term(term, prefix):
    """Turn an N-Triples term into a bare TSV value. Prefix is stripped from IRIs and %-escapes decoded."""
    if term.startswith("<"):
        iri = term[1:-1]
        if prefix and iri.startswith(prefix):
            iri = iri[len(prefix):]
        return unquote(iri)
    if term.startswith("_:"):
        return term
    # Literal: keep the lexical form, drop language tag / datatype, and make it TSV-safe.
    text = LITERAL_RE.match(term).group(1)
    text = (text.replace("\\t", " ").replace("\\n", " ").replace("\\r", " ")
                .replace('\\"', '"').replace("\\\\", "\\"))
    return text


def convert(nt_path, tsv_path, prefix="", type_predicate="type"):
    """
    Convert an N-Triples file into a TSV file of triples.

    Args:
        nt_path (str): Path to the input N-Triples file.
        tsv_path (str): Path of the TSV file to write. Parent folders are created.
        prefix (str): Namespace stripped from the start of IRIs. Empty keeps full IRIs.
        type_predicate (str): Name written for rdf:type. Empty string keeps the full IRI.

    Returns:
        tuple: (number of triples written, number of lines skipped).
    """
    written = skipped = 0
    seen = set()
    os.makedirs(os.path.dirname(os.path.abspath(tsv_path)), exist_ok=True)

    with open(nt_path, "r", encoding="utf-8") as nt, open(tsv_path, "w", encoding="utf-8") as tsv:
        for line_number, line in enumerate(nt, start=1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            match = TRIPLE_RE.match(line)
            if not match:
                print(f"Skipping line {line_number}: not a valid N-Triples statement", file=sys.stderr)
                skipped += 1
                continue

            s, p, o = match.groups()
            if type_predicate and p == f"<{RDF_TYPE}>":
                predicate = type_predicate
            else:
                predicate = from_term(p, prefix)
            row = "\t".join((from_term(s, prefix), predicate, from_term(o, prefix)))

            if row in seen:
                skipped += 1
                continue
            seen.add(row)
            tsv.write(row + "\n")
            written += 1

    return written, skipped


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert an N-Triples file into a TSV triples file.")
    parser.add_argument("nt", help="input .nt file")
    parser.add_argument("tsv", help="output .tsv file (subject, predicate, object)")
    parser.add_argument("--prefix", default="",
                        help="namespace stripped from IRIs, e.g. http://FrenchRoyalty.org/ (default: keep full IRIs)")
    parser.add_argument("--type-predicate", default="type",
                        help="name written for rdf:type (default: 'type'; use '' to keep the full IRI)")
    args = parser.parse_args()

    n_written, n_skipped = convert(args.nt, args.tsv, args.prefix, args.type_predicate)
    print(f"Wrote {n_written} triples to {args.tsv} ({n_skipped} lines skipped)")
