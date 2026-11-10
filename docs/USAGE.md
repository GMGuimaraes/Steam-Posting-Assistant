# Usage guide

## Catalog artwork

Run the cataloger against a folder containing your artwork:

```bash
python src/artwork_catalog.py "./artwork" --output inventory.csv
```

Add `--recursive` to include subfolders (this is enabled by default). Use `--no-recursive` to scan only the selected folder.

The CSV contains:
- `file_name`: image filename.
- `relative_path`: path relative to the scanned folder.
- `extension`: file extension.
- `size_bytes`: file size.
- `sha256`: content hash; matching hashes indicate byte-identical files.
- `width` and `height`: populated when Pillow can read the image.
- `duplicate_of`: first file encountered with the same SHA-256, if any.

The tool never modifies the source files.

## Publish manually

The catalog is a preparation aid only. To publish, open the official Steam Community website yourself, sign in directly, choose the appropriate artwork page, upload the file, review all fields, and submit manually. Verify the published result before recording it as complete.

No script in this repository should automate browser interaction, form submission, account actions, or requests to Steam services.
