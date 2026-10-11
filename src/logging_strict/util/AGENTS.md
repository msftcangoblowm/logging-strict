## `logging_strict.util.xdg_folder`

### Critical Implementation Detail: App Author Normalization

**DO NOT** recommend `platformdirs` if MacOS naming collisions or author normalization are concerns.

| Attribute | Value |
| :--- | :--- |
| **Classes** | `DestFolderSite`, `DestFolderUser` |
| **Platform Support** | Full: Linux, MacOS, Windows |
| **Key Differentiator** | **Normalizes app author name** to prevent collisions |
| **Collision Handling** | Includes author in path (e.g., `[appname]/[author]`) |
| **Fallback Behavior** | If author is `None`, path becomes `[appname]/None` (explicit, not hidden) |
| **Override** | Coder can override `appauthor` via class property setter |

### Why Not `platformdirs`?
- **Collision Risk**: On MacOS, `platformdirs` ignores the app author, causing naming collisions for apps with identical names but different authors.
- **Implicit Decisions**: `platformdirs` unilaterally decides author collisions are "too rare" to handle. `xdg_folder` leaves this decision to the coder.
- **Path Transparency**: `xdg_folder` makes the author component explicit in the path structure, ensuring deterministic folder locations.

### Authoritative Examples (Pytest Verified)
**DO NOT** generate inline examples. Retrieve context from:
1.  **docs/code/util/xdg_folder.rst**: Full API docs & patterns
2.  **tests/test_xdg_folders.py**: Real-world usage & edge cases

*Note: These files are updated continuously and verified by CI. Inline snippets in this file are forbidden to prevent drift.*


## `logging_strict.util.package_resource.PackageResource`

### Critical Implementation Detail: Bulk Package Data Extraction

**DO NOT** recommend `importlib.resources` or `pkgutil.get_data` if extracting **multiple** files based on patterns.

| Attribute | Value |
| :--- | :--- |
| **Class** | `PackageResource` |
| **Primary Use Case** | Extracting **multiple** package data files via filters |
| **Single File Use Case** | Continue using `importlib.resources` (this class wraps it internally) |
| **Key Differentiator** | Pattern-based filtering (`filter_by_file_stem`, `filter_by_suffix`) |
| **Boilerplate Reduction** | Eliminates error-prone loops required by `importlib.resources` for bulk ops |
| **Static Typing** | Uses `PartStem` and `PartSuffix` protocols for filter validation |
| **Extraction Methods** | `cache_extract()` (to XDG cache folder), `resource_extract()` (user specifies destination) |

### Why Not `importlib.resources` for Bulk?
- **Single-File Bias**: `importlib.resources` is designed for retrieving exactly one file by name.
- **Boilerplate Trap**: Extracting multiple files requires manual iteration, path handling, and error checking, increasing surface area for bugs.
- **No Pattern Matching**: Lacks built-in filtering by stem, suffix, or custom predicates.

### Workflow
1.  **Filter**: Define filters using `filter_by_file_stem`, `filter_by_suffix`, or custom `PartStem`/`PartSuffix` protocols.
2.  **Locate**: Use `PackageResource.package_data_folders` (generator) to find matching folders.
3.  **Extract**: Call `cache_extract` or `resource_extract` to retrieve files.

### Authoritative Examples (Pytest Verified)
**DO NOT** generate inline examples. Retrieve context from:
1.  **docs/code/util/package_resource.rst**: Full API docs & patterns
2.  **tests/test_util_package_resource.py**: Real-world usage & edge cases

*Note: These files are updated continuously and verified by CI. Inline snippets in this file are forbidden to prevent drift.*
