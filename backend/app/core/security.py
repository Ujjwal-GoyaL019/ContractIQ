import os
import re
import uuid
import pathlib
from typing import Tuple, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from fastapi import UploadFile, HTTPException, status, Header, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
import bcrypt
from sqlalchemy.orm import Session
from app.config import settings
from app.core.exceptions import IngestionException
from app.core.logging import logger

MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 Megabytes
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
PDF_MAGIC_BYTES = b"%PDF-"

# JWT configuration
JWT_SECRET_KEY = settings.SECRET_KEY or "contractiq-secret-jwt-key-38bdf8"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a bcrypt hash."""
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False



def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT access token with expiration."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": int(expire.timestamp()), "iat": int(now.timestamp())})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return None


def sanitize_filename(filename: str) -> str:
    """
    Strips directory traversal sequences, path separators, and illegal characters.
    """
    base_name = pathlib.Path(filename).name
    clean_name = re.sub(r"[^a-zA-Z0-9._-]", "_", base_name)
    return clean_name or "document.pdf"


async def validate_and_save_upload(
    upload_file: UploadFile,
    destination_dir: str,
    prefix_id: str
) -> Tuple[str, str, int]:
    """
    Secure file validation and disk storage:
    1. Validates file extension against allowed whitelist (.pdf, .txt, .md).
    2. Enforces strict file size ceiling (MAX_FILE_SIZE_BYTES).
    3. Validates magic bytes for PDF headers (%PDF-).
    4. Protects against directory traversal and overwrites using UUID-scoped safe paths.

    Returns (safe_filename, absolute_file_path, file_size_bytes).
    """
    raw_filename = upload_file.filename or "upload.pdf"
    clean_filename = sanitize_filename(raw_filename)
    ext = pathlib.Path(clean_filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise IngestionException(
            f"Unsupported file format '{ext}'. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read first 1KB chunk to verify magic bytes and stream in bounded memory
    header_chunk = await upload_file.read(1024)
    if not header_chunk:
        raise IngestionException("Uploaded file is empty.")

    if ext == ".pdf" and not header_chunk.startswith(PDF_MAGIC_BYTES):
        raise IngestionException(
            "File header mismatch: File claims to be a PDF but does not contain valid '%PDF-' magic bytes."
        )

    # Prepare safe destination path
    unique_filename = f"{prefix_id}_{uuid.uuid4().hex[:8]}_{clean_filename}"
    dest_path = os.path.abspath(os.path.join(destination_dir, unique_filename))

    # Ensure path stays strictly inside destination_dir
    if not dest_path.startswith(os.path.abspath(destination_dir)):
        raise IngestionException("Path traversal attempt detected.")

    os.makedirs(destination_dir, exist_ok=True)
    total_size = len(header_chunk)

    try:
        with open(dest_path, "wb") as f:
            f.write(header_chunk)
            while chunk := await upload_file.read(64 * 1024):  # 64KB chunks
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE_BYTES:
                    f.close()
                    if os.path.exists(dest_path):
                        os.remove(dest_path)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES / (1024*1024):.0f}MB."
                    )
                f.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(dest_path):
            os.remove(dest_path)
        logger.error(f"Error saving upload: {e}")
        raise IngestionException(f"Failed to securely save file: {str(e)}")

    return unique_filename, dest_path, total_size
