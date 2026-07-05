import json
import os

def build_standalone_docs():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dbt_dir = os.path.join(base_dir, "dbt_project")
    target_dir = os.path.join(dbt_dir, "target")

    index_path = os.path.join(target_dir, "index.html")
    manifest_path = os.path.join(target_dir, "manifest.json")
    catalog_path = os.path.join(target_dir, "catalog.json")
    out_path = os.path.join(dbt_dir, "dbt_lineage_docs.html")

    if not (os.path.exists(index_path) and os.path.exists(manifest_path)):
        print("Error: dbt target files missing")
        return

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = f.read()

    catalog_data = "{}"
    if os.path.exists(catalog_path):
        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog_data = f.read()

    # Embed manifest and catalog directly into index.html so it opens offline without web server
    inline_script = f"""
    <script type="text/javascript">
        window.o = {{
            manifest: {manifest},
            catalog: {catalog_data}
        }};
    </script>
    </body>
    """
    standalone_html = html.replace("</body>", inline_script)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(standalone_html)

    print(f"✅ Standalone dbt Docs & Lineage DAG generated: {out_path}")

if __name__ == "__main__":
    build_standalone_docs()
