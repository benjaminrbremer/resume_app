# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
npm install   # requires Node 18+
npm run dev   # http://localhost:3000
```

## App Router conventions

All pages use the Next.js 14 App Router (`app/` directory). Every route is a `page.tsx` that exports a default React component. Server components by default — add `"use client"` at the top only when the component needs state, effects, or browser APIs.

Dynamic routes use bracket syntax: `app/applications/[id]/page.tsx` receives `{ params: { id: string } }` as props.

## Backend API

The FastAPI backend runs on `http://localhost:8000`. CORS is configured in `backend/main.py` (currently commented out — uncomment it before making any fetch calls from the frontend).

All API routes are currently stubs returning 501. See `backend/routers/schemas.py` for the expected request/response shapes.

## Styling

Tailwind CSS only — no component library. Follow the conventions already in use: `rounded-xl`, `border border-gray-200`, `text-sm`, `font-semibold` for cards and labels. The primary brand color is `indigo-600`.

## Primary UI pattern

The application chat page (`/applications/[id]`) uses a two-column layout: document preview on the left, chat interface on the right. New UI added to this page should preserve this split and use `flex h-[calc(100vh-8rem)]` as the outer container.
