import pytest
import time
import statistics
from http import HTTPStatus
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import random
import uuid

pytestmark = pytest.mark.asyncio


# ============ BASIC PERFORMANCE TESTS THAT WORK ============

async def test_create_property_performance(client: AsyncClient):
    """Test performance of creating a single property"""
    start_time = time.time()
    
    response = await client.post(
        '/property/',
        json={
            'description': 'Performance test property',
            'number_bedrooms': 'T2',
            'price': 1500.50,
            'area': 85.5,
            'location': 'Performance Test Location',
        },
    )
    
    elapsed_time = time.time() - start_time
    
    assert response.status_code == HTTPStatus.CREATED
    print(f"\n✅ Single property creation time: {elapsed_time:.4f} seconds")
    assert elapsed_time < 0.5  # Should be under 500ms


async def test_bulk_create_performance(client: AsyncClient):
    """Test performance of creating multiple properties sequentially"""
    times = []
    house_types = ['T0', 'T1', 'T2', 'T3']
    
    for i in range(10):
        start_time = time.time()
        
        response = await client.post(
            '/property/',
            json={
                'description': f'Bulk Test Property {i}',
                'number_bedrooms': random.choice(house_types),
                'price': random.uniform(500, 3000),
                'area': random.uniform(30, 150),
                'location': f'Location {i}',
            },
        )
        
        elapsed_time = time.time() - start_time
        times.append(elapsed_time)
        
        assert response.status_code == HTTPStatus.CREATED
    
    avg_time = statistics.mean(times)
    max_time = max(times)
    min_time = min(times)
    
    print(f"\n📊 Bulk create performance (10 properties):")
    print(f"  Average: {avg_time:.4f}s")
    print(f"  Min: {min_time:.4f}s")
    print(f"  Max: {max_time:.4f}s")
    print(f"  Std Dev: {statistics.stdev(times):.4f}s")
    
    assert avg_time < 0.3  # Average should be under 300ms


async def test_database_query_performance(session: AsyncSession):
    """Test raw database query performance"""
    import time
    
    # Test 1: Count query
    from sqlalchemy import func, select
    from backend.model import Property
    
    start_time = time.time()
    result = await session.execute(select(func.count()).select_from(Property))
    count = result.scalar()
    count_time = time.time() - start_time
    
    print(f"\n🗃️ Database query performance:")
    print(f"  Count query time: {count_time:.4f}s")
    print(f"  Total properties: {count}")
    
    assert count_time < 0.1  # Should be very fast
    
    # Test 2: Filtered query
    start_time = time.time()
    result = await session.execute(
        select(Property).where(Property.price > 1000).limit(10)
    )
    properties = result.scalars().all()
    filter_time = time.time() - start_time
    
    print(f"  Filtered query time: {filter_time:.4f}s")
    print(f"  Properties found: {len(properties)}")
    
    assert filter_time < 0.15


async def test_pagination_performance(client: AsyncClient):
    """Test performance with pagination"""
    
    # First create some properties for testing
    for i in range(50):
        await client.post(
            '/property/',
            json={
                'description': f'Pagination test property {i}',
                'number_bedrooms': 'T1',
                'price': 1000 + i*50,
                'area': 50 + i*2,
                'location': f'Location {i % 10}',
            },
        )
    
    # Test different page sizes
    page_sizes = [10, 25, 50]
    
    print(f"\n📄 Pagination performance:")
    for page_size in page_sizes:
        start_time = time.time()
        response = await client.get(f'/property/?skip=0&limit={page_size}')
        elapsed_time = time.time() - start_time
        
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        
        print(f"  Page size {page_size:3d}: {elapsed_time:.4f}s - {len(data.get('properties', []))} properties")


async def test_not_found_performance(client: AsyncClient):
    """Test performance of non-existent resource lookups"""
    times = []
    
    for i in range(10):
        start_time = time.time()
        response = await client.get(f'/property/999999{i}')
        elapsed_time = time.time() - start_time
        times.append(elapsed_time)
        
        assert response.status_code == HTTPStatus.NOT_FOUND
    
    avg_time = statistics.mean(times)
    
    print(f"\n❌ Not-found performance:")
    print(f"  Average 404 response time: {avg_time:.4f}s")
    
    # 404 responses should be fast (faster than actual lookups)
    assert avg_time < 0.05  # Should be under 50ms