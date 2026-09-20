# Security Checklist Before GitHub Push

## ✅ Pre-Push Security Verification

### 1. Environment Variables
- [ ] `.env` file is in `.gitignore`
- [ ] `.env` file is NOT tracked by git
- [ ] All secrets are in `.env`, not in code
- [ ] Created `.env.example` with placeholder values

### 2. Service Account Files
- [ ] `*.json` files are in `.gitignore`
- [ ] Service account JSON is NOT tracked by git
- [ ] Service account JSON is NOT in any documentation

### 3. Code Review
- [ ] No hardcoded API keys in Python files
- [ ] All API keys loaded from `Config.GEMINI_API_KEY`
- [ ] No hardcoded project IDs in Python files
- [ ] All project IDs loaded from environment variables

### 4. Documentation Review
- [ ] README.md uses placeholder values
- [ ] INTEGRATION_READINESS.md uses placeholder values
- [ ] QUICK_START.md uses placeholder values
- [ ] No actual API keys in any .md files
- [ ] No actual project IDs in any .md files

### 5. Git History
- [ ] No secrets in current commit
- [ ] No secrets in git history
- [ ] Git history cleaned if secrets were committed
- [ ] Force pushed clean history to GitHub

### 6. API Key Security
- [ ] API key rotated if exposed
- [ ] New API key stored only in `.env`
- [ ] API key restrictions enabled in Google Cloud Console
- [ ] API key usage monitored

---

## 🔍 How to Verify

### Check if .env is tracked:
```bash
git ls-files | findstr .env
# Should return NOTHING
```

### Check if JSON files are tracked:
```bash
git ls-files | findstr .json
# Should return NOTHING
```

### Search for secrets in current files:
```bash
git grep -i "AIzaSy"
# Should return NOTHING

git grep -i "appoint-490412"
# Should return NOTHING in Python files
```

### Check git history for secrets:
```bash
git log --all --full-history --source --all -- .env
# Should return NOTHING

git log -p | findstr /i "AIzaSy"
# Should return NOTHING
```

---

## 🚨 If You Find Secrets

### In Current Files:
1. Replace with placeholder values
2. Move actual values to `.env`
3. Verify `.env` is in `.gitignore`

### In Git History:
1. **STOP** - Don't push!
2. Rotate API key immediately
3. Clean git history (use fix_git_history.bat)
4. Verify secrets are gone
5. Then push

---

## ✅ Safe to Push When:

- [ ] All checks above are complete
- [ ] No secrets in current files
- [ ] No secrets in git history
- [ ] `.env` and `*.json` in `.gitignore`
- [ ] API key rotated if previously exposed
- [ ] Tested that app still works with new credentials

---

## 📝 Quick Commands

### Verify no secrets before commit:
```bash
git diff --cached | findstr /i "AIzaSy api_key appoint-490412"
```

### Check what will be committed:
```bash
git status
git diff --cached
```

### Verify .gitignore is working:
```bash
git check-ignore .env
git check-ignore *.json
```

---

**Remember**: Once pushed to GitHub, secrets are public forever (even if deleted later)!
