import click
import shutil


def pretty_print(
    obj: list, delimiter: str = ",", last_delimiter: str = "and", repr_: bool = False
) -> str:
    """
    Returns a formatted string representation of an array
    """
    if repr_:
        sorted_ = sorted(repr(element) for element in obj)
    else:
        sorted_ = sorted(f"'{element}'" for element in obj)

    if len(sorted_) > 1:
        sorted_[-1] = f"{last_delimiter} {sorted_[-1]}"

    return f"{delimiter} ".join(sorted_)


def raise_error_on_duplicate_keys(ordered_pairs):
    """Reject duplicate keys."""
    d = {}
    duplicate_keys = []
    for k, v in ordered_pairs:
        if k in d:
            duplicate_keys.append(k)
        else:
            d[k] = v
    if duplicate_keys:
        raise ValueError(f"Duplicate keys: {pretty_print(duplicate_keys)}")
    return d


def prompt_for_choice_from_list(
    choices, initial_prompt, index=False, ignore_case=False
):
    """Prompt a user to choose from options in a list format"""
    if ignore_case:
        choices = [c.lower() for c in choices]
    prompt = []
    for i, item in enumerate(choices):
        prompt.append(f"  {i+1}. {item}\n")

    prompt.append(initial_prompt)

    choices.append("exit")

    prompt_str = "".join(prompt)
    choice = None

    # Prompt user for choice
    while True:
        choice = click.prompt(prompt_str, type=str)
        if ignore_case:
            choice = choice.lower()
        # Case: user enters number
        if choice.isnumeric() and 0 < int(choice) <= len(choices):
            choice = choices[int(choice) - 1]
            break
        elif choice in choices:  # Case: user enters id
            break
        else:  # Case: user enters invalid
            click.echo("Please enter a valid choice.")

    if choice == "exit":
        click.echo("Exited.")
        return None

    if index:
        return choices.index(choice)

    return choice


def print_divider():
    """Print a horizontal line the width of the terminal"""
    w, _ = shutil.get_terminal_size()
    click.echo("—" * w)
