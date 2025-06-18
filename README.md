# RecruitX

RecruitX is an AI-driven phone interview assistant that automates candidate interviews using Twilio for outbound calls, Groq LLM for question generation and scoring, and Supabase (Postgres) for data storage. The backend is built with FastAPI and is ready for cloud deployment (e.g., Railway).

---

## Features
- **Automated outbound phone interviews** (no inbound calls required)
- **AI-generated interview questions** based on job description
- **Speech-to-text** via Twilio, with language support
- **LLM-powered scoring**: Each candidate response is analyzed and scored out of 10
- **Interview flow management**: Handles greeting, question/response, timing, and completion
- **Error handling**: Graceful fallback for any application error
- **Comprehensive reporting**: Stores all responses and generates a final report
- **API-first**: All features accessible via REST endpoints

---

## Tech Stack
- **Backend:** FastAPI (Python)
- **AI/LLM:** Groq (Llama-3.3-70b-versatile)
- **Telephony:** Twilio Voice API
- **Database:** Supabase (Postgres)
- **Deployment:** Railway (recommended), or any cloud

---

## Setup Instructions

### 1. Clone the Repo
```sh
git clone https://github.com/yourusername/recruitx.git
cd recruitx
```

### 2. Create and Activate Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root with the following keys:

```
# LiveKit (optional)
LIVEKIT_URL=
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=

# Groq
GROQ_API_KEY=your-groq-api-key

# Twilio
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-auth
TWILIO_PHONE_NUMBER=your-twilio-number

# Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
DATABASE_URL=your-supabase-postgres-url

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Public Base URL
PUBLIC_BASE_URL=your-public-url (e.g., Railway URL after deploy)
```

---

## Running Locally
```sh
uvicorn app.main:app --reload
```
- Access Swagger UI at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Deploying to Railway
1. Push your code to GitHub.
2. Create a new Railway project and link your repo.
3. Set all environment variables in the Railway dashboard.
4. Use the start command:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
5. After deploy, update `PUBLIC_BASE_URL` to your Railway URL.
6. Update Twilio webhooks to use your Railway URL.

---

## API Overview
- **/api/v1/candidates/**: Manage candidates
- **/api/v1/interviews/schedule**: Schedule a new interview
- **/api/v1/interviews/{interview_id}/start**: Start an interview (initiates call)
- **/api/v1/interviews/{interview_id}/twiml**: Twilio webhook for call flow
- **/api/v1/interviews/{interview_id}/response/{question_index}**: Handles candidate responses
- **/api/v1/interviews/{interview_id}/complete**: Completes interview and generates report
- **/api/v1/reports/**: Access interview reports

---

## Interview Flow
1. **Outbound call** to candidate (no inbound calls)
2. **Greeting**: Candidate is greeted by name and job role
3. **Questions**: 5 AI-generated questions, each with a 7-second pause after answer
4. **Scoring**: Each answer is scored out of 10 by the LLM
5. **Data Storage**: All questions, responses, and marks are stored
6. **Completion**: After last question, candidate is thanked and call ends
7. **Report**: Final report is generated and stored

---

## Notes
- All sensitive data (API keys, DB URLs) should be kept in `.env` (never committed)
- For local Twilio testing, use ngrok or deploy to Railway for public webhooks
- Error handling ensures candidates always get a friendly message, even if something goes wrong


---

**Built with ❤️ by [Ritam Nandy]** 