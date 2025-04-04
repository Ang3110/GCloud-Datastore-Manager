#!/usr/bin/env python3
import os
import csv
import sys
import time
import concurrent.futures
from google.cloud import datastore

# -------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------

def safe_input(prompt):
    """
    A safe wrapper around input() that exits gracefully when Ctrl+C is pressed.
    """
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print("\nExiting.")
        sys.exit(0)

def clear_screen():
    """
    Clears the terminal screen.
    """
    os.system('clear')

def show_about():
    """
    Displays an About page with information on GCloud Datastore Manager,
    including a description of the DOCUMENT command.
    """
    clear_screen()
    about_text = (
        "=== ABOUT GCloud Datastore Manager ===\n\n"
        "GCloud Datastore Manager is a backend tool for managing your Google Cloud Datastore, by Angello.\n"
        "It allows you to view, export, import, and delete datastore kinds and namespaces using a terminal-based menu system.\n"
        "Filter lists, create new namespaces or kinds, and perform bulk operations—all from a streamlined interface\n"
        "that maximizes your terminal's workspace.\n\n"
        "Commands:\n"
        "  NEW <n>        - Create a new namespace or kind with the given name.\n"
        "  RM                - Remove one or more items (using comma or range notation).\n"
        "  SEARCH <keywords> - Filter lists by keywords (special characters are allowed).\n"
        "  DOCUMENT          - Display developer documentation (available in namespace list).\n"
        "  CAB               - Reset filter / return to previous menu.\n"
        "  ABOUT             - Show this about page.\n"
        "  Ctrl+C            - Exit the application at any time.\n\n"
        "Press Enter to return to the main menu..."
    )
    safe_input(about_text)
    clear_screen()

def show_documentation():
    """
    Displays detailed developer documentation explaining the tool's features and code structure.
    This command is available only in the main namespace list.
    """
    clear_screen()
    doc_text = (
        "=== Developer Documentation ===\n\n"
        "Features:\n"
        "  - View, export, import, and delete datastore kinds and namespaces.\n"
        "  - Bulk deletion, filtering, and search functionality for namespaces, kinds, and CSV files.\n"
        "  - Two setup modes: enter a GCP Project ID to use Application Default Credentials (ADC),\n"
        "    or select a service account JSON key to use explicit credentials.\n\n"
        "Code Structure:\n"
        "  1. Helper Functions: Manage input, screen clearing, and display of About/Documentation pages.\n"
        "  2. Utility Functions: Filtering lists, listing namespaces/kinds, parsing user selections, and progress animations.\n"
        "  3. Datastore Operation Functions: Removing, exporting, and importing datastore entities.\n"
        "  4. Sub-Menu Functions: Menus for namespace operations (export, import, deletion).\n"
        "     The DOCUMENT command is available only in the main namespace list.\n\n"
        "Press Enter to return to the namespace list..."
    )
    safe_input(doc_text)
    clear_screen()

# -------------------------------------------------------------------
# Utility / Common Functions (continued)
# -------------------------------------------------------------------

def filter_list_by_keyword(items, keyword):
    """
    Returns a list of items that contain the given keyword (case-insensitive).
    """
    if not keyword:
        return items
    return [item for item in items if keyword.lower() in item.lower()]

def list_namespaces(client):
    """
    Retrieves all namespaces from the datastore using a keys-only query.
    Ensures the default namespace (empty string) is included.
    """
    query = client.query(kind="__namespace__")
    query.keys_only()
    namespaces = []
    for entity in query.fetch():
        ns_name = entity.key.name or ""
        namespaces.append(ns_name)
    if "" not in namespaces:
        namespaces.append("")
    namespaces.sort(key=lambda x: (x != "", x))
    return namespaces

def list_kinds_in_namespace(client, namespace):
    """
    Retrieves all kinds within the specified namespace using a keys-only query.
    """
    query = client.query(kind="__kind__", namespace=namespace)
    query.keys_only()
    kinds = []
    for entity in query.fetch():
        kinds.append(entity.key.name)
    kinds.sort()
    return kinds

def parse_selection(selection_str, max_index):
    """
    Parses a user input selection string into a list of indices.
    Accepts single numbers, comma-separated lists, and ranges (e.g., 1,3-5).
    Returns None if the user inputs 'CAB'.
    """
    selection_str = selection_str.strip().upper()
    if selection_str == "CAB":
        return None
    if selection_str == "ALL":
        return list(range(1, max_index + 1))
    indices = set()
    parts = [p.strip() for p in selection_str.split(",")]
    for part in parts:
        if "-" in part:
            try:
                start_str, end_str = part.split("-")
                start, end = int(start_str), int(end_str)
                if start > end:
                    start, end = end, start
                for i in range(start, end + 1):
                    if 1 <= i <= max_index:
                        indices.add(i)
            except ValueError:
                pass
        else:
            try:
                val = int(part)
                if 1 <= val <= max_index:
                    indices.add(val)
            except ValueError:
                pass
    return sorted(indices)

def animate_progress(task, duration=3):
    """
    Displays a simple progress animation for a given task.
    """
    print(task, end="", flush=True)
    for _ in range(duration * 2):
        print(".", end="", flush=True)
        time.sleep(0.5)
    print("")

def select_key_credentials(directory="."):
    """
    Searches for .json files (service account keys) in the specified directory.
    - If one file is found, returns its absolute path automatically.
    - If multiple files are found, displays a searchable list.
      In search mode, typing 'CAB' resets the list to the full list.
      If the full list is already displayed and 'CAB' is entered, returns "CAB_BACK"
      to signal going back to the initial menu.
    Returns:
        The absolute path of the selected JSON file, or "CAB_BACK" if cancelled.
    """
    json_files = [f for f in os.listdir(directory)
                  if f.lower().endswith(".json") and os.path.isfile(os.path.join(directory, f))]
    original_files = json_files[:]  # Save the full list for resets
    if not json_files:
        print("No key credential JSON files found in the directory.")
        return None
    if len(json_files) == 1:
        print("Automatically using key credential JSON file: " + json_files[0])
        return os.path.abspath(os.path.join(directory, json_files[0]))
    
    filtered_files = json_files[:]
    while True:
        clear_screen()
        print("=== Available Key Credential JSON files ===")
        for i, filename in enumerate(filtered_files, start=1):
            print(f"{i}. {filename}")
            
        print("\nType the following:")
        print("any number from the list")
        print("SEARCH <keywords to filter>")
        print("CAB to go back")
        
        selection = safe_input("\nselection: ").strip()
        if selection.upper() == "CAB":
            if filtered_files != original_files:
                # If in search mode, reset to original list instead of going back.
                filtered_files = original_files[:]
                continue
            else:
                return "CAB_BACK"
        if selection.upper().startswith("SEARCH"):
            parts = selection.split(maxsplit=1)
            if len(parts) < 2:
                print("No keyword provided for search. Resetting to original list.")
                filtered_files = original_files[:]
                continue
            keyword = parts[1].strip().lower()
            new_filtered = [f for f in original_files if keyword in f.lower()]
            if not new_filtered:
                print("No files match your search. Resetting to original list.")
                filtered_files = original_files[:]
            else:
                filtered_files = new_filtered
            continue
        try:
            index = int(selection) - 1
            if 0 <= index < len(filtered_files):
                return os.path.abspath(os.path.join(directory, filtered_files[index]))
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input. Please enter a number, 'SEARCH <keywords>' or 'CAB'.")

# -------------------------------------------------------------------
# Datastore Operation Functions
# -------------------------------------------------------------------

def remove_all_entities_in_kind(client, namespace, kind_name, silent=False):
    """
    Removes all entities for a specific kind within a namespace.
    """
    if not silent:
        print(f"\nRemoving all entities for [namespace={namespace or '(default)'}], kind {kind_name}...")
    batch_size = 500
    total_deleted = 0
    while True:
        query = client.query(kind=kind_name, namespace=namespace)
        query.keys_only()
        entities = list(query.fetch(limit=batch_size))
        if not entities:
            break
        keys = [e.key for e in entities]
        client.delete_multi(keys)
        total_deleted += len(keys)
    if not silent:
        print(f"Removed {total_deleted} entities for kind {kind_name}.\n")
    return total_deleted

def remove_namespace(client, namespace):
    """
    Deletes all kinds and their entities within a namespace.
    """
    print(f"\nRemoving namespace {namespace or '(default)'} (deleting all kinds/entities).")
    kinds = list_kinds_in_namespace(client, namespace)
    total_deleted = 0
    for kind_name in kinds:
        total_deleted += remove_all_entities_in_kind(client, namespace, kind_name, silent=True)
    print(f"Removed namespace {namespace or '(default)'}. Total entities deleted: {total_deleted}.\n")

def export_kind_to_csv(client, namespace, kind_name, csv_file_path):
    """
    Exports entities of a specific kind to a CSV file.
    Uses threading for improved performance.
    """
    print(f"\nExporting [namespace={namespace or '(default)'}] kind {kind_name} → {csv_file_path}")
    
    # Fetch all entities (this is a network bottleneck)
    query = client.query(kind=kind_name, namespace=namespace)
    entities = list(query.fetch())
    
    if not entities:
        print(f"No entities found in kind {kind_name}")
        with open(csv_file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["EntityKey"])  # Write header with just the key
        print(f"Export completed: 0 entities.\n")
        return
    
    # Find all unique property names across all entities
    all_props = set()
    for e in entities:
        all_props.update(e.keys())
    
    # Prepare column headers
    columns = sorted(all_props)
    columns.insert(0, "EntityKey")
    
    total_entities = len(entities)
    print(f"Processing {total_entities} entities...")
    
    # Split entities into batches for parallel processing
    batch_size = 100
    batches = [entities[i:i + batch_size] for i in range(0, len(entities), batch_size)]
    
    # Function to process a batch of entities and return rows
    def process_batch(batch_entities):
        rows = []
        for e in batch_entities:
            entity_key = e.key.name or e.key.id
            row = [entity_key]
            for col in columns[1:]:
                row.append(e.get(col, ""))
            rows.append(row)
        return rows
    
    # Process batches in parallel
    all_rows = []
    all_rows.append(columns)  # Add header row
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_batch, batch) for batch in batches]
        
        # Show progress as batches complete
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            batch_rows = future.result()
            all_rows.extend(batch_rows)
            progress = (i + 1) / len(batches) * 100
            print(f"\rProcessing: {progress:.1f}% complete", end="", flush=True)
    
    # Write all rows to CSV
    print("\nWriting data to CSV file...")
    with open(csv_file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(all_rows)
    
    print(f"Export completed: {total_entities} entities.\n")

def import_csv_to_kind(client, namespace, csv_file_path, kind_name):
    """
    Imports entities from a CSV file into a specific kind.
    Uses threading for improved performance.
    """
    print(f"\nImporting CSV {csv_file_path} → [namespace={namespace or '(default)'}] kind {kind_name}")
    
    # Read all rows from the CSV file
    with open(csv_file_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "EntityKey" not in reader.fieldnames:
            raise ValueError("CSV must have a column named EntityKey.")
        rows = list(reader)
    
    if not rows:
        print(f"No data to import from {csv_file_path}")
        return
    
    total_rows = len(rows)
    print(f"Processing {total_rows} records...")
    
    # Define a batch size for processing
    batch_size = 50
    batches = [rows[i:i + batch_size] for i in range(0, len(rows), batch_size)]
    
    # Function to process a batch of rows
    def process_batch(batch_rows):
        batch_count = 0
        entities = []
        
        for row in batch_rows:
            raw_key = row["EntityKey"]
            props = {k: v for k, v in row.items() if k != "EntityKey"}
            
            if raw_key.isdigit():
                key = client.key(kind_name, int(raw_key), namespace=namespace)
            else:
                key = client.key(kind_name, raw_key, namespace=namespace)
                
            entity = datastore.Entity(key=key)
            for k, v in props.items():
                entity[k] = v
            
            entities.append(entity)
            batch_count += 1
        
        # Use put_multi for better performance
        if entities:
            client.put_multi(entities)
        
        return batch_count
    
    # Process batches in parallel
    count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_batch, batch) for batch in batches]
        
        # Show progress as batches complete
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            count += future.result()
            progress = (i + 1) / len(batches) * 100
            print(f"\rProgress: {progress:.1f}% ({count}/{total_rows} entities)", end="", flush=True)
    
    print(f"\nImport completed. Inserted/updated {count} entities.\n")

# -------------------------------------------------------------------
# Sub-Menu Functions (Namespace-Level)
# -------------------------------------------------------------------

def menu_remove_kinds(client, namespace):
    """
    Menu to remove one or multiple kinds from a namespace.
    """
    clear_screen()
    kinds = list_kinds_in_namespace(client, namespace)
    if not kinds:
        print(f"No kinds found in [namespace={namespace or '(default)'}].")
        safe_input("Press Enter to return...")
        return
        
    original_kinds = kinds[:]  # Save the original list for reset
    filtered_kinds = kinds[:]  # Current working list
    search_active = False
    
    while True:
        clear_screen()
        print(f"=== Remove Kinds [namespace={namespace or '(default)'}] ===")
        for i, k in enumerate(filtered_kinds, start=1):
            print(f"{i}. {k}")
            
        print("\nType one of the following commands:")
        print("ALL to remove all")
        print("any number from the list or comma/range notation (e.g. 1,3-5) to select kinds")
        print("SEARCH <keywords to filter>")
        print("CAB reset filter/go back")
        
        choice = safe_input("\nselection: ").strip()
        if choice.upper() == "CAB":
            if search_active:
                # Reset filter
                filtered_kinds = original_kinds[:]
                search_active = False
                continue
            else:
                # Go back
                return
                
        if choice.upper().startswith("SEARCH"):
            search_term = choice[6:].strip()
            filtered_kinds = filter_list_by_keyword(original_kinds, search_term)
            if not filtered_kinds:
                print("No kinds match the search keyword.")
                filtered_kinds = original_kinds[:]  # Reset filter on no matches
                search_active = False
            else:
                search_active = True
            continue
            
        # Process selection
        selected_indices = parse_selection(choice, len(filtered_kinds))
        if selected_indices is None:
            return
        if not selected_indices:
            print("No valid selection.")
            continue
            
        print("You have selected the following kinds for deletion:")
        selected_kinds = [filtered_kinds[idx - 1] for idx in selected_indices]
        print(", ".join(selected_kinds))
        confirm = safe_input("Remove these kinds? [Y/N]: ").strip().upper()
        if confirm == "Y":
            for kind_name in selected_kinds:
                remove_all_entities_in_kind(client, namespace, kind_name)
        else:
            print("Deletion cancelled.")
        # Reset the filtered list after deletion
        kinds = list_kinds_in_namespace(client, namespace)
        if not kinds:
            print(f"No kinds found in [namespace={namespace or '(default)'}].")
            safe_input("Press Enter to return...")
            return
        original_kinds = kinds[:]
        filtered_kinds = kinds[:]
        search_active = False
        clear_screen()

def menu_export_kinds(client, namespace):
    """
    Menu to export one or multiple kinds to CSV files.
    """
    clear_screen()
    kinds = list_kinds_in_namespace(client, namespace)
    if not kinds:
        print(f"No kinds found in [namespace={namespace or '(default)'}].")
        safe_input("Press Enter to return...")
        return
        
    original_kinds = kinds[:]  # Save the original list for reset
    filtered_kinds = kinds[:]  # Current working list
    search_active = False
    
    while True:
        clear_screen()
        print(f"=== Export Kinds [namespace={namespace or '(default)'}] ===")
        for i, k in enumerate(filtered_kinds, start=1):
            print(f"{i}. {k}")
            
        print("\nType one of the following commands:")
        print("ALL to export all")
        print("any number from the list or comma/range notation (e.g. 1,3-5) to select kinds")
        print("SEARCH <keywords to filter>")
        print("CAB reset filter/go back")
        
        choice = safe_input("\nselection: ").strip()
        if choice.upper() == "CAB":
            if search_active:
                # Reset filter
                filtered_kinds = original_kinds[:]
                search_active = False
                continue
            else:
                # Go back
                return
                
        if choice.upper().startswith("SEARCH"):
            search_term = choice[6:].strip()
            filtered_kinds = filter_list_by_keyword(original_kinds, search_term)
            if not filtered_kinds:
                print("No kinds match the search keyword.")
                filtered_kinds = original_kinds[:]  # Reset filter on no matches
                search_active = False
            else:
                search_active = True
            continue
            
        # Process selection
        selected_indices = parse_selection(choice, len(filtered_kinds))
        if selected_indices is None:
            return
        if not selected_indices:
            print("No valid selection.")
            continue
            
        os.makedirs("export", exist_ok=True)
        for idx in selected_indices:
            kind_name = filtered_kinds[idx - 1]
            default_csv_name = f"{kind_name}.csv" if not namespace else f"{namespace}_{kind_name}.csv"
            csv_name = safe_input(f"Enter CSV filename for kind {kind_name} (default: {default_csv_name}): ").strip()
            if not csv_name:
                csv_name = default_csv_name
            if not csv_name.lower().endswith(".csv"):
                csv_name += ".csv"
            csv_file_path = os.path.join("export", csv_name)
            export_kind_to_csv(client, namespace, kind_name, csv_file_path)
        
        safe_input("Press Enter to continue...")

def menu_import_kinds(client, namespace):
    """
    Menu to import CSV files into a selected namespace.
    """
    clear_screen()
    while True:
        print(f"=== Import Menu [namespace={namespace or '(default)'}] ===")
        print("Select folder to import from:")
        print("1) import folder")
        print("2) export folder")
        print("CAB) to go back to the previous menu.")
        choice = safe_input("\nselection: ").strip().upper()
        if choice == "CAB":
            return
        if choice not in ["1", "2"]:
            print("Invalid choice. Please try again.")
            continue
        folder = "import" if choice == "1" else "export"
        os.makedirs(folder, exist_ok=True)
        files = [f for f in os.listdir(folder) if f.lower().endswith(".csv")]
        if not files:
            print(f"No CSV files found in ./{folder}.")
            continue
        original_files = files[:]  # Save the original list for reset
        filtered_files = files[:]  # Current working list
        search_active = False
        
        while True:
            clear_screen()
            print(f"=== CSV Files in ./{folder} ===")
            for i, f in enumerate(filtered_files, start=1):
                print(f"{i}. {f}")
                
            print("\nType one of the following commands:")
            print("ALL to import all")
            print("any number from the list or comma/range notation (e.g. 1,3-5) to select CSV files")
            print("SEARCH <keywords to filter>")
            print("CAB reset filter/go back")
            
            sel = safe_input("\nselection: ").strip().upper()
            if sel == "CAB":
                if search_active:
                    # Reset filter 
                    filtered_files = original_files[:]
                    search_active = False
                    continue
                else:
                    # Go back to folder selection
                    break
                    
            if sel.startswith("SEARCH"):
                search_term = sel[6:].strip()
                filtered_files = filter_list_by_keyword(original_files, search_term)
                if not filtered_files:
                    print("No files match your search. Resetting to original list.")
                    filtered_files = original_files[:]
                else:
                    search_active = True
                continue
                
            # Process selection
            selected_indices = parse_selection(sel, len(filtered_files))
            if selected_indices is None:
                break  # Go back to folder selection
            if not selected_indices:
                print("No valid selection.")
                continue
                
            selected_files = [filtered_files[idx - 1] for idx in selected_indices]
            for csv_file in selected_files:
                csv_path = os.path.join(folder, csv_file)
                csv_file_without_ext = os.path.splitext(os.path.basename(csv_file))[0]
                
                # For existing kinds menu with search function
                kinds = list_kinds_in_namespace(client, namespace)
                original_kinds = kinds[:]
                filtered_kinds = kinds[:]
                search_active_kinds = False
                
                while True:
                    clear_screen()
                    print(f"=== Existing kinds in [namespace={namespace or '(default)'}] ===")
                    if filtered_kinds:
                        for i, k in enumerate(filtered_kinds, start=1):
                            print(f"{i}. {k}")
                    else:
                        print("(No kinds exist yet)")
                    
                    print("\nType one of the following commands:")
                    print("any number from the list to select a kind")
                    print("NEW <new kind>")
                    print("SEARCH <keywords to filter>")
                    print("CAB reset filter/go back")
                    print(f"Press Enter to use '{csv_file_without_ext}' as the kind name")
                    
                    kind_choice = safe_input(f"\nSelect or create a kind for {csv_file}: ").strip()
                    
                    if kind_choice == "":
                        # User pressed Enter without typing anything, use CSV filename without extension
                        import_csv_to_kind(client, namespace, csv_path, csv_file_without_ext)
                        break
                        
                    if kind_choice.upper() == "CAB":
                        if search_active_kinds:
                            # Reset filter
                            filtered_kinds = original_kinds[:]
                            search_active_kinds = False
                            continue
                        else:
                            # Go back to file selection
                            break
                            
                    if kind_choice.upper().startswith("SEARCH"):
                        search_term = kind_choice[6:].strip()
                        filtered_kinds = filter_list_by_keyword(original_kinds, search_term)
                        if not filtered_kinds and original_kinds:
                            print("No kinds match the search keyword.")
                            filtered_kinds = original_kinds[:]  # Reset filter on no matches
                            search_active_kinds = False
                        else:
                            search_active_kinds = True
                        continue
                        
                    if kind_choice.upper().startswith("NEW"):
                        parts = kind_choice.split(maxsplit=1)
                        if len(parts) == 2:
                            new_kind = parts[1].strip()
                        else:
                            default_kind = csv_file_without_ext
                            new_kind = safe_input(f"Enter new kind name (default: {default_kind}): ").strip() or default_kind
                        if not new_kind:
                            print("No kind name provided, skipping.\n")
                            break
                        import_csv_to_kind(client, namespace, csv_path, new_kind)
                        break
                    else:
                        try:
                            kc_idx = int(kind_choice)
                            if 1 <= kc_idx <= len(filtered_kinds):
                                chosen_kind = filtered_kinds[kc_idx - 1]
                                import_csv_to_kind(client, namespace, csv_path, chosen_kind)
                                break
                            else:
                                print("Invalid selection.")
                        except ValueError:
                            print("Invalid input. Please try again.")

def menu_namespace_actions(client, namespace):
    """
    Top-level namespace menu to choose export, import, deletion operations.
    Typing CAB returns control to the key credential section.
    """
    clear_screen()
    while True:
        print(f"=== Namespace Menu [namespace={namespace or '(default)'}] ===")
        print("1) Export selected kinds to CSV")
        print("2) Import CSV into this namespace")
        print("3) Remove one or multiple datastore kinds")
        print("CAB) to go back to the namespace list.")
        choice = safe_input("\nselection: ").strip().upper()
        if choice == "CAB":
            return "CAB"  # Signal to go back to key credential selection.
        elif choice == "1":
            menu_export_kinds(client, namespace)
            clear_screen()  # Clear screen when returning from submenu
        elif choice == "2":
            menu_import_kinds(client, namespace)
            clear_screen()  # Clear screen when returning from submenu
        elif choice == "3":
            menu_remove_kinds(client, namespace)
            clear_screen()  # Clear screen when returning from submenu
        else:
            print("Invalid choice. Please try again.")

def main_menu_namespaces(client):
    """
    Displays the main namespace selection menu where the user can choose a namespace
    or perform operations such as creating, removing, or searching namespaces.
    """
    clear_screen()
    namespaces = list_namespaces(client)
    original_namespaces = namespaces[:]  # Save original list for resets
    filtered_namespaces = namespaces[:]  # Current working list
    search_active = False
    
    while True:
        clear_screen()
        print("=== GCloud Datastore Manager ===\n")
        
        # Show list of namespaces at the top
        for i, ns in enumerate(filtered_namespaces, start=1):
            display_ns = ns if ns else "(default)"
            print(f"{i}. {display_ns}")
        
        # Command options in new format
        print("\nType one of the following commands:")
        print("any number from the list")
        print("RM (use comma/range notation, e.g. 1,3-5) to remove a namespace")
        print("SEARCH <keywords to filter>")
        print("NEW <new namespace>")
        print("DOCUMENT")
        print("ABOUT")
        print("CAB")
        print("Ctrl+C to exit.")
            
        # Handle search state message
        if search_active:
            user_input = safe_input("\nSelection (or type CAB to reset filter): ").strip()
        else:
            user_input = safe_input("\nSelection: ").strip()
            
        if not user_input:
            print("No input. Please try again.")
            continue
        
        # CAB behavior depends on search state
        if user_input.upper() == "CAB":
            if search_active:
                # Reset filter and continue
                filtered_namespaces = original_namespaces[:]
                search_active = False
                continue
            else:
                # Go back to credential selection
                return
                
        if user_input.upper() == "ABOUT":
            show_about()
            clear_screen()
            continue
            
        if user_input.upper() == "DOCUMENT":
            show_documentation()
            clear_screen()
            continue
            
        if user_input.upper().startswith("NEW"):
            parts = user_input.split(maxsplit=1)
            new_ns = parts[1].strip() if len(parts) == 2 else safe_input("Enter new namespace name (or leave blank for default): ").strip()
            print(f"Namespace {new_ns or '(default)'} will be created once an entity is written.")
            result = menu_namespace_actions(client, new_ns)
            # Update the namespace list in case new ones were created
            namespaces = list_namespaces(client)
            original_namespaces = namespaces[:]
            filtered_namespaces = namespaces[:]
            search_active = False
            clear_screen()
            continue
            
        if user_input.upper().startswith("RM"):
            parts = user_input.split(None, 1)
            if len(parts) < 2:
                print("No indices provided. Format: rm 1,3-5")
                continue
                
            remove_str = parts[1].strip().upper()
            selected_indices = parse_selection(remove_str, len(filtered_namespaces))
            if selected_indices is None:
                continue
                
            if not selected_indices:
                print("No valid selection.")
                continue
                
            for idx in selected_indices:
                ns = filtered_namespaces[idx - 1]
                display_ns = ns if ns else "(default)"
                confirm = safe_input(f"Remove namespace {display_ns}? [Y/N]: ").strip().upper()
                if confirm == "Y":
                    remove_namespace(client, ns)
                else:
                    print(f"Skipped removing namespace {display_ns}.")
                    
            # Update the namespace list after removal
            namespaces = list_namespaces(client)
            original_namespaces = namespaces[:]
            filtered_namespaces = namespaces[:]
            search_active = False
            continue
            
        if user_input.upper().startswith("SEARCH"):
            search_term = user_input[6:].strip()
            if search_term.upper() == "ALL":
                filtered_namespaces = original_namespaces[:]
                search_active = False
            else:
                filtered_namespaces = filter_list_by_keyword(original_namespaces, search_term)
                if not filtered_namespaces:
                    print("No namespaces match the search keyword.")
                    filtered_namespaces = original_namespaces[:]  # Reset on no matches
                    search_active = False
                else:
                    search_active = True
            continue
            
        try:
            sel_idx = int(user_input)
            if 1 <= sel_idx <= len(filtered_namespaces):
                chosen_ns = filtered_namespaces[sel_idx - 1]
                result = menu_namespace_actions(client, chosen_ns)
                # After returning from menu_namespace_actions, update namespace list
                # in case namespaces were modified
                namespaces = list_namespaces(client)
                original_namespaces = namespaces[:]
                filtered_namespaces = namespaces[:]
                search_active = False
                clear_screen()
                continue
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input. Please try again.")

def main():
    """
    Main configuration function.
    Displays an initial menu with two options:
      1) Enter your GCP Project ID (uses Application Default Credentials) 
      2) Find available default key credentials (uses the selected key)
    If option 2 is chosen, the key credential is used without prompting for a project ID.
    Then, a Datastore client is created and control passes to the main namespace menu.
    """
    while True:
        clear_screen()
        print("=== GCloud Datastore Manager ===")
        print("1) Enter your GCP Project ID")
        print("2) Find available default key credentials")
        print("CAB)/(Ctrl+C) to exit")
        option = safe_input("\nSelection: ").strip().upper()
        if option == "CAB":
            sys.exit(0)
        elif option == "1":
            project_id = safe_input("Enter your GCP Project ID (or press Enter for default): ").strip()
            break
        elif option == "2":
            key_credential_path = select_key_credentials()
            if key_credential_path == "CAB_BACK":
                continue  # Go back to the initial menu
            if key_credential_path:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_credential_path
                print("Using key credential:", key_credential_path)
            else:
                print("No key credential selected. Continuing without explicit credentials.")
            # When using a key credential, we assume the key contains the project info.
            project_id = None
            break
        else:
            print("Invalid selection. Please try again.")
            safe_input("Press Enter to continue...")

    # Create the Datastore client
    try:
        client = datastore.Client(project=project_id or None)
        # Test access with a simple query.
        list(client.query(kind="__namespace__").fetch(limit=1))
    except Exception as e:
        print(f"Error creating Datastore client: {e}")
        safe_input("Press Enter to re-enter configuration...")
        main()
        return

    # Start the main namespace menu, and if we return, restart the main() function
    while True:
        main_menu_namespaces(client)
        # Restart the main function to select new credentials
        break
    
    main()

if __name__ == "__main__":
    main()
