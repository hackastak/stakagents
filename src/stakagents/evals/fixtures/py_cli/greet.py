import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Greet someone by name.")
    parser.add_argument("name", help="who to greet")
    args = parser.parse_args()
    print(f"Hello, {args.name}!")


if __name__ == "__main__":
    main()
