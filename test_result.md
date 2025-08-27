#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "Build a fully functional typing practice website with a 3D interactive experience using React frontend and FastAPI+Mongo backend. Track sessions, show stats, and a leaderboard."
backend:
  - task: "Root health endpoint (/api/)"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implemented APIRouter with prefix /api and root GET returning {message: 'Hello World'}."
      - working: true
        agent: "testing"
        comment: "✅ PASSED: GET /api/ returns correct {message: 'Hello World'} response with status 200. Endpoint working perfectly."
  - task: "Create typing session (/api/sessions POST)"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Validates input, saves UUID doc to Mongo, returns created session with id and created_at."
      - working: true
        agent: "testing"
        comment: "✅ PASSED: POST /api/sessions creates sessions with valid UUID ids, ISO datetime strings for created_at, persists to MongoDB correctly. Validation works - negative wpm/accuracy properly returns 400 status. All requirements met."
  - task: "List sessions (/api/sessions GET)"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Supports optional user_id filter and sorts by created_at desc."
      - working: true
        agent: "testing"
        comment: "✅ PASSED: GET /api/sessions returns all sessions and correctly filters by user_id parameter. All returned sessions match the filter criteria when specified."
  - task: "Leaderboard (/api/leaderboard GET)"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Fetches top sessions by wpm with projected fields."
      - working: true
        agent: "testing"
        comment: "✅ PASSED: GET /api/leaderboard returns entries correctly sorted by WPM descending. Tested with multiple entries (92.7, 85.2, 75.5, 68.4 WPM) - perfect sorting confirmed. Response format includes all required fields."
  - task: "CORS and env adherence"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "CORS enabled, Mongo uses MONGO_URL and DB_NAME from env; all routes under /api."
      - working: true
        agent: "testing"
        comment: "✅ PASSED: All routes properly prefixed with /api, CORS working (successful API calls from external URL), environment variables correctly used (MONGO_URL, DB_NAME), UUIDs used instead of ObjectIDs, datetime fields returned as ISO strings."
frontend:
  - task: "3D-like typing UI with keyboard animation and hands"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "CSS 3D scene with monitor, animated keys reacting to keydown, and hand movement. No external 3D engine to keep MVP fast."
  - task: "Frontend API integration via REACT_APP_BACKEND_URL"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Uses process.env.REACT_APP_BACKEND_URL + '/api' without hardcoding."
metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 0
  run_ui: false

test_plan:
  current_focus:
    - "Root health endpoint (/api/)"
    - "Create typing session (/api/sessions POST)"
    - "List sessions (/api/sessions GET)"
    - "Leaderboard (/api/leaderboard GET)"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "Please verify backend endpoints per test_plan. Use default env; no auth. For POST /api/sessions use a realistic payload. Also verify that invalid metrics (negative wpm/accuracy) return 400."