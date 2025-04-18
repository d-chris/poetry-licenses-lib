def main() -> None:
    """Main function to demonstrate the usage of the library."""

    from poetry_licenses_lib import cache_packageinfo
    from poetry_licenses_lib import get_poetry_packages

    @cache_packageinfo(maxsize=1)
    def cached_poetry_packages():
        """Cache the package info as dictionary."""
        return get_poetry_packages("pyproject.toml")

    for dependency, packageinfo in cached_poetry_packages().items():

        if "UNKNOWN" in packageinfo.license:
            license = ""
        else:
            license = f"[{packageinfo.license}] "

        print(f" {dependency} {license}".center(80, "="), end="\n\n")

        for file, text in packageinfo.licenses:
            if "dist-info" in file:
                print(text.strip("\n"), end="\n\n")
                break
        else:
            print("No license file found.", end="\n\n")


if __name__ == "__main__":
    main()
