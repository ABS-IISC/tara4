#!/bin/bash
# Restart the application after deployment
echo "Post-deploy hook: Restarting application"
systemctl restart web.service || true
