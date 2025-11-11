from django.shortcuts import redirect, render, get_object_or_404
from django.conf import settings
from django.http import JsonResponse, HttpResponse

from .models import Escaparate, Articulo, Reservation
from django.core.paginator import Paginator, EmptyPage
from django.urls import reverse
from .utils.scraping import scrape_herbalife_product

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
    contexto = {
        "address": "Av. Santa Lucía, 6241500 Alcalá de Guadaíra, Sevilla",
        "owner": "Nombre del Propietario",
        "email": "owner@example.com",
        "map_data": {
            "lat": 37.3369,   # Coordenadas aproximadas
            "lng": -5.8367,
            "address": "Av. Santa Lucía, 6241500 Alcalá de Guadaíra, Sevilla"
        }
    }
    return render(request, "contact.html", contexto)




def product_detail(request, product_id):
    """
    View to handle product details. Redirects to Herbalife if the product exists there.
    """
    product = get_object_or_404(Articulo, id=product_id)

    # Check if the product exists on Herbalife
    if not product.herbalife_url:
        product.herbalife_url = scrape_herbalife_product(product.nombre)
        product.save()

    if product.herbalife_url:
        return redirect(product.herbalife_url)
    else:
        return HttpResponse("<h1>Oops, este Herbalife no vende este producto...</h1>")


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

def reservar(request):
    return render(request, "reservas/reservartions.html")

def crear_reserva(request):
    if request.method == "POST":
        nombre = request.POST["name"]
        fecha = request.POST["fecha"]
        hora = request.POST["hora"]
        Reservation.objects.create(nombre=nombre, fecha=fecha, hora=hora)
        return render(request, "reservas/reservations.html", {"message": "¡Reserva creada con éxito!"})
    return redirect("reservar")

def available_slots(request):
    date = request.GET.get("date")
    booked = list(Reservation.objects.filter(fecha=date).values_list("hora", flat=True))
    return JsonResponse({"booked": booked})