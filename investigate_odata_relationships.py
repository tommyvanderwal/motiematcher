#!/usr/bin/env python3
"""
Investigate OData Metadata for Entity Relationships
Find navigation properties between Zaak, Stemming, and Besluit entities.
"""

import requests
import xml.etree.ElementTree as ET
from collections import defaultdict

def investigate_odata_metadata():
    """Parse OData $metadata to find entity relationships."""

    base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
    metadata_url = f"{base_url}/$metadata"

    print("🔍 INVESTIGATING ODATA METADATA FOR ENTITY RELATIONSHIPS")
    print("=" * 60)

    try:
        response = requests.get(metadata_url, timeout=30)
        if response.status_code != 200:
            print(f"❌ Failed to get metadata: {response.status_code}")
            return

        # Parse XML metadata
        root = ET.fromstring(response.text)

        # Find entity types
        entity_types = {}
        navigation_properties = defaultdict(list)

        # Namespace handling for OData
        ns = {'edmx': 'http://docs.oasis-open.org/odata/ns/edmx',
              'edm': 'http://docs.oasis-open.org/odata/ns/edm'}

        # Find all EntityType definitions
        for entity_type in root.findall(".//edm:EntityType", ns):
            entity_name = entity_type.get('Name')
            if entity_name:
                entity_types[entity_name] = []
                print(f"\n📋 Entity: {entity_name}")

                # Find properties
                for prop in entity_type.findall(".//edm:Property", ns):
                    prop_name = prop.get('Name')
                    prop_type = prop.get('Type')
                    entity_types[entity_name].append((prop_name, prop_type))
                    print(f"   Property: {prop_name} ({prop_type})")

                # Find navigation properties (relationships)
                for nav_prop in entity_type.findall(".//edm:NavigationProperty", ns):
                    nav_name = nav_prop.get('Name')
                    nav_type = nav_prop.get('Type')
                    navigation_properties[entity_name].append((nav_name, nav_type))
                    print(f"   → Navigation: {nav_name} → {nav_type}")

        print(f"\n🎯 KEY ENTITIES ANALYSIS:")
        key_entities = ['Zaak', 'Stemming', 'Besluit', 'Document']

        for entity in key_entities:
            if entity in entity_types:
                print(f"\n🔗 {entity} Relationships:")
                if entity in navigation_properties:
                    for nav_name, nav_type in navigation_properties[entity]:
                        print(f"   → {nav_name}: {nav_type}")
                else:
                    print("   No navigation properties found")
            else:
                print(f"\n❌ {entity} not found in metadata")

        # Look for specific relationships we're interested in
        print(f"\n🔍 SPECIFIC RELATIONSHIP SEARCH:")
        print("Looking for links between Zaak ↔ Stemming ↔ Besluit")

        # Check if Stemming has navigation to Zaak
        if 'Stemming' in navigation_properties:
            stemming_navs = navigation_properties['Stemming']
            zaak_links = [nav for nav in stemming_navs if 'Zaak' in nav[1]]
            if zaak_links:
                print("✅ FOUND: Stemming → Zaak navigation properties:")
                for nav_name, nav_type in zaak_links:
                    print(f"   {nav_name}: {nav_type}")
            else:
                print("❌ NO direct Stemming → Zaak navigation found")

        # Check if Besluit has navigation to Zaak or Stemming
        if 'Besluit' in navigation_properties:
            besluit_navs = navigation_properties['Besluit']
            zaak_links = [nav for nav in besluit_navs if 'Zaak' in nav[1]]
            stemming_links = [nav for nav in besluit_navs if 'Stemming' in nav[1]]

            if zaak_links or stemming_links:
                print("✅ FOUND: Besluit navigation properties:")
                for nav_name, nav_type in zaak_links + stemming_links:
                    print(f"   {nav_name}: {nav_type}")
            else:
                print("❌ NO Besluit → Zaak/Stemming navigation found")

        # Check reverse: does Zaak have navigation to Stemming/Besluit
        if 'Zaak' in navigation_properties:
            zaak_navs = navigation_properties['Zaak']
            stemming_links = [nav for nav in zaak_navs if 'Stemming' in nav[1]]
            besluit_links = [nav for nav in zaak_navs if 'Besluit' in nav[1]]

            if stemming_links or besluit_links:
                print("✅ FOUND: Zaak → Stemming/Besluit navigation:")
                for nav_name, nav_type in stemming_links + besluit_links:
                    print(f"   {nav_name}: {nav_type}")
            else:
                print("❌ NO Zaak → Stemming/Besluit navigation found")

    except Exception as e:
        print(f"❌ Error parsing metadata: {e}")
        print("This might indicate the API doesn't provide detailed metadata")

def test_expand_queries():
    """Test OData $expand queries to see if relationships can be traversed."""

    base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"

    print(f"\n🧪 TESTING ODATA $expand QUERIES")
    print("=" * 40)

    # Test different expand scenarios
    test_queries = [
        ("Zaak", "$top=1&$expand=Besluit"),
        ("Zaak", "$top=1&$expand=Stemming"),
        ("Besluit", "$top=1&$expand=Zaak"),
        ("Besluit", "$top=1&$expand=Stemming"),
        ("Stemming", "$top=1&$expand=Zaak"),
        ("Stemming", "$top=1&$expand=Besluit"),
    ]

    for entity, query_params in test_queries:
        try:
            url = f"{base_url}/{entity}?{query_params}"
            response = requests.get(url, timeout=15)

            print(f"\n🔗 {entity}?$expand test:")
            print(f"   URL: {url}")
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if 'value' in data and data['value']:
                    record = data['value'][0]
                    expanded_keys = [k for k in record.keys() if not k.startswith('@') and k != entity.lower()]
                    if expanded_keys:
                        print(f"   ✅ Expanded data found: {expanded_keys}")
                    else:
                        print("   ⚠️ No expanded data in response")
                else:
                    print("   ❌ No data in response")
            else:
                print(f"   ❌ Query failed: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    investigate_odata_metadata()
    test_expand_queries()