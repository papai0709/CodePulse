#!/bin/bash

# CodePulse AI Analysis Dashboard Log Monitor
# Usage: ./monitor_logs.sh

echo "🔍 CodePulse AI Analysis Dashboard - Live Log Monitor"
echo "=================================================="
echo "📊 Monitoring AI analysis logs..."
echo "🔄 Press Ctrl+C to stop"
echo ""

# Monitor both Docker container logs and application log file
docker logs -f codepulse-app 2>&1 | grep -E "(🧠|🏗️|📊|✅|❌|⚠️|🔍|💡|🎉|📄|🧹)"