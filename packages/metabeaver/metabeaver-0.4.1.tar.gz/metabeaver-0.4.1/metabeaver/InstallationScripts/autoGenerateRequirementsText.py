"""
Note the following will consider all packages linked to the current INTERPRETER.

Make sure you are using a new interpreter for the project if you want ONLY the dataBeaver packages.
"""


import os
import sys

# Check if pkg_resources is available
try:
    import pkg_resources
except ImportError:
    # If pkg_resources is not available, attempt to install it
    exit_code = os.system(f"{sys.executable} -m pip install pkg_resources")
    if exit_code != 0:
        # Log the error to an error.log file
        with open('error.log', 'a') as log_file:
            log_file.write(f"Failed to install pkg_resources\n")
        print("Failed to install pkg_resources.")
        print("Please check the error.log file for more information.")
        exit(1)

# Get a list of all installed packages
installed_packages = pkg_resources.working_set

# Extract package names and versions
package_list = []
for package in installed_packages:
    package_name = package.project_name
    package_version = package.version
    package_list.append(f"{package_name}=={package_version}")

# Write the packages to a requirements.txt file
with open('requirements.txt', 'w') as file:
    file.write('\n'.join(package_list))