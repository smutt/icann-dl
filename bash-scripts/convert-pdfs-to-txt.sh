#!/bin/bash
echo "Script to automatically generate txt files from pdfs and save them with same name. If .txt exists, will not do anything. Requires ebook-convert."
echo ""
# Set the Internal Field Separator to handle filenames with spaces
IFS=$'\n'

# Check if ebook-convert is installed
if ! command -v ebook-convert >/dev/null 2>&1; then
  echo "ebook-convert is not installed."
  echo "Please download and install Calibre from https://calibre-ebook.com/download"
  exit 1
fi

# Set default timeout value
timeout_value=20

# Check if a timeout value is provided as an argument
if [[ $# -gt 0 ]] && [[ $1 =~ ^[0-9]+$ ]]; then
  timeout_value=$1
fi

# Detect the operating system
OS=$(uname)

# Change the find command's syntax based on the detected OS
if [[ "$OS" == "Darwin" ]]; then
  FIND_CMD="find -E . -iregex '.*\.(pdf|txt)$'"
else
  FIND_CMD="find . -iregex '.*\.\(pdf\|txt\)$' -type f"
fi

# Find all PDF and TXT files
all_files=($(eval "$FIND_CMD"))
total_files=${#all_files[@]}
found_files=0

echo "Finding PDF and TXT files..."

# Initialize empty arrays for PDF and TXT files
pdf_files=()
txt_files=()

# Separate PDF and TXT files into respective arrays
for file in "${all_files[@]}"; do
  if [[ "${file,,}" == *.pdf ]]; then
    pdf_files+=("$file")
  elif [[ "${file,,}" == *.txt ]]; then
    txt_files+=("$file")
  fi

  # Calculate and display progress percentage
  ((found_files++))
  progress_percentage=$((found_files * 100 / total_files))
  if ((progress_percentage % 20 == 0)) && [[ "$last_percentage" != "$progress_percentage" ]]; then
    echo "Progress: $progress_percentage% ($found_files/$total_files)"
    last_percentage=$progress_percentage
  fi
done

# Create or empty the "tbc" file
> tbc

# Check for PDF files without corresponding TXT files
pdf_total=${#pdf_files[@]}
checked_files=0

echo "Checking for PDF files without corresponding TXT files..."

for pdf in "${pdf_files[@]}"; do
  txt="${pdf%.pdf}.txt"
  if ! [[ " ${txt_files[@]} " =~ " ${txt} " ]]; then
    echo "$pdf" >> tbc
  fi

  # Calculate and display progress percentage
  ((checked_files++))
  progress_percentage=$((checked_files * 100 / pdf_total))
  last_percentage=0
  if ((progress_percentage % 10 == 0)) && [[ "$last_percentage" != "$progress_percentage" ]]; then
    echo "Progress: $progress_percentage% ($checked_files/$pdf_total)"
    last_percentage=$progress_percentage
  fi
done

# Convert PDFs listed in the "tbc" file to TXT using ebook-convert
tbc_files=($(cat tbc))
total_files=${#tbc_files[@]}
converted_files=0

if [ "$total_files" -gt 0 ]; then
  echo "Starting the conversion process..."
  start_time=$(date +%s)

  for i in "${!tbc_files[@]}"; do
    pdf="${tbc_files[i]}"
    noext="${pdf%.pdf}"
    timeout "$timeout_value" ebook-convert "$pdf" "$noext.txt"
    ((converted_files++))

    # Calculate and display progress percentage
    progress_percentage=$((converted_files * 100 / total_files))
    last_percentage=0
    if ((progress_percentage % 5 == 0)) && [[ "$last_percentage" != "$progress_percentage" ]]; then  
      echo "Progress: $progress_percentage% ($converted_files/$total_files)"
      last_percentage=$progress_percentage
    fi
  done

  end_time=$(date +%s)
  time_elapsed=$((end_time - start_time))

  # Display the number of files converted and the time it took

  echo "Conversion complete: $converted_files files converted in $time_elapsed seconds."
else
  echo "No files need conversion."
fi

# Clean up temporary files
rm tbc

