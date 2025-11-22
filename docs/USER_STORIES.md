# 📖 AI-PRISM USER STORIES & TEST SCENARIOS

**Date:** November 20, 2025
**Purpose:** Comprehensive end-to-end testing scenarios for all features

---

## 🎯 USER PERSONAS

### Persona 1: Sarah - Investigation Analyst
- **Role:** Senior Investigation Analyst
- **Goal:** Review investigation reports and ensure Hawkeye compliance
- **Tech Savvy:** Medium
- **Pain Points:** Manual review takes too long, misses compliance issues

### Persona 2: Mike - Team Lead
- **Role:** Investigation Team Lead
- **Goal:** Quickly review team's investigation reports
- **Tech Savvy:** High
- **Pain Points:** Needs to review 10+ reports daily

---

## 📋 EPIC 1: DOCUMENT UPLOAD & SETUP

### User Story 1.1: Upload Investigation Document
**As** Sarah
**I want to** upload my Word document
**So that** I can get AI-powered analysis

**Acceptance Criteria:**
- ✅ Upload button visible on landing page
- ✅ Accepts .docx files
- ✅ Shows upload progress
- ✅ Displays success notification
- ✅ Extracts sections automatically
- ✅ Section dropdown populated

**Test Steps:**
1. Open http://localhost:8080
2. Click "Choose File" button
3. Select test document
4. Click "Upload & Start Analysis" button
5. Verify notification appears
6. Verify section dropdown shows sections

**Expected Backend Calls:**
- `POST /upload` with FormData
- Response: `{success: true, session_id: "...", sections: [...]}`

**Logs to Check:**
- Document uploaded successfully
- Sections extracted: X sections
- Session created: session_id

---

### User Story 1.2: Upload with Guidelines
**As** Mike
**I want to** upload custom guidelines with my document
**So that** analysis uses our team's standards

**Acceptance Criteria:**
- ✅ Guidelines file upload option visible
- ✅ Radio buttons for guidelines preference
- ✅ Guidelines uploaded with document

**Test Steps:**
1. Select guidelines preference radio button
2. Choose guidelines file
3. Upload document
4. Verify both files uploaded

**Expected Backend Calls:**
- `POST /upload` with both document and guidelines files

---

## 📋 EPIC 2: SECTION NAVIGATION & ANALYSIS

### User Story 2.1: View Section List
**As** Sarah
**I want to** see all document sections
**So that** I can navigate through them

**Acceptance Criteria:**
- ✅ Section dropdown shows all sections
- ✅ Sections listed in order
- ✅ First option is placeholder

**Test Steps:**
1. After upload, click section dropdown
2. Verify all sections visible
3. Verify sections match document structure

---

### User Story 2.2: Analyze Section On-Demand
**As** Sarah
**I want to** analyze a section when I click on it
**So that** I have control over the analysis process

**Acceptance Criteria:**
- ✅ Clicking section triggers analysis (NOT auto-analyze)
- ✅ Loading spinner appears with modal overlay
- ✅ Background freezes during analysis
- ✅ Analysis takes 20-40 seconds
- ✅ Feedback displays when complete
- ✅ Section content displays

**Test Steps:**
1. Select first section from dropdown
2. Verify loading spinner appears
3. Verify background is frozen (modal overlay)
4. Wait for analysis to complete
5. Verify feedback items appear
6. Verify section content displays

**Expected Backend Calls:**
- `POST /analyze_section` with `{session_id, section_name}`
- Response: `{async: true, task_id: "...", section_content: "..."}`
- `GET /task_status/{task_id}` (polling every 2s)
- Final response: `{state: "SUCCESS", result: {feedback_items: [...]}}`

**Logs to Check:**
- Analysis task submitted
- Task ID: ...
- Polling attempts
- Task completed: X items

---

### User Story 2.3: Navigate Between Sections
**As** Sarah
**I want to** navigate between sections using Next/Previous
**So that** I can review sequentially

**Acceptance Criteria:**
- ✅ Next button advances to next section
- ✅ Previous button goes to previous section
- ✅ Already-analyzed sections load instantly (cached)
- ✅ New sections trigger analysis

**Test Steps:**
1. Click "Next Section" button
2. Verify section advances
3. Verify new section analyzes
4. Click "Previous Section" button
5. Verify returns to previous section
6. Verify loads instantly from cache

**Expected Backend Calls:**
- `POST /analyze_section` (only for new sections)
- No backend call for cached sections

---

## 📋 EPIC 3: FEEDBACK MANAGEMENT

### User Story 3.1: Review AI Feedback
**As** Sarah
**I want to** see AI-generated feedback for current section
**So that** I can understand what needs improvement

**Acceptance Criteria:**
- ✅ Feedback items displayed in cards
- ✅ Each card shows: ID, type, category, description, suggestion
- ✅ Risk level indicated with color
- ✅ Hawkeye references shown
- ✅ Confidence score visible

**Test Steps:**
1. Analyze a section
2. Scroll to feedback panel
3. Verify all feedback cards display
4. Verify card contains all fields
5. Verify risk level color coding

---

### User Story 3.2: Accept AI Feedback
**As** Sarah
**I want to** accept relevant feedback items
**So that** they're included in final document

**Acceptance Criteria:**
- ✅ Accept button visible on each feedback card
- ✅ Clicking Accept button marks item as accepted
- ✅ Accepted items show green checkmark
- ✅ Accepted items tracked in statistics
- ✅ Accept state persists when navigating sections

**Test Steps:**
1. Click "Accept" button on first feedback item
2. Verify button changes to green checkmark
3. Verify statistics update (accepted count +1)
4. Navigate to different section
5. Return to original section
6. Verify accept state preserved

**Expected Backend Calls:**
- None (client-side state in `window.sectionData`)

**Logs to Check:**
- Feedback accepted: FB001
- Statistics updated

---

### User Story 3.3: Reject AI Feedback
**As** Sarah
**I want to** reject irrelevant feedback items
**So that** they're excluded from final document

**Acceptance Criteria:**
- ✅ Reject button visible on each feedback card
- ✅ Clicking Reject button marks item as rejected
- ✅ Rejected items show red X
- ✅ Rejected items tracked in statistics
- ✅ Reject state persists when navigating sections

**Test Steps:**
1. Click "Reject" button on second feedback item
2. Verify button changes to red X
3. Verify statistics update (rejected count +1)
4. Navigate to different section
5. Return to original section
6. Verify reject state preserved

---

### User Story 3.4: Add Custom Feedback
**As** Mike
**I want to** add my own feedback items
**So that** I can include team-specific observations

**Acceptance Criteria:**
- ✅ "Add Custom Feedback" button visible
- ✅ Clicking opens form modal
- ✅ Form has fields: type, category, description, suggestion
- ✅ Form validates required fields
- ✅ Submitting adds item to feedback list
- ✅ Custom items marked with "Custom" badge

**Test Steps:**
1. Click "Add Custom Feedback" button
2. Verify form modal appears
3. Fill in all fields
4. Click "Submit" button
5. Verify new feedback card appears
6. Verify card has "Custom" badge

**Expected Backend Calls:**
- `POST /add_user_feedback` with feedback data
- Response: `{success: true, feedback_id: "..."}`

**Logs to Check:**
- Custom feedback added
- Feedback ID: ...

---

## 📋 EPIC 4: TEXT HIGHLIGHTING

### User Story 4.1: Highlight Text in Document
**As** Sarah
**I want to** highlight specific text passages
**So that** I can mark areas that need attention

**Acceptance Criteria:**
- ✅ Can select text in document content area
- ✅ "Highlight" button appears on text selection
- ✅ Clicking Highlight colors the text
- ✅ Multiple highlights supported
- ✅ Highlights saved per section

**Test Steps:**
1. Select text in section content
2. Verify highlight button appears
3. Click highlight button
4. Verify text is highlighted (yellow background)
5. Select different text
6. Highlight again
7. Verify both highlights visible

**Expected Backend Calls:**
- None (client-side highlighting)

**Logs to Check:**
- Text highlighted: "sample text"
- Highlight saved

---

### User Story 4.2: Remove Highlights
**As** Sarah
**I want to** remove incorrect highlights
**So that** I can correct my selections

**Acceptance Criteria:**
- ✅ Clicking highlighted text shows "Remove" option
- ✅ Clicking Remove clears the highlight
- ✅ Removal persists when navigating sections

**Test Steps:**
1. Click on highlighted text
2. Verify "Remove Highlight" option appears
3. Click "Remove Highlight"
4. Verify highlight is removed
5. Navigate away and back
6. Verify highlight remains removed

---

### User Story 4.3: Add Comments to Highlights
**As** Mike
**I want to** add comments to highlighted text
**So that** I can explain why I marked it

**Acceptance Criteria:**
- ✅ Right-click on highlight shows "Add Comment" option
- ✅ Comment modal appears
- ✅ Comment text can be entered
- ✅ Comment icon appears on highlight
- ✅ Hovering shows comment tooltip

**Test Steps:**
1. Right-click highlighted text
2. Click "Add Comment"
3. Enter comment text
4. Submit comment
5. Verify comment icon appears
6. Hover over highlight
7. Verify comment displays

---

## 📋 EPIC 5: CHAT ASSISTANT

### User Story 5.1: Ask Questions About Section
**As** Sarah
**I want to** ask questions about the current section
**So that** I can get AI guidance

**Acceptance Criteria:**
- ✅ Chat panel visible on right side
- ✅ Chat input field available
- ✅ Can type question
- ✅ Pressing Enter sends message
- ✅ Question appears in chat history
- ✅ AI response appears within 30 seconds
- ✅ Response contextual to current section

**Test Steps:**
1. Type question in chat input
2. Press Enter (or click Send)
3. Verify question appears in chat
4. Verify "Thinking..." indicator appears
5. Wait for response
6. Verify response appears
7. Verify response is relevant to section

**Expected Backend Calls:**
- `POST /chat` with `{message, session_id, current_section}`
- Response: `{async: true, task_id: "..."}`
- `GET /task_status/{task_id}` (polling)
- Final: `{state: "SUCCESS", result: {response: "..."}}`

**Logs to Check:**
- Chat message received
- Task ID: ...
- Chat response generated

---

### User Story 5.2: View Chat History
**As** Mike
**I want to** see previous chat messages
**So that** I can reference earlier guidance

**Acceptance Criteria:**
- ✅ All messages visible in chat panel
- ✅ User messages aligned left
- ✅ AI messages aligned right
- ✅ Chat scrollable
- ✅ Auto-scrolls to latest message

**Test Steps:**
1. Send multiple chat messages
2. Verify all messages appear
3. Verify user/AI alignment
4. Scroll up to older messages
5. Send new message
6. Verify auto-scrolls to bottom

---

## 📋 EPIC 6: STATISTICS & MONITORING

### User Story 6.1: View Analysis Statistics
**As** Mike
**I want to** see summary statistics
**So that** I can track progress

**Acceptance Criteria:**
- ✅ Statistics panel visible
- ✅ Shows: sections analyzed, total feedback, accepted/rejected counts
- ✅ Shows risk level breakdown
- ✅ Updates in real-time

**Test Steps:**
1. Complete analysis of first section
2. Verify statistics update
3. Accept some feedback
4. Verify accepted count increases
5. Reject some feedback
6. Verify rejected count increases

**Expected Backend Calls:**
- `GET /get_statistics?session_id=...`
- Response: `{sections_analyzed, total_feedback, high_risk_count, ...}`

---

## 📋 EPIC 7: DOCUMENT GENERATION

### User Story 7.1: Complete Review & Generate Document
**As** Sarah
**I want to** generate final document with all accepted feedback
**So that** I have a complete reviewed document

**Acceptance Criteria:**
- ✅ "Complete Review" button visible
- ✅ Button disabled until at least one section analyzed
- ✅ Clicking shows confirmation modal
- ✅ Confirmation shows summary (X feedback items to add)
- ✅ Submitting generates document
- ✅ Download link appears
- ✅ Downloaded document has comments in margins

**Test Steps:**
1. Analyze at least one section
2. Accept some feedback items
3. Click "Complete Review" button
4. Verify confirmation modal appears
5. Verify summary is accurate
6. Click "Generate Document"
7. Wait for generation
8. Verify download link appears
9. Click download link
10. Open downloaded document in Word
11. Verify comments appear in margins
12. Verify only accepted feedback included

**Expected Backend Calls:**
- `POST /complete_review` with `{session_id, accepted_feedback_ids: [...]}`
- Response: `{success: true, download_url: "/download/..."}`

**Logs to Check:**
- Complete review initiated
- Generating document with X feedback items
- Document generated: filename.docx

---

## 📋 EPIC 8: ERROR HANDLING

### User Story 8.1: Handle Upload Errors
**As** Sarah
**I want to** see clear error messages when upload fails
**So that** I know what went wrong

**Acceptance Criteria:**
- ✅ Invalid file type shows error
- ✅ File too large shows error
- ✅ Network error shows error
- ✅ Error messages are clear and actionable

**Test Steps:**
1. Try uploading .pdf file
2. Verify error message appears
3. Try uploading very large file
4. Verify error message appears

---

### User Story 8.2: Handle Analysis Errors
**As** Sarah
**I want to** know when analysis fails
**So that** I can retry or report issue

**Acceptance Criteria:**
- ✅ Analysis timeout shows error
- ✅ API error shows error
- ✅ Error notification dismissible
- ✅ Can retry failed analysis

**Test Steps:**
1. Disconnect internet (simulate)
2. Try analyzing section
3. Verify error message appears
4. Reconnect internet
5. Verify can retry

---

## 📋 TEST MATRIX - ALL UI BUTTONS

| # | Button/Element | Location | Expected Action | Backend Call | Test Status |
|---|---------------|----------|-----------------|--------------|-------------|
| 1 | Choose File | Landing page | Open file picker | None | ⏳ Pending |
| 2 | Upload & Start Analysis | Landing page | Upload document | POST /upload | ⏳ Pending |
| 3 | Section Dropdown | Top nav | Show sections | None | ⏳ Pending |
| 4 | Section Option | Dropdown | Analyze section | POST /analyze_section | ⏳ Pending |
| 5 | Next Section | Content area | Navigate forward | POST /analyze_section (if new) | ⏳ Pending |
| 6 | Previous Section | Content area | Navigate backward | None (cached) | ⏳ Pending |
| 7 | Accept Feedback | Feedback card | Mark accepted | None (client-side) | ⏳ Pending |
| 8 | Reject Feedback | Feedback card | Mark rejected | None (client-side) | ⏳ Pending |
| 9 | Add Custom Feedback | Feedback panel | Open form | None | ⏳ Pending |
| 10 | Submit Custom Feedback | Form modal | Add feedback | POST /add_user_feedback | ⏳ Pending |
| 11 | Cancel Custom Feedback | Form modal | Close form | None | ⏳ Pending |
| 12 | Highlight Text | Context menu | Highlight selection | None | ⏳ Pending |
| 13 | Remove Highlight | Context menu | Remove highlight | None | ⏳ Pending |
| 14 | Add Comment to Highlight | Context menu | Open comment form | None | ⏳ Pending |
| 15 | Chat Send | Chat panel | Send message | POST /chat | ⏳ Pending |
| 16 | Chat Input (Enter key) | Chat panel | Send message | POST /chat | ⏳ Pending |
| 17 | Complete Review | Bottom bar | Open confirmation | None | ⏳ Pending |
| 18 | Generate Document | Confirmation modal | Generate doc | POST /complete_review | ⏳ Pending |
| 19 | Download Document | Result modal | Download file | GET /download/... | ⏳ Pending |
| 20 | Help Button | Top nav | Show help modal | None | ⏳ Pending |
| 21 | Close Modal (X) | Any modal | Close modal | None | ⏳ Pending |
| 22 | Statistics Panel | Side panel | Show stats | GET /get_statistics | ⏳ Pending |

---

## 🐛 KNOWN ISSUES TO TEST FOR

1. **Color Highlighting Not Working** (mentioned by user)
   - Test: Select text → Click highlight → Verify background changes
   - Check: CSS classes applied, highlight state saved

2. **Modal Overlay Freezing**
   - Test: Trigger analysis → Verify can't click behind modal
   - Check: z-index, backdrop-filter CSS

3. **Section Content Display**
   - Test: Analyze section → Verify content appears
   - Check: `displaySectionContent()` function called

4. **Feedback Persistence**
   - Test: Accept feedback → Navigate away → Return → Verify still accepted
   - Check: `window.sectionData` structure

5. **Chat Context**
   - Test: Chat about section → Verify response is contextual
   - Check: `current_section` passed to backend

---

## 📊 SUCCESS CRITERIA

**For each user story:**
- ✅ All test steps pass
- ✅ Expected backend calls made
- ✅ Logs show correct behavior
- ✅ No console errors
- ✅ UI updates correctly
- ✅ State persists correctly

**Overall:**
- ✅ 100% of buttons functional
- ✅ 0 critical bugs
- ✅ All user flows complete successfully

---

**Next Steps:**
1. Execute all test scenarios
2. Record logs for each action
3. Document issues found
4. Fix all issues
5. Re-test until 100% pass rate

**Report Date:** 2025-11-20
