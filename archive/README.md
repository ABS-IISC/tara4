# Archive Directory

This directory contains files that are not required for running the live application but are kept for reference and historical purposes.

## 📂 Directory Structure

```
archive/
├── documentation/      # 51 markdown documentation files
├── tests/             # 16 test scripts
├── scripts/           # 16 setup and deployment scripts
└── enterprise_architecture/  # 20 enterprise architecture files
```

## 📋 Contents

### Documentation (51 files)
- Fix reports and summaries
- Implementation guides
- Root cause analyses
- Session summaries
- Feature documentation
- AWS setup guides
- Model configuration docs

**Note**: README.md in the root directory is kept for GitHub visibility.

### Tests (16 files)
- `test_*.py` - Various test scripts for:
  - Activity logging
  - App Runner startup
  - Claude S3 functionality
  - Feedback functions
  - Clean fixes
  - And more...

### Scripts (16 files)
- `setup_*.py` - AWS and credential setup scripts
- `run_*.py` - Alternative run scripts
- `deploy*.bat/.sh` - Deployment scripts
- `fix_claude_connection.py` - Connection fix script
- `missing_functions.js` - Old/backup JavaScript file

### Enterprise Architecture (20 files)
- Architecture guides and strategies
- API design documentation
- Data architecture management
- DevOps deployment strategies
- PDF generation scripts

## 🔄 Restoration

If you need to restore any file from the archive:

```bash
# Restore a specific file
cp archive/documentation/FILENAME.md .

# Restore all documentation
cp archive/documentation/*.md .

# Restore all tests
cp archive/tests/test_*.py .
```

## 🗑️ Deletion

These files can be safely deleted if you want to reduce repository size:

```bash
# Delete entire archive (use with caution!)
rm -rf archive/
```

---

**Created**: November 16, 2025
**Purpose**: Keep tara2 root directory clean and focused on live code only
