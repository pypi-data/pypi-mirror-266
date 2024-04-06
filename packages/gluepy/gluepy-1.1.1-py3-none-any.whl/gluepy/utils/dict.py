def merge(a, b, path: str = None, allow_new_key: bool = True):
    """Recursively merge two dictionaries"""
    path = path or []
    a = {} if a is None else a
    b = {} if b is None else b

    for key in b:
        if key in a:
            if (
                a[key] is not None
                and b[key] is not None
                and not isinstance(a[key], type(b[key]))
            ):
                raise TypeError(
                    f"Conflicting types '{a[key].__class__.__name__}' and "
                    f"'{b[key].__class__.__name__}' at '{'.'.join(path + [str(key)])}'"
                )

            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)], allow_new_key)
            else:
                a[key] = b[key]
        elif not allow_new_key:
            raise ValueError(
                f"Key '{'.'.join(path + [str(key)])}' missing in source dictionary"
            )
        else:
            a[key] = b[key]

    return a
