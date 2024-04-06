#!/bin/bash
LICENSE_FILE="src/LICENSE.txt"
TARGET_DIR="src/smskillsdk/models"
EXCLUDE_PATTERNS=("__init__.py")

# Function to prompt the user for confirmation
user_confirms() {
    local answer
    while true; do
        read -p "Do you want to proceed? (y/n) " answer
        case "$answer" in
            [Yy] ) return 0;; # Indicates success/true
            [Nn] ) return 1;; # Indicates failure/false
            * ) echo "Please answer yes or no.";;
        esac
    done
}

add_license_to_file() {
    local file=$1
    local license_file=$2

    local temp_file=$(mktemp)
    # the <(echo) bit is to insert a newline between the license headerand the file
    cat "$license_file" <(echo) "$file" > "$temp_file"
    mv "$temp_file" "$file"
}

# Export the function so it can be used by child processes spawned by find
export -f add_license_to_file

# You can use -o to add more extensions, example "-name '*.py' -o -name '*.txt'"
find_extensions="-name '*.py'"

exclude_conditions=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    exclude_conditions="$exclude_conditions ! -name \"$pattern\""
done

# Show files to be edited
file_list="find $TARGET_DIR \( $find_extensions \) $exclude_conditions"
echo "The files to be modified are:"
eval $file_list

if user_confirms; then
    # Add license headers
    cmd="find $TARGET_DIR \( $find_extensions \) $exclude_conditions -exec bash -c 'add_license_to_file \"\$0\" \"$LICENSE_FILE\"' {} \;"
    eval $cmd
    # Place the action you want to perform here.
    echo "License headers added."
fi
