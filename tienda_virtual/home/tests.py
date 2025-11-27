from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from home.models import Articulo, Reservation
import unittest
from unittest.mock import patch, Mock
from home.utils.scraping import scrape_herbalife_product

# ===========================

# Tests de modelo

# ===========================

class ArticuloModelTests(TestCase):


    def test_str(self):
        a = Articulo.objects.create(nombre="Producto X", descripcion="Desc")
        self.assertEqual(str(a), "Producto X")


# ===========================

# Tests de vista: página principal

# ===========================

class IndexViewTests(TestCase):


    def setUp(self):
        self.client = Client()
        Articulo.objects.create(nombre="Test", descripcion="Desc")

    @patch("home.views._fetch_instagram_posts", return_value=[])
    @patch("home.views._fetch_instagram_profile", return_value=None)
    def test_index_view_loads(self, mock_profile, mock_posts):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test")  # nombre del artículo en el template


# ===========================

# Tests de vista: catálogo y API

# ===========================

class CatalogViewTests(TestCase):


    def setUp(self):
        self.client = Client()
        for i in range(15):
            Articulo.objects.create(nombre=f"Prod {i}", descripcion="d")

    def test_catalog_first_page_renders(self):
        response = self.client.get(reverse("catalog"))
        self.assertEqual(response.status_code, 200)
        # Deben aparecer los 12 primeros productos
        self.assertContains(response, "Prod 0")
        self.assertContains(response, "Prod 11")

    def test_products_api_pagination(self):
        response = self.client.get(reverse("products_api") + "?page=2")
        data = response.json()
        self.assertFalse(data["has_next"])
        self.assertEqual(len(data["products"]), 3)  # los 3 restantes


# ===========================

# Tests de vista: detalle de producto

# ===========================

class ProductDetailTests(TestCase):


    def setUp(self):
        self.client = Client()
        self.articulo = Articulo.objects.create(
            nombre="Producto Herbalife",
            descripcion="d"
        )

    @patch("home.views.scrape_herbalife_product", return_value="https://herbalife.test/producto")
    def test_redirects_to_herbalife(self, mock_scrape):
        url = reverse("product_detail", args=[self.articulo.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("herbalife.test", response["Location"])

    @patch("home.views.scrape_herbalife_product", return_value=None)
    def test_herbalife_not_found(self, mock_scrape):
        url = reverse("product_detail", args=[self.articulo.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Oops, este Herbalife no vende este producto")


# ===========================

# Tests de interfaz: reservas

# ===========================

class ReservationViewInterfaceTests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_reservation_get_renders_page(self):
        """Comprobar que la página de reservas carga correctamente."""
        response = self.client.get(reverse("reservations"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reservar un masaje")

    def test_reservation_post_creates_object(self):
        """Verificar que al enviar la reserva se crea un objeto en DB."""
        data = {
            "name": "Carlos",
            "fecha": "2025-01-02",   # ← Cambiado de 'date' a 'fecha'
            "hora": "15:00",         # ← Cambiado de 'time' a 'hora'
            "service": "Masaje"
        }
        response = self.client.post(reverse("reservations"), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reservation.objects.count(), 1)
        r = Reservation.objects.first()
        self.assertEqual(r.nombre, "Carlos")
        self.assertEqual(str(r.fecha), "2025-01-02")
        self.assertEqual(str(r.hora), "15:00:00")
        self.assertEqual(r.servicio, "Masaje")


# ===========================
# Tests de utilidad: scraping Herbalife
# ===========================

class HerbalifeScrapingTests(TestCase):

    @patch("home.utils.scraping.requests.get")
    def test_scrape_product_found(self, mock_get):
        """Verifica que se devuelve la URL cuando el producto existe."""
        html = '<html><body><a href="/product/123">Masaje</a></body></html>'
        mock_resp = Mock(status_code=200, text=html)
        mock_get.return_value = mock_resp

        url = scrape_herbalife_product("Masaje")
        self.assertEqual(url, "https://www.herbalife.com/product/123")

    @patch("home.utils.scraping.requests.get")
    def test_scrape_product_not_found(self, mock_get):
        """Verifica que devuelve None si no encuentra el producto."""
        html = '<html><body>No products here</body></html>'
        mock_resp = Mock(status_code=200, text=html)
        mock_get.return_value = mock_resp

        url = scrape_herbalife_product("Masaje")
        self.assertIsNone(url)

    @patch("home.utils.scraping.requests.get")
    def test_scrape_request_exception(self, mock_get):
        """Verifica que devuelve None si ocurre un error en la request."""
        mock_get.side_effect = Exception("Network error")
        url = scrape_herbalife_product("Masaje")
        self.assertIsNone(url)

# ===========================
# Tests de vistas adicionales
# ===========================

class AdditionalViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.articulo = Articulo.objects.create(nombre="Producto Test", descripcion="Desc")

    def test_contact_view_renders(self):
        response = self.client.get(reverse("contact"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Av. Santa Lucía")

    def test_catalog_view_contains_products(self):
        response = self.client.get(reverse("catalog"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.articulo.nombre)

    def test_products_api_returns_json(self):
        response = self.client.get(reverse("products_api") + "?page=1&per_page=1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("products", data)
        self.assertTrue(len(data["products"]) > 0)
        self.assertIn("detail_url", data["products"][0])

    def test_available_slots_returns_booked_times(self):
        Reservation.objects.create(nombre="Ana", fecha="2025-01-05", hora="10:00")
        response = self.client.get(reverse("available_slots") + "?date=2025-01-05")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("10:00:00", data["booked"])

    def test_crear_reserva_post_creates_reservation(self):
        data = {"name": "Juan", "fecha": "2025-02-02", "hora": "16:00"}
        response = self.client.post(reverse("crear_reserva"), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reservation.objects.count(), 1)
        r = Reservation.objects.first()
        self.assertEqual(r.nombre, "Juan")
        self.assertEqual(str(r.fecha), "2025-02-02")
        self.assertEqual(str(r.hora), "16:00:00")

    def test_crear_reserva_get_redirects(self):
        response = self.client.get(reverse("crear_reserva"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("reservar"), response.url)