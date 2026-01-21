def get_example_filename(field):
    """
    Helper to generate example filename based on field type.
    """
    field_types = field.get("type") if isinstance(field, dict) else getattr(field, "type", [])
    if isinstance(field_types, (list, tuple)) and len(field_types) > 0:
        content_type = field_types[0]
    elif isinstance(field_types, str):
        content_type = field_types
    else:
        content_type = "application/octet-stream"

    # Map content types to example filenames
    examples = {
        "image/jpeg": "example.jpg",
        "image/png": "example.png",
        "text/plain": "example.txt",
        "text/csv": "data.csv",
        "application/json": "data.json",
        "application/pdf": "document.pdf",
        "application/zip": "archive.zip",
        "audio/mpeg": "audio.mp3",
        "audio/ogg": "audio.ogg",
    }

    return examples.get(content_type, "input.file")
