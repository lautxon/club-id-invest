# Club ID Invest Frontend

Next.js 14 frontend for Club ID Invest platform.

## Getting Started

### Install dependencies

```bash
npm install
```

### Configure environment

Create `.env.local`:

```env
API_URL=http://localhost:8000/api
```

### Run development server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
src/
├── app/
│   ├── dashboard/
│   │   └── page.tsx          # Dashboard page
│   ├── login/
│   │   └── page.tsx          # Login page
│   ├── register/
│   │   └── page.tsx          # Register page
│   ├── globals.css           # Global styles
│   ├── layout.tsx            # Root layout
│   ├── page.tsx              # Home page
│   └── providers.tsx         # React Query + Auth providers
├── components/
│   ├── AlertSystem.tsx       # Alert notifications
│   ├── DashboardMember.tsx   # Main dashboard
│   ├── ProjectCard.tsx       # Project display card
│   └── ui.tsx                # UI primitives
└── lib/
    ├── api.ts                # API client
    ├── auth-store.ts         # Auth state management
    └── utils.ts              # Utility functions
```

## Features

- **Authentication**: JWT-based auth with refresh tokens
- **Dashboard**: Portfolio overview with stats and alerts
- **Projects**: Browse and invest in available projects
- **Alerts**: Real-time notifications for deadlines and payments

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Framer Motion (animations)
- Zustand (state management)
- TanStack Query (data fetching)
- Axios (HTTP client)
