with open("docker-compose.yaml") as f:
    content = f.read()

old = "  - ${AIRFLOW_PROJ_DIR:-.}/plugins:/opt/airflow/plugins"
new = old + "\n  - ../:/opt/bd_platform"

if old in content and "/opt/bd_platform" not in content:
    content = content.replace(old, new, 1)
    with open("docker-compose.yaml", "w") as f:
        f.write(content)
    print("Mount added successfully")
elif "/opt/bd_platform" in content:
    print("Mount already present")
else:
    print("Pattern not found - manual check needed")
