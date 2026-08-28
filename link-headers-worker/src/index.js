// paulromeo.net edge services:
// 1. RFC 8288 Link discovery headers on HTML responses
// 2. RFC 9727 API catalog at /.well-known/api-catalog
// 3. A small real API: site status (health) endpoint + OpenAPI spec + docs,
//    so the catalog describes working resources, not dangling links.
const LINK_HEADERS = [
  '</.well-known/api-catalog>; rel="api-catalog"',
  '</llms.txt>; rel="describedby"',
];

const CATALOG = {
  linkset: [
    {
      anchor: "https://paulromeo.net/status",
      "service-desc": [
        { href: "https://paulromeo.net/openapi.json", type: "application/json" },
      ],
      "service-doc": [
        { href: "https://paulromeo.net/api-docs", type: "text/html" },
      ],
      status: [
        { href: "https://paulromeo.net/status", type: "application/json" },
      ],
    },
  ],
};

const OPENAPI = {
  openapi: "3.1.0",
  info: {
    title: "paulromeo.net Site Status API",
    version: "1.0.0",
    description:
      "Minimal status API for paulromeo.net, served at the Cloudflare edge. Machine-readable catalog: /.well-known/api-catalog (RFC 9727).",
  },
  servers: [{ url: "https://paulromeo.net" }],
  paths: {
    "/status": {
      get: {
        operationId: "getStatus",
        summary: "Site status / health check",
        responses: {
          "200": {
            description: "Site is up",
            content: {
              "application/json": {
                schema: {
                  type: "object",
                  properties: {
                    status: { type: "string", enum: ["ok"] },
                    service: { type: "string" },
                    time: { type: "string", format: "date-time" },
                  },
                  required: ["status", "service", "time"],
                },
              },
            },
          },
        },
      },
    },
  },
};

const API_DOCS = `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>paulromeo.net — Site Status API</title>
<style>body{font-family:system-ui,sans-serif;max-width:44rem;margin:2rem auto;padding:0 1rem;line-height:1.6;color:#1a1a1a}
code,pre{background:#f4f4f4;border-radius:4px;padding:2px 6px;font-size:.9em}pre{padding:1rem;overflow-x:auto}
h1{font-size:1.5rem}table{border-collapse:collapse}td,th{border:1px solid #ddd;padding:.4rem .7rem;text-align:left}</style>
</head><body>
<h1>paulromeo.net — Site Status API</h1>
<p>A minimal status API served at the Cloudflare edge. No authentication required. Cataloged per <a href="https://www.rfc-editor.org/rfc/rfc9727">RFC 9727</a> at <code>/.well-known/api-catalog</code>.</p>
<h2>Endpoints</h2>
<table><tr><th>Method</th><th>Path</th><th>Description</th></tr>
<tr><td>GET</td><td><code>/status</code></td><td>Health check. Returns <code>{"status":"ok",...}</code></td></tr>
<tr><td>GET</td><td><code>/openapi.json</code></td><td>OpenAPI 3.1 spec (machine-readable, <code>service-desc</code>)</td></tr>
<tr><td>GET</td><td><code>/api-docs</code></td><td>This page (human-readable, <code>service-doc</code>)</td></tr>
<tr><td>GET</td><td><code>/.well-known/api-catalog</code></td><td>API catalog (RFC 9727 linkset)</td></tr></table>
<h2>Example</h2>
<pre>curl https://paulromeo.net/status
{"status":"ok","service":"paulromeo.net edge","time":"2026-08-28T03:21:00Z"}</pre>
<p><a href="/">← paulromeo.net</a></p>
</body></html>`;

const AUTH_MD = `# paulromeo.net auth.md

Machine-readable agent authentication policy for paulromeo.net, per the Auth.md convention.

## Audience

Agents and automated clients calling the public paulromeo.net Site Status API
(cataloged at \`/.well-known/api-catalog\` per RFC 9727, spec at \`/openapi.json\`).

## Protected resources

- \`GET https://paulromeo.net/status\` — public site health endpoint. Read-only, no sensitive data.

## Authentication

- **Method: none (anonymous public access).** No registration, no API keys, no OAuth.
- Requests are rate-limited and cached at the Cloudflare edge. Send a descriptive
  \`User-Agent\` so traffic is attributable; generic or abusive clients may be challenged.
- There is no credential to provision and nothing to store. Do not send secrets to this host.

## Agent registration

- **register_uri: none.** This service does not accept agent registration.
- No provisioning endpoint exists; public read-only access needs no account.

## OAuth

- This host is not an OAuth authorization server or protected resource, and publishes
  no \`/.well-known/oauth-protected-resource\` or authorization-server metadata, because
  none applies to its public endpoints.

## Contact

- Operator: Paul Joseph Romeo — pauljromeo@proton.me
`;

const json = (obj, cache = "public, max-age=3600") =>
  new Response(JSON.stringify(obj, null, 2) + "\n", {
    headers: { "content-type": "application/json", "cache-control": cache },
  });

export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (url.pathname === "/.well-known/api-catalog") {
      return new Response(JSON.stringify(CATALOG, null, 2) + "\n", {
        headers: {
          "content-type":
            'application/linkset+json; profile="https://www.rfc-editor.org/info/rfc9727"',
          "cache-control": "public, max-age=14400",
        },
      });
    }
    if (url.pathname === "/status") {
      return json(
        {
          status: "ok",
          service: "paulromeo.net edge",
          time: new Date().toISOString(),
        },
        "no-store"
      );
    }
    if (url.pathname === "/openapi.json") return json(OPENAPI);
    if (url.pathname === "/auth.md") {
      return new Response(AUTH_MD, {
        headers: {
          "content-type": "text/markdown; charset=utf-8",
          "cache-control": "public, max-age=14400",
        },
      });
    }
    if (url.pathname === "/api-docs") {
      return new Response(API_DOCS, {
        headers: {
          "content-type": "text/html; charset=utf-8",
          "cache-control": "public, max-age=14400",
        },
      });
    }

    const response = await fetch(request);
    const ct = response.headers.get("content-type") || "";
    if (!response.ok || !ct.includes("text/html")) return response;

    const res = new Response(response.body, response);
    for (const link of LINK_HEADERS) res.headers.append("Link", link);
    return res;
  },
};
