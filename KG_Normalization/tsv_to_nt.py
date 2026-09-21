"""
Convert a tab-separated triples file (subject <TAB> predicate <TAB> object) into N-Triples,
the format expected by Symbolic_predictions.py.
"""
import argparse
import os
import sys
from urllib.parse import quote

RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"


def to_iri(term, prefix):
    """Build an IRI from a bare name. Characters that are illegal in IRIs are percent-encoded."""
    if term.startswith(("http://", "https://")):
        return f"<{term}>"
    return f"<{prefix}{quote(term, safe='_-.~:()')}>"


def convert(tsv_path, nt_path, prefix, type_predicate="type"):
    """
    Convert a TSV file of triples into an N-Triples file.

    Args:
        tsv_path (str): Path to the input TSV file (three tab-separated columns per line).
        nt_path (str): Path of the N-Triples file to write. Parent folders are created.
        prefix (str): Namespace prepended to every bare subject, predicate and object.
        type_predicate (str): Predicate name mapped to rdf:type. Empty string disables the mapping.

    Returns:
        tuple: (number of triples written, number of lines skipped).
    """
    written = skipped = 0
    seen = set()
    os.makedirs(os.path.dirname(os.path.abspath(nt_path)), exist_ok=True)

    with open(tsv_path, "r", encoding="utf-8") as tsv, open(nt_path, "w", encoding="utf-8") as nt:
        for line_number, line in enumerate(tsv, start=1):
            line = line.rstrip("\r\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) != 3 or not all(p.strip() for p in parts):
                print(f"Skipping line {line_number}: expected 3 tab-separated fields, got {len(parts)}",
                      file=sys.stderr)
                skipped += 1
                continue

            s, p, o = (part.strip() for part in parts)
            predicate = f"<{RDF_TYPE}>" if type_predicate and p == type_predicate else to_iri(p, prefix)
            triple = f"{to_iri(s, prefix)} {predicate} {to_iri(o, prefix)} ."

            if triple in seen:
                skipped += 1
                continue
            seen.add(triple)
            nt.write(triple + "\n")
            written += 1

    return written, skipped


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a TSV triples file into N-Triples.")
    parser.add_argument("tsv", help="input .tsv file (subject, predicate, object)")
    parser.add_argument("nt", help="output .nt file")
    parser.add_argument("--prefix", required=True,
                        help="namespace for bare names, e.g. http://FrenchRoyalty.org/")
    parser.add_argument("--type-predicate", default="type",
                        help="predicate name mapped to rdf:type (default: 'type'; use '' to disable)")
    args = parser.parse_args()

    n_written, n_skipped = convert(args.tsv, args.nt, args.prefix, args.type_predicate)
    print(f"Wrote {n_written} triples to {args.nt} ({n_skipped} lines skipped)")
