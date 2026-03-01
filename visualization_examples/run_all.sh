#!/bin/bash

# Define python interpreter
PYTHON="/home/vinay/others/envs/py312/bin/python"
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
RESPONSES="$BASE_DIR/../responses"

mkdir -p "$RESPONSES"

run_pipeline() {
    SCRIPT_NAME=$1
    SCRIPT_PATH="$SCRIPT_NAME"
    RESPONSE_PATH="$RESPONSES/${2}_prompt+response.txt"
    CSV_PATH="$RESPONSES/${2}_matches.csv"
    HTML_PATH="$RESPONSES/${2}_viz.html"
    MAPPING_MD="$RESPONSES/${2}_mapping.md"
    MAPPING_HTML="$RESPONSES/${2}_mapping_viewer.html"

    echo "----------------------------------------------------------------"
    echo "Running $SCRIPT_NAME..."
    $PYTHON "$SCRIPT_PATH"

    echo "Generating Mapping Visualization ($MAPPING_HTML)..."
    if [ -f "$MAPPING_MD" ]; then
        echo "$PYTHON" "$BASE_DIR/visualizer.py" "$SCRIPT_PATH" "$RESPONSE_PATH" "$MAPPING_MD" "$MAPPING_HTML"
        "$PYTHON" "$BASE_DIR/visualizer.py" "$SCRIPT_PATH" "$RESPONSE_PATH" "$MAPPING_MD" "$MAPPING_HTML"
    else
        echo "Warning: $MAPPING_MD not found, skipping mapping visualization."
    fi

    echo "Done."
}

run_pipeline "$BASE_DIR/01_basic_qa.py" "01"
run_pipeline "$BASE_DIR/02_chain_of_thought.py" "02"
run_pipeline "$BASE_DIR/03_classification.py" "03"
run_pipeline "$BASE_DIR/04_simple_rag.py" "04"
run_pipeline "$BASE_DIR/05_structured_output.py" "05"
run_pipeline "$BASE_DIR/08_few_shot_examples.py" "08"
run_pipeline "$BASE_DIR/09_typed_predictors.py" "09"
run_pipeline "$BASE_DIR/14_optimizer.py" "14"
run_pipeline "$BASE_DIR/15_mipro_optimizer.py" "15"

echo -e "\n\nAll examples completed. Check the '$RESPONSES' directory."
ls -l $RESPONSES/*.html
