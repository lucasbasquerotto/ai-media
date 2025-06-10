
if __name__ == "__main__":
    import os
    import sys
    from src import sketch

    if len(sys.argv) < 2:
        print("Usage: python sketch.py <project>")
        print("Examples:")
        print("  python sketch.py demo")
        sys.exit(1)

    project_name = sys.argv[1]

    if project_name == "demo":
        project_path = "demo"
    else:
        project_path = os.path.join("projects", project_name)

    os.environ['PROJECT'] = project_name
    os.environ['PROJECT_PATH'] = project_path
    os.environ['SKETCH_ALL'] = 'true'
    os.environ['SKETCH_FORCE'] = 'false'
    os.environ['SKETCH_AI'] = 'void'

    sketch.run()
