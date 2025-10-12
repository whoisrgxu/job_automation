#!/usr/bin/env python3
"""
Proxy testing utility for LinkedIn job scraper
"""
import asyncio
import aiohttp
from typing import List, Dict


async def test_proxy(proxy_url: str, test_url: str = "https://httpbin.org/ip") -> Dict:
    """Test a single proxy"""
    result = {
        'proxy': proxy_url,
        'status': 'failed',
        'response_time': 0,
        'error': None,
        'ip': None
    }
    
    try:
        connector = aiohttp.TCPConnector(limit=1)
        timeout = aiohttp.ClientTimeout(total=10)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            start_time = asyncio.get_event_loop().time()
            
            async with session.get(test_url, proxy=proxy_url) as response:
                response_time = asyncio.get_event_loop().time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    result.update({
                        'status': 'success',
                        'response_time': round(response_time, 2),
                        'ip': data.get('origin', 'Unknown')
                    })
                else:
                    result['error'] = f"HTTP {response.status}"
    
    except asyncio.TimeoutError:
        result['error'] = "Timeout"
    except Exception as e:
        result['error'] = str(e)
    
    return result


async def test_proxy_list(proxy_list: List[str]) -> List[Dict]:
    """Test a list of proxies"""
    print(f"Testing {len(proxy_list)} proxies...")
    print("=" * 60)
    
    tasks = [test_proxy(proxy) for proxy in proxy_list]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successful = []
    failed = []
    
    for result in results:
        if isinstance(result, dict):
            if result['status'] == 'success':
                successful.append(result)
                print(f"✅ {result['proxy']} - {result['response_time']}s - IP: {result['ip']}")
            else:
                failed.append(result)
                print(f"❌ {result['proxy']} - {result['error']}")
        else:
            failed.append({'proxy': 'Unknown', 'error': str(result)})
            print(f"❌ Unknown proxy - {result}")
    
    print("=" * 60)
    print(f"Results: {len(successful)} successful, {len(failed)} failed")
    
    if successful:
        print("\nWorking proxies:")
        for proxy in successful:
            print(f"  - {proxy['proxy']} ({proxy['response_time']}s)")
    
    return successful


async def main():
    """Main function for testing proxies"""
    # Example proxy list - replace with your actual proxies
    test_proxies = [
        # Add your proxy URLs here
        # Example: 'http://username:password@proxy.example.com:8080'
    ]
    
    if not test_proxies:
        print("No proxies configured for testing.")
        print("Add proxy URLs to the test_proxies list in this script.")
        return
    
    working_proxies = await test_proxy_list(test_proxies)
    
    if working_proxies:
        print(f"\n✅ Found {len(working_proxies)} working proxies")
        print("You can use these in your config.py file:")
        print("PROXY_LIST = [")
        for proxy in working_proxies:
            print(f"    '{proxy['proxy']}',")
        print("]")
    else:
        print("\n❌ No working proxies found")
        print("Please check your proxy configuration and credentials")


if __name__ == "__main__":
    asyncio.run(main())
