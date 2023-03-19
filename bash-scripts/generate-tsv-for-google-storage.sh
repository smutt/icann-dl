#!/bin/bash

# Help message function
print_help() {
  echo "Usage: $0 [OPTIONS]"
  echo ""
  echo "Script to create generate TSV file with url of files to be served and a base64 md5 hash as well as the size"
  echo "Can be used to upload files to google cloud storage."
  echo "More info: https://cloud.google.com/storage-transfer/docs/create-url-list"
  echo "***AS A SAFETY CHECK YOU NEED TO ADD "TsvHttpData-1.0" AS THE FIRST LINE OF GENERATED FILE***"
  echo ""
  echo "Optional arguments:"
  echo "  -o, --output FILE          The name of the output TSV file (default: print to screen)."
  echo "  -d, --dir DIRECTORY        The target folder to process (default: ./)."
  echo "  -h, --hostname HOSTNAME    The hostname for the URLs (default: example.com)."
  echo "  -p, --port PORT            The port for the URLs (default: 80)."
  echo "  -u, --url-path PATH        The URL path for the URLs (default: files)."
  echo "  -m, --match PATTERN        A pattern to match filenames (default: *)."
  echo "  -H, --help                 Show this help message."
}

# Set default values
OUTPUT_TSV=""
TARGET_FOLDER="./"
HOSTNAME="example.com"
PORT="80"
URL_PATH="files"
PATTERN="*"

# Parse input arguments
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -o|--output)
      OUTPUT_TSV="$2"
      shift
      shift
      ;;
    -d|--dir)
      TARGET_FOLDER="$2"
      shift
      shift
      ;;
    -h|--hostname)
      HOSTNAME="$2"
      shift
      shift
      ;;
    -p|--port)
      PORT="$2"
      shift
      shift
      ;;
    -u|--url-path)
      URL_PATH="$2"
      shift
      shift
      ;;
    -m|--match)
      PATTERN="$2"
      shift
      shift
      ;;
    -H|--help)
      print_help
      exit 0
      ;;
    *)
      echo "Unknown parameter passed: $1"
      print_help
      exit 1
      ;;
  esac
done

# Change directory to the target folder
cd "$TARGET_FOLDER"

# Determine the operating system
os=$(uname)

# Function to get file size
get_file_size() {
  if [ "$os" == "Darwin" ]; then
    stat -f%z "$1"
  else
    stat -c%s "$1"
  fi
}

# Function to process a file
process_file() {
  file="$1"
  url="http://${HOSTNAME}:${PORT}/${URL_PATH}/${file}"
  size=$(get_file_size "$file")
  md5_base64=$(openssl dgst -md5 -binary "$file" | openssl enc -base64)
  line="${url}\t${size}\t${md5_base64}"

  if [ -n "$OUTPUT_TSV" ]; then
    echo -e "$line" >> "$OUTPUT_TSV"
  else
    echo -e "$line"
  fi
}

# If an output file is provided, create it and add header
if [ -n "$OUTPUT_TSV" ]; then
  echo -e "URL\tSize(Bytes)\tMD5(Base64)" > "$OUTPUT_TSV"
fi

# Function to process files recursively
process_files_recursively() {
  local dir="$1"
  local pattern="$2"

  while IFS= read -r -d $'\0' file; do
    if [ -f "$file" ]; then
      process_file "$file"
    fi
      done < <(find "$dir" -type f -name "$pattern" -print0)
}

# Call the function to process files recursively
process_files_recursively "$TARGET_FOLDER" "$PATTERN"
