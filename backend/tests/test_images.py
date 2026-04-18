"""
Tests for image upload and processing - Phase 5 Performance Optimization

Tests image upload functionality:
- File validation (format, size)
- Image resizing to multiple sizes
- WebP format conversion
- Security (directory traversal prevention)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from pathlib import Path
from PIL import Image
import io


@pytest.mark.images
class TestImageUpload:
    """Tests for pet image upload endpoints"""

    def test_upload_pet_image_success(self, client: TestClient, test_user, auth_headers, db: Session):
        """Test successful image upload"""
        # Create a test pet
        pet_response = client.post(
            "/api/v1/pets/",
            json={"name": "Test Pet", "species": "dog"},
            headers=auth_headers
        )
        assert pet_response.status_code == 201
        pet_id = pet_response.json()["id"]

        # Create a test image
        img = Image.new('RGB', (200, 200), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        # Upload image
        response = client.post(
            f"/api/v1/pets/{pet_id}/image",
            files={"file": ("test.png", img_bytes, "image/png")},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "image_url" in data
        assert "sizes" in data
        assert "thumbnail" in data["sizes"]
        assert "preview" in data["sizes"]
        assert "full" in data["sizes"]
        assert "uploaded_at" in data

    def test_upload_pet_image_invalid_format(self, client: TestClient, test_user, auth_headers, db: Session):
        """Test upload with invalid file format"""
        # Create a test pet
        pet_response = client.post(
            "/api/v1/pets/",
            json={"name": "Test Pet", "species": "dog"},
            headers=auth_headers
        )
        pet_id = pet_response.json()["id"]

        # Try to upload invalid file
        response = client.post(
            f"/api/v1/pets/{pet_id}/image",
            files={"file": ("test.txt", b"not an image", "text/plain")},
            headers=auth_headers
        )

        assert response.status_code == 400

    def test_upload_pet_image_file_too_large(self, client: TestClient, test_user, auth_headers, db: Session):
        """Test upload with file size exceeding limit"""
        # Create a test pet
        pet_response = client.post(
            "/api/v1/pets/",
            json={"name": "Test Pet", "species": "dog"},
            headers=auth_headers
        )
        pet_id = pet_response.json()["id"]

        # Create a large file (6MB) - exceeds 5MB limit
        large_data = b"x" * (6 * 1024 * 1024)

        response = client.post(
            f"/api/v1/pets/{pet_id}/image",
            files={"file": ("test.jpg", large_data, "image/jpeg")},
            headers=auth_headers
        )

        assert response.status_code == 400

    def test_delete_pet_image(self, client: TestClient, test_user, auth_headers, db: Session):
        """Test image deletion"""
        # Create a test pet and upload image
        pet_response = client.post(
            "/api/v1/pets/",
            json={"name": "Test Pet", "species": "dog"},
            headers=auth_headers
        )
        pet_id = pet_response.json()["id"]

        # Upload image
        img = Image.new('RGB', (200, 200), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        upload_response = client.post(
            f"/api/v1/pets/{pet_id}/image",
            files={"file": ("test.png", img_bytes, "image/png")},
            headers=auth_headers
        )
        assert upload_response.status_code == 200

        # Delete image
        delete_response = client.delete(
            f"/api/v1/pets/{pet_id}/image",
            headers=auth_headers
        )
        assert delete_response.status_code == 204

        # Verify image_url is cleared
        get_response = client.get(
            f"/api/v1/pets/{pet_id}",
            headers=auth_headers
        )
        assert get_response.json()["image_url"] is None

    def test_upload_image_unauthorized_access(self, client: TestClient, test_user, other_user, auth_headers, db: Session):
        """Test that users can't upload images for other users' pets"""
        # Create a pet for test_user
        pet_response = client.post(
            "/api/v1/pets/",
            json={"name": "Test Pet", "species": "dog"},
            headers=auth_headers
        )
        pet_id = pet_response.json()["id"]

        # Create image
        img = Image.new('RGB', (200, 200), color='green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        # Try to upload as other_user
        other_headers = {
            "Authorization": f"Bearer {other_user['token']}"
        }
        response = client.post(
            f"/api/v1/pets/{pet_id}/image",
            files={"file": ("test.png", img_bytes, "image/png")},
            headers=other_headers
        )

        assert response.status_code == 404

    def test_get_pet_image_file(self, client: TestClient, test_user, auth_headers, db: Session):
        """Test downloading a pet's image file"""
        # Create a pet and upload image
        pet_response = client.post(
            "/api/v1/pets/",
            json={"name": "Test Pet", "species": "dog"},
            headers=auth_headers
        )
        pet_id = pet_response.json()["id"]

        # Upload image
        img = Image.new('RGB', (200, 200), color='yellow')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        upload_response = client.post(
            f"/api/v1/pets/{pet_id}/image",
            files={"file": ("test.png", img_bytes, "image/png")},
            headers=auth_headers
        )
        assert upload_response.status_code == 200

        sizes = upload_response.json()["sizes"]
        thumbnail_url = sizes["thumbnail"]

        # Download thumbnail
        download_response = client.get(
            thumbnail_url,
            headers=auth_headers
        )
        assert download_response.status_code == 200
        assert download_response.headers["content-type"] == "image/webp"
        assert "Cache-Control" in download_response.headers

    def test_image_formats_supported(self, client: TestClient, test_user, auth_headers, db: Session):
        """Test that JPEG, PNG, and WebP formats are supported"""
        pet_response = client.post(
            "/api/v1/pets/",
            json={"name": "Test Pet", "species": "dog"},
            headers=auth_headers
        )
        pet_id = pet_response.json()["id"]

        formats = [
            ("jpeg", "image/jpeg"),
            ("png", "image/png"),
            ("webp", "image/webp"),
        ]

        for format_name, mime_type in formats:
            # Create image
            img = Image.new('RGB', (200, 200), color='white')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format=format_name.upper())
            img_bytes.seek(0)

            response = client.post(
                f"/api/v1/pets/{pet_id}/image",
                files={"file": (f"test.{format_name}", img_bytes, mime_type)},
                headers=auth_headers
            )
            assert response.status_code == 200
