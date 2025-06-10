"""
sketch.py

Production script for Step 3: Use AI to Generate Scene Sketches
Creates simple black and white sketches for story chapters using AI.

Usage:
    python sketch.py <project> [all]

Examples:
    python sketch.py demo          # Process next chapter without sketch
    python sketch.py demo all      # Process all chapters without sketches
"""
import os
import sys
import glob
from pathlib import Path
from src import ai

def get_all_chapters(project_path):
    """Get all chapter files in order from the project's arcs directory."""
    arcs_dir = os.path.join(project_path, "arcs")
    if not os.path.exists(arcs_dir):
        print(f"Error: Arcs directory not found at {arcs_dir}")
        return []

    chapters = []
    # Get all arc directories in order
    arc_dirs = sorted([
        d for d in os.listdir(arcs_dir)
        if os.path.isdir(os.path.join(arcs_dir, d))
    ])

    for arc_dir in arc_dirs:
        arc_path = os.path.join(arcs_dir, arc_dir)
        # Get all .txt files in order
        chapter_files = sorted(glob.glob(os.path.join(arc_path, "*.txt")))
        for chapter_file in chapter_files:
            chapters.append((arc_dir, os.path.basename(chapter_file), chapter_file))

    return chapters

def get_sketch_path(project_path, arc_name, chapter_file):
    """Get the output path for a sketch."""
    sketches_dir = os.path.join(project_path, "sketches", arc_name)
    sketch_name = Path(chapter_file).stem + ".png"
    return os.path.join(sketches_dir, sketch_name)

def get_sketch_tmp_path(project_path, arc_name, chapter_file):
    """Get the output path for a sketch."""
    sketches_dir = os.path.join(project_path, "tmp/sketches", arc_name)
    sketch_name = Path(chapter_file).stem + ".png"
    return os.path.join(sketches_dir, sketch_name)

def sketch_exists(sketch_path):
    """Check if a sketch already exists."""
    return os.path.exists(sketch_path)

def run():
    project_name = os.getenv('PROJECT', '')
    project_path = os.getenv('PROJECT_PATH', '')
    process_all = os.getenv('SKETCH_ALL', '').lower() == 'true'
    force = os.getenv('SKETCH_FORCE', '').lower() == 'true'

    if not os.path.exists(project_path):
        print(f"Error: Project path not found at {project_path}")
        sys.exit(1)

    # Get all chapters
    chapters = get_all_chapters(project_path)
    if not chapters:
        print("No chapters found.")
        sys.exit(1)

    processed_count = 0

    for arc_name, chapter_file, chapter_path in chapters:
        sketch_path = get_sketch_path(project_path, arc_name, chapter_file)

        if (force and process_all) or not sketch_exists(sketch_path):
            tmp_path = get_sketch_tmp_path(project_path, arc_name, chapter_file)
            ai.create_sketch(
                project=project_name,
                project_path=project_path,
                chapter_path=chapter_path,
                tmp_path=tmp_path,
                output_path=sketch_path)
            processed_count += 1
            if not process_all:
                break
        elif process_all:
            print(f"Sketch already exists: {sketch_path}")

    if processed_count == 0:
        print("No new sketches to create.")
    else:
        print(f"Processed {processed_count} chapter(s).")
