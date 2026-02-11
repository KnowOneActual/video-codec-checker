#!/bin/bash
# Example: Check all videos in a playlist for CasparCG compatibility

echo "Checking playlist for CasparCG compatibility..."
echo "=========================================="

failed_count=0
warning_count=0
success_count=0

for video in playlist/*.mp4 playlist/*.mov; do
    if [ -f "$video" ]; then
        echo ""
        echo "Checking: $(basename "$video")"
        
        if videowise check "$video" --system casparcg --quiet; then
            ((success_count++))
            echo "✓ Compatible"
        elif [ $? -eq 1 ]; then
            ((warning_count++))
            echo "⚠ Warning - check details above"
        else
            ((failed_count++))
            echo "✗ Incompatible - requires fixing"
        fi
    fi
done

echo ""
echo "Summary:"
echo "--------"
echo "✓ Compatible: $success_count"
echo "⚠ Warnings: $warning_count"
echo "✗ Failed: $failed_count"

if [ $failed_count -gt 0 ]; then
    echo ""
    echo "⚠️  WARNING: Some files are incompatible and will not play!"
    exit 1
fi
