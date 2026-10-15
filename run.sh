#!/usr/bin/env bash
# ALTair convenience commands (P1-P2, synthetic mode).
# Usage:  ./run.sh data | run | test | clean
set -e
cmd="${1:-run}"
case "$cmd" in
  data)  python3 run_pipeline.py --regen ;;
  run)   python3 run_pipeline.py ;;
  test)  python3 tests/run_all_tests.py ;;
  clean) rm -f data/processed/trial_*.csv data/processed/_trials_index.csv
         rm -f experiments/reports/*.md ;;
  *) echo "usage: ./run.sh data|run|test|clean" ;;
esac
