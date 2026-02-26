---
name: process-drop
description: |
  Process files dropped into the AI Employee vault.
  Reads files from /Needs_Action folder, analyzes content,
  takes appropriate actions, and moves completed items to /Done.
  
  Use when:
  - New files appear in /Needs_Action folder
  - User requests processing of dropped files
  - Scheduled file processing task runs
  
  NOT when:
  - Only monitoring is needed (use filesystem_watcher.py instead)
  - Processing external APIs (Gmail, WhatsApp, etc.)
---

# Process Drop Skill

Process files dropped into the AI Employee vault for automated handling.

## Usage

### Via Qwen Code

```bash
# Process all pending files
qwen "Process all files in AI_Employee_Vault/Needs_Action folder"

# Process specific file
qwen "Process FILE_document.pdf in Needs_Action and move to Done"
```

### Via Python Script

```bash
# Process all pending files
python skills/process-drop/process_drop.py AI_Employee_Vault

# Process with verbose output
python skills/process-drop/process_drop.py AI_Employee_Vault --verbose

# Dry run (show what would be done)
python skills/process-drop/process_drop.py AI_Employee_Vault --dry-run
```

## Workflow

1. **Scan** `/Needs_Action` folder for `.md` action files
2. **Read** metadata and content from each file
3. **Analyze** file type and suggested actions
4. **Execute** appropriate processing:
   - Documents: Extract key information, summarize
   - Spreadsheets: Update accounting records
   - Images: OCR if needed, categorize
5. **Move** completed items to `/Done`
6. **Update** Dashboard.md with activity summary

## File Types Handled

| Type | Action |
|------|--------|
| document | Summarize, extract key points, file appropriately |
| spreadsheet | Parse data, update records, archive |
| image | Describe content, OCR if text present |
| audio | Note for transcription |
| video | Note for review |
| archive | Extract and process contents |

## Output Format

After processing, the skill:

1. Moves original file to `/Done/<date>/`
2. Moves companion `.md` file to `/Done/<date>/`
3. Updates `Dashboard.md` with:
   - Number of files processed
   - Summary of actions taken
   - Any items requiring attention

## Error Handling

- **File not found**: Log error, skip to next file
- **Permission denied**: Log error, create error report
- **Unknown file type**: Categorize as 'unknown', flag for manual review
- **Processing failure**: Move to `/Needs_Action/failed/`, create error report

## Integration with Watchers

```
File Dropped → filesystem_watcher.py → /Needs_Action/
                                            ↓
                              process_drop skill (this)
                                            ↓
                                      /Done/
```

## Example Session

```bash
$ python skills/process-drop/process_drop.py AI_Employee_Vault

[INFO] Process Drop Skill starting
[INFO] Vault: /path/to/AI_Employee_Vault
[INFO] Found 2 pending file(s)

[INFO] Processing: FILE_invoice.pdf
[INFO] Type: document (PDF)
[INFO] Extracted: Invoice #1234, Amount: $500, Due: 2026-03-01
[INFO] Created accounting entry
[INFO] Moved to: /Done/2026-02-26/

[INFO] Processing: FILE_notes.txt
[INFO] Type: document (text)
[INFO] Summary: Meeting notes from client call
[INFO] Filed under: /Done/2026-02-26/

[INFO] Processed 2 file(s) successfully
[INFO] Updated Dashboard.md
```

## Configuration

Create `skills/process-drop/config.json` for custom settings:

```json
{
  "auto_categorize": true,
  "extract_text": true,
  "update_dashboard": true,
  "archive_days": 30
}
```

## Related Skills

- `browsing-with-playwright` - For web-based file processing
- Future: `process-email` - For Gmail watcher integration
- Future: `process-whatsapp` - For WhatsApp watcher integration
