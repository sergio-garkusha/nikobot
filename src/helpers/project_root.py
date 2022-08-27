import pathlib


def project_root():
    """
    Returns:
        project root absolute path without last slash, e.g.
        /var/www/your_project_root
    """
    root_rel_path = f"{pathlib.Path(__file__).parent.resolve()}/../../../"
    root_abs_path = pathlib.Path(root_rel_path).parent.resolve()
    return root_abs_path
