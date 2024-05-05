"""Generate the code reference pages and navigation."""

from pathlib import Path
import os
import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

for path in sorted(Path("ark_sdk_python").rglob("*.py")):
    if "examples" in path.as_posix():
        continue
    module_path = path.relative_to("ark_sdk_python").with_suffix("")
    doc_path = path.relative_to("ark_sdk_python").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue
    if len(parts) == 0:
        parts = ('.')
    nav[parts] = doc_path.as_posix()
    os.makedirs(os.path.dirname(full_doc_path), exist_ok=True)
    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        if ident != '.':
            fd.write(f"::: ark_sdk_python.{ident}")
        else:
            fd.write(f"::: ark_sdk_python")

    mkdocs_gen_files.set_edit_path(Path("reference", doc_path), Path('../', path))

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
