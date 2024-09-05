#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pathlib import Path

current_path = Path(__file__).parent
root_path = current_path.parent
readme_md_path = root_path / "README.md"

# Import the README and use it as the long-description.
# Replace image links at release to point to this tag instead of main, so they do not change with new releases
long_description = readme_md_path.read_text(encoding="utf-8")
# replace links
github_ref = os.getenv("GITHUB_REF", "")
temp = []
if github_ref:
    # refs/heads/<branch_name>, for pull requests it is refs/pull/<pr_number>/merge, 
    # and for tags it is refs/tags/<tag_name>
    print(f"GITHUB_REF: {str(github_ref)}")
    ref_suffix = github_ref.split("refs/heads/")
    if len(ref_suffix) > 1:
        # is feature branch - don't adjust for prerelease
        pass
    else:
        if len(ref_suffix) == 1: # if not a branch, check if it is a tag
            ref_suffix = github_ref.split("tags")
        if len(ref_suffix) > 1: # if it is a tag, replace the links
            link = "conan_explorer" + ref_suffix[1].replace(" ", "")
            main_link = "conan_explorer/main"
            for line in long_description.splitlines():
                if main_link in line:
                    line = line.replace(main_link, link)
                    print(f"replaced {main_link} with {link}")
                temp.append(line)
            long_description = "\n".join(temp)
else:
    print("No GITHUB_REF envvar found!")

# overwrite the README.md file with the new links
readme_md_path.write_text(long_description, encoding="utf-8")


