#!/usr/bin/env python3
"""Test sicuro per storage - NON espone credenziali"""

import sys
import os

sys.path.append(".")


def test_safe():
    print("🔍 Test configurazione sicura...")

    try:
        from app.config import settings

        print(f"✅ Storage backend: {settings.storage_backend}")
        print(f"✅ S3 bucket: {settings.s3_bucket_name}")
        print(f"✅ S3 region: {settings.s3_region}")
        # NON mostriamo credenziali
        print("✅ Credenziali: [NASCOSTO PER SICUREZZA]")

        if settings.s3_access_key_id:
            print("⚠️  ATTENZIONE: Credenziali nel .env - rimuovi per sicurezza!")
        else:
            print("✅ Nessuna credenziale nel .env (usa aws configure)")

    except Exception as e:
        print(f"❌ Errore: {e}")


def simple_test():
    print("🔍 Test semplice salvataggio...")

    try:
        # Usa il FileManager esistente
        from app.core.file_manager import FileManager

        file_manager = FileManager()

        # Salva un file JSON semplice
        test_data = {"test": "Prova di salvataggio", "success": True}

        result = file_manager.save_json(
            data=test_data, content="Test content", extraction_type="test"
        )

        print(f"✅ File salvato: {result}")
        print("🎉 Test completato!")

    except Exception as e:
        print(f"❌ Errore: {e}")


if __name__ == "__main__":
    test_safe()
    simple_test()
