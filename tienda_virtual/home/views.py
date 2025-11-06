from django.shortcuts import render
from django.conf import settings

from .models import Escaparate, Articulo, Reservation
from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse, Http404
from django.urls import reverse

import time
import json
import urllib.request
import urllib.error

# Simple in-memory cache for Instagram feed to avoid hitting the API on every request
_INSTAGRAM_CACHE = {
    "ts": 0,
    "data": [],
    "profile": None,
}


def _fetch_instagram_posts(access_token, limit=6):
    """Fetch recent Instagram media using the Basic Display API access token.

    Returns a list of dicts: {media_url, permalink, caption, media_type}
    If the access_token is missing or the request fails, returns an empty list.
    """
    if not access_token:
        return []

    ttl = getattr(settings, "INSTAGRAM_FEED_TTL", 300)
    now = time.time()
    # use cached data when fresh
    if now - _INSTAGRAM_CACHE["ts"] < ttl and _INSTAGRAM_CACHE["data"]:
        return _INSTAGRAM_CACHE["data"]

    url = (
        "https://graph.instagram.com/me/media?fields=id,caption,media_type,media_url,permalink,thumbnail_url,timestamp"
        f"&access_token={access_token}"
    )
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            body = resp.read()
            data = json.loads(body.decode("utf-8"))
            items = []
            for m in data.get("data", [])[:limit]:
                media_url = m.get("media_url") or m.get("thumbnail_url")
                # If carousel and no direct media_url, fetch first child's media
                if m.get("media_type") == "CAROUSEL_ALBUM" and not media_url:
                    try:
                        child_url = (
                            f"https://graph.instagram.com/{m.get('id')}?fields=children{{id,media_type,media_url,thumbnail_url}}&access_token={access_token}"
                        )
                        with urllib.request.urlopen(child_url, timeout=6) as creq:
                            cbody = creq.read()
                            cdata = json.loads(cbody.decode("utf-8"))
                            children = cdata.get("children", {}).get("data", [])
                            if children:
                                child = children[0]
                                media_url = child.get("media_url") or child.get("thumbnail_url")
                    except Exception:
                        # ignore child fetch errors, keep media_url None
                        media_url = media_url

                items.append({
                    "media_url": media_url,
                    "permalink": m.get("permalink"),
                    "caption": (m.get("caption") or "")[:300],
                    "media_type": m.get("media_type"),
                    "timestamp": m.get("timestamp"),
                })
            _INSTAGRAM_CACHE["ts"] = now
            _INSTAGRAM_CACHE["data"] = items
            return items
    except urllib.error.HTTPError as e:
        # log and return empty
        try:
            err = e.read().decode()
        except Exception:
            err = str(e)
        print("Instagram fetch error:", err)
        return []
    except Exception as e:
        print("Instagram fetch exception:", e)
        return []


def _fetch_instagram_profile(access_token):
    """Fetch simple profile info (username) for the configured Instagram account."""
    if not access_token:
        return None

    # Use cached profile when fresh
    ttl = getattr(settings, "INSTAGRAM_FEED_TTL", 300)
    now = time.time()
    if _INSTAGRAM_CACHE.get("profile") and (now - _INSTAGRAM_CACHE["ts"] < ttl):
        return _INSTAGRAM_CACHE.get("profile")

    url = f"https://graph.instagram.com/me?fields=id,username&access_token={access_token}"
    try:
        with urllib.request.urlopen(url, timeout=6) as resp:
            body = resp.read()
            data = json.loads(body.decode("utf-8"))
            profile = {"id": data.get("id"), "username": data.get("username")}
            _INSTAGRAM_CACHE["profile"] = profile
            return profile
    except Exception as e:
        print("Instagram profile fetch error:", e)
        return None


def index(request):
    """Home page: show featured article and a carousel of articles."""
    articulos = Articulo.objects.all()
    articulo = articulos.first()

    # Attempt to load Instagram posts server-side if configured
    access_token = getattr(settings, "INSTAGRAM_ACCESS_TOKEN", None)
    instagram_posts = _fetch_instagram_posts(access_token, limit=6) if access_token else []
    instagram_profile = _fetch_instagram_profile(access_token) if access_token else None

    contexto = {
        "nombre_articulo": articulo.nombre if articulo else "Artículo",
        "articulos": articulos,
    "instagram_posts": instagram_posts,
    "instagram_profile": instagram_profile,
    }
    return render(request, "index.html", contexto)


def reservations(request):
    """Reservation page for massages. Saves reservation to database."""
    message = None
    if request.method == "POST":
        cliente = request.POST.get("name")
        fecha = request.POST.get("date")
        hora = request.POST.get("time")
        servicio = request.POST.get("service")
        # Basic save to DB
        try:
            Reservation.objects.create(
                name=cliente or "Cliente",
                date=fecha,
                time=hora,
                service=servicio or "Masaje"
            )
            cliente_display = cliente if cliente else "Cliente"
            message = f"Reserva confirmada para {cliente_display} - {servicio} el {fecha} a las {hora}"
        except Exception as e:
            message = f"No se pudo crear la reserva: {e}"
    return render(request, "reservations.html", {"message": message})


def contact(request):
    """Contact page with company, store and owner info and an embedded Google Map."""
    address = getattr(settings, "COMPANY_ADDRESS", "Calle Falsa 123, Ciudad")
    owner = getattr(settings, "COMPANY_OWNER", "Propietario")
    email = getattr(settings, "COMPANY_EMAIL", "owner@example.com")
    # Build a Google Maps embed URL using the address
    import urllib.parse
    q = urllib.parse.quote_plus(address)
    map_src = f"https://www.google.com/maps?q={q}&output=embed"
    contexto = {"address": address, "owner": owner, "email": email, "map_src": map_src}
    return render(request, "contact.html", contexto)


def product_detail(request, pk):
    """Show product detail and a link to Herbalife with the client's sale code."""
    try:
        product = Articulo.objects.get(pk=pk)
    except Articulo.DoesNotExist:
        raise Http404("Producto no encontrado")

    sale_code = getattr(settings, "HERBALIFE_SALE_CODE", "YOUR_SALE_CODE")
    base = getattr(settings, "HERBALIFE_BASE_URL", "https://www.herbalife.com/product")
    # Construct an example external link - adapt parameters to the actual affiliate format
    herbalife_url = f"{base}/{product.id}?ref={sale_code}"
    contexto = {"product": product, "herbalife_url": herbalife_url}
    return render(request, "product_detail.html", contexto)


def catalog(request):
    """Catalog page: initial page render includes first page of products. Infinite scroll uses products_api."""
    qs = Articulo.objects.all().order_by('id')
    paginator = Paginator(qs, 12)
    page1 = paginator.get_page(1)
    contexto = {"products": page1, "has_next": page1.has_next(), "next_page": 2}
    return render(request, "catalog.html", contexto)


def products_api(request):
    """API endpoint returning JSON list of products for infinite scroll."""
    page = int(request.GET.get('page', '1'))
    per_page = int(request.GET.get('per_page', '12'))
    qs = Articulo.objects.all().order_by('id')
    paginator = Paginator(qs, per_page)
    try:
        pg = paginator.get_page(page)
    except EmptyPage:
        return JsonResponse({"products": [], "has_next": False})

    products = []
    for p in pg:
        products.append({
            "id": p.id,
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "price": str(p.price),
            "image_url": p.image_url or "",
            "detail_url": reverse('product_detail', args=[p.id]),
        })

    return JsonResponse({"products": products, "has_next": pg.has_next(), "next_page": pg.next_page_number() if pg.has_next() else None})