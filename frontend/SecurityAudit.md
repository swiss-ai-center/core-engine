# Frontend Security Audit

Audit date: 2026-05-21  
Scope: `frontend` plus frontend-to-backend trust boundaries  
Scan bundle: `/tmp/codex-security-scans/core-engine/c84d2aa_20260521T124043Z`

## Executive Summary

I did not find a standalone high-severity frontend-only bug such as unsafe HTML rendering or direct DOM script injection. The main frontend risk is that the app talks directly to a backend that has no repository-visible authentication or authorization, so the UI exposes powerful backend actions to any browser that can reach the configured engine URL.

## Finding: Frontend Calls A Public Backend Without An Auth Boundary

Priority: P1  
Severity: high, inherited from backend  
Confidence: high  
CWE: CWE-306, CWE-862  
Affected lines:

- `frontend/src/utils/api.tsx:48` builds requests directly from `REACT_APP_ENGINE_URL`.
- `frontend/src/utils/useWebSocketConnection.tsx:9` connects directly to `REACT_APP_ENGINE_WS_URL`.
- `frontend/src/utils/api.tsx:163` creates pipelines.
- `frontend/src/utils/api.tsx:296` posts files to dynamic service/pipeline routes.
- `frontend/src/utils/api.tsx:341` wakes services.

### Summary

The frontend does not attach credentials or enforce a user/session boundary before calling backend control-plane APIs and WebSocket endpoints. Client-side checks cannot protect the backend, and the backend currently does not provide the missing auth boundary either.

### Impact

Any user who can open the app, or call the backend directly, can reach backend actions that create pipelines, trigger services, wake services, fetch tasks, and download storage objects. The backend audit contains the critical follow-on findings: pipeline `eval` code execution and storage credential disclosure to registered services.

### Remediation

Implement server-side authentication and authorization in the backend, then update the frontend to use the selected login/session/token flow. Avoid treating React route visibility, hidden buttons, or browser state as access control. Add integration tests that unauthenticated browser/API calls fail.

## Reviewed And Not Promoted

- Markdown rendering: `frontend/src/components/InformationDrawer/InformationDrawer.tsx:355` renders service descriptions with `react-markdown`, `defaultUrlTransform`, and `skipHtml={true}` at line 363. I did not find `dangerouslySetInnerHTML`.
- API query construction: `frontend/src/utils/api.tsx` concatenates query strings manually. This should use `URLSearchParams` or `encodeURIComponent`, but I did not find a frontend-only high-impact exploit from it.
- WebSocket handling: the frontend sends execution IDs after task creation, but the server accepts arbitrary IDs. The vulnerability is server-side and covered in the backend audit.

## Frontend Hardening Notes

- `frontend/nginx.conf` serves the app without explicit security headers. Add a CSP appropriate for the app, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, and clickjacking protection if the app should not be framed.
- Remove the request header `Access-Control-Allow-Origin` in `frontend/src/utils/api.tsx:5`; CORS is controlled by server responses, not browser request headers.
- Run a current dependency advisory audit in CI. I could not run `npm audit` locally because `npm` was unavailable in this environment.

## Backend Findings Affecting Frontend Users

- Critical: pipeline step conditions are executed with backend Python `eval`.
- Critical: registered service URLs receive S3/MinIO credentials in task payloads.
- High: backend HTTP and WebSocket control plane lacks server-side auth.
- High: MinIO manifests expose public hosts with committed static credentials.
