# 🚀 Quick Start - Push to GitHub (5 Minutes)

## Step 1: Setup Authentication (Choose One)

### 🔑 Option A: SSH (Recommended)
```bash
# Run automated setup
./setup_github_ssh.sh

# Copy the SSH key shown
# Add to GitHub: https://github.com/settings/keys
```

### 🎫 Option B: HTTPS (Faster but less secure)
```bash
# Create token: https://github.com/settings/tokens
# Select: repo (full control)
# Copy the token
```

## Step 2: Push

### If using SSH:
```bash
git push -u origin feature/adaptive-concurrency-limiter
```

### If using HTTPS:
```bash
git push -u origin feature/adaptive-concurrency-limiter
# Username: manuelstellian-dev
# Password: <paste-your-token>
```

## Step 3: Create Pull Request

1. Open: https://github.com/manuelstellian-dev/omni-system/pulls
2. Click "New Pull Request"
3. Title: `feat: Adaptive Concurrency + Complex Prompt Success`
4. Copy description from PUSH_TO_GITHUB.md
5. Click "Create Pull Request"

## Step 4: Merge

1. Review changes (optional)
2. Click "Merge Pull Request"
3. Confirm merge
4. Delete branch (optional)

## Step 5: Start Phase 1

After merge, we'll implement:
- LTS version preference
- Breaking change detection
- Auto-downgrade system

Expected: 30% → 70% build success! 🎯

---

**Total Time: 5-10 minutes**  
**Difficulty: Easy**  
**Help available in: PUSH_TO_GITHUB.md**
