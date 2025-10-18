import requests
import json
import psycopg2
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

load_dotenv()

# Test configuration
BASE_URL = "http://localhost:5000"
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:CassidyMadando16@db.amtfabgmtsujurppknfg.supabase.co:5432/postgres')

def test_database_connection():
    print("Testing database connection...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print(f"SUCCESS: Database connected: {db_version[0]}")
        
        tables = ['users', 'employers', 'jobs', 'applications', 'ussd_sessions']
        for table in tables:
            cur.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (table,))
            exists = cur.fetchone()[0]
            status = "SUCCESS" if exists else "FAILED"
            print(f"{status}: Table '{table}': {'Exists' if exists else 'Missing'}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"FAILED: Database connection failed: {e}")
        return False

def test_health_endpoint():
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Health endpoint: {data}")
            return True
        else:
            print(f"FAILED: Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"FAILED: Health endpoint error: {e}")
        return False

def test_ussd_endpoint():
    print("Testing USSD endpoint...")
    
    test_data = {
        "sessionId": "test_session_123",
        "phoneNumber": "+260971234567",
        "text": ""
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ussd", json=test_data)
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: USSD welcome menu received")
            
            test_options = ["1", "2", "3", "4"]
            for option in test_options:
                test_data["text"] = option
                response = requests.post(f"{BASE_URL}/ussd", json=test_data)
                if response.status_code == 200:
                    print(f"SUCCESS: Menu option {option}: Received response")
                else:
                    print(f"FAILED: Menu option {option} failed: {response.status_code}")
            
            return True
        else:
            print(f"FAILED: USSD endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"FAILED: USSD endpoint error: {e}")
        return False

def test_africas_talking_ussd():
    print("Testing Africa's Talking USSD endpoint...")
    
    try:
        response = requests.post(f"{BASE_URL}/at-ussd", data={
            "sessionId": "at_test_123",
            "phoneNumber": "+260971234567",
            "text": ""
        })
        
        if response.status_code == 200:
            print(f"SUCCESS: Africa's Talking USSD welcome received")
            
            test_options = ["1", "2", "3", "4"]
            for option in test_options:
                response = requests.post(f"{BASE_URL}/at-ussd", data={
                    "sessionId": "at_test_123",
                    "phoneNumber": "+260971234567",
                    "text": option
                })
                if response.status_code == 200:
                    print(f"SUCCESS: AT Menu option {option}: Received response")
                else:
                    print(f"FAILED: AT Menu option {option} failed: {response.status_code}")
            
            return True
        else:
            print(f"FAILED: Africa's Talking USSD failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"FAILED: Africa's Talking USSD error: {e}")
        return False

def run_comprehensive_test():
    print("Starting JOWA Comprehensive Test Suite")
    print("=" * 50)
    
    test_results = {}
    
    test_results['database_connection'] = test_database_connection()
    test_results['health_endpoint'] = test_health_endpoint()
    test_results['ussd_endpoint'] = test_ussd_endpoint()
    test_results['africas_talking_ussd'] = test_africas_talking_ussd()
    
    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
    
    print(f"Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! JOWA is working properly!")
    else:
        print("Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    run_comprehensive_test()