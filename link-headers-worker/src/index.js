// Adds RFC 8288 Link discovery headers to HTML responses for paulromeo.net,
// and serves /.well-known/api-catalog per RFC 9727 (empty linkset = no APIs
// published yet, which is the truth — but the link resolves instead of 404ing).
const LINK_HEADERS = [
  '</.well-known/api-catalog>; rel="api-catalog"',
  '</llms.txt>; rel="describedby"',
];

const API_CATALOG = `{"linkset": []}`;

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === "/.well-known/api-catalog") {
      return new Response(API_CATALOG, {
        headers: {
          "content-type": 'application/linkset+json; profile="https://www.rfc-editor.org/info/rfc9727"',
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
