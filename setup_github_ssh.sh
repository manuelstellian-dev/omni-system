#!/bin/bash

echo "🔑 GitHub SSH Setup Script"
echo "=========================="
echo ""

# Check if SSH key exists
if [ -f ~/.ssh/id_ed25519 ]; then
    echo "✅ SSH key already exists!"
    echo ""
    echo "Your public key:"
    echo "================"
    cat ~/.ssh/id_ed25519.pub
    echo ""
    echo "Copy the above key and add it to GitHub:"
    echo "https://github.com/settings/keys"
else
    echo "🔧 Generating new SSH key..."
    ssh-keygen -t ed25519 -C "manuelstellian-dev@users.noreply.github.com" -f ~/.ssh/id_ed25519 -N ""
    echo ""
    echo "✅ SSH key generated!"
    echo ""
    echo "Your public key:"
    echo "================"
    cat ~/.ssh/id_ed25519.pub
    echo ""
    echo "📋 Copy the above key and add it to GitHub:"
    echo "   1. Go to: https://github.com/settings/keys"
    echo "   2. Click 'New SSH key'"
    echo "   3. Paste the key above"
    echo "   4. Save"
fi

echo ""
echo "🔄 Updating git remote to use SSH..."
cd /home/venom/omni-system
git remote set-url origin git@github.com:manuelstellian-dev/omni-system.git

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add SSH key to GitHub (see above)"
echo "2. Test connection: ssh -T git@github.com"
echo "3. Push: git push -u origin feature/adaptive-concurrency-limiter"
