#!/bin/bash

# ============================================================
#  System Information Script
#  Author : Suhas
#  Purpose: DevOps Homework - Session 3 Shell Scripting
# ============================================================

echo "=============================================="
echo "       🖥️  SYSTEM INFORMATION REPORT"
echo "=============================================="
echo ""

# ----------------------------
# Take user input
# ----------------------------
read -p "👤 Enter your name for this report: " USER_NAME
read -p "📁 Enter a name for the output directory: " DIR_NAME

echo ""
echo "----------------------------------------------"
echo "  Generating report for: $USER_NAME"
echo "----------------------------------------------"
echo ""

# ----------------------------
# Variables - System Info
# ----------------------------
CURRENT_DATE=$(date "+%Y-%m-%d %H:%M:%S")
HOST_NAME=$(hostname)
LOGGED_USER=$(whoami)
DISK_USAGE=$(df -h)
RUNNING_PROCESSES=$(ps aux)
REPORT_DIR="/Users/suhas/Downloads/devops-assignment-main/session3-shell-scripting/$DIR_NAME"
REPORT_FILE="$REPORT_DIR/system_report.txt"

# ----------------------------
# Step 1: Print Current Date
# ----------------------------
echo "📅 Current Date & Time : $CURRENT_DATE"

# ----------------------------
# Step 2: Print Hostname
# ----------------------------
echo "🌐 Hostname            : $HOST_NAME"

# ----------------------------
# Step 3: Print Username
# ----------------------------
echo "👤 Logged-in User      : $LOGGED_USER"
echo "📝 Report Prepared by  : $USER_NAME"

# ----------------------------
# Step 4: Print Disk Usage
# ----------------------------
echo ""
echo "----------------------------------------------"
echo "💾 DISK USAGE:"
echo "----------------------------------------------"
echo "$DISK_USAGE"

# ----------------------------
# Step 5: Print Running Processes (top 10)
# ----------------------------
echo "----------------------------------------------"
echo "⚙️  TOP 10 RUNNING PROCESSES:"
echo "----------------------------------------------"
ps aux | head -11

# ----------------------------
# Step 6: Create Directory
# ----------------------------
echo ""
echo "📁 Creating output directory: $REPORT_DIR"
mkdir -p "$REPORT_DIR"
echo "✅ Directory created successfully!"

# ----------------------------
# Step 7: Create File
# ----------------------------
touch "$REPORT_FILE"
echo "📄 Created report file: $REPORT_FILE"

# ----------------------------
# Step 8: Store Processes info in file using > redirection
# ----------------------------
{
  echo "=============================================="
  echo "  SYSTEM REPORT"
  echo "  Prepared by : $USER_NAME"
  echo "  Date        : $CURRENT_DATE"
  echo "  Hostname    : $HOST_NAME"
  echo "  User        : $LOGGED_USER"
  echo "=============================================="
  echo ""
  echo "--- DISK USAGE ---"
  echo "$DISK_USAGE"
  echo ""
  echo "--- ALL RUNNING PROCESSES ---"
  echo "$RUNNING_PROCESSES"
} > "$REPORT_FILE"

echo "✅ Process info saved to: $REPORT_FILE"
echo ""
echo "=============================================="
echo "  ✅ Report generated successfully!"
echo "  📂 Location: $REPORT_DIR"
echo "=============================================="
