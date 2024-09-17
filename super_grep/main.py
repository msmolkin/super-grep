#!/usr/bin/env python3

import os
import re
import argparse
import multiprocessing
import mmap
import sys

def transform_pattern(pattern):
    # Normalize the pattern by replacing all separator characters with a common placeholder, e.g., a space
    normalized_pattern = re.sub(r'[-_\s]+', ' ', pattern)
    
    # Split the normalized pattern into words
    words = normalized_pattern.split()
    
    # Transform each word to match any variation of camelCase, snake_case, etc.
    transformed_words = []
    for word in words:
        parts = re.split(r'([A-Z][a-z]*|\d+)', word)
        transformed_parts = [re.escape(part) for part in parts if part]
        transformed_word = r'[-_\s]*'.join(transformed_parts)
        transformed_words.append(transformed_word)
    
    # Join words with a regex that matches any sequence of separator characters
    transformed_pattern = r'[-_\s]*'.join(transformed_words)
    
    # Add case insensitivity flag
    return r'(?i)' + transformed_pattern

def format_output(file_path, line_num, line_content, colorize, hide_path):
    if hide_path:
        file_path = os.path.basename(file_path)
    if colorize:
        # Changing so the matched part of response is green with a bold font will slow down the search even further
        return f"\033[35m{file_path}\033[0m" + (f":\033[32m{line_num}\033[0m:{line_content}" if line_num else "")
    else:
        return f"{file_path}" + (f":{line_num}:{line_content}" if line_num else "")

def search_file(file_path, pattern, search_contents, colorize, stop_on_first_match, hide_path, files_with_matches):
    if search_contents:
        if pattern.search(os.path.basename(file_path)):
            if files_with_matches:
                return [os.path.basename(file_path) if hide_path else file_path]
            return [format_output(file_path, 0, "", colorize, hide_path)]
        return []

    results = []
    try:
        with open(file_path, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                for i, line in enumerate(iter(mm.readline, b''), 1):
                    try:
                        line = line.decode('utf-8')
                    except UnicodeDecodeError:
                        continue
                    if pattern.search(line):
                        if files_with_matches:
                            return [os.path.basename(file_path) if hide_path else file_path]
                        results.append(format_output(file_path, i, line.strip(), colorize, hide_path))
                        if stop_on_first_match:
                            return results
    except (IOError, ValueError):
        pass
    return results

def worker(file_queue, pattern, result_queue, search_contents, colorize, stop_on_first_match, hide_path, files_with_matches):
    while True:
        try:
            file_path = file_queue.get_nowait()
        except:
            break
        results = search_file(file_path, pattern, search_contents, colorize, stop_on_first_match, hide_path, files_with_matches)
        if results:
            result_queue.put(results)

def super_grep(directory, pattern, num_workers, search_contents, colorize, depth, stop_on_first_match, hide_path, files_with_matches):
    transformed_pattern = transform_pattern(pattern)
    regex = re.compile(transformed_pattern)

    file_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    for root, _, files in os.walk(directory):
        rel_path = os.path.relpath(root, directory)
        current_depth = 0 if rel_path == '.' else len(rel_path.split(os.sep))
        if depth is not None and current_depth > depth:
            continue

        for file in files:
            file_path = os.path.join(root, file)
            file_queue.put(file_path)

    processes = []
    for _ in range(num_workers):
        p = multiprocessing.Process(target=worker, args=(file_queue, regex, result_queue, search_contents, colorize, stop_on_first_match, hide_path, files_with_matches))
        p.start()
        processes.append(p)

    printed = 0
    try:
        while any(p.is_alive() for p in processes) or not result_queue.empty():
            try:
                results = result_queue.get_nowait()
                for result in results:
                    print(result, flush=True)
                    printed += 1
            except:
                pass
    except KeyboardInterrupt:
        print("\nInterrupted by user. Stopping gracefully...", file=sys.stderr)
        for p in processes:
            p.terminate()

    for p in processes:
        p.join()

    while not result_queue.empty():
        results = result_queue.get()
        for result in results:
            print(result, flush=True)
            printed += 1

    if printed == 0:
        print("No matches found.")

def main():
    parser = argparse.ArgumentParser(
        description="Super Grep: Python implementation with depth control and format-agnostic search",
        epilog="""
Recommendation: Always include the -C flag for prettier output unless you have a reason not to.

Examples:
  Search only in the given directory:
    super-grep /path/to/search "FooBar|first_name"

  Search up to 2 levels deep:
    super-grep /path/to/search "FooBar|first_name" -d 2

  Search all subdirectories:
    super-grep /path/to/search "FooBar|first_name" -d -1

  Search file contents up to 3 levels deep with colored output:
    super-grep /path/to/search "FooBar|first_name" -d 3 -C

  Use 8 worker processes:
    super-grep /path/to/search "FooBar|first_name" --workers 8
    super-grep /path/to/search "FooBar|first_name" -w 8

  Hide the directory path in the output:
    super-grep /path/to/search "getValueFromSection" -H

  Show only filenames and stop on the first match:
    super-grep /path/to/search "getValueFromSection" -H -s
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("directory", help="Directory to search in")
    parser.add_argument("pattern", help="Search pattern")
    parser.add_argument("-w", "--workers", type=int, default=multiprocessing.cpu_count(), help="Number of worker processes (default: CPU count)")
    parser.add_argument("-f", "--filenames-only", action="store_true", help="Search only within filenames (default: search within file contents)")
    parser.add_argument("-C", "--color", action="store_true", help="Colorize the output")
    parser.add_argument("-d", "--depth", type=int, default=0, help="Depth of directory search (default: 0, search only in given directory; use -1 for unlimited depth)")
    parser.add_argument("-s", "--stop-on-first-match", action="store_true", help="Stop searching a file after the first match is found")
    parser.add_argument("-H", "--hide-path", action="store_true", help="Hide the directory path, showing only the filename")
    parser.add_argument("-l", "--files-with-matches", action="store_true", help="Only the names of files containing matches are written to standard output (the matched lines are not shown).")

    try:
        args = parser.parse_args()
    except SystemExit as e:
        print("Error: An unexpected flag was used or a required argument is missing.")
        print("Please check the command and refer to the help message for valid options.")
        print("Use 'super-grep --help' for more information.")
        sys.exit(1)

    super_grep(args.directory,
               args.pattern,
               args.workers,
               not args.filenames_only,
               args.color,
               args.depth,
               args.stop_on_first_match,
               args.hide_path,
               args.files_with_matches)

def testSuperGrep():
    # Test cases
    test_filenames = [
        "create_periodic_table_data",
        "periodic-Table",
        "periodic Table",
        "periodictable",
        "periodic-table"
    ]
    matches = []
    
    # Pattern to test
    input_patterns = ["periodic-table", "periodic Table", "Periodic Table", "Periodic-Table", "periodiC_table"]
    input_pattern = input_patterns[3]  # 3 and 4 don't match anything
    compiled_pattern = re.compile(transform_pattern(input_pattern))

    # Testing
    for filename in test_filenames:
        match = compiled_pattern.search(filename)
        if match:
            print(f"Testing '\033[32m{filename}\033[0m': Matched")
            matches.append(filename)
        else:
            print(f"Testing '\033[31m{filename}\033[0m': No match")

    print(transform_pattern(input_pattern))
    print("Matches: ", len(matches))

if __name__ == "__main__":
    # testSuperGrep()
    main()