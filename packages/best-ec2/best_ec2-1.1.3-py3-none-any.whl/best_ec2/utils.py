def remove_none_values(d):
    """Remove keys with None values from a dictionary."""
    return {k: v for k, v in d.items() if v is not None}
