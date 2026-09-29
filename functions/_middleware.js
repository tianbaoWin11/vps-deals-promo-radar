export function onRequest(context) {
  const url = new URL(context.request.url);
  if (url.hostname === "vps-deals-promo-radar-7iu.pages.dev") {
    url.hostname = "vpsdealbeacon.com";
    url.protocol = "https:";
    return Response.redirect(url.toString(), 301);
  }
  return context.next();
}
