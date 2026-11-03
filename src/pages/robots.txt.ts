import type { APIRoute } from "astro";
import { BASE } from "../lib/site";

export const GET: APIRoute = () => new Response(`User-agent: *\nAllow: /\nSitemap: ${BASE}sitemap.xml\n`);
