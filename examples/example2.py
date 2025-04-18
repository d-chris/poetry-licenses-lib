def main() -> None:
    """Main function to demonstrate the usage of the library."""

    from poetry_licenses_lib.packages import PoetryPackageInfo

    poetry = PoetryPackageInfo("pyproject.toml")

    for group in sorted(poetry.groups):
        for dependency, packageinfo in poetry.licenses(group):

            if packageinfo is None:
                print(
                    f" <{group}> {dependency} [UNKNOWN] ".center(80, "="),
                    end="\n\n",
                )
                continue

            if "UNKNOWN" in packageinfo.license:
                license = ""
            else:
                license = f"[{packageinfo.license}] "

            print(f" <{group}> {dependency} {license}".center(80, "="), end="\n\n")

            for file, text in packageinfo.licenses:
                if "dist-info" in file:
                    print(text.strip("\n"), end="\n\n")
                    break
            else:
                print("No license file found.", end="\n\n")


if __name__ == "__main__":
    main()
